"""
Multi-Agent Collaborative LangGraph StateGraph for CareerPilot AI.

Architecture:
- Supervisor Agent (Router / Orchestrator)
- Resume & JD Analyst Agent
- Resume Tailor Agent (Actor) & Compliance Auditor Agent (Critic) Loop
- Human-in-the-Loop Interrupt Checkpoint (`interrupt_after=["tailor_resume"]`)
- RAG Interview Coach Agent
- Battlecard Strategist Agent
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.ai.state import PipelineState
from app.ai.agents.analyst import run_analyst_agent
from app.ai.agents.tailor import run_tailor_agent
from app.ai.agents.auditor import run_auditor_agent
from app.ai.agents.coach import run_coach_agent
from app.ai.agents.strategist import run_strategist_agent
from app.ai.agents.supervisor import run_supervisor_agent, route_next_agent


def human_checkpoint_node(state: PipelineState) -> dict:
    """
    Checkpoint node that marks the end of automated tailoring & auditing.
    The graph genuinely HALTS after this node due to `interrupt_after=["tailor_resume"]`.
    """
    return {
        "current_agent": "HumanApprovalCheckpoint",
    }


def build_graph():
    graph = StateGraph(PipelineState)

    # Add Multi-Agent Worker and Supervisor nodes
    graph.add_node("analyst", run_analyst_agent)
    graph.add_node("tailor", run_tailor_agent)
    graph.add_node("auditor", run_auditor_agent)
    graph.add_node("supervisor", run_supervisor_agent)
    graph.add_node("tailor_resume", human_checkpoint_node)
    graph.add_node("coach", run_coach_agent)
    graph.add_node("strategist", run_strategist_agent)

    # Entry point -> Analyst Agent
    graph.set_entry_point("analyst")

    # Analyst -> Supervisor
    graph.add_edge("analyst", "supervisor")

    # Supervisor conditional routing
    graph.add_conditional_edges(
        "supervisor",
        route_next_agent,
        {
            "tailor": "tailor",
            "tailor_resume": "tailor_resume",
            "end": END,
        },
    )

    # Actor-Critic Loop: Tailor -> Auditor -> Supervisor
    graph.add_edge("tailor", "auditor")
    graph.add_edge("auditor", "supervisor")

    # Post-interrupt resuming workflow: tailor_resume -> coach -> strategist -> END
    graph.add_edge("tailor_resume", "coach")
    graph.add_edge("coach", "strategist")
    graph.add_edge("strategist", END)

    # In-memory checkpointer keyed by thread_id (= run_id)
    checkpointer = MemorySaver()

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_after=["tailor_resume"],  # Real human-in-the-loop halt
    )


# Singleton compiled graph reused across requests within this process.
pipeline_graph = build_graph()
