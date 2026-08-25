"""
All LangGraph node functions for the CareerPilot AI pipeline.

Kept in one module (per project layout) but each node is a small, pure
function of (state) -> partial_state_update, and each calls a separate
`_call_llm_*` helper so tests can mock just the LLM call without
touching node control-flow logic.
"""
from app.ai.state import PipelineState
from app.ai.llm_client import get_llm
from app.ai.json_utils import safe_json_parse
from app.ai.prompts import (
    PARSE_RESUME_PROMPT,
    PARSE_JD_PROMPT,
    GAP_ANALYSIS_PROMPT,
    TAILOR_RESUME_PROMPT,
    SELF_REFLECTION_PROMPT,
    INTERVIEW_PREP_PROMPT,
    BATTLECARD_PROMPT,
)
from app.ai.rag.chroma_setup import get_question_collection

MAX_TAILOR_REVISIONS = 2


# =================================================================
# Node 1: parse_resume
# =================================================================
def _call_llm_parse_resume(resume_text: str) -> dict:
    llm = get_llm(tier="light", temperature=0.1)
    prompt = PARSE_RESUME_PROMPT.format(resume_text=resume_text)
    response = llm.invoke(prompt)
    return safe_json_parse(response.content)


def parse_resume_node(state: PipelineState) -> dict:
    try:
        data = _call_llm_parse_resume(state["resume_text"])
        return {
            "resume_skills": data.get("skills", []),
            "resume_summary": data.get("summary", ""),
        }
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"parse_resume_node: {e}"], "status": "failed"}


# =================================================================
# Node 2: parse_jd
# =================================================================
def _call_llm_parse_jd(jd_text: str) -> dict:
    llm = get_llm(tier="light", temperature=0.1)
    prompt = PARSE_JD_PROMPT.format(jd_text=jd_text)
    response = llm.invoke(prompt)
    return safe_json_parse(response.content)


def parse_jd_node(state: PipelineState) -> dict:
    try:
        data = _call_llm_parse_jd(state["jd_text"])
        return {
            "jd_requirements": data.get("requirements", []),
            "jd_role_title": data.get("role_title", ""),
            "jd_company": data.get("company", ""),
        }
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"parse_jd_node: {e}"], "status": "failed"}


# =================================================================
# Node 3: gap_analysis
# =================================================================
def _call_llm_gap_analysis(resume_skills, jd_requirements) -> dict:
    llm = get_llm(tier="light", temperature=0.2)
    prompt = GAP_ANALYSIS_PROMPT.format(resume_skills=resume_skills, jd_requirements=jd_requirements)
    response = llm.invoke(prompt)
    return safe_json_parse(response.content)


def gap_analysis_node(state: PipelineState) -> dict:
    try:
        data = _call_llm_gap_analysis(state.get("resume_skills", []), state.get("jd_requirements", []))
        return {
            "fit_score": float(data.get("fit_score", 0)),
            "matching_keywords": data.get("matching_keywords", []),
            "missing_keywords": data.get("missing_keywords", []),
            "gap_notes": data.get("gap_notes", ""),
        }
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"gap_analysis_node: {e}"], "status": "failed"}


# =================================================================
# Node 4: tailor_resume (+ self-reflection fabrication guardrail loop)
# =================================================================
def _call_llm_draft_tailored_resume(resume_text, jd_requirements, missing_keywords, extra_notes=""):
    llm = get_llm(tier="heavy", temperature=0.4)
    prompt = TAILOR_RESUME_PROMPT.format(
        resume_text=resume_text, jd_requirements=jd_requirements, missing_keywords=missing_keywords,
    )
    if extra_notes:
        prompt += f"\n\nIMPORTANT — fix these fabrication issues from the previous draft:\n{extra_notes}"
    return llm.invoke(prompt).content


def _call_llm_reflect(original_resume: str, tailored_resume: str) -> dict:
    llm = get_llm(tier="light", temperature=0.0)
    prompt = SELF_REFLECTION_PROMPT.format(original_resume=original_resume, tailored_resume=tailored_resume)
    response = llm.invoke(prompt)
    return safe_json_parse(response.content)


def tailor_resume_node(state: PipelineState) -> dict:
    try:
        resume_text = state["resume_text"]
        draft = _call_llm_draft_tailored_resume(
            resume_text, state.get("jd_requirements", []), state.get("missing_keywords", [])
        )

        revision_count = 0
        reflection = _call_llm_reflect(resume_text, draft)

        while reflection.get("has_fabrication") and revision_count < MAX_TAILOR_REVISIONS:
            issues = "; ".join(reflection.get("issues", []))
            draft = _call_llm_draft_tailored_resume(
                resume_text, state.get("jd_requirements", []), state.get("missing_keywords", []),
                extra_notes=issues,
            )
            revision_count += 1
            reflection = _call_llm_reflect(resume_text, draft)

        # NOTE: no "awaiting_approval"/status write needed here — the
        # actual pause is enforced by LangGraph's interrupt_after
        # mechanism in graph.py, not by a status flag. The status field
        # is set by pipeline_service.py after the graph actually halts.
        return {
            "tailored_resume_draft": draft,
            "tailoring_reflection_notes": reflection.get("notes", ""),
            "tailoring_revision_count": revision_count,
        }
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"tailor_resume_node: {e}"], "status": "failed"}


# =================================================================
# Node 5: retrieve_questions (ChromaDB RAG)
# =================================================================
def retrieve_questions_node(state: PipelineState) -> dict:
    try:
        collection = get_question_collection()
        query_text = (
            f"{state.get('jd_role_title', '')} interview questions covering: "
            + ", ".join(state.get("jd_requirements", [])[:8])
        )
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
        return {"retrieved_questions": retrieved}
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"retrieve_questions_node: {e}"]}


# =================================================================
# Node 6: generate_prep
# =================================================================
def _call_llm_generate_prep(jd_requirements, gap_notes, retrieved_questions) -> dict:
    llm = get_llm(tier="light", temperature=0.4)
    prompt = INTERVIEW_PREP_PROMPT.format(
        jd_requirements=jd_requirements, gap_notes=gap_notes, retrieved_questions=retrieved_questions,
    )
    response = llm.invoke(prompt)
    return safe_json_parse(response.content)


def generate_prep_node(state: PipelineState) -> dict:
    try:
        data = _call_llm_generate_prep(
            state.get("jd_requirements", []), state.get("gap_notes", ""), state.get("retrieved_questions", []),
        )
        return {"interview_prep": data}
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"generate_prep_node: {e}"]}


# =================================================================
# Node 7: generate_battlecard (final node)
# =================================================================
def _call_llm_generate_battlecard(resume_summary, jd_role_title, jd_company, fit_score,
                                   matching_keywords, missing_keywords) -> dict:
    llm = get_llm(tier="heavy", temperature=0.5)
    prompt = BATTLECARD_PROMPT.format(
        resume_summary=resume_summary, jd_role_title=jd_role_title, jd_company=jd_company,
        fit_score=fit_score, matching_keywords=matching_keywords, missing_keywords=missing_keywords,
    )
    response = llm.invoke(prompt)
    return safe_json_parse(response.content)


def generate_battlecard_node(state: PipelineState) -> dict:
    try:
        data = _call_llm_generate_battlecard(
            state.get("resume_summary", ""), state.get("jd_role_title", ""), state.get("jd_company", ""),
            state.get("fit_score", 0), state.get("matching_keywords", []), state.get("missing_keywords", []),
        )
        return {"battlecard": data, "status": "completed"}
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"generate_battlecard_node: {e}"], "status": "failed"}
