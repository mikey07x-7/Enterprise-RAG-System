"""
Authentication Schemas
"""

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """
    Request body for user registration.
    """

    username: str = Field(
        min_length=3,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100,
    )


class UserLogin(BaseModel):
    """
    Request body for user login.
    """

    username: str

    password: str


class TokenResponse(BaseModel):
    """
    JWT authentication response.
    """

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """
    Public user information.
    """

    id: int
    username: str
    email: EmailStr
    is_active: bool

    model_config = {
        "from_attributes": True
    }