"""Script to create database tables."""
from sqlmodel import SQLModel

from app.database import engine
from app.models import Session, User, EvCar  # noqa: F401 - Import models to register them


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    create_db_and_tables()
