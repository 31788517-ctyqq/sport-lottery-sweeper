"""
智能体管理API路由
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import asyncio
import logging

from ...dependencies import get_db, get_current_user
from ...api.schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse, AgentListResponse,
    AgentControlRequest, AgentTaskRequest, AgentTaskResponse,
    AgentMetricsResponse, AgentExecutionLogResponse, AgentAlertResponse,
    AgentBulkControlRequest, AgentBulkControlResponse,
    AgentBulkUpdateRequest, AgentBulkUpdateResponse,
    AgentBulkDeleteRequest, AgentBulkDeleteResponse,
    AgentBulkExportRequest, AgentBulkExportResponse,
    AgentBulkImportRequest, AgentBulkImportResponse,
    LangChainRunRequest, LangChainRunResponse, LangChainStatsResponse,
    AgentTypes, AgentStatuses, AgentActions,
    AgentTemplateListResponse, AgentTemplateResponse, AgentTemplateCreate, 
    AgentTemplateUpdate, AgentTemplateBase, AgentTemplateBulkCreateRequest,
    AgentTemplateBulkCreateResponse, AgentTemplateImportRequest, AgentTemplateImportResponse
)
from ...models.agent_models import (
    AgentModel, AgentExecutionLog, AgentAlert, AgentMetric,
    AgentChain, AgentTool, AgentWorkflow, AgentTemplate, LangChainRun
)
from ...services.agent_manager import get_agent_manager, ManagedAgent
from ...services.langchain_service import LangChainService
from ...services.llm_service import LLMService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["智能体管理"])


# 权限检查函数
async def check_agent_permission(user: dict, permission: str = "read"):
    """检查用户对智能体的权限"""
    user_role = user.get("role", "viewer")
    
    if permission == "read":
        return user_role in ["admin", "operator", "viewer"]
    elif permission == "write":
        return user_role in ["admin", "operator"]
    elif permission == "execute":
        return user_role in ["admin"]
    
    return False


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    agent_type: Optional[str] = Query(None, description="智能体类型过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    enabled: Optional[bool] = Query(None, description="是否启用过滤"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取智能体列表"""
    if not await check_agent_permission(current_user, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问智能体列表"
        )
    
    # 构建查询
    query = db.query(AgentModel).filter(AgentModel.deleted_at.is_(None))
    
    if agent_type:
        query = query.filter(AgentModel.agent_type == agent_type)
    
    if status:
        query = query.filter(AgentModel.status == status)
    
    if enabled is not None:
        query = query.filter(AgentModel.enabled == enabled)
    
    # 分页
    total = query.count()
    agents = query.offset((page - 1) * page_size).limit(page_size).all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return AgentListResponse(
        agents=agents,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建新智能体"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限创建智能体"
        )
    
    # 检查名称是否重复
    existing_agent = db.query(AgentModel).filter(
        AgentModel.name == agent_data.name,
        AgentModel.deleted_at.is_(None)
    ).first()
    
    if existing_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"智能体名称 '{agent_data.name}' 已存在"
        )
    
    # 创建智能体
    db_agent = AgentModel(**agent_data.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    logger.info(f"创建智能体成功: {db_agent.name} (ID: {db_agent.id})")
    
    return db_agent


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取智能体详情"""
    if not await check_agent_permission(current_user, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问智能体详情"
        )
    
    agent = db.query(AgentModel).filter(
        AgentModel.id == agent_id,
        AgentModel.deleted_at.is_(None)
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体 ID {agent_id} 不存在"
        )
    
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新智能体"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新智能体"
        )
    
    agent = db.query(AgentModel).filter(
        AgentModel.id == agent_id,
        AgentModel.deleted_at.is_(None)
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体 ID {agent_id} 不存在"
        )
    
    # 检查名称是否重复（如果更新了名称）
    if agent_data.name and agent_data.name != agent.name:
        existing_agent = db.query(AgentModel).filter(
            AgentModel.name == agent_data.name,
            AgentModel.deleted_at.is_(None),
            AgentModel.id != agent_id
        ).first()
        
        if existing_agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"智能体名称 '{agent_data.name}' 已存在"
            )
    
    # 更新字段
    update_data = agent_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    agent.updated_at = datetime.now()
    db.commit()
    db.refresh(agent)
    
    logger.info(f"更新智能体成功: {agent.name} (ID: {agent.id})")
    
    return agent


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除智能体"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除智能体"
        )
    
    agent = db.query(AgentModel).filter(
        AgentModel.id == agent_id,
        AgentModel.deleted_at.is_(None)
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体 ID {agent_id} 不存在"
        )
    
    # 软删除
    agent.deleted_at = datetime.now()
    db.commit()
    
    logger.info(f"删除智能体成功: {agent.name} (ID: {agent.id})")
    
    return {"message": f"智能体 {agent.name} 删除成功"}


@router.post("/{agent_id}/control")
async def control_agent(
    agent_id: int,
    control_data: AgentControlRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """控制智能体（启动/停止/重启等）"""
    if not await check_agent_permission(current_user, "execute"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限控制智能体"
        )
    
    agent = db.query(AgentModel).filter(
        AgentModel.id == agent_id,
        AgentModel.deleted_at.is_(None)
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体 ID {agent_id} 不存在"
        )
    
    # 获取智能体管理器
    agent_manager = get_agent_manager()
    
    try:
        if control_data.action == AgentActions.START:
            # 这里需要将数据库智能体转换为运行时智能体
            # 暂时返回成功，实际实现需要集成智能体管理器
            agent.status = AgentStatuses.RUNNING
            
        elif control_data.action == AgentActions.STOP:
            agent.status = AgentStatuses.STOPPED
            
        elif control_data.action == AgentActions.RESTART:
            agent.status = AgentStatuses.STOPPED
            # 短暂延迟后启动
            await asyncio.sleep(1)
            agent.status = AgentStatuses.RUNNING
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的操作: {control_data.action}"
            )
        
        db.commit()
        
        logger.info(f"智能体控制成功: {agent.name} {control_data.action}")
        
        return {
            "message": f"智能体 {agent.name} {control_data.action} 操作成功",
            "agent_id": agent_id,
            "status": agent.status
        }
        
    except Exception as e:
        logger.error(f"智能体控制失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"智能体控制失败: {str(e)}"
        )


@router.post("/{agent_id}/execute", response_model=AgentTaskResponse)
async def execute_agent_task(
    agent_id: int,
    task_data: AgentTaskRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """执行智能体任务"""
    if not await check_agent_permission(current_user, "execute"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限执行智能体任务"
        )
    
    agent = db.query(AgentModel).filter(
        AgentModel.id == agent_id,
        AgentModel.deleted_at.is_(None)
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体 ID {agent_id} 不存在"
        )
    
    if agent.status != AgentStatuses.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"智能体 {agent.name} 未运行，无法执行任务"
        )
    
    # 创建执行日志
    execution_log = AgentExecutionLog(
        agent_id=agent_id,
        task_type=task_data.task_type,
        task_data=task_data.task_data,
        input_data=task_data.task_data,
        started_at=datetime.now()
    )
    
    db.add(execution_log)
    db.commit()
    
    start_time = datetime.now()
    
    try:
        # 这里需要实际执行智能体任务
        # 暂时模拟一个简单的任务执行
        await asyncio.sleep(1)  # 模拟执行时间
        
        # 模拟任务结果
        result = {
            "success": True,
            "message": "任务执行完成",
            "data": {"processed": len(task_data.task_data)}
        }
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # 更新执行日志
        execution_log.success = True
        execution_log.execution_time = execution_time
        execution_log.output_data = result
        execution_log.completed_at = datetime.now()
        
        db.commit()
        
        logger.info(f"智能体任务执行成功: {agent.name} - {task_data.task_type}")
        
        return AgentTaskResponse(
            success=True,
            result=result,
            execution_time=execution_time,
            agent_id=agent_id,
            task_id=str(execution_log.id),
            started_at=start_time,
            completed_at=datetime.now()
        )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # 更新执行日志（错误）
        execution_log.success = False
        execution_log.execution_time = execution_time
        execution_log.error_message = str(e)
        execution_log.completed_at = datetime.now()
        
        db.commit()
        
        logger.error(f"智能体任务执行失败: {e}")
        
        return AgentTaskResponse(
            success=False,
            error_message=str(e),
            execution_time=execution_time,
            agent_id=agent_id,
            task_id=str(execution_log.id),
            started_at=start_time,
            completed_at=datetime.now()
        )


@router.get("/{agent_id}/metrics", response_model=AgentMetricsResponse)
async def get_agent_metrics(
    agent_id: int,
    time_window: int = Query(3600, description="时间窗口(秒)", ge=60, le=86640),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取智能体指标"""
    if not await check_agent_permission(current_user, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问智能体指标"
        )
    
    agent = db.query(AgentModel).filter(
        AgentModel.id == agent_id,
        AgentModel.deleted_at.is_(None)
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体 ID {agent_id} 不存在"
        )
    
    # 计算时间窗口
    now = datetime.now()
    window_start = now - timedelta(seconds=time_window)
    window_1h_start = now - timedelta(hours=1)
    window_24h_start = now - timedelta(hours=24)
    
    # 获取执行统计
    executions_total = db.query(AgentExecutionLog).filter(
        AgentExecutionLog.agent_id == agent_id
    ).count()
    
    errors_total = db.query(AgentExecutionLog).filter(
        AgentExecutionLog.agent_id == agent_id,
        AgentExecutionLog.success == False
    ).count()
    
    # 时间窗口内统计
    executions_window = db.query(AgentExecutionLog).filter(
        AgentExecutionLog.agent_id == agent_id,
        AgentExecutionLog.started_at >= window_start
    ).count()
    
    errors_window = db.query(AgentExecutionLog).filter(
        AgentExecutionLog.agent_id == agent_id,
        AgentExecutionLog.success == False,
        AgentExecutionLog.started_at >= window_start
    ).count()
    
    # 1小时统计
    executions_1h = db.query(AgentExecutionLog).filter(
        AgentExecutionLog.agent_id == agent_id,
        AgentExecutionLog.started_at >= window_1h_start
    ).count()
    
    errors_1h = db.query(AgentExecutionLog).filter(
        AgentExecutionLog.agent_id == agent_id,
        AgentExecutionLog.success == False,
        AgentExecutionLog.started_at >= window_1h_start
    ).count()
    
    # 24小时统计
    executions_24h = db.query(AgentExecutionLog).filter(
        AgentExecutionLog.agent_id == agent_id,
        AgentExecutionLog.started_at >= window_24h_start
    ).count()
    
    # 平均响应时间（使用时间窗口内的数据）
    avg_time_query = db.query(
        AgentExecutionLog.execution_time
    ).filter(
        AgentExecutionLog.agent_id == agent_id,
        AgentExecutionLog.success == True,
        AgentExecutionLog.started_at >= window_start,
        AgentExecutionLog.execution_time.isnot(None)
    ).all()
    
    if avg_time_query:
        avg_response_time = sum([log[0] for log in avg_time_query]) / len(avg_time_query)
    else:
        avg_response_time = 0.0
    
    # 1小时内平均响应时间
    avg_time_1h_query = db.query(
        AgentExecutionLog.execution_time
    ).filter(
        AgentExecutionLog.agent_id == agent_id,
        AgentExecutionLog.success == True,
        AgentExecutionLog.started_at >= window_1h_start,
        AgentExecutionLog.execution_time.isnot(None)
    ).all()
    
    if avg_time_1h_query:
        avg_response_time_1h = sum([log[0] for log in avg_time_1h_query]) / len(avg_time_1h_query)
    else:
        avg_response_time_1h = 0.0
    
    # 成功率计算
    success_rate_total = (1 - (errors_total / max(executions_total, 1))) * 100
    success_rate_1h = (1 - (errors_1h / max(executions_1h, 1))) * 100 if executions_1h > 0 else 100.0
    
    # 最后执行时间
    last_execution = db.query(AgentExecutionLog).filter(
        AgentExecutionLog.agent_id == agent_id
    ).order_by(AgentExecutionLog.started_at.desc()).first()
    
    last_execution_time = last_execution.started_at if last_execution else None
    
    return AgentMetricsResponse(
        agent_id=agent_id,
        executions=executions_total,
        errors=errors_total,
        avg_response_time=avg_response_time,
        success_rate=success_rate_total,
        last_execution=last_execution_time,
        active_tasks=0,  # 暂时返回0，需要运行时状态
        executions_1h=executions_1h,
        executions_24h=executions_24h,
        avg_response_time_1h=avg_response_time_1h,
        success_rate_1h=success_rate_1h
    )


@router.get("/{agent_id}/logs", response_model=List[AgentExecutionLogResponse])
async def get_agent_logs(
    agent_id: int,
    limit: int = Query(50, ge=1, le=1000, description="返回日志数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    success: Optional[bool] = Query(None, description="成功状态过滤"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取智能体执行日志"""
    if not await check_agent_permission(current_user, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问智能体日志"
        )
    
    agent = db.query(AgentModel).filter(
        AgentModel.id == agent_id,
        AgentModel.deleted_at.is_(None)
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体 ID {agent_id} 不存在"
        )
    
    # 构建查询
    query = db.query(AgentExecutionLog).filter(
        AgentExecutionLog.agent_id == agent_id
    )
    
    if success is not None:
        query = query.filter(AgentExecutionLog.success == success)
    
    # 按时间倒序排列
    logs = query.order_by(AgentExecutionLog.started_at.desc()).offset(offset).limit(limit).all()
    
    return logs


@router.post("/bulk-control", response_model=AgentBulkControlResponse)
async def bulk_control_agents(
    bulk_data: AgentBulkControlRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """批量控制智能体"""
    if not await check_agent_permission(current_user, "execute"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限批量控制智能体"
        )
    
    success_ids = []
    failed_items = []
    
    for agent_id in bulk_data.agent_ids:
        try:
            agent = db.query(AgentModel).filter(
                AgentModel.id == agent_id,
                AgentModel.deleted_at.is_(None)
            ).first()
            
            if not agent:
                failed_items.append({
                    "agent_id": agent_id,
                    "error": "智能体不存在"
                })
                continue
            
            # 更新状态（模拟控制操作）
            if bulk_data.action == AgentActions.START:
                agent.status = AgentStatuses.RUNNING
            elif bulk_data.action == AgentActions.STOP:
                agent.status = AgentStatuses.STOPPED
            elif bulk_data.action == AgentActions.RESTART:
                agent.status = AgentStatuses.STOPPED
                # 实际实现中需要更复杂的重启逻辑
                agent.status = AgentStatuses.RUNNING
            
            db.commit()
            success_ids.append(agent_id)
            
        except Exception as e:
            failed_items.append({
                "agent_id": agent_id,
                "error": str(e)
            })
    
    return AgentBulkControlResponse(
        success=success_ids,
        failed=failed_items,
        message=f"批量操作完成，成功: {len(success_ids)}, 失败: {len(failed_items)}"
    )


@router.post("/bulk-update", response_model=AgentBulkUpdateResponse)
async def bulk_update_agents(
    bulk_data: AgentBulkUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """批量更新智能体"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限批量更新智能体"
        )
    
    success_ids = []
    failed_items = []
    
    for agent_id in bulk_data.agent_ids:
        try:
            agent = db.query(AgentModel).filter(
                AgentModel.id == agent_id,
                AgentModel.deleted_at.is_(None)
            ).first()
            
            if not agent:
                failed_items.append({
                    "agent_id": agent_id,
                    "error": "智能体不存在"
                })
                continue
            
            # 应用更新
            update_data = bulk_data.update_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(agent, field, value)
            
            agent.updated_at = datetime.now()
            db.commit()
            success_ids.append(agent_id)
            
        except Exception as e:
            failed_items.append({
                "agent_id": agent_id,
                "error": str(e)
            })
    
    return AgentBulkUpdateResponse(
        success=success_ids,
        failed=failed_items,
        message=f"批量更新完成，成功: {len(success_ids)}, 失败: {len(failed_items)}"
    )


@router.post("/bulk-delete", response_model=AgentBulkDeleteResponse)
async def bulk_delete_agents(
    bulk_data: AgentBulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """批量删除智能体"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限批量删除智能体"
        )
    
    success_ids = []
    failed_items = []
    
    for agent_id in bulk_data.agent_ids:
        try:
            agent = db.query(AgentModel).filter(
                AgentModel.id == agent_id,
                AgentModel.deleted_at.is_(None)
            ).first()
            
            if not agent:
                failed_items.append({
                    "agent_id": agent_id,
                    "error": "智能体不存在"
                })
                continue
            
            # 软删除
            agent.deleted_at = datetime.now()
            db.commit()
            success_ids.append(agent_id)
            
        except Exception as e:
            failed_items.append({
                "agent_id": agent_id,
                "error": str(e)
            })
    
    return AgentBulkDeleteResponse(
        success=success_ids,
        failed=failed_items,
        message=f"批量删除完成，成功: {len(success_ids)}, 失败: {len(failed_items)}"
    )


@router.post("/bulk-export", response_model=AgentBulkExportResponse)
async def bulk_export_agents(
    export_request: AgentBulkExportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """批量导出智能体"""
    if not await check_agent_permission(current_user, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限批量导出智能体"
        )
    
    try:
        agents = []
        for agent_id in export_request.agent_ids:
            agent = db.query(AgentModel).filter(
                AgentModel.id == agent_id,
                AgentModel.deleted_at.is_(None)
            ).first()
            
            if agent:
                agent_data = {
                    "id": agent.id,
                    "name": agent.name,
                    "type": agent.agent_type,
                    "status": agent.status,
                    "config": agent.config if export_request.include_config else {},
                    "created_at": agent.created_at.isoformat() if agent.created_at else None,
                    "updated_at": agent.updated_at.isoformat() if agent.updated_at else None
                }
                
                if export_request.include_logs:
                    logs = db.query(AgentExecutionLog).filter(
                        AgentExecutionLog.agent_id == agent_id
                    ).limit(100).all()
                    
                    agent_data["logs"] = [
                        {
                            "id": log.id,
                            "task_type": log.task_type,
                            "success": log.success,
                            "execution_time": log.execution_time,
                            "started_at": log.started_at.isoformat() if log.started_at else None,
                            "completed_at": log.completed_at.isoformat() if log.completed_at else None
                        }
                        for log in logs
                    ]
                
                agents.append(agent_data)
        
        # 生成导出ID
        export_id = f"export_{int(datetime.now().timestamp())}_{len(agents)}"
        filename = f"agents_export_{export_id}.{export_request.export_format}"
        
        # 在实际应用中，这里会将数据保存到文件系统或云存储
        # 暂时返回模拟结果
        
        return AgentBulkExportResponse(
            export_id=export_id,
            filename=filename,
            size=len(str(agents)),
            download_url=f"/api/v1/agents/exports/{export_id}/download"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导出失败: {str(e)}"
        )


@router.post("/bulk-import", response_model=AgentBulkImportResponse)
async def bulk_import_agents(
    import_request: AgentBulkImportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """批量导入智能体"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限批量导入智能体"
        )
    
    imported_ids = []
    skipped_items = []
    failed_items = []
    
    try:
        # 解析导入数据
        import_data = import_request.import_data
        agents_data = import_data.get("agents", [])
        
        for agent_data in agents_data:
            try:
                # 检查是否已存在
                existing_agent = db.query(AgentModel).filter(
                    AgentModel.name == agent_data.get("name"),
                    AgentModel.deleted_at.is_(None)
                ).first()
                
                if existing_agent:
                    if import_request.conflict_resolution == "skip":
                        skipped_items.append({
                            "name": agent_data.get("name"),
                            "reason": "智能体已存在，跳过"
                        })
                        continue
                    elif import_request.conflict_resolution == "overwrite":
                        # 更新现有智能体
                        for field, value in agent_data.items():
                            if field not in ["id", "created_at", "updated_at"]:
                                setattr(existing_agent, field, value)
                        
                        existing_agent.updated_at = datetime.now()
                        db.commit()
                        imported_ids.append(existing_agent.id)
                        continue
                    elif import_request.conflict_resolution == "rename":
                        # 重命名导入
                        agent_data["name"] = f"{agent_data.get('name')}_imported_{int(datetime.now().timestamp())}"
                
                # 创建新智能体
                new_agent = AgentModel(**agent_data)
                db.add(new_agent)
                db.commit()
                db.refresh(new_agent)
                
                imported_ids.append(new_agent.id)
                
            except Exception as e:
                failed_items.append({
                    "name": agent_data.get("name", "unknown"),
                    "error": str(e)
                })
        
        if import_request.dry_run:
            return AgentBulkImportResponse(
                imported=[],
                skipped=skipped_items,
                failed=failed_items,
                message="试运行完成，未实际导入"
            )
        
        return AgentBulkImportResponse(
            imported=imported_ids,
            skipped=skipped_items,
            failed=failed_items,
            message=f"批量导入完成，成功: {len(imported_ids)}, 跳过: {len(skipped_items)}, 失败: {len(failed_items)}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导入失败: {str(e)}"
        )


# 智能体模板管理路由
@router.get("/templates", response_model=AgentTemplateListResponse)
async def list_agent_templates(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    template_type: Optional[str] = Query(None, description="模板类型过滤"),
    category: Optional[str] = Query(None, description="分类过滤"),
    published: Optional[bool] = Query(None, description="发布状态过滤"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取智能体模板列表"""
    if not await check_agent_permission(current_user, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问智能体模板列表"
        )
    
    # 构建查询
    query = db.query(AgentTemplate).filter(AgentTemplate.deleted_at.is_(None))
    
    if template_type:
        query = query.filter(AgentTemplate.template_type == template_type)
    
    if category:
        query = query.filter(AgentTemplate.category == category)
    
    if published is not None:
        query = query.filter(AgentTemplate.published == published)
    
    # 分页
    total = query.count()
    templates = query.offset((page - 1) * page_size).limit(page_size).all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return AgentTemplateListResponse(
        templates=templates,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/templates", response_model=AgentTemplateResponse)
async def create_agent_template(
    template_data: AgentTemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建智能体模板"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限创建智能体模板"
        )
    
    # 检查名称是否重复
    existing_template = db.query(AgentTemplate).filter(
        AgentTemplate.name == template_data.name,
        AgentTemplate.deleted_at.is_(None)
    ).first()
    
    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"模板名称 '{template_data.name}' 已存在"
        )
    
    # 创建模板
    db_template = AgentTemplate(**template_data.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    logger.info(f"创建智能体模板成功: {db_template.name} (ID: {db_template.id})")
    
    return db_template


@router.get("/templates/{template_id}", response_model=AgentTemplateResponse)
async def get_agent_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取智能体模板详情"""
    if not await check_agent_permission(current_user, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问智能体模板详情"
        )
    
    template = db.query(AgentTemplate).filter(
        AgentTemplate.id == template_id,
        AgentTemplate.deleted_at.is_(None)
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体模板 ID {template_id} 不存在"
        )
    
    return template


@router.put("/templates/{template_id}", response_model=AgentTemplateResponse)
async def update_agent_template(
    template_id: int,
    template_data: AgentTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新智能体模板"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新智能体模板"
        )
    
    template = db.query(AgentTemplate).filter(
        AgentTemplate.id == template_id,
        AgentTemplate.deleted_at.is_(None)
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体模板 ID {template_id} 不存在"
        )
    
    # 检查名称是否重复（如果更新了名称）
    if template_data.name and template_data.name != template.name:
        existing_template = db.query(AgentTemplate).filter(
            AgentTemplate.name == template_data.name,
            AgentTemplate.deleted_at.is_(None),
            AgentTemplate.id != template_id
        ).first()
        
        if existing_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"模板名称 '{template_data.name}' 已存在"
            )
    
    # 更新字段
    update_data = template_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    template.updated_at = datetime.now()
    db.commit()
    db.refresh(template)
    
    logger.info(f"更新智能体模板成功: {template.name} (ID: {template.id})")
    
    return template


@router.delete("/templates/{template_id}")
async def delete_agent_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除智能体模板"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除智能体模板"
        )
    
    template = db.query(AgentTemplate).filter(
        AgentTemplate.id == template_id,
        AgentTemplate.deleted_at.is_(None)
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体模板 ID {template_id} 不存在"
        )
    
    # 软删除
    template.deleted_at = datetime.now()
    db.commit()
    
    logger.info(f"删除智能体模板成功: {template.name} (ID: {template.id})")
    
    return {"message": f"智能体模板 {template.name} 删除成功"}


@router.post("/templates/{template_id}/publish")
async def publish_agent_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """发布智能体模板"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限发布智能体模板"
        )
    
    template = db.query(AgentTemplate).filter(
        AgentTemplate.id == template_id,
        AgentTemplate.deleted_at.is_(None)
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体模板 ID {template_id} 不存在"
        )
    
    template.published = True
    template.updated_at = datetime.now()
    db.commit()
    
    logger.info(f"发布智能体模板成功: {template.name} (ID: {template.id})")
    
    return {"message": f"智能体模板 {template.name} 已发布"}


@router.post("/templates/{template_id}/unpublish")
async def unpublish_agent_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """取消发布智能体模板"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限取消发布智能体模板"
        )
    
    template = db.query(AgentTemplate).filter(
        AgentTemplate.id == template_id,
        AgentTemplate.deleted_at.is_(None)
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"智能体模板 ID {template_id} 不存在"
        )
    
    template.published = False
    template.updated_at = datetime.now()
    db.commit()
    
    logger.info(f"取消发布智能体模板成功: {template.name} (ID: {template.id})")
    
    return {"message": f"智能体模板 {template.name} 已取消发布"}


@router.post("/templates/bulk-create", response_model=AgentTemplateBulkCreateResponse)
async def bulk_create_agent_templates(
    bulk_data: AgentTemplateBulkCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """批量创建智能体模板"""
    if not await check_agent_permission(current_user, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限批量创建智能体模板"
        )
    
    success_ids = []
    failed_items = []
    
    for template_data in bulk_data.templates:
        try:
            # 检查是否已存在
            existing_template = db.query(AgentTemplate).filter(
                AgentTemplate.name == template_data.name,
                AgentTemplate.deleted_at.is_(None)
            ).first()
            
            if existing_template:
                failed_items.append({
                    "name": template_data.name,
                    "error": "模板名称已存在"
                })
                continue
            
            # 创建模板
            db_template = AgentTemplate(**template_data.dict())
            db.add(db_template)
            db.commit()
            db.refresh(db_template)
            
            success_ids.append(db_template.id)
            
        except Exception as e:
            failed_items.append({
                "name": template_data.name,
                "error": str(e)
            })
    
    return AgentTemplateBulkCreateResponse(
        success=success_ids,
        failed=failed_items,
        message=f"批量创建完成，成功: {len(success_ids)}, 失败: {len(failed_items)}"
    )


# LangChain相关路由
@router.post("/langchain/run", response_model=LangChainRunResponse)
async def run_langchain_chain(
    run_request: LangChainRunRequest,
    current_user: dict = Depends(get_current_user)
):
    """运行LangChain链"""
    if not await check_agent_permission(current_user, "execute"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限运行LangChain链"
        )
    
    # 这里需要集成LangChain服务
    # 暂时返回模拟结果
    
    start_time = datetime.now()
    
    try:
        # 模拟LangChain执行
        await asyncio.sleep(0.5)
        
        result = {
            "output": f"LangChain链 '{run_request.chain_name}' 执行完成",
            "input": run_request.input_data,
            "config": run_request.run_config
        }
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return LangChainRunResponse(
            run_id=f"run_{int(start_time.timestamp())}",
            success=True,
            result=result,
            execution_time=execution_time,
            token_usage={"prompt_tokens": 100, "completion_tokens": 200},
            cost_estimation=0.005
        )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return LangChainRunResponse(
            run_id=f"run_{int(start_time.timestamp())}",
            success=False,
            execution_time=execution_time,
            error_message=str(e)
        )


@router.get("/langchain/stats", response_model=LangChainStatsResponse)
async def get_langchain_stats(
    current_user: dict = Depends(get_current_user)
):
    """获取LangChain统计信息"""
    if not await check_agent_permission(current_user, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问LangChain统计"
        )
    
    # 返回模拟统计信息
    return LangChainStatsResponse(
        total_runs=150,
        successful_runs=145,
        failed_runs=5,
        avg_execution_time=1.2,
        total_tokens=45000,
        total_cost=0.225,
        runs_last_hour=12,
        runs_last_24h=89
    )


# 智能体协作路由
@router.post("/collaboration/analyze")
async def analyze_collaboration(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """运行智能体协作分析（平局预测 + 对冲策略）"""
    if not await check_agent_permission(current_user, "execute"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限运行协作分析"
        )
    
    start_time = datetime.now()
    
    try:
        # 获取LangChain服务
        from ...services.langchain_service import get_default_service
        langchain_service = get_default_service()
        
        # 创建协作智能体
        from ...agents.sequential_collaboration_agent import SequentialCollaborationAgent
        collaboration_agent = SequentialCollaborationAgent(
            name="collaboration_analyzer",
            description="平局预测与对冲策略协作分析智能体",
            langchain_service=langchain_service
        )
        
        # 执行协作分析
        result = await collaboration_agent.execute(request)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "result": result,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        return {
            "success": False,
            "error": str(e),
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }


# WebSocket实时通信
@router.websocket("/ws/{agent_id}")
async def agent_websocket(
    websocket: WebSocket,
    agent_id: int,
    db: Session = Depends(get_db)
):
    """智能体WebSocket连接"""
    await websocket.accept()
    
    agent = db.query(AgentModel).filter(
        AgentModel.id == agent_id,
        AgentModel.deleted_at.is_(None)
    ).first()
    
    if not agent:
        await websocket.close(code=1008)
        return
    
    # 获取智能体管理器并添加连接
    agent_manager = get_agent_manager()
    agent_manager.websocket_connections.add(websocket)
    
    try:
        # 发送初始状态
        await websocket.send_json({
            "type": "agent_status",
            "agent_id": agent_id,
            "status": agent.status,
            "timestamp": datetime.now().isoformat()
        })
        
        # 保持连接并处理消息
        while True:
            data = await websocket.receive_text()
            
            # 处理客户端消息
            # 这里可以实现实时控制等功能
            
            await websocket.send_json({
                "type": "ack",
                "message": "消息已接收",
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        # 移除连接
        agent_manager.websocket_connections.remove(websocket)
        logger.info(f"智能体 {agent_id} WebSocket连接已关闭")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        agent_manager.websocket_connections.remove(websocket)


@router.get("/health")
async def health_check():
    """智能体系统健康检查"""
    try:
        agent_manager = get_agent_manager()
        
        # 检查基本状态
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "agent_manager": "running",
                "websocket": len(agent_manager.websocket_connections),
                "total_agents": len(agent_manager.agents)
            }
        }
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# 确保路由被导出
__all__ = ["router"]
