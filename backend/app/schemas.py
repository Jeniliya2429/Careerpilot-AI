from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any


# ---------- Auth ----------
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Job Description ----------
class JobDescriptionCreate(BaseModel):
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    raw_text: str


class JobDescriptionOut(BaseModel):
    id: str
    company_name: Optional[str]
    role_title: Optional[str]
    raw_text: str

    class Config:
        from_attributes = True


# ---------- Resume ----------
class ResumeOut(BaseModel):
    id: str
    filename: str

    class Config:
        from_attributes = True


# ---------- Pipeline ----------
class PipelineRunCreate(BaseModel):
    resume_id: str
    jd_id: str


class MockInterviewAnswerRequest(BaseModel):
    question: str
    answer: str


class ApproveTailoringRequest(BaseModel):
    approved: bool
    edited_content: Optional[str] = None  # user's hand-edited version, if any


class PipelineRunOut(BaseModel):
    run_id: str
    status: str
    fit_score: Optional[float] = None
    matching_keywords: Optional[List[str]] = None
    missing_keywords: Optional[List[str]] = None
    gap_notes: Optional[str] = None
    tailored_resume_draft: Optional[str] = None
    tailoring_reflection_notes: Optional[str] = None
    interview_prep: Optional[Dict[str, Any]] = None
    battlecard: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None


# ---------- New Feature Schemas ----------
class SalaryNegotiationResponse(BaseModel):
    salary_range: str
    equity_benchmark: str
    top_leverage_points: List[str]
    email_template_initial: str
    email_template_counter: str
    email_template_competing: str


class ActionPlanResponse(BaseModel):
    day_30_goals: List[str]
    day_60_goals: List[str]
    day_90_goals: List[str]
    key_success_metrics: List[str]


class ElevatorPitchResponse(BaseModel):
    storyteller_pitch: str
    metric_driver_pitch: str
    executive_leader_pitch: str

