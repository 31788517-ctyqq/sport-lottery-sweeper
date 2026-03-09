"""
Token相关数据模式
"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """
    令牌响应模型
    """
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    """
    令牌数据模型
    """
    username: Optional[str] = None
    user_id: Optional[int] = None
    scopes: list[str] = []