"""
Security-related utilities and constants.
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional

from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import get_settings

# JWT算法常量
ALGORITHM = "HS256"

settings = get_settings()

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against its hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generates a hash for a plain text password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an access token with the given data and expiration time.

    Args:
        data: A dictionary containing the claims to be included in the token.
        expires_delta: The timedelta for how long the token should be valid.
                       Defaults to ACCESS_TOKEN_EXPIRE_MINUTES if not provided.

    Returns:
        The encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a refresh token with the given data and expiration time.

    Args:
        data: A dictionary containing the claims (usually user identifier).
        expires_delta: The timedelta for how long the token should be valid.
                       Defaults to 7 days if not provided.

    Returns:
        The encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(days=7))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def verify_token(token: str) -> Union[dict, None]:
    """
    Verify the given token and return the payload if valid.

    Args:
        token: The JWT token string to verify.

    Returns:
        A dictionary containing token data if valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = {"username": username}
        return token_data
    except jwt.JWTError:
        return None


def decode_token(token: str) -> Union[dict, None]:
    """
    Decode the given token and return the full payload if valid.

    Args:
        token: The JWT token string to decode.

    Returns:
        A dictionary containing the full token payload if valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None


def generate_verification_code(length: int = 6) -> str:
    """
    Generates a random numeric verification code.

    Args:
        length: The desired length of the code (default is 6).

    Returns:
        A string containing the verification code.
    """
    return "".join(secrets.choice("0123456789") for _ in range(length))


def generate_secret_key(length: int = 32) -> str:
    """
    Generates a random secret key suitable for cryptographic use (e.g., for JWT signing).
    This is a utility function, typically run once during setup.

    Args:
        length: The desired length of the key in bytes (default is 32).

    Returns:
        A URL-safe base64-encoded string of the random key.
    """
    return secrets.token_urlsafe(length)