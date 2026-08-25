"""
Supervisor Agent (Router / Orchestrator).
Evaluates current state, agent execution logs, and audit outputs to dynamically determine graph routing.
"""
from app.ai.state import PipelineState
from app.ai.agents.base import append_agent_log

AGENT_NAME = "SupervisorAgent"
MAX_REVISIONS = 2


def run_supervisor_agent(state: PipelineState) -> dict:
    """
    Supervisor Agent Node:
    Determines next router step (`next_step`) based on overall workflow progress and actor-critic audit outputs.
    """
    current = state.get("current_agent", "")
    audit_history = state.get("audit_history") or []
    revision_count = state.get("tailoring_revision_count", 0)

    # Determine next routing decision
    if not current or current == AGENT_NAME:
        next_step = "analyst"
    elif current == "ResumeAnalystAgent":
        next_step = "tailor"
    elif current == "ResumeTailorAgent":
        next_step = "auditor"
    elif current == "ComplianceAuditorAgent":
        latest_audit = audit_history[-1] if audit_history else {}
        has_fabrication = latest_audit.get("has_fabrication", False)
        
        if has_fabrication and revision_count < MAX_REVISIONS:
            next_step = "tailor"  # Route back to tailor actor to fix fabrication issues
        else:
            next_step = "tailor_resume"  # Proceed to human-in-the-loop interrupt checkpoint
    elif current == "InterviewCoachAgent":
        next_step = "strategist"
    elif current == "BattlecardStrategistAgent":
        next_step = "end"
    else:
        next_step = "end"

    logs = append_agent_log(
        state,
        AGENT_NAME,
        "routing_decision",
        {"previous_agent": current, "next_step": next_step},
    )

    return {
        "next_step": next_step,
        "agent_logs": logs,
        "current_agent": AGENT_NAME,
    }


def route_next_agent(state: PipelineState) -> str:
    """
    Conditional edge function used by LangGraph StateGraph.
    Reads `next_step` from state and returns node key string.
    """
    return state.get("next_step", "end")
