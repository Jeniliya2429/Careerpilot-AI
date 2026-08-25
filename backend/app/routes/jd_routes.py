from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import JobDescriptionCreate
from app.auth import get_current_user_payload

router = APIRouter(prefix="/job-descriptions", tags=["job-descriptions"])


@router.post("")
def create_jd(payload: JobDescriptionCreate, current_user: dict = Depends(get_current_user_payload),
              db: Session = Depends(get_db)):
    jd = models.JobDescription(
        user_id=current_user["id"],
        company_name=payload.company_name,
        role_title=payload.role_title,
        raw_text=payload.raw_text,
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)
    return {"id": jd.id, "company_name": jd.company_name, "role_title": jd.role_title, "raw_text": jd.raw_text}


@router.get("")
def list_jds(current_user: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)):
    rows = db.query(models.JobDescription).filter(models.JobDescription.user_id == current_user["id"]) \
        .order_by(models.JobDescription.created_at.desc()).all()
    return [{"id": j.id, "company_name": j.company_name, "role_title": j.role_title, "raw_text": j.raw_text}
            for j in rows]
