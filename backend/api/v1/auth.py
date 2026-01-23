"""
认证API端点
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from sqlalchemy.orm import Session

# 使用正确的相对导入
from ...config import settings
from ...core.database import get_db
from ...core.response import success_response
from ...schemas.user import UserCreate, UserResponse
from ...services.auth_service import AuthenticationService
from ...core.auth import get_current_user
from ...models.user import User as UserModel

router = APIRouter()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(username: str, expires_delta: Optional[timedelta] = None):
    to_encode = {"sub": username}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    auth_service = AuthenticationService(db)
    success, user, message = auth_service.register_user(user_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 创建token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.username, expires_delta=access_token_expires)
    
    # 使用统一响应格式
    return success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "username": user.username,
                "email": user.email,
                "is_active": user.status.value == "active"
            }
        },
        message="注册成功"
    )

@router.post("/login", response_model=dict)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口
    """
    auth_service = AuthenticationService(db)
    user = auth_service.authenticate_user(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.username, expires_delta=access_token_expires)
    
    # 使用统一响应格式
    return success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "username": user.username,
                "email": user.email,
                "is_active": user.status.value == "active"
            }
        },
        message="登录成功"
    )