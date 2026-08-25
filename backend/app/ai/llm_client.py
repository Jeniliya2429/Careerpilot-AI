"""
Thin wrapper around LangChain's ChatOpenAI so every node grabs a
consistently-configured client instead of instantiating its own.

Two tiers, matching the project's cost/quality tradeoff:
  - "heavy" (gpt-4o)      -> tailoring, battlecard: where quality matters most
  - "light" (gpt-4o-mini) -> parsing, gap analysis, prep generation
"""
from langchain_openai import ChatOpenAI
from app.config import settings


def get_llm(tier: str = "light", temperature: float = 0.3) -> ChatOpenAI:
    model = settings.OPENAI_MODEL_HEAVY if tier == "heavy" else settings.OPENAI_MODEL_LIGHT
    return ChatOpenAI(
        model=model,
        api_key=settings.OPENAI_API_KEY,
        temperature=temperature,
    )
