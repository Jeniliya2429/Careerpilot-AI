from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import PipelineRunCreate, ApproveTailoringRequest, MockInterviewAnswerRequest
from app.auth import get_current_user_payload
from app.utils.pdf_utils import generate_resume_pdf
from app.ai.pipeline_service import start_pipeline_run, get_run_state, approve_tailoring_and_resume
from app.ai.mock_interview import score_mock_answer

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run")
def run_pipeline(payload: PipelineRunCreate, current_user: dict = Depends(get_current_user_payload),
                  db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == payload.resume_id).first()
    jd = db.query(models.JobDescription).filter(models.JobDescription.id == payload.jd_id).first()

    if not resume or not jd:
        raise HTTPException(status_code=404, detail="Resume or job description not found")

    result = start_pipeline_run(
        db=db,
        user_id=current_user["id"],
        resume_id=payload.resume_id,
        resume_text=resume.extracted_text,
        jd_id=payload.jd_id,
        jd_text=jd.raw_text,
        candidate_name=current_user.get("email", "Candidate"),
    )
    return result


@router.get("/{run_id}/status")
def pipeline_status(run_id: str, current_user: dict = Depends(get_current_user_payload),
                     db: Session = Depends(get_db)):
    run = get_run_state(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    state = run.state_json or {}
    return {
        "run_id": run.id,
        "status": run.status,
        "fit_score": run.fit_score,
        "matching_keywords": run.matching_keywords,
        "missing_keywords": run.missing_keywords,
        "gap_notes": state.get("gap_notes"),
        "tailored_resume_draft": state.get("tailored_resume_draft"),
        "tailoring_reflection_notes": state.get("tailoring_reflection_notes"),
        "interview_prep": state.get("interview_prep"),
        "battlecard": state.get("battlecard"),
        "errors": state.get("errors", []),
    }


@router.post("/{run_id}/approve-tailoring")
def approve_tailoring(run_id: str, payload: ApproveTailoringRequest,
                       current_user: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)):
    """
    THE human-in-the-loop checkpoint. approved=False marks the run
    rejected and the graph is never resumed (interview prep never runs).
    approved=True resumes the real LangGraph interrupt — see
    app/ai/pipeline_service.approve_tailoring_and_resume.
    """
    try:
        result = approve_tailoring_and_resume(
            db=db, run_id=run_id, approved=payload.approved, edited_content=payload.edited_content
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Run not found")
    return result


@router.get("/{run_id}/tailored-resume")
def get_tailored_resume(run_id: str, current_user: dict = Depends(get_current_user_payload),
                         db: Session = Depends(get_db)):
    row = db.query(models.TailoredResume).filter(models.TailoredResume.run_id == run_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Tailored resume not found")
    return {
        "run_id": run_id,
        "draft_content": row.draft_content,
        "final_content": row.final_content,
        "approved": row.approved,
    }


@router.get("/{run_id}/tailored-resume/download")
def download_tailored_resume(run_id: str, current_user: dict = Depends(get_current_user_payload),
                              db: Session = Depends(get_db)):
    row = db.query(models.TailoredResume).filter(models.TailoredResume.run_id == run_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Tailored resume not found")
    
    content = row.final_content or row.draft_content
    if not content:
        raise HTTPException(status_code=404, detail="No resume content available to download")

    pdf_bytes = generate_resume_pdf(content, candidate_name=current_user.get("email", "Candidate"))
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=tailored_resume.pdf"},
    )


@router.post("/{run_id}/mock-interview/answer")
def mock_interview_answer(run_id: str, payload: MockInterviewAnswerRequest,
                           current_user: dict = Depends(get_current_user_payload),
                           db: Session = Depends(get_db)):
    """
    Live mock-interview scoring. Requires the pipeline to have completed
    (so we have jd_requirements available for alignment scoring).
    """
    run = db.query(models.PipelineRun).filter(models.PipelineRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    state = run.state_json or {}
    jd_requirements = state.get("jd_requirements", [])

    try:
        feedback = score_mock_answer(payload.question, payload.answer, jd_requirements)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not score answer: {e}")

    return {"run_id": run_id, "question": payload.question, "feedback": feedback}


@router.get("/{run_id}/battlecard")
def get_battlecard(run_id: str, current_user: dict = Depends(get_current_user_payload),
                    db: Session = Depends(get_db)):
    row = db.query(models.Battlecard).filter(models.Battlecard.run_id == run_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Battlecard not ready yet — approve the tailored resume first.")
    return {"run_id": run_id, "content": row.content_json}


@router.get("/{run_id}/salary-negotiation")
def get_salary_negotiation(run_id: str, current_user: dict = Depends(get_current_user_payload),
                            db: Session = Depends(get_db)):
    run = db.query(models.PipelineRun).filter(models.PipelineRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    state = run.state_json or {}
    from app.ai.extra_services import generate_salary_negotiation
    result = generate_salary_negotiation(state.get("resume_text", ""), state.get("jd_text", ""))
    return {"run_id": run_id, "data": result}


@router.get("/{run_id}/action-plan")
def get_action_plan(run_id: str, current_user: dict = Depends(get_current_user_payload),
                    db: Session = Depends(get_db)):
    run = db.query(models.PipelineRun).filter(models.PipelineRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    state = run.state_json or {}
    from app.ai.extra_services import generate_action_plan
    result = generate_action_plan(state.get("resume_text", ""), state.get("jd_text", ""))
    return {"run_id": run_id, "data": result}


@router.get("/{run_id}/elevator-pitch")
def get_elevator_pitch(run_id: str, current_user: dict = Depends(get_current_user_payload),
                       db: Session = Depends(get_db)):
    run = db.query(models.PipelineRun).filter(models.PipelineRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    state = run.state_json or {}
    from app.ai.extra_services import generate_elevator_pitch
    result = generate_elevator_pitch(state.get("resume_text", ""), state.get("jd_text", ""))
    return {"run_id": run_id, "data": result}

