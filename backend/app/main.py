from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routes import auth_routes, resume_routes, jd_routes, pipeline_routes

app = FastAPI(
    title="CareerPilot AI API",
    description="AI agent pipeline for resume tailoring, interview prep, and battlecards — "
                 "built with FastAPI, LangChain, LangGraph, SQLAlchemy, and Supabase.",
    version="1.0.0",
)

origins = [origin.strip() for origin in settings.FRONTEND_ORIGIN.split(",") if origin.strip()]
if "http://localhost:5173" not in origins:
    origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(resume_routes.router)
app.include_router(jd_routes.router)
app.include_router(pipeline_routes.router)


@app.on_event("startup")
def on_startup():
    # Creates all tables (users, resumes, job_descriptions, pipeline_runs,
    # tailored_resumes, battlecards) if they don't already exist.
    init_db()


@app.get("/")
def root():
    return {"status": "ok", "service": "CareerPilot AI API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
