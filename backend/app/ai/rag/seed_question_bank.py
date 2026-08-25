"""
Seed the ChromaDB question bank from data/question_bank_seed.json.
Idempotent — safe to re-run (uses upsert).

Run from the backend/ directory (with venv activated) on Windows:
    python -m app.ai.rag.seed_question_bank

Or on macOS/Linux:
    python3 -m app.ai.rag.seed_question_bank
"""
import json
import os
from app.ai.rag.chroma_setup import get_question_collection

# backend/app/ai/rag/seed_question_bank.py -> backend/data/question_bank_seed.json
SEED_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "question_bank_seed.json")
)


def seed():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)

    collection = get_question_collection()

    ids = [f"q_{i}" for i in range(len(questions))]
    documents = [q["question"] for q in questions]
    metadatas = [{"category": q["category"], "role_tag": q["role_tag"]} for q in questions]

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Seeded {len(questions)} interview questions into ChromaDB at "
          f"{os.environ.get('CHROMA_PERSIST_DIR', './chroma_db')}")


if __name__ == "__main__":
    seed()
