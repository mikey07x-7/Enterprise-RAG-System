"""
Conversation API Schemas
"""

from datetime import datetime

from pydantic import BaseModel, Field


# ==========================================================
# Create Conversation
# ==========================================================

class ConversationCreate(BaseModel):
    """
    Request schema for creating a conversation.
    """

    title: str = Field(
        default="New Conversation",
        min_length=1,
        max_length=255,
    )


# ==========================================================
# Conversation Response
# ==========================================================

class ConversationResponse(BaseModel):
    """
    Conversation information returned by the API.
    """

    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==========================================================
# Message Response
# ==========================================================

class MessageResponse(BaseModel):
    """
    Message information returned by the API.
    """

    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================================
# Conversation Detail
# ==========================================================

class ConversationDetailResponse(BaseModel):
    """
    Conversation with its messages.
    """

    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]

    class Config:
        from_attributes = True