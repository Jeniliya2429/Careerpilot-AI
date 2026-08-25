import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.auth import get_current_user_payload
from app.utils.pdf_utils import extract_text_from_pdf
from app.utils.storage import upload_resume_pdf

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported")

    file_bytes = await file.read()
    text, low_confidence = extract_text_from_pdf(file_bytes)

    if low_confidence:
        raise HTTPException(
            status_code=422,
            detail="Couldn't extract text from this PDF — it looks scanned/image-based. "
                   "Please upload a text-based PDF export of your resume.",
        )

    storage_path = f"{current_user['id']}/{uuid.uuid4()}_{file.filename}"
    upload_resume_pdf(storage_path, file_bytes)

    resume = models.Resume(
        user_id=current_user["id"],
        filename=file.filename,
        storage_path=storage_path,
        extracted_text=text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {"id": resume.id, "filename": resume.filename, "extracted_text_preview": text[:300]}


@router.get("")
def list_resumes(current_user: dict = Depends(get_current_user_payload), db: Session = Depends(get_db)):
    rows = db.query(models.Resume).filter(models.Resume.user_id == current_user["id"]) \
        .order_by(models.Resume.uploaded_at.desc()).all()
    return [{"id": r.id, "filename": r.filename} for r in rows]
