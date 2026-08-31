"""
Authentication Service

Handles:
- Password hashing
- Password verification
- JWT access token creation
- JWT token decoding
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from core.config import settings
from core.logger import logger


ALGORITHM = "HS256"


# ==========================================================
# Password Hashing
# ==========================================================

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    """

    if not password:
        raise ValueError("Password cannot be empty.")

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    )

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """

    if not plain_password or not hashed_password:
        return False

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    except (ValueError, TypeError):
        return False


# ==========================================================
# JWT
# ==========================================================

def create_access_token(
    user_id: int,
    username: str,
) -> str:
    """
    Create a JWT access token for an authenticated user.
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )

    logger.success(
        f"Access token created for user {user_id}"
    )

    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Raises:
        ValueError: If the token is invalid or expired.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise ValueError("Invalid token: missing user ID.")

        return payload

    except JWTError as exc:
        raise ValueError(
            "Invalid or expired access token."
        ) from exc