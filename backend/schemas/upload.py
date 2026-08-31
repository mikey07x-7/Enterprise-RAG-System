"""
Document Upload API Schemas
"""

from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """
    Document information returned by the API.
    """

    id: int
    user_id: int
    filename: str
    file_type: str
    title: str | None
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True