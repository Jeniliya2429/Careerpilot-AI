"""
RAG Interview Coach Agent.
Retrieves practice questions from ChromaDB vector store and generates personalized STAR prep guidance.
"""
from app.ai.state import PipelineState
from app.ai.llm_client import get_llm
from app.ai.json_utils import safe_json_parse
from app.ai.prompts import INTERVIEW_PREP_PROMPT
from app.ai.rag.chroma_setup import get_question_collection
from app.ai.agents.base import append_agent_log

AGENT_NAME = "InterviewCoachAgent"


def run_coach_agent(state: PipelineState) -> dict:
    """
    Coach Agent Node:
    1. RAG retrieval from ChromaDB question bank using JD role title & requirements.
    2. Generates structured STAR guidance for questions tailored to gap analysis.
    """
    errors = state.get("errors", [])
    logs = state.get("agent_logs", [])

    try:
        # Step 1: RAG Retrieval
        collection = get_question_collection()
        role_title = state.get("jd_role_title", "")
        jd_requirements = state.get("jd_requirements", [])
        gap_notes = state.get("gap_notes", "")

        query_text = f"{role_title} interview questions covering: " + ", ".join(jd_requirements[:8])
        results = collection.query(query_texts=[query_text], n_results=8)

        retrieved = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        for doc, meta in zip(docs, metas):
            retrieved.append({
                "question": doc,
                "category": meta.get("category", ""),
                "role_tag": meta.get("role_tag", ""),
            })

        # Step 2: Generate STAR Prep
        llm_light = get_llm(tier="light", temperature=0.4)
        prompt = INTERVIEW_PREP_PROMPT.format(
            jd_requirements=jd_requirements,
            gap_notes=gap_notes,
            retrieved_questions=retrieved,
        )
        response = llm_light.invoke(prompt)
        interview_prep = safe_json_parse(response.content)

        logs = append_agent_log(
            state,
            AGENT_NAME,
            "prep_generated",
            {
                "questions_retrieved": len(retrieved),
                "prep_questions_count": len(interview_prep.get("questions", [])),
            },
        )

        return {
            "retrieved_questions": retrieved,
            "interview_prep": interview_prep,
            "agent_logs": logs,
            "current_agent": AGENT_NAME,
        }
    except Exception as e:
        err_msg = f"{AGENT_NAME} error: {e}"
        logs = append_agent_log(state, AGENT_NAME, "prep_failed", {"error": str(e)})
        return {
            "errors": errors + [err_msg],
            "agent_logs": logs,
            "current_agent": AGENT_NAME,
        }
