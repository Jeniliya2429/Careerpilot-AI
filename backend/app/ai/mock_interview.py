"""
Live mock-interview answer scoring. This sits outside the LangGraph
pipeline (it's an interactive, repeatable loop rather than a one-shot
pipeline stage) but reuses the same LLM client and JSON-safety helpers.
"""
from app.ai.llm_client import get_llm
from app.ai.json_utils import safe_json_parse
from app.ai.prompts import MOCK_INTERVIEW_FEEDBACK_PROMPT


def score_mock_answer(question: str, answer: str, jd_requirements: list) -> dict:
    llm = get_llm(tier="light", temperature=0.3)
    prompt = MOCK_INTERVIEW_FEEDBACK_PROMPT.format(
        question=question, jd_requirements=jd_requirements, answer=answer,
    )
    response = llm.invoke(prompt)
    return safe_json_parse(response.content)
