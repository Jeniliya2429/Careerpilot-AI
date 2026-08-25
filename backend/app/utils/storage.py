"""
Thin wrapper around the Supabase Storage client, used only for storing
uploaded resume PDFs. All relational data goes through SQLAlchemy
(app/database.py) instead — Supabase here is acting purely as an S3-like
object store.
"""
from functools import lru_cache
from supabase import create_client, Client
from app.config import settings


@lru_cache
def get_storage_client() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are not set. Copy "
            "backend/.env.example to backend/.env and fill in your Supabase "
            "project credentials (Project Settings -> API)."
        )
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def upload_resume_pdf(storage_path: str, file_bytes: bytes) -> None:
    client = get_storage_client()
    client.storage.from_(settings.SUPABASE_BUCKET).upload(
        storage_path, file_bytes, {"content-type": "application/pdf"}
    )


def get_resume_pdf_signed_url(storage_path: str, expires_in: int = 3600) -> str:
    client = get_storage_client()
    result = client.storage.from_(settings.SUPABASE_BUCKET).create_signed_url(
        storage_path, expires_in
    )
    return result.get("signedURL") or result.get("signed_url", "")
