"""
Main API Router
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.conversations import (
    router as conversations_router,
)
from app.api.v1.documents import (
    router as documents_router,
)


api_router = APIRouter(
    prefix="/api/v1",
)


# ==========================================================
# Authentication
# ==========================================================

api_router.include_router(
    auth_router,
)


# ==========================================================
# Chat / RAG
# ==========================================================

api_router.include_router(
    chat_router,
)


# ==========================================================
# Conversations
# ==========================================================

api_router.include_router(
    conversations_router,
)


# ==========================================================
# Documents
# ==========================================================

api_router.include_router(
    documents_router,
)