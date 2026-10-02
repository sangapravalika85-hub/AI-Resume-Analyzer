from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class Resume(Base):
    __tablename__ = "resumes"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_name: Mapped[str] = mapped_column(String(180), index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    filename: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    stored_filename: Mapped[str] = mapped_column(String(255))
    resume_text: Mapped[str] = mapped_column(Text)
    education: Mapped[str] = mapped_column(Text, default="")
    projects: Mapped[str] = mapped_column(Text, default="")
    certifications: Mapped[str] = mapped_column(Text, default="")
    experience: Mapped[str] = mapped_column(Text, default="")
    skills_score: Mapped[float] = mapped_column(Float)
    education_score: Mapped[float] = mapped_column(Float)
    project_score: Mapped[float] = mapped_column(Float)
    certification_score: Mapped[float] = mapped_column(Float)
    experience_score: Mapped[float] = mapped_column(Float)
    ats_score: Mapped[float] = mapped_column(Float)
    overall_score: Mapped[float] = mapped_column(Float, index=True)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    skills: Mapped[list["ResumeSkill"]] = relationship(cascade="all, delete-orphan", back_populates="resume")
    matches: Mapped[list["ResumeJobMatch"]] = relationship(cascade="all, delete-orphan", back_populates="resume")

class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

class ResumeSkill(Base):
    __tablename__ = "resume_skills"
    __table_args__ = (UniqueConstraint("resume_id", "skill_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))
    resume: Mapped[Resume] = relationship(back_populates="skills")
    skill: Mapped[Skill] = relationship()

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(180), default="Job description")
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ResumeJobMatch(Base):
    __tablename__ = "resume_job_matches"
    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    job_description_id: Mapped[int] = mapped_column(ForeignKey("job_descriptions.id"))
    match_score: Mapped[float] = mapped_column(Float)
    matching_skills: Mapped[str] = mapped_column(Text, default="")
    missing_skills: Mapped[str] = mapped_column(Text, default="")
    resume: Mapped[Resume] = relationship(back_populates="matches")
