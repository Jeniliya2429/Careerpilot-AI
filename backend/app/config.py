"""
Central app configuration. Reads from environment variables / .env file.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_HEAVY: str = "gpt-4o"
    OPENAI_MODEL_LIGHT: str = "gpt-4o-mini"

    # Supabase (Storage only — DB access is via SQLAlchemy/DATABASE_URL below)
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_BUCKET: str = "resumes"

    # Database (Supabase Postgres connection string, used by SQLAlchemy)
    DATABASE_URL: str = ""

    # Auth
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # App
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
