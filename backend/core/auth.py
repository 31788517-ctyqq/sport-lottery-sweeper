"""
Authentication logic layer.

This module contains functions for user authentication,
token validation, and retrieving current user details
based on tokens. It acts as a bridge between the security
utilities and the API endpoints or services.
"""
from datetime import datetime, timedelta
from typing import Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from ..models.user import User # Assuming your User model is defined here
from ..schemas.user import UserResponse as UserSchema # Using the correct schema
from .database import get_db
from .security import decode_token, verify_password, get_password_hash, ALGORITHM, create_access_token, create_refresh_token
from ..config import settings

# 获取settings实例
settings_instance = settings

# Define OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Standard exception for invalid credentials
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    Authenticates a user by username and password.

    Args:
        db: The database session.
        username: The username provided by the user.
        password: The plain text password provided by the user.

    Returns:
        The User object if authentication is successful, otherwise None.
    """
    # Fetch user by username from the database
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    
    # Try bcrypt verification first
    from ..core.security import verify_password, get_password_hash
    import hashlib
    
    if verify_password(password, user.password_hash):
        return user
    
    # Bcrypt failed, try SHA256 (for legacy support)
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    if sha256_hash == user.password_hash:
        # Upgrade to bcrypt hash
        from ..core.security import get_password_hash
        bcrypt_hash = get_password_hash(password)
        user.password_hash = bcrypt_hash
        db.commit()
        db.refresh(user)
        return user
    
    # Return None if password incorrect
    return None


def get_current_user_from_token(
    token_data: dict = Depends(lambda token: decode_token(token))
) -> UserSchema:
    """
    Dependency to get the current user based on the decoded token payload.

    This function relies on a preceding dependency (not shown here, usually in middleware
    or as part of the route's `Depends`) that extracts the raw JWT token from the
    Authorization header and passes it to `decode_token`.

    Args:
        token_data: The decoded token payload (dict). This is obtained via the `decode_token` utility.

    Raises:
        HTTPException: If the token is invalid, expired, missing user ID, or the user doesn't exist.

    Returns:
        A Pydantic `UserSchema` object representing the authenticated user.
    """
    if token_data is None:
        raise credentials_exception

    user_id: Union[str, int] = token_data.get("sub") # Standard JWT claim for subject/user ID
    token_type: str = token_data.get("type")

    if user_id is None:
        raise credentials_exception
    if token_type != "access": # Ensure it's an access token, not a refresh token
         raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Invalid token type",
             headers={"WWW-Authenticate": "Bearer"},
         )

    # Here, you would typically fetch the user from the database using the user_id
    # For simplicity in this example, we assume the token payload itself contains
    # enough user information (e.g., username, roles) and return a basic schema.
    # In practice, you'd likely need another dependency like `get_db_session`
    # to query the DB for the full user object.
    # Example:
    # db: AsyncSession = Depends(get_db_session)
    # user = await db.get(User, user_id)
    # if user is None:
    #     raise credentials_exception
    # return UserSchema.model_validate(user)

    # Returning a simple schema based *only* on the token payload.
    # This is less secure than fetching from DB; fetching from DB is recommended.
    return UserSchema(id=user_id, username=token_data.get("username")) # Adjust fields as per your schema


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
    """
    Get current user based on the provided token in the request header
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = {"username": username}
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def verify_websocket_token(websocket_token: str):
    """
    验证websocket连接的token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(websocket_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = {"username": username}
    except JWTError:
        return None
    
    # 这里可以根据需要查询数据库验证用户是否存在
    # 为了简单起见，我们只验证token的有效性
    return token_data


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current admin user, raises an exception if the user is not an admin
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user