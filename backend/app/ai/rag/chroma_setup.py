"""
ChromaDB client + collection setup for the interview question bank RAG.
Persisted locally to CHROMA_PERSIST_DIR so it survives restarts without
needing an external vector DB service.

Windows note: chromadb==0.5.23 ships prebuilt wheels (including its
hnswlib dependency) for cp312-win_amd64 — no local compilation, no
Visual Studio / C++ Build Tools required.
"""
import chromadb
from chromadb.utils import embedding_functions
from app.config import settings

_client = None
_collection = None

COLLECTION_NAME = "interview_question_bank"


def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client


def get_question_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        embed_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.OPENAI_API_KEY,
            model_name="text-embedding-3-small",
        )
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embed_fn,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection
