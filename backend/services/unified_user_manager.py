#!/usr/bin/env python3
"""
统一用户管理体系服务
功能：
1. 多认证源统一管理
2. 用户生命周期管理
3. 权限动态分配
4. 用户行为追踪
5. 数据同步和一致性保证
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
import hashlib
import jwt
from contextlib import contextmanager

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.database import get_db
from backend.models.user import (
    User, Role, Permission, user_roles, role_permissions, 
    UserLoginLog, UserActivity, UserSubscription
)
from backend.core.security import get_password_hash, verify_password
from backend.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

class AuthSource(Enum):
    """认证源枚举"""
    LOCAL = "local"           # 本地账号
    LDAP = "ldap"             # LDAP/AD域
    OAUTH_GOOGLE = "google"   # Google OAuth
    OAUTH_GITHUB = "github"   # GitHub OAuth
    OAUTH_WECHAT = "wechat"   # 微信登录
    API_KEY = "api_key"       # API密钥
    SSO = "sso"               # 单点登录

class UserStatus(Enum):
    """用户状态枚举"""
    ACTIVE = "active"         # 活跃
    INACTIVE = "inactive"     # 非活跃
    SUSPENDED = "suspended"   # 暂停
    BANNED = "banned"         # 禁用
    PENDING = "pending"       # 待激活
    LOCKED = "locked"         # 锁定

class UserTier(Enum):
    """用户等级枚举"""
    BRONZE = "bronze"         # 青铜
    SILVER = "silver"         # 白银
    GOLD = "gold"             # 黄金
    PLATINUM = "platinum"     # 铂金
    DIAMOND = "diamond"       # 钻石

@dataclass
class UserInfo:
    """用户信息数据类"""
    user_id: int
    username: str
    email: str
    display_name: str
    avatar_url: Optional[str]
    tier: UserTier
    status: UserStatus
    auth_sources: List[AuthSource]
    permissions: List[str]
    roles: List[str]
    created_at: datetime
    last_login_at: Optional[datetime]
    subscription_expires_at: Optional[datetime]

@dataclass
class AuthResult:
    """认证结果数据类"""
    success: bool
    user_info: Optional[UserInfo]
    access_token: Optional[str]
    refresh_token: Optional[str]
    expires_at: Optional[datetime]
    error_message: Optional[str]
    requires_2fa: bool = False

class UnifiedUserManager:
    """统一用户管理器"""
    
    def __init__(self):
        self.active_sessions = {}  # session_id -> user_info
        self.failed_attempts = {}  # username -> {count, last_attempt}
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        
    @contextmanager
    def get_db_session(self):
        """数据库会话上下文管理器"""
        db = next(get_db())
        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    async def authenticate_user(
        self, 
        username: str, 
        password: str, 
        auth_source: AuthSource = AuthSource.LOCAL,
        client_info: Optional[Dict] = None
    ) -> AuthResult:
        """统一用户认证"""
        try:
            with self.get_db_session() as db:
                # 检查账户锁定状态
                if self._is_account_locked(username):
                    return AuthResult(
                        success=False,
                        user_info=None,
                        access_token=None,
                        refresh_token=None,
                        expires_at=None,
                        error_message="账户已被锁定，请稍后再试"
                    )
                
                # 根据不同认证源处理
                if auth_source == AuthSource.LOCAL:
                    result = await self._authenticate_local(db, username, password)
                elif auth_source == AuthSource.LDAP:
                    result = await self._authenticate_ldap(username, password)
                elif auth_source in [AuthSource.OAUTH_GOOGLE, AuthSource.OAUTH_GITHUB, AuthSource.OAUTH_WECHAT]:
                    result = await self._authenticate_oauth(db, username, auth_source)
                elif auth_source == AuthSource.API_KEY:
                    result = await self._authenticate_api_key(db, username, password)
                else:
                    result = AuthResult(
                        success=False,
                        user_info=None,
                        access_token=None,
                        refresh_token=None,
                        expires_at=None,
                        error_message=f"不支持的认证方式: {auth_source}"
                    )
                
                # 记录登录日志
                await self._log_user_login(
                    db, username, result.success, client_info, 
                    result.error_message if not result.success else None
                )
                
                # 更新失败计数
                if result.success:
                    self._clear_failed_attempts(username)
                    # 更新最后登录时间
                    await self._update_last_login(db, username)
                else:
                    self._record_failed_attempt(username)
                
                return result
                
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return AuthResult(
                success=False,
                user_info=None,
                access_token=None,
                refresh_token=None,
                expires_at=None,
                error_message="认证服务暂时不可用"
            )
    
    async def _authenticate_local(self, db: Session, username: str, password: str) -> AuthResult:
        """本地账号认证"""
        # 查找用户（支持用户名或邮箱登录）
        user = db.query(User).filter(
            and_(
                or_(User.username == username, User.email == username),
                User.is_deleted == False
            )
        ).first()
        
        if not user:
            return AuthResult(
                success=False,
                user_info=None,
                access_token=None,
                refresh_token=None,
                expires_at=None,
                error_message="用户不存在"
            )
        
        # 检查用户状态
        if user.status != UserStatus.ACTIVE.value:
            status_messages = {
                UserStatus.INACTIVE.value: "账户未激活",
                UserStatus.SUSPENDED.value: "账户已被暂停",
                UserStatus.BANNED.value: "账户已被禁用",
                UserStatus.PENDING.value: "账户待激活",
                UserStatus.LOCKED.value: "账户已被锁定"
            }
            return AuthResult(
                success=False,
                user_info=None,
                access_token=None,
                refresh_token=None,
                expires_at=None,
                error_message=status_messages.get(user.status, "账户状态异常")
            )
        
        # 验证密码
        if not verify_password(password, user.password_hash):
            return AuthResult(
                success=False,
                user_info=None,
                access_token=None,
                refresh_token=None,
                expires_at=None,
                error_message="密码错误"
            )
        
        # 检查是否需要2FA
        requires_2fa = bool(user.config.get('two_factor_enabled', False))
        
        # 构建用户信息
        user_info = await self._build_user_info(db, user)
        
        # 生成令牌
        tokens = self._generate_tokens(user_info)
        
        return AuthResult(
            success=True,
            user_info=user_info,
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            expires_at=tokens['expires_at'],
            error_message=None,
            requires_2fa=requires_2fa
        )
    
    async def _authenticate_ldap(self, username: str, password: str) -> AuthResult:
        """LDAP认证（示例实现）"""
        # TODO: 集成实际的LDAP认证
        # 这里只是示例逻辑
        try:
            # ldap_client = LDAPClient(settings.LDAP_SERVER)
            # if ldap_client.authenticate(username, password):
            #     # 查找或创建本地用户记录
            #     return await self._find_or_create_ldap_user(username)
            pass
        except Exception as e:
            logger.error(f"LDAP认证失败: {e}")
        
        return AuthResult(
            success=False,
            user_info=None,
            access_token=None,
            refresh_token=None,
            expires_at=None,
            error_message="LDAP认证失败"
        )
    
    async def _authenticate_oauth(self, db: Session, username: str, auth_source: AuthSource) -> AuthResult:
        """OAuth认证"""
        # TODO: 集成实际的OAuth认证
        # 这里需要根据不同的OAuth提供商实现
        return AuthResult(
            success=False,
            user_info=None,
            access_token=None,
            refresh_token=None,
            expires_at=None,
            error_message=f"{auth_source.value} OAuth暂未实现"
        )
    
    async def _authenticate_api_key(self, db: Session, api_key: str, secret: str) -> AuthResult:
        """API密钥认证"""
        # 查找API密钥对应的用户
        # 这里需要实现API密钥的验证逻辑
        return AuthResult(
            success=False,
            user_info=None,
            access_token=None,
            refresh_token=None,
            expires_at=None,
            error_message="API密钥认证暂未实现"
        )
    
    async def create_user(
        self, 
        username: str,
        email: str,
        password: str,
        display_name: str,
        tier: UserTier = UserTier.BRONZE,
        auth_sources: List[AuthSource] = None,
        initial_roles: List[str] = None,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """创建新用户"""
        try:
            with self.get_db_session() as db:
                # 检查用户名和邮箱是否已存在
                existing_user = db.query(User).filter(
                    or_(User.username == username, User.email == email)
                ).first()
                
                if existing_user:
                    field = "用户名" if existing_user.username == username else "邮箱"
                    return {
                        'success': False,
                        'error': f'{field}已存在',
                        'user_id': None
                    }
                
                # 创建用户对象
                user = User(
                    username=username,
                    email=email,
                    password_hash=get_password_hash(password),
                    first_name=display_name.split()[0] if display_name else username,
                    last_name=' '.join(display_name.split()[1:]) if display_name and len(display_name.split()) > 1 else '',
                    nickname=display_name,
                    user_type=tier.value,
                    status=UserStatus.PENDING.value,
                    is_verified=False,
                    config=metadata or {},
                    external_source=auth_sources[0].value if auth_sources else AuthSource.LOCAL.value
                )
                
                db.add(user)
                db.flush()  # 获取用户ID
                
                # 分配初始角色
                if initial_roles:
                    await self._assign_initial_roles(db, user.id, initial_roles)
                
                # 记录用户创建活动
                await self._log_user_activity(
                    db, user.id, 'user_created', 
                    f'用户 {username} 创建成功',
                    metadata={'tier': tier.value, 'auth_sources': [src.value for src in (auth_sources or [AuthSource.LOCAL])]}
                )
                
                logger.info(f"用户创建成功: {username} (ID: {user.id})")
                
                return {
                    'success': True,
                    'error': None,
                    'user_id': user.id,
                    'username': username,
                    'email': email
                }
                
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return {
                'success': False,
                'error': f'创建用户失败: {str(e)}',
                'user_id': None
            }
    
    async def update_user_tier(self, user_id: int, new_tier: UserTier, reason: str = "") -> bool:
        """更新用户等级"""
        try:
            with self.get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return False
                
                old_tier = user.user_type
                user.user_type = new_tier.value
                
                # 记录等级变更
                await self._log_user_activity(
                    db, user_id, 'tier_changed',
                    f'用户等级从 {old_tier} 变更为 {new_tier.value}',
                    metadata={'old_tier': old_tier, 'new_tier': new_tier.value, 'reason': reason}
                )
                
                logger.info(f"用户等级更新: {user.username} {old_tier} -> {new_tier.value}")
                return True
                
        except Exception as e:
            logger.error(f"更新用户等级失败: {e}")
            return False
    
    async def suspend_user(self, user_id: int, reason: str, duration: Optional[timedelta] = None) -> bool:
        """暂停用户账户"""
        try:
            with self.get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return False
                
                user.status = UserStatus.SUSPENDED.value
                suspended_until = datetime.utcnow() + duration if duration else None
                
                # 记录暂停操作
                await self._log_user_activity(
                    db, user_id, 'account_suspended',
                    f'账户被暂停: {reason}',
                    metadata={'reason': reason, 'duration': str(duration), 'suspended_until': suspended_until}
                )
                
                logger.info(f"用户账户暂停: {user.username}, 原因: {reason}")
                return True
                
        except Exception as e:
            logger.error(f"暂停用户失败: {e}")
            return False
    
    async def get_user_info(self, user_id: int) -> Optional[UserInfo]:
        """获取用户信息"""
        try:
            with self.get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return None
                
                return await self._build_user_info(db, user)
                
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    async def _build_user_info(self, db: Session, user: User) -> UserInfo:
        """构建用户信息对象"""
        # 获取用户角色
        roles = db.query(Role).join(user_roles).filter(
            user_roles.c.user_id == user.id
        ).all()
        
        # 获取用户权限
        permissions = db.query(Permission).join(role_permissions).join(
            user_roles, role_permissions.c.role_id == user_roles.c.role_id
        ).filter(user_roles.c.user_id == user.id).distinct().all()
        
        # 获取订阅信息
        subscription = db.query(UserSubscription).filter(
            and_(
                UserSubscription.user_id == user.id,
                UserSubscription.is_active == True,
                UserSubscription.unsubscribed_at.is_(None)
            )
        ).order_by(UserSubscription.subscribed_at.desc()).first()
        
        return UserInfo(
            user_id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.nickname or f"{user.first_name} {user.last_name}".strip(),
            avatar_url=user.avatar_url,
            tier=UserTier(user.user_type),
            status=UserStatus(user.status),
            auth_sources=[AuthSource(user.external_source)] if user.external_source else [AuthSource.LOCAL],
            permissions=[p.code for p in permissions],
            roles=[r.code for r in roles],
            created_at=user.created_at,
            last_login_at=user.last_login_at,
            subscription_expires_at=subscription.unsubscribed_at if subscription else None
        )
    
    def _generate_tokens(self, user_info: UserInfo) -> Dict[str, Any]:
        """生成访问令牌"""
        payload = {
            'user_id': user_info.user_id,
            'username': user_info.username,
            'tier': user_info.tier.value,
            'permissions': user_info.permissions,
            'exp': datetime.utcnow() + timedelta(hours=24),  # 访问令牌24小时过期
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        refresh_payload = {
            'user_id': user_info.user_id,
            'exp': datetime.utcnow() + timedelta(days=7),  # 刷新令牌7天过期
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': payload['exp']
        }
    
    def _is_account_locked(self, username: str) -> bool:
        """检查账户是否被锁定"""
        if username not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[username]
        if attempts['count'] >= self.max_failed_attempts:
            lockout_time = attempts['last_attempt'] + self.lockout_duration
            if datetime.now() < lockout_time:
                return True
            else:
                # 锁定时间已过，清除失败记录
                del self.failed_attempts[username]
        
        return False
    
    def _record_failed_attempt(self, username: str):
        """记录失败尝试"""
        now = datetime.now()
        if username in self.failed_attempts:
            self.failed_attempts[username]['count'] += 1
            self.failed_attempts[username]['last_attempt'] = now
        else:
            self.failed_attempts[username] = {
                'count': 1,
                'last_attempt': now
            }
    
    def _clear_failed_attempts(self, username: str):
        """清除失败尝试记录"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
    
    async def _log_user_login(self, db: Session, username: str, success: bool, 
                             client_info: Optional[Dict], error_message: Optional[str]):
        """记录用户登录日志"""
        # 查找用户ID
        user = db.query(User).filter(
            or_(User.username == username, User.email == username)
        ).first()
        
        login_log = UserLoginLog(
            user_id=user.id if user else None,
            login_at=datetime.utcnow(),
            login_ip=client_info.get('ip_address') if client_info else None,
            user_agent=client_info.get('user_agent') if client_info else None,
            success=success,
            failure_reason=error_message,
            country=client_info.get('country') if client_info else None,
            city=client_info.get('city') if client_info else None,
            device_type=client_info.get('device_type') if client_info else None,
            browser=client_info.get('browser') if client_info else None
        )
        
        db.add(login_log)
    
    async def _log_user_activity(self, db: Session, user_id: int, activity_type: str, 
                                description: str, metadata: Dict = None):
        """记录用户活动"""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            details=metadata or {},
            activity_time=datetime.utcnow()
        )
        
        db.add(activity)
    
    async def _update_last_login(self, db: Session, username: str):
        """更新最后登录时间"""
        user = db.query(User).filter(
            or_(User.username == username, User.email == username)
        ).first()
        
        if user:
            user.last_login_at = datetime.utcnow()
            user.login_count += 1
    
    async def _assign_initial_roles(self, db: Session, user_id: int, role_codes: List[str]):
        """分配初始角色"""
        roles = db.query(Role).filter(Role.code.in_(role_codes)).all()
        
        for role in roles:
            # 插入用户角色关联
            db.execute(
                user_roles.insert().values(
                    user_id=user_id,
                    role_id=role.id,
                    assigned_at=datetime.utcnow()
                )
            )

# 全局用户管理器实例
unified_user_manager = UnifiedUserManager()