"""
认证和授权业务服务
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..core.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    create_refresh_token
)
from ..core.database import get_db_session
from ..models.user import (
    User, 
    Role, 
    Permission, 
    UserLoginLog, 
    UserActivity,
    UserStatusEnum,
    UserTypeEnum
)
from ..schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserResponse,
    TokenData,
    LoginRequest
)
from backend.config import settings

# 设置日志
logger = logging.getLogger(__name__)

class AuthenticationService:
    """认证服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        验证用户凭据
        
        Args:
            username: 用户名或邮箱
            password: 密码
            
        Returns:
            Optional[User]: 验证成功的用户，失败返回None
        """
        try:
            # 尝试通过用户名或邮箱查找用户
            user = self.db.query(User).filter(
                or_(
                    User.username == username,
                    User.email == username
                )
            ).first()
            
            if not user:
                logger.warning(f"用户不存在: {username}")
                return None
            
            if not verify_password(password, user.hashed_password):
                logger.warning(f"密码错误: {username}")
                return None
            
            if not user.is_active:
                logger.warning(f"用户被禁用: {username}")
                return None
            
            # 记录登录日志
            self._log_user_login(user, success=True)
            
            return user
            
        except Exception as e:
            logger.error(f"用户认证失败: {str(e)}")
            return None
    
    def register_user(self, user_data: UserCreate) -> Tuple[bool, Optional[User], str]:
        """
        注册新用户
        
        Args:
            user_data: 用户注册数据
            
        Returns:
            Tuple[bool, Optional[User], str]: (成功标志, 用户对象, 错误消息)
        """
        try:
            # 检查用户名是否已存在
            existing_user = self.db.query(User).filter(
                User.username == user_data.username
            ).first()
            if existing_user:
                return False, None, "用户名已存在"
            
            # 检查邮箱是否已存在
            existing_email = self.db.query(User).filter(
                User.email == user_data.email
            ).first()
            if existing_email:
                return False, None, "邮箱已存在"
            
            # 创建新用户
            hashed_password = get_password_hash(user_data.password)
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                is_active=True,
                is_verified=False,
                is_superuser=False,
                user_type=UserTypeEnum.NORMAL,
                status=UserStatusEnum.ACTIVE
            )
            
            # 分配默认角色
            default_role = self.db.query(Role).filter(
                Role.is_default == True
            ).first()
            if default_role:
                user.roles.append(default_role)
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            # 记录用户活动
            self._log_user_activity(
                user.id, 
                "register", 
                "用户注册",
                resource_type="user",
                resource_id=str(user.id)
            )
            
            logger.info(f"用户注册成功: {user.username} (ID: {user.id})")
            return True, user, "注册成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"用户注册失败: {str(e)}")
            return False, None, f"注册失败: {str(e)}"
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        修改用户密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            Tuple[bool, str]: (成功标志, 消息)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在"
            
            if not verify_password(old_password, user.hashed_password):
                return False, "旧密码错误"
            
            user.hashed_password = get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # 记录用户活动
            self._log_user_activity(
                user.id,
                "change_password",
                "修改密码",
                resource_type="user",
                resource_id=str(user.id)
            )
            
            logger.info(f"用户密码修改成功: {user.username}")
            return True, "密码修改成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"密码修改失败: {str(e)}")
            return False, f"密码修改失败: {str(e)}"
    
    def reset_password(self, email: str, new_password: str) -> Tuple[bool, str]:
        """
        重置用户密码（管理员或忘记密码功能）
        
        Args:
            email: 用户邮箱
            new_password: 新密码
            
        Returns:
            Tuple[bool, str]: (成功标志, 消息)
        """
        try:
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                return False, "用户不存在"
            
            user.hashed_password = get_password_hash(new_password)
            user.reset_password_token = None
            user.reset_password_expires = None
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # 记录用户活动
            self._log_user_activity(
                user.id,
                "reset_password",
                "重置密码",
                resource_type="user",
                resource_id=str(user.id)
            )
            
            logger.info(f"用户密码重置成功: {user.email}")
            return True, "密码重置成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"密码重置失败: {str(e)}")
            return False, f"密码重置失败: {str(e)}"
    
    def verify_email(self, user_id: int) -> Tuple[bool, str]:
        """
        验证用户邮箱
        
        Args:
            user_id: 用户ID
            
        Returns:
            Tuple[bool, str]: (成功标志, 消息)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在"
            
            user.is_verified = True
            user.email_verified_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # 记录用户活动
            self._log_user_activity(
                user.id,
                "verify_email",
                "验证邮箱",
                resource_type="user",
                resource_id=str(user.id)
            )
            
            logger.info(f"用户邮箱验证成功: {user.email}")
            return True, "邮箱验证成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"邮箱验证失败: {str(e)}")
            return False, f"邮箱验证失败: {str(e)}"
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Tuple[bool, Optional[User], str]:
        """
        更新用户资料
        
        Args:
            user_id: 用户ID
            profile_data: 资料数据
            
        Returns:
            Tuple[bool, Optional[User], str]: (成功标志, 用户对象, 消息)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, None, "用户不存在"
            
            # 检查邮箱是否已被其他用户使用
            if 'email' in profile_data and profile_data['email'] != user.email:
                existing_email = self.db.query(User).filter(
                    User.email == profile_data['email'],
                    User.id != user_id
                ).first()
                if existing_email:
                    return False, None, "邮箱已被其他用户使用"
            
            # 更新字段
            for field, value in profile_data.items():
                if hasattr(user, field) and field not in ['id', 'username', 'hashed_password', 'is_superuser']:
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            # 记录用户活动
            self._log_user_activity(
                user.id,
                "update_profile",
                "更新资料",
                resource_type="user",
                resource_id=str(user.id)
            )
            
            logger.info(f"用户资料更新成功: {user.username}")
            return True, user, "资料更新成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"用户资料更新失败: {str(e)}")
            return False, None, f"资料更新失败: {str(e)}"
    
    def _log_user_login(self, user: User, success: bool = True, ip_address: str = None, user_agent: str = None):
        """记录用户登录日志"""
        try:
            login_log = UserLoginLog(
                user_id=user.id,
                success=success,
                login_ip=ip_address,
                user_agent=user_agent,
                login_at=datetime.utcnow()
            )
            
            self.db.add(login_log)
            
            # 更新用户登录信息
            if success:
                user.last_login = datetime.utcnow()
                user.login_count += 1
                user.failed_login_count = 0
            else:
                user.failed_login_count += 1
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"记录登录日志失败: {str(e)}")
            self.db.rollback()
    
    def _log_user_activity(self, user_id: int, activity_type: str, description: str, 
                          resource_type: str = None, resource_id: str = None,
                          details: Dict = None):
        """记录用户活动日志"""
        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                activity_time=datetime.utcnow(),
                description=description,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {}
            )
            
            self.db.add(activity)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"记录用户活动失败: {str(e)}")
            self.db.rollback()

class TokenService:
    """令牌服务"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_tokens(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        创建访问令牌和刷新令牌
        
        Args:
            user_data: 用户数据
            
        Returns:
            Dict[str, str]: 令牌字典
        """
        # 创建访问令牌
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user_data.get("username")},
            expires_delta=access_token_expires
        )
        
        # 创建刷新令牌
        refresh_token_expires = timedelta(days=self.refresh_token_expire_days)
        refresh_token = create_refresh_token(
            data={"sub": user_data.get("username")},
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            Optional[Dict[str, Any]]: 令牌载荷，验证失败返回None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        使用刷新令牌获取新的访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            Optional[Dict[str, str]]: 新的令牌，失败返回None
        """
        try:
            payload = self.verify_token(refresh_token)
            if not payload:
                return None
            
            username = payload.get("sub")
            if not username:
                return None
            
            # 创建新的访问令牌
            access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
            access_token = create_access_token(
                data={"sub": username},
                expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,  # 返回原来的刷新令牌
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
            
        except Exception as e:
            logger.error(f"刷新令牌失败: {str(e)}")
            return None

class PermissionService:
    """权限服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_permission(self, user_id: int, permission_code: str) -> bool:
        """
        检查用户是否拥有指定权限
        
        Args:
            user_id: 用户ID
            permission_code: 权限代码
            
        Returns:
            bool: 是否拥有权限
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # 超级用户拥有所有权限
            if user.is_superuser:
                return True
            
            # 检查用户角色是否拥有该权限
            for role in user.roles:
                for permission in role.permissions:
                    if permission.code == permission_code:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查权限失败: {str(e)}")
            return False
    
    def check_resource_permission(self, user_id: int, resource: str, action: str = "read") -> bool:
        """
        检查用户是否可以对指定资源执行指定操作
        
        Args:
            user_id: 用户ID
            resource: 资源名称
            action: 操作类型
            
        Returns:
            bool: 是否拥有权限
        """
        permission_code = f"{resource}.{action}"
        return self.check_permission(user_id, permission_code)
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        获取用户所有权限代码
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[str]: 权限代码列表
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            # 超级用户拥有所有权限
            if user.is_superuser:
                permissions = self.db.query(Permission).all()
                return [p.code for p in permissions]
            
            # 获取用户所有角色的权限
            permissions = set()
            for role in user.roles:
                for permission in role.permissions:
                    permissions.add(permission.code)
            
            return list(permissions)
            
        except Exception as e:
            logger.error(f"获取用户权限失败: {str(e)}")
            return []
    
    def assign_role_to_user(self, user_id: int, role_id: int) -> Tuple[bool, str]:
        """
        为用户分配角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            
        Returns:
            Tuple[bool, str]: (成功标志, 消息)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在"
            
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role:
                return False, "角色不存在"
            
            # 检查是否已拥有该角色
            if role in user.roles:
                return False, "用户已拥有该角色"
            
            # 分配角色
            user.roles.append(role)
            self.db.commit()
            
            logger.info(f"为用户分配角色成功: 用户ID={user_id}, 角色ID={role_id}")
            return True, "角色分配成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"分配角色失败: {str(e)}")
            return False, f"分配角色失败: {str(e)}"
    
    def remove_role_from_user(self, user_id: int, role_id: int) -> Tuple[bool, str]:
        """
        移除用户的角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
            
        Returns:
            Tuple[bool, str]: (成功标志, 消息)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在"
            
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role:
                return False, "角色不存在"
            
            # 检查是否拥有该角色
            if role not in user.roles:
                return False, "用户未拥有该角色"
            
            # 不能移除超级管理员角色的超级用户
            if role.code == "super_admin" and user.is_superuser:
                return False, "不能移除超级管理员的超级用户角色"
            
            # 移除角色
            user.roles.remove(role)
            self.db.commit()
            
            logger.info(f"移除用户角色成功: 用户ID={user_id}, 角色ID={role_id}")
            return True, "角色移除成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"移除角色失败: {str(e)}")
            return False, f"移除角色失败: {str(e)}"

class UserManagementService:
    """用户管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_users(self, page: int = 1, page_size: int = 20, filters: Dict = None) -> Dict[str, Any]:
        """
        获取用户列表
        
        Args:
            page: 页码
            page_size: 每页数量
            filters: 过滤条件
            
        Returns:
            Dict[str, Any]: 用户列表和分页信息
        """
        try:
            query = self.db.query(User)
            
            # 应用过滤条件
            if filters:
                if 'username' in filters and filters['username']:
                    query = query.filter(User.username.ilike(f"%{filters['username']}%"))
                
                if 'email' in filters and filters['email']:
                    query = query.filter(User.email.ilike(f"%{filters['email']}%"))
                
                if 'is_active' in filters and filters['is_active'] is not None:
                    query = query.filter(User.is_active == filters['is_active'])
                
                if 'is_superuser' in filters and filters['is_superuser'] is not None:
                    query = query.filter(User.is_superuser == filters['is_superuser'])
                
                if 'user_type' in filters and filters['user_type']:
                    query = query.filter(User.user_type == filters['user_type'])
                
                if 'status' in filters and filters['status']:
                    query = query.filter(User.status == filters['status'])
            
            # 获取总数
            total = query.count()
            
            # 应用分页
            offset = (page - 1) * page_size
            users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()
            
            return {
                "users": users,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            return {
                "users": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象
        """
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"获取用户失败: {str(e)}")
            return None
    
    def update_user_status(self, user_id: int, is_active: bool) -> Tuple[bool, str]:
        """
        更新用户状态（激活/禁用）
        
        Args:
            user_id: 用户ID
            is_active: 是否激活
            
        Returns:
            Tuple[bool, str]: (成功标志, 消息)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在"
            
            user.is_active = is_active
            user.status = UserStatusEnum.ACTIVE if is_active else UserStatusEnum.INACTIVE
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            status_text = "激活" if is_active else "禁用"
            logger.info(f"用户状态更新成功: 用户ID={user_id}, 状态={status_text}")
            return True, f"用户已{status_text}"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户状态失败: {str(e)}")
            return False, f"更新用户状态失败: {str(e)}"
    
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Tuple[bool, str]: (成功标志, 消息)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在"
            
            # 不能删除超级用户
            if user.is_superuser:
                return False, "不能删除超级用户"
            
            # 软删除
            user.is_active = False
            user.status = UserStatusEnum.BANNED
            user.is_deleted = True
            user.deleted_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"用户删除成功: 用户ID={user_id}")
            return True, "用户删除成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除用户失败: {str(e)}")
            return False, f"删除用户失败: {str(e)}"
    
    def get_user_stats(self) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 总用户数
            total_users = self.db.query(func.count(User.id)).scalar()
            
            # 活跃用户数
            active_users = self.db.query(func.count(User.id)).filter(
                User.is_active == True
            ).scalar()
            
            # 今日新增用户数
            today = datetime.utcnow().date()
            today_users = self.db.query(func.count(User.id)).filter(
                func.date(User.created_at) == today
            ).scalar()
            
            # 用户类型分布
            user_type_stats = self.db.query(
                User.user_type,
                func.count(User.id)
            ).group_by(User.user_type).all()
            
            # 用户状态分布
            user_status_stats = self.db.query(
                User.status,
                func.count(User.id)
            ).group_by(User.status).all()
            
            # 最近7天用户增长
            last_7_days = []
            for i in range(6, -1, -1):
                date = today - timedelta(days=i)
                count = self.db.query(func.count(User.id)).filter(
                    func.date(User.created_at) == date
                ).scalar()
                last_7_days.append({
                    "date": date.isoformat(),
                    "count": count
                })
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "today_new_users": today_users,
                "user_type_distribution": [
                    {"type": t[0].value if t[0] else "unknown", "count": t[1]}
                    for t in user_type_stats
                ],
                "user_status_distribution": [
                    {"status": s[0].value if s[0] else "unknown", "count": s[1]}
                    for s in user_status_stats
                ],
                "last_7_days_growth": last_7_days
            }
            
        except Exception as e:
            logger.error(f"获取用户统计失败: {str(e)}")
            return {
                "total_users": 0,
                "active_users": 0,
                "today_new_users": 0,
                "user_type_distribution": [],
                "user_status_distribution": [],
                "last_7_days_growth": []
            }

# 创建服务实例的工厂函数
def get_auth_service(db: Session = None) -> AuthenticationService:
    """获取认证服务实例"""
    if db is None:
        db = next(get_db_session())
    return AuthenticationService(db)

def get_token_service() -> TokenService:
    """获取令牌服务实例"""
    return TokenService()

def get_permission_service(db: Session = None) -> PermissionService:
    """获取权限服务实例"""
    if db is None:
        db = next(get_db_session())
    return PermissionService(db)

def get_user_management_service(db: Session = None) -> UserManagementService:
    """获取用户管理服务实例"""
    if db is None:
        db = next(get_db_session())
    return UserManagementService(db)