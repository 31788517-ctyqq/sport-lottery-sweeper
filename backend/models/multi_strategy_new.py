#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多策略配置数据库模型
"""

import logging

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()
logger = logging.getLogger(__name__)


class MultiStrategyTask(Base):
    __tablename__ = "multi_strategy_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), nullable=False)
    user_id = Column(String(50), nullable=False)
    strategy_ids = Column(Text, nullable=False)  # JSON格式存储策略ID列表
    cron_expression = Column(String(100), nullable=False)
    message_format = Column(String(20), default='text')  # 'text' 或 'table'
    dingtalk_webhook_encrypted = Column(Text)  # 加密存储的钉钉Webhook URL
    dingtalk_webhook_masked = Column(String(200))  # 掩码显示的Webhook URL（用于日志）
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<MultiStrategyTask(id={self.id}, task_name='{self.task_name}', user_id='{self.user_id}')"
    
    @property
    def dingtalk_webhook(self):
        """解密获取Webhook URL"""
        if not self.dingtalk_webhook_encrypted:
            return None
        
        try:
            from backend.services.webhook_security import decrypt_webhook_from_storage
            return decrypt_webhook_from_storage(self.dingtalk_webhook_encrypted)
        except Exception as e:
            logger.error(f"解密Webhook失败: {str(e)}")
            return None
    
    @dingtalk_webhook.setter
    def dingtalk_webhook(self, webhook_url):
        """设置Webhook URL（自动加密）"""
        if not webhook_url:
            self.dingtalk_webhook_encrypted = None
            self.dingtalk_webhook_masked = None
            return
        
        try:
            from backend.services.webhook_security import validate_and_process_webhook
            is_valid, encrypted, error_msg = validate_and_process_webhook(webhook_url)
            
            if is_valid:
                self.dingtalk_webhook_encrypted = encrypted
                # 生成掩码用于显示
                from backend.services.webhook_security import webhook_security
                self.dingtalk_webhook_masked = webhook_security.mask_webhook_url(webhook_url)
            else:
                raise ValueError(error_msg)
        except Exception as e:
            logger.error(f"设置Webhook失败: {str(e)}")
            raise