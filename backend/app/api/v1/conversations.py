"""
Conversation API

Provides endpoints for creating, listing,
viewing, and deleting conversations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import get_current_user
from database.database import get_db
from models.conversation import Conversation
from models.user import User
from schemas.conversation import (
    ConversationCreate,
    ConversationDetailResponse,
    ConversationResponse,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


# ==========================================================
# Create Conversation
# ==========================================================

@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new conversation for the authenticated user.
    """

    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


# ==========================================================
# List Conversations
# ==========================================================

@router.get(
    "",
    response_model=list[ConversationResponse],
)
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all conversations belonging to the current user.
    """

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == current_user.id
        )
        .order_by(
            Conversation.updated_at.desc()
        )
        .all()
    )

    return conversations


# ==========================================================
# Get Conversation
# ==========================================================

@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return a conversation and all its messages.
    """

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return conversation


# ==========================================================
# Delete Conversation
# ==========================================================

@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a conversation belonging to the current user.
    """

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    db.delete(conversation)
    db.commit()

    return None