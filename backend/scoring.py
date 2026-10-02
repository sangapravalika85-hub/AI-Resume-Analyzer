import re
from skill_extractor import TECHNICAL, ATS_KEYWORDS
def present(text, *terms): return any(re.search(r"\b"+re.escape(t)+r"\b", text, re.I) for t in terms)
def score(data, skills):
    text=data['text']; technical=len(set(skills)&TECHNICAL)
    skills_score=round(min(30, technical*3 + max(0,len(skills)-technical)),1)
    education_score=15 if present(text,"phd","doctorate") else 13 if present(text,"master","m.tech","m.sc","mba") else 11 if present(text,"bachelor","b.tech","b.e.","bsc") else 4 if data['education'] else 0
    projects_n=len(re.findall(r"(?:^|\n)\s*(?:[-•*]|\d+[.)])",data['projects'])); project_score=min(20, 5+projects_n*4) if data['projects'] else 0
    cert_n=len(re.findall(r"(?:certified|certification|certificate)",text,re.I)); certification_score=min(10, cert_n*3) if data['certifications'] or cert_n else 0
    years=re.findall(r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",text,re.I); experience_score=min(10, float(max(years,key=float))*2) if years else (4 if data['experience'] else 0)
    ats_score=round(15*sum(present(text,k) for k in ATS_KEYWORDS)/len(ATS_KEYWORDS),1)
    scores=dict(skills_score=skills_score,education_score=education_score,project_score=project_score,certification_score=certification_score,experience_score=experience_score,ats_score=ats_score)
    scores['overall_score']=round(min(100,sum(scores.values())),1); return scores
def recommendations(resume):
    r=[]
    if resume.project_score<12:r.append("Add more projects with measurable outcomes and your specific contribution.")
    if resume.ats_score<10:r.append("Improve ATS keyword coverage with relevant tools, methods, and role terms.")
    if resume.certification_score<5:r.append("Add relevant professional certifications where applicable.")
    if resume.experience_score<6:r.append("Describe internships, work experience, or leadership outcomes with dates and impact.")
    if not r:r.append("Strong profile—tailor skills and achievements to each target job description.")
    return r
