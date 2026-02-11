#!/usr/bin/env python3
"""
用户活动日志服务
提供用户行为追踪和审计日志功能
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import json
import logging

from backend.models.log_entry import LogEntry
from backend.models.user import User
from backend.models.admin_user import AdminUser

class UserActivityLogger:
    """
    用户活动日志记录器
    
    提供统一的用户行为日志记录接口，支持：
    - 用户认证事件（登录、登出、失败尝试）
    - 用户资料修改
    - 权限变更
    - 敏感操作审计
    - 会话管理事件
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    def log_user_login(self, 
                      user_id: int, 
                      username: str, 
                      ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None,
                      success: bool = True,
                      failure_reason: Optional[str] = None):
        """
        记录用户登录事件
        
        Args:
            user_id: 用户ID
            username: 用户名
            ip_address: 客户端IP地址
            user_agent: 用户代理字符串
            success: 登录是否成功
            failure_reason: 失败原因（如果登录失败）
        """
        level = "INFO" if success else "WARN"
        message = f"用户 {username} 登录{'成功' if success else '失败'}"
        if not success and failure_reason:
            message += f": {failure_reason}"
        
        self._create_log_entry(
            level=level,
            module="auth",
            message=message,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=json.dumps({
                "event_type": "login",
                "success": success,
                "username": username,
                "failure_reason": failure_reason
            })
        )
    
    def log_user_logout(self, 
                       user_id: int, 
                       username: str, 
                       ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None):
        """
        记录用户登出事件
        
        Args:
            user_id: 用户ID
            username: 用户名
            ip_address: 客户端IP地址
            user_agent: 用户代理字符串
        """
        self._create_log_entry(
            level="INFO",
            module="auth",
            message=f"用户 {username} 已登出",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=json.dumps({
                "event_type": "logout",
                "username": username
            })
        )
    
    def log_profile_update(self, 
                          user_id: int, 
                          username: str,
                          updated_fields: Dict[str, Any],
                          ip_address: Optional[str] = None,
                          user_agent: Optional[str] = None):
        """
        记录用户资料更新事件
        
        Args:
            user_id: 用户ID
            username: 用户名
            updated_fields: 更新的字段字典
            ip_address: 客户端IP地址
            user_agent: 用户代理字符串
        """
        # 过滤敏感字段（如密码）
        safe_fields = {k: v for k, v in updated_fields.items() 
                      if k not in ['password', 'hashed_password']}
        
        if not safe_fields:
            return  # 如果没有可记录的安全字段，跳过记录
            
        message = f"用户 {username} 更新了个人资料: {', '.join(safe_fields.keys())}"
        
        self._create_log_entry(
            level="INFO",
            module="user_profile",
            message=message,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=json.dumps({
                "event_type": "profile_update",
                "username": username,
                "updated_fields": list(safe_fields.keys())
            })
        )
    
    def log_password_change(self, 
                           user_id: int, 
                           username: str,
                           ip_address: Optional[str] = None,
                           user_agent: Optional[str] = None):
        """
        记录用户密码修改事件
        
        Args:
            user_id: 用户ID
            username: 用户名
            ip_address: 客户端IP地址
            user_agent: 用户代理字符串
        """
        self._create_log_entry(
            level="INFO",
            module="user_profile",
            message=f"用户 {username} 修改了密码",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=json.dumps({
                "event_type": "password_change",
                "username": username
            })
        )
    
    def log_avatar_upload(self, 
                         user_id: int, 
                         username: str,
                         avatar_url: str,
                         ip_address: Optional[str] = None,
                         user_agent: Optional[str] = None):
        """
        记录用户头像上传事件
        
        Args:
            user_id: 用户ID
            username: 用户名
            avatar_url: 头像URL
            ip_address: 客户端IP地址
            user_agent: 用户代理字符串
        """
        self._create_log_entry(
            level="INFO",
            module="user_profile",
            message=f"用户 {username} 上传了新头像",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=json.dumps({
                "event_type": "avatar_upload",
                "username": username,
                "avatar_url": avatar_url
            })
        )
    
    def log_permission_change(self, 
                             user_id: int, 
                             username: str,
                             old_role: str,
                             new_role: str,
                             changed_by_user_id: int,
                             changed_by_username: str,
                             ip_address: Optional[str] = None,
                             user_agent: Optional[str] = None):
        """
        记录用户权限变更事件
        
        Args:
            user_id: 被修改权限的用户ID
            username: 被修改权限的用户名
            old_role: 原角色
            new_role: 新角色
            changed_by_user_id: 执行修改的用户ID
            changed_by_username: 执行修改的用户名
            ip_address: 客户端IP地址
            user_agent: 用户代理字符串
        """
        message = f"用户 {username} 的角色从 {old_role} 变更为 {new_role} (由 {changed_by_username} 操作)"
        
        self._create_log_entry(
            level="WARN",  # 权限变更是重要事件
            module="user_management",
            message=message,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=json.dumps({
                "event_type": "permission_change",
                "target_user": {"id": user_id, "username": username},
                "changed_by": {"id": changed_by_user_id, "username": changed_by_username},
                "old_role": old_role,
                "new_role": new_role
            })
        )
    
    def log_token_refresh(self, 
                         user_id: int, 
                         username: str,
                         ip_address: Optional[str] = None,
                         user_agent: Optional[str] = None):
        """
        记录令牌刷新事件
        
        Args:
            user_id: 用户ID
            username: 用户名
            ip_address: 客户端IP地址
            user_agent: 用户代理字符串
        """
        self._create_log_entry(
            level="INFO",
            module="auth",
            message=f"用户 {username} 刷新了访问令牌",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=json.dumps({
                "event_type": "token_refresh",
                "username": username
            })
        )
    
    def _create_log_entry(self, 
                         level: str, 
                         module: str, 
                         message: str,
                         user_id: Optional[int] = None,
                         ip_address: Optional[str] = None,
                         user_agent: Optional[str] = None,
                         extra_data: Optional[str] = None):
        """
        创建日志条目
        
        Args:
            level: 日志级别
            module: 模块名称
            message: 日志消息
            user_id: 用户ID
            ip_address: IP地址
            user_agent: 用户代理
            extra_data: 额外数据（JSON字符串）
        """
        try:
            log_entry = LogEntry(
                timestamp=datetime.utcnow(),
                level=level,
                module=module,
                message=message,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                extra_data=extra_data
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Failed to create log entry: {e}")
            self.db.rollback()

# 便捷函数
def get_user_activity_logger(db: Session) -> UserActivityLogger:
    """获取用户活动日志记录器实例"""
    return UserActivityLogger(db)