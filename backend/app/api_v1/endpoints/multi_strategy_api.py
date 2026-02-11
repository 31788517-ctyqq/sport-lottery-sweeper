#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多策略筛选与钉钉通知API端点
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from backend.services.multi_strategy_service import multi_strategy_scheduler
from backend.database import get_db
from backend.models import MultiStrategyTask
from backend.crud.multi_strategy_crud import (
    get_multi_strategy_tasks,
    create_multi_strategy_task,
    delete_multi_strategy_tasks
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/multi-strategy", tags=["multi-strategy"])

# 请求模型
class MultiStrategyConfigRequest(BaseModel):
    task_name: str
    strategy_ids: List[str]
    cron_expression: str
    message_format: str = "text"  # 'text' or 'table'
    user_id: str
    dingtalk_webhook: Optional[str] = None
    enabled: bool = True


class ExecuteMultipleStrategiesRequest(BaseModel):
    strategy_ids: List[str]
    message_format: str = "text"


# 响应模型
class MultiStrategyConfigResponse(BaseModel):
    id: int
    task_name: str
    strategy_ids: List[str]
    cron_expression: str
    message_format: str
    user_id: str
    dingtalk_webhook: Optional[str]
    enabled: bool
    created_at: datetime
    updated_at: datetime


class ExecuteMultipleStrategiesResponse(BaseModel):
    success: bool
    message: str
    results: Dict[str, Any]


@router.post("/config", summary="保存多策略配置")
async def save_multi_strategy_config(config: MultiStrategyConfigRequest, db: Session = Depends(get_db)):
    """
    保存多策略配置
    """
    try:
        # 创建数据库记录
        task_record = create_multi_strategy_task(
            db=db,
            task_name=config.task_name,
            user_id=config.user_id,
            strategy_ids=config.strategy_ids,
            cron_expression=config.cron_expression,
            message_format=config.message_format,
            dingtalk_webhook=config.dingtalk_webhook,
            enabled=config.enabled
        )
        
        # 准备任务配置给调度器
        task_config = {
            "task_name": config.task_name,
            "strategy_ids": config.strategy_ids,
            "cron_expression": config.cron_expression,
            "message_format": config.message_format,
            "user_id": config.user_id,
            "dingtalk_webhook": config.dingtalk_webhook,
            "enabled": config.enabled
        }
        
        # 添加到调度器
        if config.enabled:
            multi_strategy_scheduler.add_scheduled_task(task_config)
        
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
                "updated_at": task_record.updated_at
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存多策略配置失败: {str(e)}")


@router.get("/config", summary="获取用户的所有多策略配置")
async def get_multi_strategy_config(user_id: str, db: Session = Depends(get_db)):
    """
    获取用户的所有多策略配置
    """
    try:
        # 从数据库获取用户的所有配置
        records = get_multi_strategy_tasks(db, user_id)
        
        configs = []
        for record in records:
            configs.append({
                "id": record.id,
                "task_name": record.task_name,
                "strategy_ids": json.loads(record.strategy_ids),  # 解析JSON数据
                "cron_expression": record.cron_expression,
                "message_format": record.message_format,
                "user_id": record.user_id,
                "dingtalk_webhook": record.dingtalk_webhook,
                "enabled": record.enabled,
                "created_at": record.created_at,
                "updated_at": record.updated_at
            })
        
        return {
            "success": True,
            "data": configs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取多策略配置失败: {str(e)}")


@router.delete("/config/{user_id}", summary="删除多策略配置")
async def delete_multi_strategy_config(user_id: str, db: Session = Depends(get_db)):
    """
    删除多策略配置
    """
    try:
        # 从数据库删除用户的所有配置
        deleted_count = delete_multi_strategy_tasks(db, user_id)
        
        # 从调度器中移除任务
        multi_strategy_scheduler.remove_scheduled_task(user_id)
        
        return {
            "success": True,
            "message": f"多策略配置删除成功，共删除 {deleted_count} 条记录"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除多策略配置失败: {str(e)}")


@router.post("/execute", summary="手动执行多策略筛选")
async def execute_multiple_strategies_manual(request: ExecuteMultipleStrategiesRequest):
    """
    手动执行多策略筛选
    """
    try:
        results = multi_strategy_scheduler.execute_multiple_strategies_now(
            request.strategy_ids, 
            request.message_format
        )
        
        return {
            "success": True,
            "message": "多策略筛选执行成功",
            "results": results['results'],
            "formatted_message": results['formatted_message']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行多策略筛选失败: {str(e)}")


@router.get("/strategies", summary="获取所有可用策略")
async def get_available_strategies():
    """
    获取所有可用的策略列表
    """
    try:
        strategies = multi_strategy_scheduler.strategy_manager.get_all_strategies()
        
        return {
            "success": True,
            "data": strategies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取策略列表失败: {str(e)}")


@router.get("/", summary="获取多策略功能信息")
async def get_multi_strategy_info():
    """
    获取多策略功能的基本信息
    """
    return {
        "success": True,
        "message": "多策略筛选与钉钉通知功能已启用",
        "features": [
            "自动执行策略筛选",
            "钉钉消息通知",
            "多种策略筛选",
            "表格形式结果展示"
        ]
    }