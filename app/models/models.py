from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlmodel import Field, Relationship, SQLModel


class UserRole(int, Enum):
    """Enumeration for user roles."""

    USER = 0
    PREMIUM_USER = 1
    ADMIN = 2


class User(SQLModel, table=True):
    """User model representing app users."""

    __tablename__ = "user"

    user_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, index=True, autoincrement=True),
    )
    name: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(
        sa_column=Column(String(255), unique=True, index=True, nullable=False)
    )
    password_hash: str = Field(sa_column=Column(String(255), nullable=False))
    role: int = Field(
        default=UserRole.USER.value,
        sa_column=Column(Integer, default=UserRole.USER.value, nullable=False),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )
    last_login: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    # Relationships
    sessions: List["Session"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email='{self.email}')>"


class Session(SQLModel, table=True):
    """Represents a user session for a logged-in device."""

    __tablename__ = "session"

    id: Optional[int] = Field(
        default=None, sa_column=Column(Integer, primary_key=True, index=True)
    )
    user_id: int = Field(
        sa_column=Column(
            Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False
        )
    )
    token: str = Field(
        sa_column=Column(String(64), unique=True, index=True, nullable=False)
    )
    issued_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    revoked: bool = Field(
        default=False, sa_column=Column(Boolean, default=False, nullable=False)
    )
    device_info: Optional[str] = Field(
        default=None, sa_column=Column(String(255), nullable=True)
    )
    ip_address: Optional[str] = Field(
        default=None, sa_column=Column(String(100), nullable=True)
    )

    # Relationship to User
    user: "User" = Relationship(back_populates="sessions")

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, revoked={self.revoked})>"


class EvCar(SQLModel, table=True):
    """Electric vehicle data owned by a user."""

    __tablename__ = "evcar"

    id: Optional[int] = Field(
        default=None, sa_column=Column(Integer, primary_key=True, index=True)
    )
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    )
    make: str = Field(sa_column=Column(String(255), nullable=False))
    model: str = Field(sa_column=Column(String(255), nullable=False))
    year: Optional[str] = Field(default=None, sa_column=Column(String(32), nullable=True))
    plug_type: Optional[str] = Field(default=None, sa_column=Column(String(100), nullable=True))
    battery_kwh: Optional[str] = Field(default=None, sa_column=Column(String(100), nullable=True))
    range_km: Optional[str] = Field(default=None, sa_column=Column(String(100), nullable=True))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
    )

    # Relationship to User (optional backref)
    # user: "User" = Relationship(back_populates="evcars")

    def __repr__(self) -> str:
        return f"<EvCar(id={self.id}, user_id={self.user_id}, make={self.make}, model={self.model})>"
