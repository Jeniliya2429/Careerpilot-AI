"""
Resume Tailoring Agent (Actor).
Drafts and refines candidate resume based on job requirements and compliance auditor feedback.
"""
from app.ai.state import PipelineState
from app.ai.llm_client import get_llm
from app.ai.prompts import TAILOR_RESUME_PROMPT
from app.ai.agents.base import append_agent_log

AGENT_NAME = "ResumeTailorAgent"


def run_tailor_agent(state: PipelineState) -> dict:
    """
    Tailor Agent Node (Actor):
    Drafts tailored resume text. If previous audit history contains issues, incorporates them as correction guidance.
    """
    errors = state.get("errors", [])
    logs = state.get("agent_logs", [])
    audit_history = state.get("audit_history") or []
    revision_count = state.get("tailoring_revision_count", 0)

    try:
        resume_text = state.get("resume_text", "")
        jd_requirements = state.get("jd_requirements", [])
        missing_keywords = state.get("missing_keywords", [])

        # Check if latest audit history has feedback
        extra_notes = ""
        if audit_history:
            latest_audit = audit_history[-1]
            issues = latest_audit.get("issues", [])
            if issues:
                extra_notes = "; ".join(issues)

        llm_heavy = get_llm(tier="heavy", temperature=0.4)
        prompt = TAILOR_RESUME_PROMPT.format(
            resume_text=resume_text,
            jd_requirements=jd_requirements,
            missing_keywords=missing_keywords,
        )
        if extra_notes:
            prompt += f"\n\nIMPORTANT — fix these fabrication issues from the previous draft:\n{extra_notes}"

        draft = llm_heavy.invoke(prompt).content

        new_revision_count = revision_count + (1 if audit_history else 0)

        logs = append_agent_log(
            state,
            AGENT_NAME,
            "draft_generated",
            {
                "revision": new_revision_count,
                "draft_length": len(draft),
                "had_feedback": bool(extra_notes),
            },
        )

        return {
            "tailored_resume_draft": draft,
            "tailoring_revision_count": new_revision_count,
            "agent_logs": logs,
            "current_agent": AGENT_NAME,
        }
    except Exception as e:
        err_msg = f"{AGENT_NAME} error: {e}"
        logs = append_agent_log(state, AGENT_NAME, "draft_failed", {"error": str(e)})
        return {
            "errors": errors + [err_msg],
            "agent_logs": logs,
            "current_agent": AGENT_NAME,
            "status": "failed",
        }
