from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.auth import hash_password, verify_password, create_access_token, get_current_user_payload

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(name=payload.name, email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user_id=user.id, email=user.email)
    return TokenResponse(access_token=token, user={"id": user.id, "name": user.name, "email": user.email})


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user_id=user.id, email=user.email)
    return TokenResponse(access_token=token, user={"id": user.id, "name": user.name, "email": user.email})


@router.get("/me")
def me(current_user: dict = Depends(get_current_user_payload)):
    return current_user
