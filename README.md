# CareerPilot AI

An AI agent that takes your resume + a job description and produces a
fit/gap analysis, a truthfully-tailored resume (with a **real** human
approval checkpoint), personalized STAR interview prep, a live mock
interview with rubric feedback, and a one-page pre-interview battlecard.

Built with **FastAPI + SQLAlchemy + Supabase (Postgres + Storage) + LangChain +
LangGraph + OpenAI + ChromaDB (RAG) + React/Vite**.

## What makes the agent real, not a form

- **Real LangGraph interrupt** (`interrupt_after=["tailor_resume"]`) — the
  graph genuinely halts after drafting your tailored resume. Nothing
  downstream (interview prep, battlecard) runs until you call the approve
  endpoint. This is enforced server-side, not by a frontend "Next" button.
- **Self-reflection fabrication guardrail** — after each draft, a second
  LLM call fact-checks the tailored resume against your original and
  flags invented employers, titles, skills, or metrics. If fabrication is
  found, the node redrafts (up to 2 retries) before ever reaching you.
- **RAG-backed interview prep** — questions are retrieved from a curated
  ChromaDB question bank via vector search on the job title + requirements,
  not hardcoded per role.
- **Interactive mock interview** — a live Q&A loop that scores each typed
  answer against a structure / specificity / JD-alignment rubric and gives
  concrete feedback, not just a static question list.

## Project structure

```
careerpilot-ai/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint, creates DB tables on startup
│   │   ├── config.py          # env-driven settings
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── auth.py            # bcrypt + JWT
│   │   ├── routes/            # auth, resumes, job descriptions, pipeline
│   │   ├── ai/
│   │   │   ├── state.py       # LangGraph state schema
│   │   │   ├── nodes.py       # all pipeline nodes (parse, gap, tailor, RAG, prep, battlecard)
│   │   │   ├── graph.py       # LangGraph StateGraph + the real interrupt
│   │   │   ├── mock_interview.py
│   │   │   ├── pipeline_service.py
│   │   │   └── rag/           # ChromaDB setup + seed script
│   │   └── utils/
│   │       ├── pdf_utils.py   # resume text extraction + tailored resume PDF export
│   │       └── storage.py     # Supabase Storage wrapper (resume blobs only)
│   ├── data/question_bank_seed.json
│   ├── tests/                 # pytest, all LLM calls mocked — no API key needed to run
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
└── frontend/
    ├── src/
    │   ├── pages/              # Login, Register, Dashboard, GapAnalysis,
    │   │                       # TailoredResume, InterviewPrep, MockInterview, Battlecard
    │   ├── components/         # Navbar, Toast, Skeleton, FlightPlan, ProtectedRoute
    │   └── api/                 # axios client + auth context
    ├── package.json
    ├── .env.example
    └── .gitignore
```

## Prerequisites

- Python 3.12 (Windows: install from python.org, tick "Add to PATH")
- Node.js 18+
- A free [Supabase](https://supabase.com) project (for Postgres + resume file storage)
- An OpenAI API key

No Visual Studio / C++ Build Tools required — every package in
`requirements.txt` ships a prebuilt Windows wheel for Python 3.12.

## Windows setup (PowerShell)

### 1. Supabase

1. Create a project at supabase.com.
2. **Project Settings → Database → Connection string → URI** (use the
   "Session pooler" variant) — this is your `DATABASE_URL`.
3. **Project Settings → API** — copy the Project URL (`SUPABASE_URL`) and
   the `service_role` secret key (`SUPABASE_SERVICE_ROLE_KEY`).
4. **Storage** → create a new bucket named `resumes` (private is fine).

Tables (`users`, `resumes`, `job_descriptions`, `pipeline_runs`,
`tailored_resumes`, `battlecards`) are created automatically the first
time the backend starts — no manual SQL needed.

### 2. Backend

```powershell
cd backend

py -3.12 -m venv venv

.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

copy .env.example .env
# now edit .env and fill in OPENAI_API_KEY, SUPABASE_URL,
# SUPABASE_SERVICE_ROLE_KEY, DATABASE_URL, JWT_SECRET

python -m app.ai.rag.seed_question_bank

uvicorn app.main:app --reload --port 8000
```

Backend is now running at `http://localhost:8000` (docs at `/docs`).

### 3. Frontend

Open a **second** PowerShell window:

```powershell
cd frontend

npm install

copy .env.example .env
# defaults to http://localhost:8000, only change if your backend runs elsewhere

npm run dev
```

Frontend is now running at `http://localhost:5173`.

### 4. Run the tests (no OpenAI key needed — every LLM call is mocked)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

## The pipeline

```
parse_resume ──┐
               ├──► gap_analysis ──► tailor_resume
parse_jd ──────┘                          │
                              (self-reflection fabrication check,
                               redrafts up to 2x if issues found)
                                           │
                         ═══ REAL LangGraph interrupt — pipeline halts ═══
                                           │
                          user reviews / edits / approves in the UI
                                           │
                    POST /pipeline/{run_id}/approve-tailoring
                                           │
                         ═══ graph.invoke(None, config) resumes ═══
                                           │
              retrieve_questions (ChromaDB RAG) ──► generate_prep ──► generate_battlecard ──► END
```

A separate, repeatable loop (not part of the graph) powers the mock
interview: `POST /pipeline/{run_id}/mock-interview/answer` scores each
typed answer against a structure/specificity/JD-alignment rubric.

## Notes

- Uploaded resumes must be text-based PDFs (not scanned images) — the
  upload endpoint rejects PDFs it can't extract meaningful text from.
- The tailored-resume PDF download always reflects the **human-approved**
  final text, never the unreviewed AI draft.
- Never commit `.env`, `venv/`, `node_modules/`, or `chroma_db/` — see
  `.gitignore` in both `backend/` and `frontend/`.
