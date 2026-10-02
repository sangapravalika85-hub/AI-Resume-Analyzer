"""Query helpers. Ranking order is intentionally enforced at the database layer."""
from sqlalchemy.orm import Session
from models import Resume

def ranked_resumes(db: Session):
    return db.query(Resume).order_by(Resume.overall_score.desc(), Resume.candidate_name.asc())
