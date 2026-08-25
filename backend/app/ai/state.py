"""
Shared state that flows through every node of the LangGraph pipeline.
Every node reads what it needs and returns a partial dict update —
LangGraph merges it back into the running state automatically.
"""
from typing import TypedDict, List, Dict


class PipelineState(TypedDict, total=False):
    # ---- identifiers ----
    run_id: str
    user_id: str
    candidate_name: str

    # ---- inputs ----
    resume_text: str
    jd_text: str

    # ---- parse_resume ----
    resume_skills: List[str]
    resume_summary: str

    # ---- parse_jd ----
    jd_requirements: List[str]
    jd_role_title: str
    jd_company: str

    # ---- gap_analysis ----
    fit_score: float
    missing_keywords: List[str]
    matching_keywords: List[str]
    gap_notes: str

    # ---- tailor_resume (+ self-reflection fabrication guardrail) ----
    tailored_resume_draft: str
    tailoring_reflection_notes: str
    tailoring_revision_count: int

    # ---- human-in-the-loop checkpoint (REAL LangGraph interrupt) ----
    tailored_resume_final: str   # set only after human approval
    approved: bool

    # ---- retrieve_questions (ChromaDB RAG) ----
    retrieved_questions: List[Dict]

    # ---- generate_prep (STAR-format interview prep) ----
    interview_prep: Dict

    # ---- generate_battlecard ----
    battlecard: Dict

    # ---- multi-agent logs & audit traces ----
    agent_logs: List[Dict]       # traces of agent messages and decisions
    audit_history: List[Dict]    # logs of critic auditor evaluations
    current_agent: str           # name of the currently active agent/supervisor
    next_step: str               # router decision for supervisor

    # ---- bookkeeping ----
    status: str          # pending | awaiting_approval | rejected | completed | failed
    errors: List[str]
