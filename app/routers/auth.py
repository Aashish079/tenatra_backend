import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import select

from app.database import SessionDependency as DBSession
from app.models import Session as UserSession
from app.models import User
from app.security import BasicAuthUser, BearerAuthUser

auth_router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class SessionResponse(BaseModel):
    token: str
    expires_at: str


class LoginResponse(BaseModel):
    id: int
    name: str
    email: str
    session: SessionResponse


@auth_router.post("/register", response_model=UserResponse)
def register_user(req: RegisterRequest, db: DBSession):
    """Register a new user."""
    existing_user = db.exec(select(User).where(User.email == req.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_pw = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt())
    user = User(name=req.name, email=req.email, password_hash=hashed_pw.decode("utf-8"))

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(id=user.user_id, name=user.name, email=user.email)


@auth_router.post("/login", response_model=LoginResponse)
def login_user(user: BasicAuthUser, db: DBSession):
    """Login with Basic Auth and receive a session token."""
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    session = UserSession(
        token=session_token, user_id=user.user_id, expires_at=expires_at
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    user.sessions.append(session)
    db.add(user)
    db.commit()

    return LoginResponse(
        id=user.user_id,
        name=user.name,
        email=user.email,
        session=SessionResponse(
            token=session.token,
            expires_at=session.expires_at.isoformat(),
        ),
    )


@auth_router.get("/me", response_model=UserResponse)
def get_current_user(user: BearerAuthUser):
    """Get current authenticated user (requires Bearer token)."""
    return UserResponse(id=user.user_id, name=user.name, email=user.email)
