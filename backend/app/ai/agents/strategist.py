"""
Battlecard Strategist Agent.
Synthesizes candidate profile, fit score, and gap notes into a pre-interview strategy battlecard.
"""
from app.ai.state import PipelineState
from app.ai.llm_client import get_llm
from app.ai.json_utils import safe_json_parse
from app.ai.prompts import BATTLECARD_PROMPT
from app.ai.agents.base import append_agent_log

AGENT_NAME = "BattlecardStrategistAgent"


def run_strategist_agent(state: PipelineState) -> dict:
    """
    Strategist Agent Node:
    Synthesizes pre-interview battlecard. Marks pipeline status as completed.
    """
    errors = state.get("errors", [])
    logs = state.get("agent_logs", [])

    try:
        resume_summary = state.get("resume_summary", "")
        jd_role_title = state.get("jd_role_title", "")
        jd_company = state.get("jd_company", "")
        fit_score = state.get("fit_score", 0)
        matching_keywords = state.get("matching_keywords", [])
        missing_keywords = state.get("missing_keywords", [])

        llm_heavy = get_llm(tier="heavy", temperature=0.5)
        prompt = BATTLECARD_PROMPT.format(
            resume_summary=resume_summary,
            jd_role_title=jd_role_title,
            jd_company=jd_company,
            fit_score=fit_score,
            matching_keywords=matching_keywords,
            missing_keywords=missing_keywords,
        )
        response = llm_heavy.invoke(prompt)
        battlecard = safe_json_parse(response.content)

        logs = append_agent_log(
            state,
            AGENT_NAME,
            "battlecard_generated",
            {
                "fit_score": fit_score,
                "role_title": jd_role_title,
                "company": jd_company,
            },
        )

        return {
            "battlecard": battlecard,
            "agent_logs": logs,
            "current_agent": AGENT_NAME,
            "status": "completed",
        }
    except Exception as e:
        err_msg = f"{AGENT_NAME} error: {e}"
        logs = append_agent_log(state, AGENT_NAME, "battlecard_failed", {"error": str(e)})
        return {
            "errors": errors + [err_msg],
            "agent_logs": logs,
            "current_agent": AGENT_NAME,
            "status": "failed",
        }
