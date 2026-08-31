"""
Chat API Schemas
"""

from pydantic import BaseModel, Field


# ==========================================================
# Chat Request
# ==========================================================

class ChatRequest(BaseModel):
    """
    Request body for the RAG chat endpoint.
    """

    query: str = Field(
        ...,
        min_length=1,
        description="Question to ask the RAG system.",
    )

    conversation_id: int = Field(
        ...,
        gt=0,
        description="Conversation in which the message will be stored.",
    )

    top_k: int = Field(
        default=12,
        ge=1,
        le=20,
        description="Number of document chunks to retrieve.",
    )


# ==========================================================
# Chat Source
# ==========================================================

class ChatSource(BaseModel):
    """
    Source information returned with an answer.
    """

    document_id: int
    chunk_id: int
    chunk_index: int
    score: float


# ==========================================================
# Chat Response
# ==========================================================

class ChatResponse(BaseModel):
    """
    Response returned by the RAG chat endpoint.
    """

    query: str
    answer: str
    conversation_id: int
    sources: list[ChatSource]