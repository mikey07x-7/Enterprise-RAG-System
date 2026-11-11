"""
Chat API Schemas
"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Question to ask the RAG system.")
    conversation_id: int = Field(..., gt=0, description="Conversation in which the message will be stored.")
    top_k: int = Field(default=12, ge=1, le=20, description="Number of authorised document chunks to retrieve.")


class ChatSource(BaseModel):
    document_id: int
    chunk_id: int
    chunk_index: int
    page_number: int | None = None
    section_title: str | None = None
    score: float
    filename: str = "Document"
    document_title: str = "Document"
    content: str = ""


class ChatResponse(BaseModel):
    query: str
    answer: str
    conversation_id: int
    sources: list[ChatSource]
