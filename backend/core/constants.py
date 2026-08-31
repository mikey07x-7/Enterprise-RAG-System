"""
Application Constants

This module contains application-wide constant values.
These values should remain fixed and should not be loaded
from environment variables.
"""

from pathlib import Path

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

BACKEND_DIR = BASE_DIR / "backend"

STORAGE_DIR = BACKEND_DIR / "storage"

UPLOAD_DIR = STORAGE_DIR / "uploads"

VECTOR_STORE_DIR = STORAGE_DIR / "vectorstore"

LOG_DIR = STORAGE_DIR / "logs"

TEMP_DIR = STORAGE_DIR / "temp"

# ==========================================================
# API
# ==========================================================

API_PREFIX = "/api"

API_VERSION = "v1"

# ==========================================================
# Supported File Types
# ==========================================================

SUPPORTED_DOCUMENT_TYPES = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".csv",
    ".xlsx",
}

# ==========================================================
# Upload Limits
# ==========================================================

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB

# ==========================================================
# Text Chunking
# ==========================================================

DEFAULT_CHUNK_SIZE = 1000

DEFAULT_CHUNK_OVERLAP = 200

# ==========================================================
# Embeddings
# ==========================================================

EMBEDDING_DIMENSION = 768

TOP_K_RESULTS = 5

# ==========================================================
# Logging
# ==========================================================

LOG_FILE_NAME = "enterprise_rag.log"

LOG_ROTATION = "10 MB"

LOG_RETENTION = "10 days"

# ==========================================================
# Create Required Directories
# ==========================================================

REQUIRED_DIRECTORIES = [
    STORAGE_DIR,
    UPLOAD_DIR,
    VECTOR_STORE_DIR,
    LOG_DIR,
    TEMP_DIR,
]