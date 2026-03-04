#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config import settings
from backend.core.database import get_db
from backend.core.security import oauth2_scheme
from backend.crud.multi_strategy_crud import (
    create_multi_strategy_task,
    get_multi_strategy_task,
    get_multi_strategy_tasks,
)
from backend.dependencies import get_current_user as get_current_user_dependency
from backend.services.multi_strategy_service import multi_strategy_scheduler


router = APIRouter(prefix="/multi-strategy", tags=["multi-strategy"])


def get_current_user_dict(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> dict:
    """Return current user in dict form, with dev fallback."""
    try:
        user = get_current_user_dependency(db=db, token=token)
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": getattr(user, "is_admin", False) or getattr(user, "is_superuser", False),
            "role": getattr(user, "role", "user"),
        }
    except Exception:
        if getattr(settings, "ENVIRONMENT", "development") == "development":
            return {
                "id": "1",
                "username": "admin",
                "email": "",
                "is_admin": True,
                "role": "admin",
            }
        raise


def _safe_parse_strategy_ids(raw_value: Any) -> List[str]:
    """Parse strategy_ids from JSON/list/comma-string safely."""
    if raw_value is None:
        return []
    if isinstance(raw_value, list):
        return [str(v) for v in raw_value]
    if isinstance(raw_value, str):
        value = raw_value.strip()
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(v) for v in parsed]
            if isinstance(parsed, str):
                return [parsed]
            return []
        except Exception:
            return [v.strip() for v in value.split(",") if v.strip()]
    return []


class MultiStrategyConfigRequest(BaseModel):
    task_name: str
    strategy_ids: List[str]
    cron_expression: str
    message_format: str = "text"
    user_id: str
    dingtalk_webhook: Optional[str] = None
    enabled: bool = True


class ExecuteMultipleStrategiesRequest(BaseModel):
    strategy_ids: List[str]
    message_format: str = "text"


class ToggleTaskRequest(BaseModel):
    enabled: bool


@router.post("/config", summary="保存多策略配置")
async def save_multi_strategy_config(
    config: MultiStrategyConfigRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_dict),
):
    if current_user["username"] != config.user_id and not current_user.get("is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作该用户配置")

    try:
        task_record = create_multi_strategy_task(
            db=db,
            task_name=config.task_name,
            user_id=config.user_id,
            strategy_ids=config.strategy_ids,
            cron_expression=config.cron_expression,
            message_format=config.message_format,
            dingtalk_webhook=config.dingtalk_webhook,
            enabled=config.enabled,
        )

        if config.enabled:
            multi_strategy_scheduler.add_scheduled_task(
                {
                    "task_name": config.task_name,
                    "strategy_ids": config.strategy_ids,
                    "cron_expression": config.cron_expression,
                    "message_format": config.message_format,
                    "user_id": config.user_id,
                    "dingtalk_webhook": config.dingtalk_webhook,
                    "enabled": config.enabled,
                }
            )

        return {
            "success": True,
            "message": "多策略配置保存成功",
            "data": {
                "id": task_record.id,
                "task_name": task_record.task_name,
                "strategy_ids": config.strategy_ids,
                "cron_expression": task_record.cron_expression,
                "message_format": task_record.message_format,
                "user_id": task_record.user_id,
                "dingtalk_webhook": task_record.dingtalk_webhook,
                "enabled": task_record.enabled,
                "created_at": task_record.created_at,
                "updated_at": task_record.updated_at,
            },
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存多策略配置失败: {str(e)}")


@router.get("/config", summary="获取用户多策略配置")
async def get_multi_strategy_config(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_dict),
):
    if current_user["username"] != user_id and not current_user.get("is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看该用户配置")

    try:
        records = get_multi_strategy_tasks(db, user_id)
        configs = []
        for record in records:
            configs.append(
                {
                    "id": record.id,
                    "task_name": record.task_name,
                    "strategy_ids": _safe_parse_strategy_ids(record.strategy_ids),
                    "cron_expression": record.cron_expression,
                    "message_format": record.message_format,
                    "user_id": record.user_id,
                    "dingtalk_webhook": record.dingtalk_webhook,
                    "enabled": record.enabled,
                    "created_at": record.created_at,
                    "updated_at": record.updated_at,
                }
            )

        return {"success": True, "data": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取多策略配置失败: {str(e)}")


@router.delete("/config/{task_id}", summary="删除单个多策略任务")
async def delete_multi_strategy_config(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_dict),
):
    try:
        task = get_multi_strategy_task(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")

        if current_user["username"] != task.user_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除该任务")

        db.delete(task)
        db.commit()
        return {"success": True, "message": "任务删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


@router.post("/execute", summary="手动执行多策略筛选")
async def execute_multiple_strategies_manual(
    request: ExecuteMultipleStrategiesRequest,
    current_user: dict = Depends(get_current_user_dict),
):
    try:
        execution_result = multi_strategy_scheduler.execute_multiple_strategies_now(
            request.strategy_ids, request.message_format
        )
        if not execution_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"执行失败: {execution_result.get('error', '未知错误')}",
            )

        return {
            "success": True,
            "message": "多策略执行成功",
            "results": execution_result.get("results", {}),
            "formatted_message": execution_result.get("formatted_message", ""),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行多策略失败: {str(e)}")


@router.post("/toggle-task/{user_id}", summary="启停用户任务")
async def toggle_scheduled_task(
    user_id: str,
    request: ToggleTaskRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_dict),
):
    if current_user["username"] != user_id and not current_user.get("is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作该用户任务")

    try:
        if request.enabled:
            tasks = get_multi_strategy_tasks(db, user_id)
            for task in tasks:
                if task.enabled:
                    multi_strategy_scheduler.add_scheduled_task(
                        {
                            "user_id": task.user_id,
                            "strategy_ids": _safe_parse_strategy_ids(task.strategy_ids),
                            "cron_expression": task.cron_expression,
                            "dingtalk_webhook": task.dingtalk_webhook,
                            "message_format": task.message_format or "text",
                        }
                    )
            message = "定时任务已启动"
        else:
            multi_strategy_scheduler.remove_task(user_id)
            message = "定时任务已停止"

        return {"success": True, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换任务状态失败: {str(e)}")


@router.get("/strategies", summary="获取可用策略列表")
async def get_available_strategies():
    try:
        strategies = multi_strategy_scheduler.strategy_manager.get_all_strategies()
        return {"success": True, "data": strategies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取策略列表失败: {str(e)}")


@router.get("/", summary="获取多策略功能信息")
async def get_multi_strategy_info():
    return {
        "success": True,
        "message": "多策略筛选与通知功能已启用",
        "features": [
            "自动执行策略筛选",
            "钉钉消息通知",
            "多策略组合筛选",
            "表格形式结果展示",
        ],
    }
