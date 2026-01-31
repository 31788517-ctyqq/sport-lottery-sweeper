"""
Schemas package initialization.

This file can be used to expose key Pydantic models from the submodules
for easier imports at higher levels.
"""

from .user import (
    User, UserCreate, UserUpdate, 
    UserListResponse, UserStatusEnum, 
    UserTypeEnum, AdminRoleEnum, 
    AdminStatusEnum, LoginRequest, UserLogin,
    LoginResponse, ChangePasswordRequest,
    UserStatsResponse, AdminStatsResponse,
    AdminUserBase, AdminUserCreate, 
    AdminUserUpdate, AdminUserResponse,
    AdminUserListResponse,
    BaseResponse  # BaseResponse is defined in user.py
)

from .admin_user import AdminUserDetailResponse, AdminUserResetPassword, AdminUserStatsResponse

# 兼容性别名
AdminDataCreate = AdminUserCreate
AdminDataUpdate = AdminUserUpdate
AdminDataResponse = AdminUserResponse
AdminDataListResponse = AdminUserListResponse

# 其他模型...
from .response import UnifiedResponse, PageResponse, ErrorResponse
from .system_config import SystemConfigCreate, SystemConfigUpdate
from .crawler_config import CrawlerConfigCreate, CrawlerConfigUpdate, CrawlerConfigResponse
from .intelligence_record import IntelligenceRecordCreate, IntelligenceRecordUpdate

# 重新导出所有模型
__all__ = [
    # 用户相关
    "User", "UserCreate", "UserUpdate", 
    "UserListResponse", "UserStatusEnum", 
    "UserTypeEnum", "AdminRoleEnum", 
    "AdminStatusEnum", "LoginRequest", "UserLogin",
    "LoginResponse", "ChangePasswordRequest",
    "UserStatsResponse", "AdminStatsResponse",
    "AdminUserBase", "AdminUserCreate", 
    "AdminUserUpdate", "AdminUserResponse",
    "AdminUserListResponse",
    "AdminUserDetailResponse", "AdminUserResetPassword", "AdminUserStatsResponse",
    
    # 响应相关
    "BaseResponse", "UnifiedResponse", "PageResponse", "ErrorResponse",
    
    # 系统配置相关
    "SystemConfigCreate", "SystemConfigUpdate",
    
    # 爬虫配置相关
    "CrawlerConfigCreate", "CrawlerConfigUpdate", "CrawlerConfigResponse",
    
    # 情报记录相关
    "IntelligenceRecordCreate", "IntelligenceRecordUpdate"
]
