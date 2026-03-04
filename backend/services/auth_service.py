#!/usr/bin/env python3
"""
认证业务逻辑模块
处理用户认证、授权和相关业务逻辑
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import secrets
import re

from ..models.user import (
    User, UserRoleMapping, SocialAccount, LoginRecord, 
    PasswordResetToken, EmailVerificationToken, UserRole, UserStatus
)
from core.security import (
    get_password_hash, verify_password, validate_password_strength,
    create_access_token, create_refresh_token, verify_token
)
# AI_WORKING: coder1 @2026-01-26 - 修复UserLogin导入错误，改为LoginRequest
from ..schemas.user import UserCreate, LoginRequest, UserUpdate, ChangePasswordRequest
from utils.email import email_service
from utils.exceptions import (
    AuthenticationError, ValidationError, UserNotFoundError,
    UserAlreadyExistsError, AccountDisabledError, InvalidTokenError
)

# 临时定义异常类
class AuthenticationError(Exception): pass
class ValidationError(Exception): pass
class UserNotFoundError(Exception): pass
class UserAlreadyExistsError(Exception): pass
class AccountDisabledError(Exception): pass
class InvalidTokenError(Exception): pass

# 配置日志
logger = logging.getLogger(__name__)

class AuthenticationService:
    """认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
    def register_user(self, username: str, email: str, password: str, 
                     confirm_password: str) -> Tuple[bool, Optional[User], str]:
        """
        注册新用户
        
        Args:
            username: 用户名
            email: 邮箱地址
            password: 密码
            confirm_password: 确认密码
            
        Returns:
            (成功标志, 用户对象, 消息)
        """
        try:
            # 检查密码一致性
            if password != confirm_password:
                return False, None, "两次输入的密码不一致"
            
            # 验证密码强度
            password_validation = validate_password_strength(password)
            if not password_validation["valid"]:
                errors = "; ".join(password_validation["errors"])
                return False, None, f"密码强度不足: {errors}"
            
            # 检查用户名是否已存在
            existing_user = self.db.query(User).filter(
                or_(User.username == username, User.email == email)
            ).first()
            
            if existing_user:
                if existing_user.username == username:
                    return False, None, "用户名已存在"
                else:
                    return False, None, "邮箱已被注册"
            
            # 创建用户对象
            hashed_password = get_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                status=UserStatus.PENDING,
                email_verified=False,
                login_count=0
            )
            
            # 保存到数据库
            self.db.add(new_user)
            self.db.flush()  # 获取用户ID但不提交事务
            
            # 分配默认用户角色
            default_role = UserRoleMapping(
                user_id=new_user.id,
                role=UserRole.USER,
                granted_by=new_user.id  # 自授权
            )
            self.db.add(default_role)
            
            # 提交事务
            self.db.commit()
            self.db.refresh(new_user)
            
            # 发送欢迎邮件
            try:
                email_service.send_welcome_email(new_user.email, new_user.username)
            except Exception as e:
                logger.warning(f"发送欢迎邮件失败: {str(e)}")
            
            # 记录注册日志
            logger.info(f"用户注册成功: {username} ({email})")
            
            return True, new_user, "注册成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"用户注册异常: {str(e)}")
            return False, None, "注册过程中发生错误"
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        用户认证
        
        Args:
            username: 用户名或邮箱
            password: 密码
            
        Returns:
            用户对象或None
        """
        try:
            # 查找用户（支持用户名或邮箱登录）
            user = self.db.query(User).filter(
                and_(
                    or_(User.username == username, User.email == username),
                    User.status != UserStatus.BANNED
                )
            ).first()
            
            if not user:
                # 记录失败的登录尝试
                self._record_login_attempt(username, None, False, "用户不存在")
                return None
            
            # 检查账户状态
            if not user.is_active:
                self._record_login_attempt(username, user.id, False, "账户未激活或被禁用")
                raise AccountDisabledError("账户已被禁用")
            
            # 验证密码
            if not verify_password(password, user.hashed_password):
                self._record_login_attempt(username, user.id, False, "密码错误")
                return None
            
            # 更新最后登录信息
            self.update_last_login(user.id)
            
            # 记录成功的登录
            self._record_login_attempt(username, user.id, True)
            
            logger.info(f"用户登录成功: {user.username} ({user.email})")
            
            return user
            
        except AccountDisabledError:
            raise
        except Exception as e:
            logger.error(f"用户认证异常: {str(e)}")
            self._record_login_attempt(username, None, False, f"认证异常: {str(e)}")
            return None
    
    def update_last_login(self, user_id: int, ip_address: str = None, user_agent: str = None):
        """
        更新用户最后登录信息
        
        Args:
            user_id: 用户ID
            ip_address: IP地址
            user_agent: 用户代理
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login_time = datetime.utcnow()
                user.last_login_ip = ip_address
                user.login_count += 1
                self.db.commit()
        except Exception as e:
            logger.error(f"更新最后登录信息失败: {str(e)}")
            self.db.rollback()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象或None
        """
        try:
            return self.db.query(User).filter(
                and_(User.id == user_id, User.status != UserStatus.BANNED)
            ).first()
        except Exception as e:
            logger.error(f"获取用户信息异常: {str(e)}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            用户对象或None
        """
        try:
            return self.db.query(User).filter(
                and_(User.username == username, User.status != UserStatus.BANNED)
            ).first()
        except Exception as e:
            logger.error(f"根据用户名获取用户信息异常: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: int, user_data: UserUpdate) -> Tuple[bool, str]:
        """
        更新用户资料
        
        Args:
            user_id: 用户ID
            user_data: 用户更新数据
            
        Returns:
            (成功标志, 消息)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在"
            
            # 更新字段
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)
            
            self.db.commit()
            logger.info(f"用户资料更新成功: {user.username}")
            
            return True, "资料更新成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户资料异常: {str(e)}")
            return False, "更新过程中发生错误"
    
    def change_password(self, user_id: int, password_data: ChangePasswordRequest) -> Tuple[bool, str]:
        """
        修改用户密码
        
        Args:
            user_id: 用户ID
            password_data: 密码更新数据
            
        Returns:
            (成功标志, 消息)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在"
            
            # 验证原密码
            if not verify_password(password_data.old_password, user.hashed_password):
                return False, "原密码错误"
            
            # 验证新密码强度
            password_validation = validate_password_strength(password_data.new_password)
            if not password_validation["valid"]:
                errors = "; ".join(password_validation["errors"])
                return False, f"新密码强度不足: {errors}"
            
            # 更新密码
            new_hashed_password = get_password_hash(password_data.new_password)
            user.hashed_password = new_hashed_password
            
            self.db.commit()
            
            # 使所有现有的刷新令牌失效
            self._invalidate_user_tokens(user_id)
            
            logger.info(f"用户密码修改成功: {user.username}")
            
            return True, "密码修改成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"修改用户密码异常: {str(e)}")
            return False, "修改过程中发生错误"
    
    def create_password_reset_token(self, email: str) -> Tuple[bool, str]:
        """
        创建密码重置令牌
        
        Args:
            email: 用户邮箱
            
        Returns:
            (成功标志, 消息)
        """
        try:
            user = self.db.query(User).filter(
                and_(User.email == email, User.status != UserStatus.BANNED)
            ).first()
            
            if not user:
                # 为了安全，即使用户不存在也返回成功消息
                return True, "如果该邮箱存在，重置链接将发送到您的邮箱"
            
            # 生成重置令牌
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=1)  # 1小时有效期
            
            # 使之前的重置令牌失效
            self.db.query(PasswordResetToken).filter(
                and_(
                    PasswordResetToken.user_id == user.id,
                    PasswordResetToken.used == False
                )
            ).update({"used": True})
            
            # 创建新的重置令牌
            new_reset_token = PasswordResetToken(
                user_id=user.id,
                token=reset_token,
                expires_at=expires_at
            )
            
            self.db.add(new_reset_token)
            self.db.commit()
            
            # 发送重置邮件
            try:
                email_service.send_password_reset_email(
                    user.email, user.username, reset_token
                )
            except Exception as e:
                logger.error(f"发送密码重置邮件失败: {str(e)}")
                return False, "发送重置邮件失败"
            
            logger.info(f"密码重置令牌创建成功: {user.username}")
            
            return True, "重置链接已发送到您的邮箱"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建密码重置令牌异常: {str(e)}")
            return False, "创建重置令牌时发生错误"
    
    def reset_password(self, token: str, new_password: str) -> Tuple[bool, str]:
        """
        重置密码
        
        Args:
            token: 重置令牌
            new_password: 新密码
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 查找有效的重置令牌
            reset_token = self.db.query(PasswordResetToken).filter(
                and_(
                    PasswordResetToken.token == token,
                    PasswordResetToken.used == False,
                    PasswordResetToken.expires_at > datetime.utcnow()
                )
            ).first()
            
            if not reset_token:
                return False, "重置链接无效或已过期"
            
            # 验证新密码强度
            password_validation = validate_password_strength(new_password)
            if not password_validation["valid"]:
                errors = "; ".join(password_validation["errors"])
                return False, f"密码强度不足: {errors}"
            
            # 更新用户密码
            user = self.db.query(User).filter(User.id == reset_token.user_id).first()
            if not user:
                return False, "用户不存在"
            
            user.hashed_password = get_password_hash(new_password)
            
            # 标记令牌为已使用
            reset_token.used = True
            reset_token.used_at = datetime.utcnow()
            
            self.db.commit()
            
            # 使所有现有的令牌失效
            self._invalidate_user_tokens(user.id)
            
            logger.info(f"密码重置成功: {user.username}")
            
            return True, "密码重置成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"重置密码异常: {str(e)}")
            return False, "重置密码时发生错误"
    
    def verify_email(self, token: str) -> Tuple[bool, str]:
        """
        验证邮箱
        
        Args:
            token: 验证令牌
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 查找有效的验证令牌
            verification_token = self.db.query(EmailVerificationToken).filter(
                and_(
                    EmailVerificationToken.token == token,
                    EmailVerificationToken.used == False,
                    EmailVerificationToken.expires_at > datetime.utcnow()
                )
            ).first()
            
            if not verification_token:
                return False, "验证链接无效或已过期"
            
            # 更新用户邮箱验证状态
            user = self.db.query(User).filter(User.id == verification_token.user_id).first()
            if not user:
                return False, "用户不存在"
            
            user.email_verified = True
            user.status = UserStatus.ACTIVE
            
            # 标记令牌为已使用
            verification_token.used = True
            verification_token.used_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"邮箱验证成功: {user.username}")
            
            return True, "邮箱验证成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"邮箱验证异常: {str(e)}")
            return False, "验证过程中发生错误"
    
    def assign_role(self, user_id: int, role: UserRole, granted_by: int) -> Tuple[bool, str]:
        """
        为用户分配角色
        
        Args:
            user_id: 用户ID
            role: 角色
            granted_by: 授权人ID
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 检查用户是否存在
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "用户不存在"
            
            # 检查授权人权限
            granter = self.db.query(User).filter(User.id == granted_by).first()
            if not granter or not granter.has_admin_role:
                return False, "没有权限分配角色"
            
            # 检查角色是否已存在
            existing_role = self.db.query(UserRoleMapping).filter(
                and_(
                    UserRoleMapping.user_id == user_id,
                    UserRoleMapping.role == role
                )
            ).first()
            
            if existing_role:
                return False, "用户已拥有该角色"
            
            # 分配角色
            new_role_mapping = UserRoleMapping(
                user_id=user_id,
                role=role,
                granted_by=granted_by
            )
            
            self.db.add(new_role_mapping)
            self.db.commit()
            
            logger.info(f"角色分配成功: 用户{user.username} -> 角色{role.value}")
            
            return True, "角色分配成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"分配角色异常: {str(e)}")
            return False, "分配角色时发生错误"
    
    def remove_role(self, user_id: int, role: UserRole, removed_by: int) -> Tuple[bool, str]:
        """
        移除用户角色
        
        Args:
            user_id: 用户ID
            role: 角色
            removed_by: 操作者ID
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 检查操作者权限
            remover = self.db.query(User).filter(User.id == removed_by).first()
            if not remover or not remover.has_admin_role:
                return False, "没有权限移除角色"
            
            # 查找并删除角色映射
            role_mapping = self.db.query(UserRoleMapping).filter(
                and_(
                    UserRoleMapping.user_id == user_id,
                    UserRoleMapping.role == role
                )
            ).first()
            
            if not role_mapping:
                return False, "用户没有该角色"
            
            self.db.delete(role_mapping)
            self.db.commit()
            
            logger.info(f"角色移除成功: 用户{user_id} -> 角色{role.value}")
            
            return True, "角色移除成功"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"移除角色异常: {str(e)}")
            return False, "移除角色时发生错误"
    
    def get_user_roles(self, user_id: int) -> List[UserRole]:
        """
        获取用户角色列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            角色列表
        """
        try:
            role_mappings = self.db.query(UserRoleMapping).filter(
                UserRoleMapping.user_id == user_id
            ).all()
            
            return [mapping.role for mapping in role_mappings]
            
        except Exception as e:
            logger.error(f"获取用户角色异常: {str(e)}")
            return []
    
    def _record_login_attempt(self, username: str, user_id: Optional[int], 
                           success: bool, failure_reason: str = None):
        """
        记录登录尝试
        
        Args:
            username: 用户名
            user_id: 用户ID
            success: 是否成功
            failure_reason: 失败原因
        """
        try:
            login_record = LoginRecord(
                user_id=user_id,
                login_ip="127.0.0.1",  # 实际应用中从请求中获取
                user_agent="Unknown",   # 实际应用中从请求中获取
                success=success,
                failure_reason=failure_reason
            )
            
            self.db.add(login_record)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"记录登录尝试失败: {str(e)}")
            self.db.rollback()
    
    def _invalidate_user_tokens(self, user_id: int):
        """
        使用户的令牌失效
        
        Args:
            user_id: 用户ID
        """
        try:
            # 标记所有密码重置令牌为已使用
            self.db.query(PasswordResetToken).filter(
                and_(
                    PasswordResetToken.user_id == user_id,
                    PasswordResetToken.used == False
                )
            ).update({"used": True})
            
            # 标记所有邮箱验证令牌为已使用
            self.db.query(EmailVerificationToken).filter(
                and_(
                    EmailVerificationToken.user_id == user_id,
                    EmailVerificationToken.used == False
                )
            ).update({"used": True})
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"使令牌失效异常: {str(e)}")
            self.db.rollback()
    
    def cleanup_expired_tokens(self) -> int:
        """
        清理过期的令牌
        
        Returns:
            清理的令牌数量
        """
        try:
            # 清理过期的密码重置令牌
            deleted_reset = self.db.query(PasswordResetToken).filter(
                PasswordResetToken.expires_at <= datetime.utcnow()
            ).delete()
            
            # 清理过期的邮箱验证令牌
            deleted_verification = self.db.query(EmailVerificationToken).filter(
                EmailVerificationToken.expires_at <= datetime.utcnow()
            ).delete()
            
            self.db.commit()
            
            total_deleted = deleted_reset + deleted_verification
            logger.info(f"清理过期令牌: {total_deleted} 个")
            
            return total_deleted
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"清理过期令牌异常: {str(e)}")
            return 0

# 导出服务类
__all__ = ["AuthenticationService"]