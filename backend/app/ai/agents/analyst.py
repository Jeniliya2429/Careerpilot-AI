"""
Resume & JD Analyst Agent.
Combines resume parsing, JD requirement parsing, and candidate-job gap analysis.
"""
from app.ai.state import PipelineState
from app.ai.llm_client import get_llm
from app.ai.json_utils import safe_json_parse
from app.ai.prompts import PARSE_RESUME_PROMPT, PARSE_JD_PROMPT, GAP_ANALYSIS_PROMPT
from app.ai.agents.base import append_agent_log

AGENT_NAME = "ResumeAnalystAgent"


def run_analyst_agent(state: PipelineState) -> dict:
    """
    Analyst Agent Node:
    1. Parses resume text for skills & summary.
    2. Parses job description for requirements, title, company.
    3. Performs gap analysis and calculates candidate fit score.
    """
    errors = state.get("errors", [])
    logs = state.get("agent_logs", [])

    try:
        resume_text = state.get("resume_text", "")
        jd_text = state.get("jd_text", "")

        # Step 1: Parse Resume
        llm_light = get_llm(tier="light", temperature=0.1)
        r_prompt = PARSE_RESUME_PROMPT.format(resume_text=resume_text)
        r_res = llm_light.invoke(r_prompt)
        r_data = safe_json_parse(r_res.content)
        skills = r_data.get("skills", [])
        summary = r_data.get("summary", "")

        # Step 2: Parse JD
        j_prompt = PARSE_JD_PROMPT.format(jd_text=jd_text)
        j_res = llm_light.invoke(j_prompt)
        j_data = safe_json_parse(j_res.content)
        requirements = j_data.get("requirements", [])
        role_title = j_data.get("role_title", "")
        company = j_data.get("company", "")

        # Step 3: Gap Analysis
        g_prompt = GAP_ANALYSIS_PROMPT.format(resume_skills=skills, jd_requirements=requirements)
        g_res = llm_light.invoke(g_prompt)
        g_data = safe_json_parse(g_res.content)

        fit_score = float(g_data.get("fit_score", 0))
        matching_keywords = g_data.get("matching_keywords", [])
        missing_keywords = g_data.get("missing_keywords", [])
        gap_notes = g_data.get("gap_notes", "")

        logs = append_agent_log(
            state,
            AGENT_NAME,
            "analysis_completed",
            {
                "fit_score": fit_score,
                "skills_found": len(skills),
                "requirements_found": len(requirements),
                "missing_keywords_count": len(missing_keywords),
            },
        )

        return {
            "resume_skills": skills,
            "resume_summary": summary,
            "jd_requirements": requirements,
            "jd_role_title": role_title,
            "jd_company": company,
            "fit_score": fit_score,
            "matching_keywords": matching_keywords,
            "missing_keywords": missing_keywords,
            "gap_notes": gap_notes,
            "agent_logs": logs,
            "current_agent": AGENT_NAME,
        }
    except Exception as e:
        err_msg = f"{AGENT_NAME} error: {e}"
        logs = append_agent_log(state, AGENT_NAME, "analysis_failed", {"error": str(e)})
        return {
            "errors": errors + [err_msg],
            "agent_logs": logs,
            "current_agent": AGENT_NAME,
            "status": "failed",
        }
