from pydantic import BaseModel, Field  
from typing import Optional, List  
from datetime import datetime  
from enum import Enum  
  
class UserRole(str, Enum):  
    USER = "user"  
    ADMIN = "admin" 
  
class UserStatus(str, Enum):  
    ACTIVE = "active"  
    INACTIVE = "inactive"  
    PENDING = "pending"  
  
class UserBase(BaseModel):  
    username: str = Field(..., min_length=3, max_length=50)  
    email: str = Field(...)  
    nickname: Optional[str] = Field(None, max_length=50) 
  
class UserCreate(UserBase):  
    password: str = Field(..., min_length=8)  
    confirm_password: str = Field(...)  
  
class UserLogin(BaseModel):  
    username: str = Field(...)  
    password: str = Field(...)  
  
class UserInfo(UserBase):  
    id: int  
    status: UserStatus = UserStatus.PENDING  
    roles: List[str] = ["user"]  
    created_at: datetime 
  
class TokenResponse(BaseModel):  
    code: int = 200  
    message: str = "success"  
    data: dict = None  
  
