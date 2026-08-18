import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas.auth import UserCreate, UserLogin, UserOut, Token
from app.core.security import hash_password, verify_password, create_access_token, rate_limiter
from app.api.deps import get_current_user

logger = logging.getLogger("medreports")
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(f"reg_{client_ip}", max_requests=20, window_seconds=60):
        raise HTTPException(status_code=429, detail="Too many registration attempts. Please try again later.")

    try:
        # Check if email already exists
        existing = db.query(User).filter(User.email == payload.email.lower().strip()).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists. Please sign in instead."
            )

        # Create new user
        new_user = User(
            id=str(uuid.uuid4()),
            email=payload.email.lower().strip(),
            password_hash=hash_password(payload.password),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info("New user registered successfully: user_id=%s", new_user.id[:8])
        return new_user

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Registration failed: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Registration error: {type(e).__name__}: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(f"login_{client_ip}", max_requests=30, window_seconds=60):
        raise HTTPException(status_code=429, detail="Too many login attempts. Please wait a minute.")

    try:
        user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        token = create_access_token(subject=user.id)
        return Token(access_token=token)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Login failed: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Login error: {type(e).__name__}: {str(e)}")


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
