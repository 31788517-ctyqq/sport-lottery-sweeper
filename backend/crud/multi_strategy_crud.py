#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多策略任务的CRUD操作
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from backend.models import MultiStrategyTask


def get_multi_strategy_tasks(db: Session, user_id: str) -> List[MultiStrategyTask]:
    """获取用户的多策略任务"""
    return db.query(MultiStrategyTask).filter(MultiStrategyTask.user_id == user_id).all()


def get_multi_strategy_task(db: Session, task_id: int) -> Optional[MultiStrategyTask]:
    """获取特定的多策略任务"""
    return db.query(MultiStrategyTask).filter(MultiStrategyTask.id == task_id).first()


def create_multi_strategy_task(
    db: Session, 
    task_name: str, 
    user_id: str, 
    strategy_ids: List[str], 
    cron_expression: str,
    message_format: str = "text",
    dingtalk_webhook: Optional[str] = None,
    enabled: bool = True
) -> MultiStrategyTask:
    """创建多策略任务"""
    task = MultiStrategyTask(
        task_name=task_name,
        user_id=user_id,
        strategy_ids=json.dumps(strategy_ids),
        cron_expression=cron_expression,
        message_format=message_format,
        dingtalk_webhook=dingtalk_webhook,
        enabled=enabled
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_multi_strategy_task(
    db: Session,
    task_id: int,
    task_name: Optional[str] = None,
    strategy_ids: Optional[List[str]] = None,
    cron_expression: Optional[str] = None,
    message_format: Optional[str] = None,
    dingtalk_webhook: Optional[str] = None,
    enabled: Optional[bool] = None
) -> bool:
    """更新多策略任务"""
    task = db.query(MultiStrategyTask).filter(MultiStrategyTask.id == task_id).first()
    if not task:
        return False
    
    update_data = {}
    if task_name is not None:
        update_data["task_name"] = task_name
    if strategy_ids is not None:
        update_data["strategy_ids"] = json.dumps(strategy_ids)
    if cron_expression is not None:
        update_data["cron_expression"] = cron_expression
    if message_format is not None:
        update_data["message_format"] = message_format
    if dingtalk_webhook is not None:
        update_data["dingtalk_webhook"] = dingtalk_webhook
    if enabled is not None:
        update_data["enabled"] = enabled
    
    for key, value in update_data.items():
        setattr(task, key, value)
    
    task.updated_at = datetime.utcnow()
    db.commit()
    return True


def delete_multi_strategy_tasks(db: Session, user_id: str) -> int:
    """删除用户的多策略任务"""
    tasks = db.query(MultiStrategyTask).filter(MultiStrategyTask.user_id == user_id).all()
    count = len(tasks)
    
    for task in tasks:
        db.delete(task)
    
    db.commit()
    return count