"""
Service layer between the API routes and the LangGraph pipeline.
Uses SQLAlchemy (not Supabase's table client) for all relational data —
Supabase is only used for storing the resume PDF blob (see utils/storage.py).
"""
import uuid
from sqlalchemy.orm import Session

from app import models
from app.ai.graph import pipeline_graph


def start_pipeline_run(db: Session, user_id: str, resume_id: str, resume_text: str,
                        jd_id: str, jd_text: str, candidate_name: str) -> dict:
    run_id = str(uuid.uuid4())

    run = models.PipelineRun(id=run_id, user_id=user_id, resume_id=resume_id, jd_id=jd_id, status="running")
    db.add(run)
    db.commit()

    config = {"configurable": {"thread_id": run_id}}
    initial_state = {
        "run_id": run_id,
        "user_id": user_id,
        "resume_text": resume_text,
        "jd_text": jd_text,
        "candidate_name": candidate_name,
        "errors": [],
    }

    # Executes parse_resume -> parse_jd -> gap_analysis -> tailor_resume,
    # then genuinely HALTS (interrupt_after=["tailor_resume"] in graph.py).
    result = pipeline_graph.invoke(initial_state, config=config)

    final_status = "failed" if result.get("errors") and not result.get("tailored_resume_draft") \
        else "awaiting_approval"

    run.status = final_status
    run.fit_score = result.get("fit_score")
    run.missing_keywords = result.get("missing_keywords", [])
    run.matching_keywords = result.get("matching_keywords", [])
    run.state_json = result
    db.add(run)

    tailored = models.TailoredResume(
        run_id=run_id,
        draft_content=result.get("tailored_resume_draft", ""),
        approved=False,
    )
    db.add(tailored)
    db.commit()

    return {"run_id": run_id, "status": final_status, **result}


def get_run_state(db: Session, run_id: str) -> models.PipelineRun | None:
    return db.query(models.PipelineRun).filter(models.PipelineRun.id == run_id).first()


def approve_tailoring_and_resume(db: Session, run_id: str, approved: bool,
                                  edited_content: str | None = None) -> dict:
    run = db.query(models.PipelineRun).filter(models.PipelineRun.id == run_id).first()
    if not run:
        raise ValueError("Run not found")

    config = {"configurable": {"thread_id": run_id}}

    if not approved:
        run.status = "rejected"
        db.add(run)
        db.commit()
        return {"run_id": run_id, "status": "rejected"}

    # Read the currently-checkpointed state (post-interrupt) so we know
    # what the AI drafted, in case the human didn't edit anything.
    checkpointed = pipeline_graph.get_state(config)
    draft = checkpointed.values.get("tailored_resume_draft", "")
    final_content = edited_content if edited_content else draft

    # Patch the checkpoint with the human-approved final text BEFORE
    # resuming, so retrieve_questions/generate_prep/generate_battlecard
    # (and the final response) all see the approved version.
    pipeline_graph.update_state(config, {"tailored_resume_final": final_content, "approved": True})

    # THIS is the actual resume of the real LangGraph interrupt — it
    # continues execution into retrieve_questions -> ... -> END.
    result = pipeline_graph.invoke(None, config=config)

    tailored = db.query(models.TailoredResume).filter(models.TailoredResume.run_id == run_id).first()
    tailored.final_content = final_content
    tailored.approved = True
    db.add(tailored)

    battlecard = models.Battlecard(run_id=run_id, content_json=result.get("battlecard", {}))
    db.add(battlecard)

    run.status = result.get("status", "completed")
    run.state_json = result
    db.add(run)

    db.commit()

    return {"run_id": run_id, **result}
