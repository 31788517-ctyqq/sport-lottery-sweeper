#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRUD operations for multi-strategy task configuration."""

import json
import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from backend.models.multi_strategy_new import MultiStrategyTask

logger = logging.getLogger(__name__)


def ensure_multi_strategy_table(db: Session) -> None:
    """Create multi_strategy_tasks table on demand when DB wasn't migrated."""
    bind = db.get_bind()
    if bind is None:
        return
    if not inspect(bind).has_table(MultiStrategyTask.__tablename__):
        MultiStrategyTask.__table__.create(bind=bind, checkfirst=True)


def get_multi_strategy_tasks(db: Session, user_id: str) -> List[MultiStrategyTask]:
    """Get all multi-strategy tasks for a user."""
    ensure_multi_strategy_table(db)
    return db.query(MultiStrategyTask).filter(MultiStrategyTask.user_id == user_id).all()


def get_multi_strategy_task(db: Session, task_id: int) -> Optional[MultiStrategyTask]:
    """Get one multi-strategy task by id."""
    ensure_multi_strategy_table(db)
    return db.query(MultiStrategyTask).filter(MultiStrategyTask.id == task_id).first()


def create_multi_strategy_task(
    db: Session,
    task_name: str,
    user_id: str,
    strategy_ids: List[str],
    cron_expression: str,
    message_format: str = "text",
    dingtalk_webhook: Optional[str] = None,
    enabled: bool = True,
) -> MultiStrategyTask:
    """Create a multi-strategy task."""
    ensure_multi_strategy_table(db)
    task = MultiStrategyTask(
        task_name=task_name,
        user_id=user_id,
        strategy_ids=json.dumps(strategy_ids),
        cron_expression=cron_expression,
        message_format=message_format,
        enabled=enabled,
    )

    if dingtalk_webhook:
        task.dingtalk_webhook = dingtalk_webhook

    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info("Created multi-strategy task %s (user_id=%s)", task_name, user_id)
    return task


def update_multi_strategy_task(
    db: Session,
    task_id: int,
    task_name: Optional[str] = None,
    strategy_ids: Optional[List[str]] = None,
    cron_expression: Optional[str] = None,
    message_format: Optional[str] = None,
    dingtalk_webhook: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> bool:
    """Update a multi-strategy task."""
    ensure_multi_strategy_table(db)
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
    if enabled is not None:
        update_data["enabled"] = enabled

    if dingtalk_webhook is not None:
        task.dingtalk_webhook = dingtalk_webhook

    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    db.commit()
    logger.info("Updated multi-strategy task id=%s", task_id)
    return True


def delete_multi_strategy_tasks(db: Session, user_id: str) -> int:
    """Delete all multi-strategy tasks for a user."""
    ensure_multi_strategy_table(db)
    tasks = db.query(MultiStrategyTask).filter(MultiStrategyTask.user_id == user_id).all()
    count = len(tasks)

    for task in tasks:
        db.delete(task)

    db.commit()
    return count
