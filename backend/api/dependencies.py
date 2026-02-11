"""
兼容层：保持旧的 import 路径 backend.api.dependencies 可用。
"""
from backend.dependencies import (  # noqa: F401
    get_db,
    get_current_user,
    get_current_admin_user,
    get_current_active_user,
    get_current_active_admin_user,
    verify_websocket_token,
    validate_password_strength,
    get_password_hasher,
    get_password_verifier,
)

__all__ = [
    "get_db",
    "get_current_user",
    "get_current_admin_user",
    "get_current_active_user",
    "get_current_active_admin_user",
    "verify_websocket_token",
    "validate_password_strength",
    "get_password_hasher",
    "get_password_verifier",
]
