from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..api.deps import get_current_user
from ..models.user import User


security = HTTPBearer()


async def get_current_admin(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前管理员用户
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user