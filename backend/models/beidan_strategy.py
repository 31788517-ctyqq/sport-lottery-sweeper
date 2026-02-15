#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北单筛选器策略配置数据库模型
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class BeidanStrategy(Base):
    """北单筛选策略表"""
    __tablename__ = "beidan_strategies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="策略名称")
    description = Column(Text, comment="策略描述")
    
    # 三维条件配置（JSON格式存储）
    three_dimensional = Column(JSON, nullable=False, comment="三维条件配置")
    
    # 其他条件配置（JSON格式存储）
    other_conditions = Column(JSON, nullable=False, comment="其他条件配置")
    
    # 排序配置（JSON格式存储）
    sort_config = Column(JSON, nullable=False, comment="排序配置")
    
    # 用户关联（暂时使用固定用户ID，后续接入用户系统）
    user_id = Column(String(50), default="default_user", comment="用户ID")
    
    # 是否公开策略
    is_public = Column(Boolean, default=False, comment="是否公开策略")
    
    # 策略状态
    is_active = Column(Boolean, default=True, comment="策略是否激活")
    
    # 使用统计
    usage_count = Column(Integer, default=0, comment="使用次数")
    success_rate = Column(String(10), default="0%", comment="成功率")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def __repr__(self):
        return f"<BeidanStrategy(id={self.id}, name='{self.name}', user_id='{self.user_id}')"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        # 处理字符串类型的日期时间字段
        def format_datetime(dt):
            if dt is None:
                return None
            if isinstance(dt, str):
                return dt
            if hasattr(dt, 'isoformat'):
                return dt.isoformat()
            return str(dt)
            
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "threeDimensional": self.three_dimensional,
            "otherConditions": self.other_conditions,
            "sort": self.sort_config,
            "createdAt": format_datetime(self.created_at),
            "updatedAt": format_datetime(self.updated_at)
        }


class BeidanStrategyExecutionLog(Base):
    """北单策略执行日志表"""
    __tablename__ = "beidan_strategy_execution_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    strategy_id = Column(Integer, nullable=False, comment="策略ID")
    user_id = Column(String(50), default="default_user", comment="用户ID")
    
    # 执行参数
    execution_params = Column(JSON, comment="执行时的筛选参数")
    
    # 执行结果
    result_stats = Column(JSON, comment="执行结果统计")
    
    # 执行状态
    status = Column(String(20), default="success", comment="执行状态: success/failed")
    
    # 错误信息
    error_message = Column(Text, comment="错误信息")
    
    # 执行时间
    executed_at = Column(DateTime, default=datetime.utcnow, comment="执行时间")
    
    # 耗时（毫秒）
    duration_ms = Column(Integer, comment="执行耗时（毫秒）")

    def __repr__(self):
        return f"<BeidanStrategyExecutionLog(id={self.id}, strategy_id={self.strategy_id}, status='{self.status}')"