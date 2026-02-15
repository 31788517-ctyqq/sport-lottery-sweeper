#!/usr/bin/env python3
"""
邮件服务工具模块
提供发送各类邮件的功能（当前为模拟实现）
"""

import logging
from typing import Optional
from backend.config import settings

# 配置日志
logger = logging.getLogger(__name__)

class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.enabled = True  # 邮件服务开关
        
    def send_welcome_email(self, email: str, username: str) -> bool:
        """
        发送欢迎邮件
        
        Args:
            email: 用户邮箱
            username: 用户名
            
        Returns:
            发送成功标志
        """
        try:
            if not self.enabled:
                logger.info(f"邮件服务未启用，跳过发送欢迎邮件: {email}")
                return True
                
            # 模拟邮件发送逻辑
            logger.info(f"[模拟] 发送欢迎邮件到: {email}, 用户: {username}")
            logger.info(f"邮件内容: 欢迎 {username} 加入我们的平台！")
            
            # 在实际项目中，这里应该调用真实的邮件服务
            # 例如：smtplib, sendgrid, aws ses等
            
            return True
            
        except Exception as e:
            logger.error(f"发送欢迎邮件失败: {email}, 错误: {str(e)}")
            return False
    
    def send_password_reset_email(self, email: str, username: str, reset_token: str) -> bool:
        """
        发送密码重置邮件
        
        Args:
            email: 用户邮箱
            username: 用户名
            reset_token: 重置令牌
            
        Returns:
            发送成功标志
        """
        try:
            if not self.enabled:
                logger.info(f"邮件服务未启用，跳过发送密码重置邮件: {email}")
                return True
                
            # 构建重置链接（从配置中获取前端地址）
            reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password?token={reset_token}"
            
            # 模拟邮件发送逻辑
            logger.info(f"[模拟] 发送密码重置邮件到: {email}, 用户: {username}")
            logger.info(f"重置链接: {reset_url}")
            logger.info(f"重置令牌: {reset_token}")
            
            # 在实际项目中，这里应该：
            # 1. 使用模板引擎生成HTML邮件
            # 2. 调用邮件服务商API发送邮件
            # 3. 处理发送结果和异常
            
            return True
            
        except Exception as e:
            logger.error(f"发送密码重置邮件失败: {email}, 错误: {str(e)}")
            return False
    
    def send_email_verification_email(self, email: str, username: str, verification_token: str) -> bool:
        """
        发送邮箱验证邮件
        
        Args:
            email: 用户邮箱
            username: 用户名
            verification_token: 验证令牌
            
        Returns:
            发送成功标志
        """
        try:
            if not self.enabled:
                logger.info(f"邮件服务未启用，跳过发送验证邮件: {email}")
                return True
                
            # 构建验证链接（从配置中获取前端地址）
            verify_url = f"{settings.FRONTEND_BASE_URL}/verify-email?token={verification_token}"
            
            # 模拟邮件发送逻辑
            logger.info(f"[模拟] 发送邮箱验证邮件到: {email}, 用户: {username}")
            logger.info(f"验证链接: {verify_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"发送邮箱验证邮件失败: {email}, 错误: {str(e)}")
            return False

# 创建全局邮件服务实例
email_service = EmailService()

# 导出服务类
__all__ = ["EmailService", "email_service"]