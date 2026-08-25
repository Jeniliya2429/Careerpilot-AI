"""
Compliance & Fact-Checking Auditor Agent (Critic).
Evaluates tailored resume drafts against original resume text for hallucination/fabrication.
"""
from app.ai.state import PipelineState
from app.ai.llm_client import get_llm
from app.ai.json_utils import safe_json_parse
from app.ai.prompts import SELF_REFLECTION_PROMPT
from app.ai.agents.base import append_agent_log

AGENT_NAME = "ComplianceAuditorAgent"


def run_auditor_agent(state: PipelineState) -> dict:
    """
    Auditor Agent Node (Critic):
    Performs fact-checking audit on tailored resume draft vs original resume.
    Appends structured report to `audit_history`.
    """
    errors = state.get("errors", [])
    logs = state.get("agent_logs", [])
    audit_history = state.get("audit_history") or []

    try:
        original_resume = state.get("resume_text", "")
        tailored_resume = state.get("tailored_resume_draft", "")

        llm_light = get_llm(tier="light", temperature=0.0)
        prompt = SELF_REFLECTION_PROMPT.format(
            original_resume=original_resume,
            tailored_resume=tailored_resume,
        )
        response = llm_light.invoke(prompt)
        reflection = safe_json_parse(response.content)

        has_fabrication = reflection.get("has_fabrication", False)
        issues = reflection.get("issues", [])
        notes = reflection.get("notes", "")

        audit_entry = {
            "has_fabrication": has_fabrication,
            "issues": issues,
            "notes": notes,
        }
        updated_audit_history = audit_history + [audit_entry]

        action_name = "audit_flagged_issues" if has_fabrication else "audit_passed"
        logs = append_agent_log(
            state,
            AGENT_NAME,
            action_name,
            {
                "has_fabrication": has_fabrication,
                "issues_count": len(issues),
                "notes": notes,
            },
        )

        return {
            "tailoring_reflection_notes": notes,
            "audit_history": updated_audit_history,
            "agent_logs": logs,
            "current_agent": AGENT_NAME,
        }
    except Exception as e:
        err_msg = f"{AGENT_NAME} error: {e}"
        logs = append_agent_log(state, AGENT_NAME, "audit_failed", {"error": str(e)})
        return {
            "errors": errors + [err_msg],
            "agent_logs": logs,
            "current_agent": AGENT_NAME,
        }
