#!/usr/bin/env python3
"""
安全工具函数模块
提供密码加密、JWT令牌、安全验证等功能
"""

import hashlib
import hmac
import jwt
import secrets
import string
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# 导入FastAPI安全相关组件
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import OAuth2PasswordBearer

# 导入模型
from ..models.user import User as NormalUser  # 普通用户模型
from ..models.admin_user import AdminUser  # 管理员用户模型
from ..schemas.token import TokenData

# 导入异常类
from backend.utils.exceptions import (
    AuthenticationError,
    AuthorizationError,
    PasswordStrengthError,
    TokenValidationError
)

# 本地SecurityError定义（避免循环导入）
class SecurityError(Exception):
    """安全相关异常基类"""
    pass

# 密码加密上下文
pwd_context = CryptContext(
    schemes=["bcrypt", "pbkdf2_sha256"],
    deprecated="auto",
    bcrypt__rounds=12,
    pbkdf2_sha256__rounds=100000
)

# JWT配置 - 从配置文件导入
from backend.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

class SecurityError(Exception):
    """安全相关异常基类"""
    pass

class PasswordStrengthError(SecurityError):
    """密码强度不足异常"""
    pass

class TokenValidationError(SecurityError):
    """令牌验证失败异常"""
    pass

def generate_secret_key(length: int = 32) -> str:
    """
    生成随机密钥
    
    Args:
        length: 密钥长度
        
    Returns:
        随机生成的密钥字符串
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_password_hash(password: str) -> str:
    """
    对密码进行哈希加密
    
    Args:
        password: 明文密码
        
    Returns:
        哈希后的密码
    """
    if not password or len(password.strip()) == 0:
        raise ValueError("密码不能为空")
    
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配哈希值
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        验证结果
    """
    if not plain_password or not hashed_password:
        return False
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    验证密码强度
    
    Args:
        password: 待验证的密码
        
    Returns:
        验证结果字典
    """
    if not password:
        return {
            "valid": False,
            "score": 0,
            "errors": ["密码不能为空"],
            "strength": "very_weak"
        }
    
    errors = []
    score = 0
    strength_levels = {
        0: "very_weak",
        1: "weak", 
        2: "fair",
        3: "good",
        4: "strong",
        5: "very_strong"
    }
    
    # 长度检查
    if len(password) >= 8:
        score += 1
    else:
        errors.append("密码长度至少8位")
    
    if len(password) >= 12:
        score += 1
    
    # 字符类型检查
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if has_lower and has_upper:
        score += 1
    else:
        errors.append("密码必须包含大小写字母")
    
    if has_digit:
        score += 1
    else:
        errors.append("密码必须包含数字")
    
    if has_special:
        score += 1
    else:
        errors.append("密码必须包含特殊字符")
    
    # 常见密码检查
    common_passwords = [
        "123456", "password", "123456789", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey"
    ]
    
    if password.lower() in common_passwords:
        errors.append("密码过于常见，请选择更复杂的密码")
        score = max(0, score - 2)
    
    # 连续字符检查
    consecutive_count = 0
    max_consecutive = 1
    for i in range(1, len(password)):
        if ord(password[i]) == ord(password[i-1]) + 1:
            consecutive_count += 1
            max_consecutive = max(max_consecutive, consecutive_count)
        else:
            consecutive_count = 0
    
    if max_consecutive >= 3:
        errors.append("密码不能包含连续的字符")
        score = max(0, score - 1)
    
    valid = len(errors) == 0 and score >= 3
    strength = strength_levels.get(score, "very_weak")
    
    return {
        "valid": valid,
        "score": score,
        "errors": errors,
        "strength": strength,
        "has_lower": has_lower,
        "has_upper": has_upper,
        "has_digit": has_digit,
        "has_special": has_special,
        "length": len(password)
    }

def create_access_token(
    subject: str, 
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    创建JWT访问令牌
    
    Args:
        subject: 令牌主题（通常是用户ID或用户名）
        expires_delta: 过期时间增量
        additional_claims: 额外的声明信息
        
    Returns:
        JWT令牌字符串
    """
    if not subject:
        raise ValueError("令牌主题不能为空")
    
    to_encode = {"sub": subject}
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise TokenValidationError(f"令牌创建失败: {str(e)}")

def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建刷新令牌
    
    Args:
        subject: 令牌主题
        expires_delta: 过期时间增量
        
    Returns:
        刷新令牌字符串
    """
    if not subject:
        raise ValueError("令牌主题不能为空")
    
    if expires_delta is None:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": subject, 
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow(), 
        "type": "refresh"
    }
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise TokenValidationError(f"刷新令牌创建失败: {str(e)}")

def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌字符串
        token_type: 令牌类型 ("access" 或 "refresh")
        
    Returns:
        解码后的令牌载荷
        
    Raises:
        TokenValidationError: 令牌验证失败时抛出
    """
    if not token:
        raise TokenValidationError("令牌不能为空")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 检查令牌类型
        if payload.get("type") != token_type:
            raise TokenValidationError(f"无效的令牌类型，期望: {token_type}")
        
        # 检查过期时间
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise TokenValidationError("令牌已过期")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise TokenValidationError("令牌已过期")
    except jwt.InvalidTokenError as e:
        raise TokenValidationError(f"无效令牌: {str(e)}")
    except Exception as e:
        raise TokenValidationError(f"令牌验证失败: {str(e)}")

def generate_api_key(length: int = 32) -> str:
    """
    生成API密钥
    
    Args:
        length: 密钥长度
        
    Returns:
        API密钥字符串
    """
    return secrets.token_urlsafe(length)

def hash_data(data: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    对数据进行哈希处理
    
    Args:
        data: 待哈希的数据
        salt: 盐值（可选，会自动生成）
        
    Returns:
        (哈希值, 盐值) 元组
    """
    if not data:
        raise ValueError("数据不能为空")
    
    if salt is None:
        salt = secrets.token_hex(16)
    
    # 使用PBKDF2进行密钥派生
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(data.encode()))
    return key.decode(), salt

def constant_time_compare(val1: str, val2: str) -> bool:
    """
    常量时间比较，防止时序攻击
    
    Args:
        val1: 第一个值
        val2: 第二个值
        
    Returns:
        比较结果
    """
    return hmac.compare_digest(str(val1), str(val2))

def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除危险字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    if not filename:
        return "unknown_file"
    
    # 移除路径分隔符和危险字符
    dangerous_chars = '<>:"/\\|?*'
    safe_filename = ''.join(c for c in filename if c not in dangerous_chars)
    
    # 移除多余的空格和点
    safe_filename = safe_filename.strip('. ')
    
    # 如果文件名为空，使用默认值
    if not safe_filename:
        safe_filename = "unknown_file"
    
    # 限制文件名长度
    if len(safe_filename) > 255:
        name, ext = os.path.splitext(safe_filename)
        safe_filename = name[:250] + ext
    
    return safe_filename

def generate_csrf_token() -> str:
    """
    生成CSRF令牌
    
    Returns:
        CSRF令牌字符串
    """
    return secrets.token_urlsafe(32)


# 定义OAuth2密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# 为了兼容性，也使用reusable_oauth2名称
reusable_oauth2 = oauth2_scheme


from fastapi import HTTPException, status, Depends
from jose import JWTError
from ..models.admin_user import AdminUser, AdminStatusEnum, AdminRoleEnum
from ..config import settings
from .. import crud


async def get_current_user(token: str = Security(reusable_oauth2)):
    """
    根据token获取当前用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解析JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.exceptions.DecodeError:
        # 如果token格式不正确，抛出认证异常
        raise credentials_exception
    except jwt.ExpiredSignatureError:
        # 如果token过期，抛出认证异常
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # 其他JWT相关错误
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"JWT token error: {str(e)}")
        raise credentials_exception
    
    # 根据token中的信息判断是普通用户还是管理员用户
    user_id = payload.get("user_id")
    user_type = payload.get("user_type", "admin")  # 默认认为是管理员

    from ..database_async import get_async_db
    user = None
    async for db in get_async_db():
        if user_type == "admin":
            # 从管理员用户表中获取用户
            user = await crud.admin_user.get(db, id=user_id) if user_id else await crud.admin_user.get_by_username(db, username=token_data.username)
        else:
            # 从普通用户表中获取用户
            user = await crud.user.get_by_username(db, username=token_data.username)
        break
    
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: NormalUser = Security(get_current_user)):
    """
    获取当前活跃用户
    """
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_admin_user(
    current_user: AdminUser = Security(get_current_user)
) -> AdminUser:
    """
    获取当前活跃的管理员用户
    """
    # 检查用户是否为管理员
    if not hasattr(current_user, 'role') or not current_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户角色信息缺失"
        )

    # 检查是否为管理员角色
    if current_user.role not in [AdminRoleEnum.ADMIN, AdminRoleEnum.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )

    # 检查用户状态
    if not hasattr(current_user, 'status') or not current_user.status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户状态信息缺失"
        )

    # 检查是否处于活跃状态
    if current_user.status != AdminStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户未激活或已被禁用"
        )

    return current_user


def authenticate_user(username: str, password: str):
    """
    用户认证函数（简化版）
    """
    # 在实际实现中会查询数据库验证用户
    # 这里返回None表示未实现完整逻辑
    return None


# 密码强度检查器类
class PasswordStrengthChecker:
    """密码强度检查器"""
    
    def check_strength(self, password: str) -> int:
        """检查密码强度得分"""
        if not password:
            return 0
        
        score = 0
        
        # 长度检查
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        
        # 字符类型检查
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if has_lower and has_upper:
            score += 1
        if has_digit:
            score += 1
        if has_special:
            score += 1
        
        return min(score, 5)
    
    def get_issues(self, password: str) -> list:
        """获取密码问题列表"""
        issues = []
        
        if len(password) < 8:
            issues.append("密码长度至少8位")
        if not any(c.islower() for c in password):
            issues.append("密码必须包含小写字母")
        if not any(c.isupper() for c in password):
            issues.append("密码必须包含大写字母")
        if not any(c.isdigit() for c in password):
            issues.append("密码必须包含数字")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("密码必须包含特殊字符")
        
        return issues
    
    def get_strength_category(self, score: int) -> str:
        """获取密码强度分类"""
        categories = {
            1: "很弱",
            2: "弱", 
            3: "一般",
            4: "强",
            5: "很强"
        }
        return categories.get(score, "很弱")

def encrypt_sensitive_data(data: str, key: bytes) -> str:
    """
    加密敏感数据
    
    Args:
        data: 待加密数据
        key: 加密密钥
        
    Returns:
        加密后的数据（base64编码）
    """
    if not data or not key:
        raise ValueError("数据和密钥不能为空")
    
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()

def decrypt_sensitive_data(encrypted_data: str, key: bytes) -> str:
    """
    解密敏感数据
    
    Args:
        encrypted_data: 加密数据（base64编码）
        key: 解密密钥
        
    Returns:
        解密后的数据
    """
    if not encrypted_data or not key:
        raise ValueError("加密数据和密钥不能为空")
    
    try:
        fernet = Fernet(key)
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = fernet.decrypt(decoded_data)
        return decrypted.decode()
    except Exception as e:
        raise SecurityError(f"数据解密失败: {str(e)}")


# 安全审计日志记录器
class SecurityAuditLogger:
    """安全审计日志记录器"""
    
    def __init__(self):
        self.events = []
    
    def log_event(self, event_type: str, user_email: str = None, ip_address: str = None, details: dict = None):
        """记录安全事件"""
        event = {
            "event_type": event_type,
            "user_email": user_email,
            "ip_address": ip_address,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.events.append(event)
    
    def log_failed_login(self, email: str, ip_address: str, reason: str):
        """记录登录失败事件"""
        self.log_event(
            event_type="LOGIN_FAILED",
            user_email=email,
            ip_address=ip_address,
            details={"reason": reason}
        )
    
    def get_recent_events(self, limit: int = 10):
        """获取最近的安全事件"""
        return self.events[-limit:] if self.events else []

def decode_token(token: str) -> Dict[str, Any]:
    """
    解码JWT令牌（别名函数，兼容现有代码）
    
    Args:
        token: JWT令牌字符串
        
    Returns:
        解码后的令牌载荷
        
    Raises:
        TokenValidationError: 令牌无效时抛出
    """
    return verify_token(token, token_type="access")


def get_token_payload(token: str) -> Dict[str, Any]:
    """
    获取令牌载荷而不验证过期时间（用于调试和特殊场景）
    
    Args:
        token: JWT令牌字符串
        
    Returns:
        令牌载荷字典
        
    Raises:
        TokenValidationError: 令牌无效时抛出
    """
    if not token:
        raise TokenValidationError("令牌不能为空")
    
    try:
        # 不验证过期时间，直接解码
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        return payload
    except jwt.InvalidTokenError as e:
        raise TokenValidationError(f"无效令牌: {str(e)}")
    except Exception as e:
        raise TokenValidationError(f"令牌解析失败: {str(e)}")


# 导出常用函数
__all__ = [
    "get_password_hash",
    "verify_password",
    "validate_password_strength",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    "get_token_payload",
    "generate_api_key",
    "hash_data",
    "constant_time_compare",
    "sanitize_filename",
    "generate_csrf_token",
    "encrypt_sensitive_data",
    "decrypt_sensitive_data",
    "SecurityError",
    "PasswordStrengthError",
    "TokenValidationError"
]
