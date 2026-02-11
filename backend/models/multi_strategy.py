#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多策略配置数据库模型
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class MultiStrategyTask(Base):
    __tablename__ = "multi_strategy_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), nullable=False)
    user_id = Column(String(50), nullable=False)
    strategy_ids = Column(Text, nullable=False)  # JSON格式存储策略ID列表
    cron_expression = Column(String(100), nullable=False)
    message_format = Column(String(20), default='text')  # 'text' 或 'table'
    dingtalk_webhook = Column(Text)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<MultiStrategyTask(id={self.id}, task_name='{self.task_name}', user_id='{self.user_id}')>"