"""
Database Configuration

Initializes the SQLAlchemy engine, session factory,
and declarative base for ORM models.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.logger import logger


# ==========================================================
# SQLAlchemy Engine
# ==========================================================

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)


# ==========================================================
# Session Factory
# ==========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


# ==========================================================
# Base Model
# ==========================================================

class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ==========================================================
# Database Dependency
# ==========================================================

def get_db():
    """
    Creates a database session for each request.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================================================
# Database Connectivity Test
# ==========================================================

def check_database_connection():
    """
    Tests database connectivity.
    """

    try:
        with engine.connect():
            logger.success("Connected to PostgreSQL successfully.")

    except Exception as e:
        logger.exception(f"Database connection failed: {e}")
        raise