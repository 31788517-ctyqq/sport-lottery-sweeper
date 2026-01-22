"""
Schemas package initialization.

This file can be used to expose key Pydantic models from the submodules
for easier imports at higher levels.
"""

from .user import User, UserCreate, UserUpdate, UserOut, UserListResponse
from .match import MatchBase, MatchCreate, MatchUpdate, MatchResponse, MatchListResponse

# 为向后兼容提供别名
Match = MatchResponse
from .admin_user import (
    AdminUserCreate, AdminUserUpdate, AdminUserResponse,
    AdminUserChangePassword, AdminUserResetPassword,
    AdminUserListResponse, AdminUserDetailResponse,
    AdminRoleEnum, AdminStatusEnum,
    AdminOperationLogResponse, AdminOperationLogListResponse,
    AdminLoginLogResponse, AdminLoginLogListResponse,
    AdminUserStatsResponse, AdminActivityStatsResponse
)
from .admin import UserResponse as AdminUserResponse, MatchResponse as AdminMatchResponse, CreateMatchRequest, UpdateMatchRequest
from .auth import Token, LoginRequest, LoginResponse, TokenData, UserBase, UserCreate as AuthUserCreate, UserUpdate as AuthUserUpdate, UserResponse as AuthUserResponse
from .intelligence import IntelligenceBase as Intelligence, IntelligenceCreate, IntelligenceUpdate, IntelligenceResponse
from .role import RoleResponse as Role, RoleCreate, RoleUpdate, PermissionResponse as Permission
from .token import Token, TokenData
from .response import UnifiedResponse as ResponseModel, ErrorResponse
from .data import AdminData, AdminDataCreate, AdminDataUpdate
from .system_config import SystemConfig, SystemConfigCreate, SystemConfigUpdate
from .crawler_config import CrawlerConfig, CrawlerConfigCreate, CrawlerConfigUpdate
from .intelligence_record import IntelligenceRecord, IntelligenceRecordCreate, IntelligenceRecordUpdate

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserOut", "UserListResponse",
    "Match", "MatchBase", "MatchCreate", "MatchUpdate", "MatchResponse", "MatchListResponse",
    "AdminUserCreate", "AdminUserUpdate", "AdminUserResponse",
    "AdminUserChangePassword", "AdminUserResetPassword",
    "AdminUserListResponse", "AdminUserDetailResponse",
    "AdminRoleEnum", "AdminStatusEnum",
    "AdminOperationLogResponse", "AdminOperationLogListResponse",
    "AdminLoginLogResponse", "AdminLoginLogListResponse",
    "AdminUserStatsResponse", "AdminActivityStatsResponse",
    "AdminUserResponse", "AdminMatchResponse", "CreateMatchRequest", "UpdateMatchRequest",
    "Token", "LoginRequest", "LoginResponse", "TokenData", "UserBase", "AuthUserCreate", "AuthUserUpdate", "AuthUserResponse",
    "Intelligence", "IntelligenceCreate", "IntelligenceUpdate", "IntelligenceResponse",
    "Role", "RoleCreate", "RoleUpdate", "Permission",
    "Token", "TokenData",
    "ResponseModel", "ErrorResponse",
    "AdminData", "AdminDataCreate", "AdminDataUpdate",
    "SystemConfig", "SystemConfigCreate", "SystemConfigUpdate",
    "CrawlerConfig", "CrawlerConfigCreate", "CrawlerConfigUpdate",
    "IntelligenceRecord", "IntelligenceRecordCreate", "IntelligenceRecordUpdate"
]