"""
Chat API

Provides the main question-answering endpoint
for the Enterprise RAG System.

Responsibilities:

    1. Authenticate user
    2. Validate conversation ownership
    3. Store user message
    4. Execute USER-SCOPED RAG pipeline
    5. Store assistant response
    6. Update conversation timestamp
    7. Return answer and sources
"""

from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from core.security import get_current_user
from database.database import get_db

from models.conversation import Conversation
from models.message import Message
from models.user import User

from schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from services.rag_service import rag_service


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


# ==========================================================
# Chat / RAG
# ==========================================================

@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Answer a user question using the USER-SCOPED RAG pipeline.

    The authenticated user's ID is passed through the
    entire retrieval pipeline to ensure that only documents
    belonging to that user can be retrieved.

    Pipeline:

        User Query
             ↓
        Authenticate User
             ↓
        Validate Conversation Ownership
             ↓
        Save User Message
             ↓
        User-Scoped RAG Retrieval
             ↓
        Context Construction
             ↓
        Groq LLM
             ↓
        Save Assistant Message
             ↓
        Return Answer + Sources
    """

    # ======================================================
    # 1. Validate query
    # ======================================================

    query = request.query.strip()

    if not query:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty.",
        )

    # ======================================================
    # 2. Validate conversation ownership
    # ======================================================

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if conversation is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    # ======================================================
    # 3. Save user message
    # ======================================================

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=query,
    )

    db.add(user_message)

    db.flush()

    # ======================================================
    # 4. Run USER-SCOPED RAG pipeline
    # ======================================================

    try:

        result = rag_service.generate_answer(
            db=db,
            query=query,

            # IMPORTANT:
            # Pass authenticated user's ID.
            user_id=current_user.id,

            top_k=request.top_k,
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An error occurred while generating "
                "the RAG response."
            ),
        ) from exc

    # ======================================================
    # 5. Save assistant message
    # ======================================================

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=result["answer"],
    )

    db.add(assistant_message)

    # ======================================================
    # 6. Update conversation timestamp
    # ======================================================

    conversation.updated_at = datetime.utcnow()

    # ======================================================
    # 7. Commit conversation + messages
    # ======================================================

    try:

        db.commit()

        db.refresh(
            conversation
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save chat messages.",
        ) from exc

    # ======================================================
    # 8. Return response
    # ======================================================

    return ChatResponse(
        query=result["query"],
        answer=result["answer"],
        conversation_id=conversation.id,
        sources=result["sources"],
    )