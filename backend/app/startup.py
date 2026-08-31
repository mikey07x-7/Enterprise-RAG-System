"""
Application startup and shutdown lifecycle.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.constants import REQUIRED_DIRECTORIES
from database.database import check_database_connection
from core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the application starts
    and once when it shuts down.
    """

    logger.info("=" * 60)
    logger.info("Starting Enterprise RAG System")

    # ---------------------------------------------------
    # Create Required Directories
    # ---------------------------------------------------

    for directory in REQUIRED_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)

    logger.success("Storage directories initialized.")

    # ---------------------------------------------------
    # Check Database
    # ---------------------------------------------------

    check_database_connection()

    logger.success("Application started successfully.")

    yield

    # ---------------------------------------------------
    # Shutdown
    # ---------------------------------------------------

    logger.info("Shutting down Enterprise RAG System")