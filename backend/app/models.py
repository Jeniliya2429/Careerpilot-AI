"""
SQLAlchemy ORM models — mirrors the Supabase Postgres schema, but
created/managed via SQLAlchemy (Base.metadata.create_all) rather than
hand-written SQL migrations, per project spec.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=_now)

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")
    pipeline_runs = relationship("PipelineRun", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)  # path inside Supabase Storage bucket
    extracted_text = Column(Text)
    uploaded_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="resumes")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    company_name = Column(String)
    role_title = Column(String)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="job_descriptions")


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    resume_id = Column(String, ForeignKey("resumes.id", ondelete="CASCADE"))
    jd_id = Column(String, ForeignKey("job_descriptions.id", ondelete="CASCADE"))

    # pending | awaiting_approval | rejected | completed | failed
    status = Column(String, default="pending")
    fit_score = Column(Float, nullable=True)
    missing_keywords = Column(JSON, default=list)
    matching_keywords = Column(JSON, default=list)
    state_json = Column(JSON, default=dict)  # full LangGraph state snapshot
    created_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="pipeline_runs")
    tailored_resume = relationship("TailoredResume", back_populates="run", uselist=False, cascade="all, delete-orphan")
    battlecard = relationship("Battlecard", back_populates="run", uselist=False, cascade="all, delete-orphan")


class TailoredResume(Base):
    __tablename__ = "tailored_resumes"

    id = Column(String, primary_key=True, default=_uuid)
    run_id = Column(String, ForeignKey("pipeline_runs.id", ondelete="CASCADE"), unique=True)
    draft_content = Column(Text)       # AI draft, pre-approval
    final_content = Column(Text)       # human-approved / human-edited version
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_now)

    run = relationship("PipelineRun", back_populates="tailored_resume")


class Battlecard(Base):
    __tablename__ = "battlecards"

    id = Column(String, primary_key=True, default=_uuid)
    run_id = Column(String, ForeignKey("pipeline_runs.id", ondelete="CASCADE"), unique=True)
    content_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=_now)

    run = relationship("PipelineRun", back_populates="battlecard")
