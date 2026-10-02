import os, json, shutil, uuid
from collections import Counter
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from database import Base, engine, get_db
from models import Resume, Skill, ResumeSkill, JobDescription, ResumeJobMatch
from resume_parser import parse_pdf
from skill_extractor import extract_skills
from scoring import score, recommendations

Base.metadata.create_all(bind=engine)
app=FastAPI(title="AI Resume Analyzer with Skill Extraction, Rule-Based Scoring, and Visualization Dashboard", version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=os.getenv("CORS_ORIGINS","http://localhost:5173,http://127.0.0.1:5173").split(","),allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
UPLOADS=Path("uploads"); UPLOADS.mkdir(exist_ok=True)
MAX=int(os.getenv("MAX_FILE_SIZE_MB","10"))*1024*1024
def ordered(db): return db.query(Resume).options(joinedload(Resume.skills).joinedload(ResumeSkill.skill)).order_by(Resume.overall_score.desc(),Resume.candidate_name.asc())
def serialize(r, rank=None, details=False):
    d={k:getattr(r,k) for k in ["id","candidate_name","email","phone","filename","skills_score","education_score","project_score","certification_score","experience_score","ats_score","overall_score"]}; d["upload_date"]=r.upload_date.isoformat(); d["rank"]=rank
    d["skills"] = [x.skill.name for x in r.skills]
    if details: d.update({"resume_text":r.resume_text,"education":r.education,"projects":r.projects,"certifications":r.certifications,"experience":r.experience,"recommendations":recommendations(r)})
    return d
@app.get("/health")
def health(): return {"status":"ok"}
@app.post("/upload-resumes")
async def upload_resumes(files:list[UploadFile]=File(...), db:Session=Depends(get_db)):
    if not files: raise HTTPException(400,"Choose at least one PDF")
    if len(files)>150: raise HTTPException(400,"A maximum of 150 PDFs may be uploaded at once")
    success=[]; failed=[]
    for f in files:
        try:
            if not f.filename or not f.filename.lower().endswith('.pdf'): raise ValueError("Only PDF files are accepted")
            raw=await f.read()
            if not raw.startswith(b'%PDF'): raise ValueError("Invalid PDF signature")
            if len(raw)>MAX: raise ValueError(f"File exceeds {MAX//1024//1024} MB limit")
            if db.scalar(select(Resume.id).where(Resume.filename==f.filename)): raise ValueError("A resume with this filename already exists")
            data=parse_pdf(raw,f.filename); found=extract_skills(data['text']); values=score(data,found)
            saved=f"{uuid.uuid4().hex}.pdf"; (UPLOADS/saved).write_bytes(raw)
            r=Resume(candidate_name=data['name'],email=data['email'],phone=data['phone'],filename=f.filename,stored_filename=saved,resume_text=data['text'],education=data['education'],projects=data['projects'],certifications=data['certifications'],experience=data['experience'],**values); db.add(r); db.flush()
            for name in found:
                skill=db.scalar(select(Skill).where(Skill.name==name)) or Skill(name=name)
                db.add(skill); db.flush(); db.add(ResumeSkill(resume_id=r.id,skill_id=skill.id))
            db.commit(); success.append({"filename":f.filename,"id":r.id,"overall_score":r.overall_score})
        except Exception as e:
            db.rollback(); failed.append({"filename":f.filename,"error":str(e)})
    return {"successful":success,"failed":failed,"processed":len(success)+len(failed)}
@app.post("/analyze-resumes")
async def analyze_resumes(files:list[UploadFile]=File(...),db:Session=Depends(get_db)): return await upload_resumes(files,db)
@app.get("/resumes")
def resumes(search:str="", min_score:float|None=None, page:int=1, page_size:int=20, db:Session=Depends(get_db)):
    q=ordered(db)
    if search:q=q.filter(Resume.candidate_name.ilike(f"%{search}%") | Resume.email.ilike(f"%{search}%"))
    if min_score is not None:q=q.filter(Resume.overall_score>=min_score)
    total=q.count(); rows=q.offset((max(page,1)-1)*min(page_size,100)).limit(min(page_size,100)).all()
    all_ids=[x.id for x in ordered(db).all()]; ranks={id:i+1 for i,id in enumerate(all_ids)}
    return {"items":[serialize(r,ranks[r.id]) for r in rows],"total":total,"page":page,"page_size":min(page_size,100)}
@app.get("/resumes/{resume_id}")
def resume(resume_id:int,db:Session=Depends(get_db)):
    r=ordered(db).filter(Resume.id==resume_id).first()
    if not r:raise HTTPException(404,"Resume not found")
    rank=ordered(db).filter((Resume.overall_score>r.overall_score)|((Resume.overall_score==r.overall_score)&(Resume.candidate_name<r.candidate_name))).count()+1
    return serialize(r,rank,True)
@app.delete("/resumes/{resume_id}")
def delete_resume(resume_id:int,db:Session=Depends(get_db)):
    r=db.get(Resume,resume_id)
    if not r:raise HTTPException(404,"Resume not found")
    path=UPLOADS/r.stored_filename; db.delete(r); db.commit()
    if path.exists():path.unlink()
    return {"message":"Resume deleted"}
@app.get("/dashboard")
def dashboard(db:Session=Depends(get_db)):
    rs=ordered(db).all(); scores=[r.overall_score for r in rs]; skills=Counter(s.skill.name for r in rs for s in r.skills)
    return {"total_resumes":len(rs),"average_score":round(sum(scores)/len(scores),1) if scores else 0,"highest_score":max(scores,default=0),"lowest_score":min(scores,default=0),"score_distribution":[{"range":"90-100","count":sum(x>=90 for x in scores)},{"range":"80-89","count":sum(80<=x<90 for x in scores)},{"range":"70-79","count":sum(70<=x<80 for x in scores)},{"range":"60-69","count":sum(60<=x<70 for x in scores)},{"range":"Below 60","count":sum(x<60 for x in scores)}],"candidate_scores":[{"name":r.candidate_name,"score":r.overall_score} for r in rs[:10]],"category_scores":[{"category":n,"score":round(sum(getattr(r,k) for r in rs)/len(rs),1) if rs else 0,"maximum":m} for n,k,m in [("Skills","skills_score",30),("Education","education_score",15),("Projects","project_score",20),("Certifications","certification_score",10),("Experience","experience_score",10),("ATS","ats_score",15)]],"skill_distribution":[{"skill":k,"count":v} for k,v in skills.most_common(10)],"recent_uploads":[serialize(r,i+1) for i,r in enumerate(rs[:5])]}
@app.get("/skills")
def skills(db:Session=Depends(get_db)): return [x.name for x in db.scalars(select(Skill).order_by(Skill.name)).all()]
@app.post("/match-job")
def match_job(payload:dict,db:Session=Depends(get_db)):
    text=str(payload.get("description","")).strip(); ids=payload.get("resume_ids")
    if len(text)<10:raise HTTPException(400,"A job description of at least 10 characters is required")
    required=set(extract_skills(text))
    if not required:raise HTTPException(400,"No supported skills were found in the job description")
    job=JobDescription(title=str(payload.get("title","Job description"))[:180],text=text); db.add(job);db.flush(); rows=ordered(db).filter(Resume.id.in_(ids)) if ids else ordered(db)
    output=[]
    for r in rows.all():
        have={x.skill.name for x in r.skills}; matching=sorted(required&have); missing=sorted(required-have); pct=round(100*len(matching)/len(required),1)
        db.add(ResumeJobMatch(resume_id=r.id,job_description_id=job.id,match_score=pct,matching_skills=json.dumps(matching),missing_skills=json.dumps(missing)));output.append({"resume_id":r.id,"candidate_name":r.candidate_name,"match_score":pct,"matching_skills":matching,"missing_skills":missing,"recommended_skills":missing})
    db.commit(); return {"job_id":job.id,"results":output}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
