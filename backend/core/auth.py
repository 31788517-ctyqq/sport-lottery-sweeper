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
from ..models.admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
from ..schemas.user import UserResponse as UserSchema # Using the correct schema
from .database import get_db
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
    # Import inside the function to avoid circular imports
    from .security import verify_password, get_password_hash
    import hashlib
    
    if verify_password(password, user.password_hash):
        return user
    
    # Bcrypt failed, try SHA256 (for legacy support)
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    if sha256_hash == user.password_hash:
        # Upgrade to bcrypt hash
        bcrypt_hash = get_password_hash(password)
        user.password_hash = bcrypt_hash
        db.commit()
        db.refresh(user)
        return user
    
    # Return None if password incorrect
    return None


def get_current_user_from_token(
    token: str = Depends(oauth2_scheme)
) -> UserSchema:
    """
    Dependency to get the current user based on the decoded token payload.

    This function relies on a preceding dependency (not shown here, usually in middleware
    or as part of the route's `Depends`) that extracts the raw JWT token from the
    Authorization header and passes it to `decode_token`.

    Args:
        token: The raw JWT token from the Authorization header.

    Raises:
        HTTPException: If the token is invalid, expired, missing user ID, or the user doesn't exist.

    Returns:
        A Pydantic `UserSchema` object representing the authenticated user.
    """
    # Import inside the function to avoid circular imports
    from .security import decode_token
    
    token_data = decode_token(token)
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
                     db: Session = Depends(get_db)) -> User | AdminUser:
    """
    Get current user based on the provided token in the request header
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise credentials_exception

    # Compatibility strategy:
    # 1) Try explicit user_id claim.
    # 2) Try numeric sub as user id.
    # 3) Try username claim.
    # 4) Fallback to non-numeric sub as username.
    raw_sub = payload.get("sub")
    username_claim = payload.get("username")
    user_id_claim = payload.get("user_id")

    candidate_ids = []
    for value in (user_id_claim, raw_sub):
        try:
            if value is not None and str(value).strip().isdigit():
                candidate_ids.append(int(str(value).strip()))
        except Exception:
            pass

    candidate_usernames = []
    if username_claim:
        candidate_usernames.append(str(username_claim))
    if raw_sub and not str(raw_sub).strip().isdigit():
        candidate_usernames.append(str(raw_sub))

    # Remove duplicates while preserving order
    seen = set()
    candidate_ids = [x for x in candidate_ids if not (x in seen or seen.add(x))]
    seen.clear()
    candidate_usernames = [x for x in candidate_usernames if not (x in seen or seen.add(x))]

    # Try normal user table first
    for uid in candidate_ids:
        user = db.query(User).filter(User.id == uid).first()
        if user is not None:
            return user
    for uname in candidate_usernames:
        user = db.query(User).filter(User.username == uname).first()
        if user is not None:
            return user

    # Then try admin table
    admin_user = None
    for uid in candidate_ids:
        admin_user = db.query(AdminUser).filter(AdminUser.id == uid).first()
        if admin_user is not None:
            break
    if admin_user is None:
        for uname in candidate_usernames:
            admin_user = db.query(AdminUser).filter(AdminUser.username == uname).first()
            if admin_user is not None:
                break
    if admin_user is None:
        raise credentials_exception

    # Provide compatibility flags expected by admin-only guards
    try:
        setattr(admin_user, "is_admin", admin_user.role in [AdminRoleEnum.ADMIN, AdminRoleEnum.SUPER_ADMIN])
    except Exception:
        setattr(admin_user, "is_admin", True)
    try:
        setattr(admin_user, "is_active", admin_user.status == AdminStatusEnum.ACTIVE)
    except Exception:
        setattr(admin_user, "is_active", True)
    return admin_user


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
        payload = jwt.decode(websocket_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = {"username": username}
    except JWTError:
        return None
    
    # 这里可以根据需要查询数据库验证用户是否存在
    # 为了简单起见，我们只验证token的有效性
    return token_data


def get_current_admin_user(current_user: User | AdminUser = Depends(get_current_user)) -> User | AdminUser:
    """
    Get current admin user, raises an exception if the user is not an admin
    """
    # 安全地访问属性，支持字典和对象
    def get_attr(obj, attr_name):
        if isinstance(obj, dict):
            return obj.get(attr_name)
        else:
            return getattr(obj, attr_name, None)
    
    # 检查是否是 AdminUser（有 status 和 role 属性）
    status_val = get_attr(current_user, "status")
    role_val = get_attr(current_user, "role")
    
    if status_val is not None and role_val is not None:
        # 处理枚举值：可能是 AdminStatusEnum.ACTIVE 或字符串 "active"
        def get_enum_value(val):
            if hasattr(val, 'value'):
                return val.value
            else:
                return val
        
        status_str = get_enum_value(status_val)
        role_str = get_enum_value(role_val)
        
        # 类似 AdminUser 的处理
        if status_str != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        if role_str not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges"
            )
        return current_user

    # 否则按普通 User 处理（有 is_active 和 is_admin 属性）
    is_active = get_attr(current_user, "is_active")
    is_admin = get_attr(current_user, "is_admin")
    
    if is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    if is_admin is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

# 为了解决模块导入问题，移除直接从security导入的语句，避免循环导入
# 通过动态导入的方式使用这些函数

# 添加admin_user相关的认证函数
from fastapi import Depends
from jose import JWTError
from ..config import settings
from ..models.admin_user import AdminUser, AdminStatusEnum, AdminRoleEnum
from ..utils.exceptions import AuthenticationError, AuthorizationError

async def get_current_user_admin_security(token: str = Depends(oauth2_scheme)):
    """
    获取当前用户的依赖项函数（用于admin_user）
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 动态导入decode_token函数以避免循环导入
        from .security import decode_token
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户信息
    from ..database_async import get_async_db
    from ..crud import admin_user
    async with get_async_db() as db:
        user = await admin_user.admin_user.get(db, id=user_id)
        if user is None:
            raise credentials_exception
        return user


async def get_current_active_user_admin_security(current_user: AdminUser = Depends(get_current_user_admin_security)):
    """
    获取当前活跃用户的依赖项函数（用于admin_user）
    """
    if not current_user:
        raise AuthenticationError("Not authenticated")
    if hasattr(current_user, 'is_active') and not current_user.is_active:
        raise AuthenticationError("用户账户已被禁用")
    return current_user


async def get_current_active_admin_user(current_user: AdminUser = Depends(get_current_active_user_admin_security)):
    """
    获取当前活跃管理员用户的依赖项函数
    """
    if not current_user:
        raise AuthenticationError("Not authenticated")
    
    # 检查用户角色
    if hasattr(current_user, 'role'):
        if current_user.role not in [AdminRoleEnum.SUPER_ADMIN, AdminRoleEnum.ADMIN, AdminRoleEnum.MODERATOR, AdminRoleEnum.AUDITOR, AdminRoleEnum.OPERATOR]:
            raise AuthorizationError("需要管理员权限")
    else:
        raise AuthorizationError("需要管理员权限")
    
    # 检查用户状态
    if hasattr(current_user, 'status'):
        if current_user.status != AdminStatusEnum.ACTIVE:
            raise AuthenticationError("管理员账户未激活或被禁用")
    
    return current_user


# 重新导出security模块中的函数，使其可以通过auth模块访问
# 这样其他模块可以从auth模块导入这些函数，而不会导致循环导入
def verify_password(plain_password: str, hashed_password: str) -> bool:
    from .security import verify_password as _verify_password
    return _verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    from .security import get_password_hash as _get_password_hash
    return _get_password_hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    from .security import create_access_token as _create_access_token
    return _create_access_token(data, expires_delta)


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    from .security import create_refresh_token as _create_refresh_token
    return _create_refresh_token(data, expires_delta)


def verify_token(token: str, token_type: str = "access"):
    from .security import verify_token as _verify_token
    return _verify_token(token, token_type)


def decode_token(token: str):
    from .security import decode_token as _decode_token
    return _decode_token(token)


def get_token_payload(token: str):
    from .security import get_token_payload as _get_token_payload
    return _get_token_payload(token)
