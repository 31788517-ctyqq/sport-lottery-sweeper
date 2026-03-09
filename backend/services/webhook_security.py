#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉Webhook安全管理模块
提供Webhook URL的加密存储、验证和管理功能
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class WebhookSecurity:
    """Webhook安全管理类"""
    
    def __init__(self, secret_key: str = None):
        """
        初始化Webhook安全管理器
        
        Args:
            secret_key: 密钥字符串，如果为None则从环境变量获取
        """
        if secret_key is None:
            secret_key = os.getenv('WEBHOOK_SECRET_KEY', 'default-webhook-secret-key-change-in-production')
        
        # 使用PBKDF2从密钥派生加密密钥
        salt = b'sport_lottery_sweeper_salt'  # 在生产环境中应该使用随机salt并存储
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        self.fernet = Fernet(key)
    
    def encrypt_webhook(self, webhook_url: str) -> str:
        """
        加密Webhook URL
        
        Args:
            webhook_url: 原始Webhook URL
            
        Returns:
            加密后的字符串
        """
        if not webhook_url:
            return None
        
        try:
            encrypted = self.fernet.encrypt(webhook_url.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"加密Webhook URL失败: {str(e)}")
            return None
    
    def decrypt_webhook(self, encrypted_webhook: str) -> str:
        """
        解密Webhook URL
        
        Args:
            encrypted_webhook: 加密的Webhook URL
            
        Returns:
            解密后的原始URL
        """
        if not encrypted_webhook:
            return None
        
        try:
            decoded = base64.urlsafe_b64decode(encrypted_webhook.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"解密Webhook URL失败: {str(e)}")
            return None
    
    def validate_webhook_url(self, webhook_url: str) -> bool:
        """
        验证Webhook URL格式和安全性
        
        Args:
            webhook_url: 待验证的Webhook URL
            
        Returns:
            是否有效
        """
        if not webhook_url:
            return False
        
        # 基本格式检查
        if not webhook_url.startswith(('http://', 'https://')):
            return False
        
        # 钉钉域名检查
        if 'dingtalk.com' not in webhook_url:
            logger.warning(f"Webhook URL不是钉钉域名: {webhook_url}")
            return False
        
        # 长度检查
        if len(webhook_url) > 500:
            logger.warning("Webhook URL过长")
            return False
        
        # 安全检查：不允许内网地址
        if any(internal in webhook_url for internal in ['localhost', '127.0.0.1', '192.168.', '10.', '172.'])):
            logger.warning("Webhook URL包含内网地址")
            return False
        
        return True
    
    def mask_webhook_url(self, webhook_url: str) -> str:
        """
        掩码处理Webhook URL（用于日志记录）
        
        Args:
            webhook_url: 原始Webhook URL
            
        Returns:
            掩码后的URL
        """
        if not webhook_url:
            return ""
        
        try:
            # 保留协议和域名，掩码token部分
            if 'access_token=' in webhook_url:
                parts = webhook_url.split('access_token=')
                base_url = parts[0]
                token = parts[1]
                
                # 掩码token（保留前8位和后4位）
                if len(token) > 12:
                    masked_token = token[:8] + '*' * (len(token) - 12) + token[-4:]
                else:
                    masked_token = '*' * len(token)
                
                return f"{base_url}access_token={masked_token}"
            else:
                # 如果没有access_token参数，直接返回域名部分
                from urllib.parse import urlparse
                parsed = urlparse(webhook_url)
                return f"{parsed.scheme}://{parsed.netloc}/***"
        except Exception:
            return "***masked***"


# 全局实例
webhook_security = WebhookSecurity()


def encrypt_webhook_for_storage(webhook_url: str) -> str:
    """
    为存储加密Webhook URL的便捷函数
    
    Args:
        webhook_url: 原始Webhook URL
        
    Returns:
        加密后的字符串
    """
    return webhook_security.encrypt_webhook(webhook_url)


def decrypt_webhook_from_storage(encrypted_webhook: str) -> str:
    """
    从存储解密Webhook URL的便捷函数
    
    Args:
        encrypted_webhook: 加密的Webhook URL
        
    Returns:
        解密后的原始URL
    """
    return webhook_security.decrypt_webhook(encrypted_webhook)


def validate_and_process_webhook(webhook_url: str) -> tuple[bool, str, str]:
    """
    验证并处理Webhook URL的综合函数
    
    Args:
        webhook_url: 待处理的Webhook URL
        
    Returns:
        (是否有效, 处理后的URL, 错误信息)
    """
    if not webhook_url:
        return False, None, "Webhook URL不能为空"
    
    # 验证格式
    if not webhook_security.validate_webhook_url(webhook_url):
        return False, None, "Webhook URL格式无效或存在安全风险"
    
    # 加密存储
    encrypted = encrypt_webhook_for_storage(webhook_url)
    if not encrypted:
        return False, None, "Webhook URL加密失败"
    
    logger.info(f"Webhook URL验证通过并已加密: {webhook_security.mask_webhook_url(webhook_url)}")
    return True, encrypted, None