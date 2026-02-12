#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多策略筛选与钉钉通知API端点
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from backend.services.multi_strategy_service import multi_strategy_scheduler
from backend.database import get_db
from backend.models.multi_strategy_new import MultiStrategyTask
from backend.crud.multi_strategy_crud import (
    get_multi_strategy_tasks,
    create_multi_strategy_task,
    delete_multi_strategy_tasks
)
from backend.core.auth_service import oauth2_scheme, verify_token, get_current_user
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


class ToggleTaskRequest(BaseModel):
    enabled: bool


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
async def save_multi_strategy_config(
    config: MultiStrategyConfigRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    保存多策略配置
    """
    # 验证用户权限：只能操作自己的配置
    if current_user["username"] != config.user_id and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作用户的配置"
        )
    
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
async def get_multi_strategy_config(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 验证用户权限：只能查看自己的配置
    if current_user["username"] != user_id and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看其他用户的配置"
        )
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
async def delete_multi_strategy_config(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 验证用户权限：只能删除自己的配置
    if current_user["username"] != user_id and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除其他用户的配置"
        )
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
async def execute_multiple_strategies_manual(
    request: ExecuteMultipleStrategiesRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    手动执行多策略筛选
    """
    try:
        # 使用调度器的执行方法
        execution_result = multi_strategy_scheduler.execute_multiple_strategies_now(
            request.strategy_ids, 
            request.message_format
        )
        
        if execution_result['success']:
            return {
                "success": True,
                "message": "多策略筛选执行成功",
                "results": execution_result['results'],
                "formatted_message": execution_result['formatted_message']
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"执行失败: {execution_result.get('error', '未知错误')}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行多策略筛选失败: {str(e)}")


@router.post("/toggle-task/{user_id}", summary="启动/停止定时任务")
async def toggle_scheduled_task(
    user_id: str,
    request: ToggleTaskRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    启动或停止多策略的定时任务
    """
    # 验证用户权限
    if current_user["username"] != user_id and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作其他用户的任务"
        )
    
    try:
        if request.enabled:
            # 重新加载用户任务
            tasks = get_multi_strategy_tasks(db, user_id)
            for task in tasks:
                if task.enabled:
                    strategy_ids = json.loads(task.strategy_ids)
                    task_config = {
                        'user_id': task.user_id,
                        'strategy_ids': strategy_ids,
                        'cron_expression': task.cron_expression,
                        'dingtalk_webhook': task.dingtalk_webhook,
                        'message_format': task.message_format or 'text'
                    }
                    multi_strategy_scheduler.add_scheduled_task(task_config)
            message = "定时任务已启动"
        else:
            # 停止用户的定时任务
            multi_strategy_scheduler.remove_task(user_id)
            message = "定时任务已停止"
            
        return {
            "success": True,
            "message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换定时任务失败: {str(e)}")


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