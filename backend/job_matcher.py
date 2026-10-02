"""Reusable job-description matching helpers."""
from skill_extractor import extract_skills

def match_resume_to_job(resume_skills: list[str], job_text: str):
    required = set(extract_skills(job_text))
    matched = sorted(required.intersection(resume_skills))
    missing = sorted(required.difference(resume_skills))
    return {"matching_skills": matched, "missing_skills": missing,
            "match_score": round(100 * len(matched) / len(required), 1) if required else 0}
