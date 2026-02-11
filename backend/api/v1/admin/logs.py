from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from pydantic import BaseModel

from ...dependencies import get_db, get_current_active_admin_user
from backend.models.admin_user import AdminUser, AdminOperationLog, AdminLoginLog
from backend.models.log_entry import LogEntry
from backend.models.crawler_logs import CrawlerTaskLog  # 添加爬虫任务日志模型
from backend.core.config import settings

router = APIRouter()

# 简单的模式定义，避免导入缺失
class LogResponse(BaseModel):
    id: int
    timestamp: datetime
    level: str
    log_type: str = "system"  # system, user, security, api
    module: str
    message: str
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_path: Optional[str] = None
    response_status: Optional[int] = None
    duration_ms: Optional[int] = None
    extra_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class LogStatistics(BaseModel):
    total_logs: int
    logs_by_level: Dict[str, int]
    logs_by_module: Dict[str, int]
    recent_24h: int
    average_daily: float

    class Config:
        from_attributes = True

# 辅助函数：将模型对象转为 LogResponse
def to_log_response(entry):
    # 根据日志类型设置 log_type
    log_type = "system"
    if isinstance(entry, LogEntry):
        log_type = "system"
    elif isinstance(entry, AdminOperationLog):
        log_type = "user"
    elif isinstance(entry, AdminLoginLog):
        log_type = "security"
    elif isinstance(entry, CrawlerTaskLog):
        log_type = "api"
    
    if isinstance(entry, LogEntry):
        return LogResponse(
            id=entry.id,
            timestamp=entry.timestamp,
            level=entry.level,
            log_type=log_type,
            module=entry.module,
            message=entry.message,
            user_id=entry.user_id,
            ip_address=entry.ip_address,
            user_agent=entry.user_agent,
            session_id=entry.session_id,
            request_path=entry.request_path,
            response_status=entry.response_status,
            duration_ms=entry.duration_ms,
            extra_data=entry.extra_data,
            created_at=entry.created_at
        )
    # 对于其他日志类型，返回简化版本
    return LogResponse(
        id=entry.id,
        timestamp=getattr(entry, 'created_at', getattr(entry, 'login_at', datetime.utcnow())),
        level='INFO',
        log_type=log_type,
        module=entry.__class__.__name__,
        message=str(entry),
        created_at=datetime.utcnow()
    )

@router.get("/logs/db/statistics", response_model=LogStatistics)
async def read_log_statistics(
    db: Session = Depends(get_db), 
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取日志统计信息
    """
    try:
        # 系统日志统计 - 来自LogEntry表
        total_system = db.query(LogEntry).count()
        system_levels = db.query(LogEntry.level, func.count(LogEntry.id)).group_by(LogEntry.level).all()
        system_modules = db.query(LogEntry.module, func.count(LogEntry.id)).group_by(LogEntry.module).all()
        
        # 用户日志统计 - 来自AdminOperationLog表
        total_user = db.query(AdminOperationLog).count()
        user_modules = [('user_operations', total_user)] if total_user > 0 else []
        
        # 安全日志统计 - 来自AdminLoginLog表
        total_security = db.query(AdminLoginLog).count()
        security_modules = [('security_events', total_security)] if total_security > 0 else []
        
        # API日志统计 - 来自CrawlerTaskLog表
        total_api = db.query(CrawlerTaskLog).count()
        api_modules = [('api_calls', total_api)] if total_api > 0 else []
        
        # 合并统计
        total = total_system + total_user + total_security + total_api
        
        # 合并级别统计
        all_levels_dict = {level: count for level, count in system_levels}
        
        # 合并模块统计
        all_modules_dict = {module: count for module, count in system_modules}
        all_modules_dict.update({module: count for module, count in user_modules})
        all_modules_dict.update({module: count for module, count in security_modules})
        all_modules_dict.update({module: count for module, count in api_modules})
        
        # 计算最近24小时的总体日志数
        recent_time = datetime.utcnow() - timedelta(hours=24)
        recent_system = db.query(LogEntry).filter(LogEntry.timestamp >= recent_time).count()
        # 注意：其他表可能没有timestamp字段，或字段名称不同，这里简化处理
        recent_total = recent_system  # 这里只计算系统日志，如需更精确可扩展
        
        avg_daily = total / 30 if total > 0 else 0
        
        stats = LogStatistics(
            total_logs=total,
            logs_by_level=all_levels_dict,
            logs_by_module=all_modules_dict,
            recent_24h=recent_total,
            average_daily=avg_daily
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/db/system", response_model=List[LogResponse])
async def read_system_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取系统日志（LogEntry）
    """
    try:
        logs = db.query(LogEntry).order_by(LogEntry.timestamp.desc()).offset(skip).limit(limit).all()
        return [to_log_response(log) for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/db/security", response_model=Dict[str, Any])
async def read_security_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取安全日志（AdminLoginLog）
    """
    try:
        logs = db.query(AdminLoginLog).order_by(AdminLoginLog.login_at.desc()).offset(skip).limit(limit).all()
        total = db.query(AdminLoginLog).count()
        
        log_responses = [to_log_response(log) for log in logs]
        
        return {
            "code": 200,
            "message": "获取安全日志成功",
            "data": {
                "items": log_responses,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        return {
            "code": 500,
            "message": str(e),
            "data": None
        }


@router.get("/logs/db/user", response_model=Dict[str, Any])
async def read_user_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    user_id: Optional[int] = Query(None, description="用户ID"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取用户操作日志（AdminOperationLog）
    """
    try:
        query = db.query(AdminOperationLog)
        
        # 按用户ID筛选
        if user_id:
            query = query.filter(AdminOperationLog.admin_id == user_id)
        
        # 按搜索关键词筛选
        if search:
            query = query.filter(AdminOperationLog.action.ilike(f'%{search}%'))
        
        # 按日期范围筛选
        if start_date:
            query = query.filter(AdminOperationLog.created_at >= start_date)
        if end_date:
            query = query.filter(AdminOperationLog.created_at <= end_date)
        
        total = query.count()
        logs = query.order_by(AdminOperationLog.created_at.desc()).offset(skip).limit(limit).all()
        log_responses = [to_log_response(log) for log in logs]
        
        return {
            "code": 200,
            "message": "获取用户操作日志成功",
            "data": {
                "items": log_responses,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        return {
            "code": 500,
            "message": str(e),
            "data": None
        }


@router.get("/logs/db/user/count", response_model=Dict[str, int])
async def read_user_logs_count(
    user_id: Optional[int] = Query(None, description="按用户ID筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取用户操作日志总数（用于分页）
    """
    try:
        query = db.query(AdminOperationLog)
        
        # 按用户ID筛选
        if user_id:
            query = query.filter(AdminOperationLog.admin_id == user_id)
        
        # 按搜索关键词筛选
        if search:
            query = query.filter(AdminOperationLog.action.ilike(f'%{search}%'))
        
        # 按日期范围筛选
        if start_date:
            query = query.filter(AdminOperationLog.created_at >= start_date)
        if end_date:
            query = query.filter(AdminOperationLog.created_at <= end_date)
        
        count = query.count()
        return {"total": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/db/api", response_model=Dict[str, Any])
async def read_api_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取API日志（CrawlerTaskLog）
    """
    try:
        logs = db.query(CrawlerTaskLog).order_by(CrawlerTaskLog.started_at.desc()).offset(skip).limit(limit).all()
        total = db.query(CrawlerTaskLog).count()
        
        result = []
        for log in logs:
            # 为CrawlerTaskLog提供特殊的字段映射
            # 确保时间字段是datetime类型
            started_at_dt = log.started_at if log.started_at else datetime.now()
            created_at_dt = log.created_at if log.created_at else datetime.now()
            
            result.append(LogResponse(
                id=log.id,
                timestamp=started_at_dt,  # 确保是datetime类型
                level='INFO',  # 默认级别
                log_type='api',
                module='CrawlerTask',
                message=f"Crawler task {log.task_id}: {log.status}",
                user_id=log.created_by,
                ip_address=None,  # CrawlerTaskLog中没有IP地址字段
                user_agent=None,  # CrawlerTaskLog中没有user_agent字段
                session_id=None,  # CrawlerTaskLog中没有session_id字段
                request_path=f"/crawler/task/{log.task_id}",  # 映射task_id为请求路径
                response_status=200 if log.status == 'success' else 500,  # 根据状态映射响应状态
                duration_ms=int(log.duration_seconds * 1000) if log.duration_seconds else None,  # 秒转毫秒
                extra_data=json.dumps({  # 将字典转换为JSON字符串
                    'status': log.status,
                    'records_processed': log.records_processed,
                    'records_success': log.records_success,
                    'records_failed': log.records_failed,
                    'error_message': log.error_message,
                    'response_time_ms': log.response_time_ms
                }),  # 将特有字段放入extra_data
                created_at=created_at_dt  # 确保是datetime类型
            ))
        
        return {
            "code": 200,
            "message": "获取API日志成功",
            "data": {
                "items": result,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        return {
            "code": 500,
            "message": str(e),
            "data": None
        }


@router.get("/logs/db/ai", response_model=Dict[str, Any])
async def read_ai_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    level: Optional[str] = Query(None, description="日志级别: DEBUG, INFO, WARN, ERROR, CRITICAL"),
    module: Optional[str] = Query(None, description="模块名称"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取AI服务日志（LogEntry中module包含ai或llm的记录）
    """
    try:
        query = db.query(LogEntry).filter(
            LogEntry.module.ilike('%ai%') | LogEntry.module.ilike('%llm%')
        )
        
        # 应用筛选条件
        if level:
            query = query.filter(LogEntry.level == level.upper())
        if module:
            query = query.filter(LogEntry.module.ilike(f'%{module}%'))
        if user_id:
            query = query.filter(LogEntry.user_id == user_id)
        if start_date:
            query = query.filter(LogEntry.timestamp >= start_date)
        if end_date:
            query = query.filter(LogEntry.timestamp <= end_date)
        
        total = query.count()
        logs = query.order_by(LogEntry.timestamp.desc()).offset(skip).limit(limit).all()
        log_responses = [to_log_response(log) for log in logs]
        
        return {
            "code": 200,
            "message": "获取AI服务日志成功",
            "data": {
                "items": log_responses,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        return {
            "code": 500,
            "message": str(e),
            "data": None
        }


@router.get("/logs/db/search", response_model=Dict[str, Any])
async def search_logs(
    q: str = Query(None, description="搜索关键词"),
    log_type: str = Query("all", description="日志类型: all, system, user, security, api, ai"),
    level: str = Query(None, description="日志级别: DEBUG, INFO, WARN, ERROR, CRITICAL"),
    module: str = Query(None, description="模块名称"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """
    高级日志搜索功能
    支持按关键词、日志类型、级别、模块、用户、时间范围等条件搜索
    """
    try:
        all_logs = []
        total_count = 0
        
        # 根据日志类型确定要查询的表
        if log_type == "all" or log_type == "system":
            # 查询系统日志 (LogEntry)
            query = db.query(LogEntry)
            
            # 应用搜索条件
            if q:
                query = query.filter(LogEntry.message.ilike(f'%{q}%'))
            if level:
                query = query.filter(LogEntry.level == level.upper())
            if module:
                query = query.filter(LogEntry.module.ilike(f'%{module}%'))
            if user_id:
                query = query.filter(LogEntry.user_id == user_id)
            if start_date:
                query = query.filter(LogEntry.timestamp >= start_date)
            if end_date:
                query = query.filter(LogEntry.timestamp <= end_date)
            
            # 获取总数和分页数据
            total_count += query.count()
            if log_type == "system" or log_type == "all":
                logs = query.order_by(LogEntry.timestamp.desc()).offset(skip).limit(limit).all()
                all_logs.extend([to_log_response(log) for log in logs])
        
        if log_type == "all" or log_type == "user":
            # 查询用户操作日志 (AdminOperationLog)
            query = db.query(AdminOperationLog)
            
            if q:
                query = query.filter(AdminOperationLog.action.ilike(f'%{q}%'))
            if user_id:
                query = query.filter(AdminOperationLog.admin_id == user_id)
            if start_date:
                query = query.filter(AdminOperationLog.created_at >= start_date)
            if end_date:
                query = query.filter(AdminOperationLog.created_at <= end_date)
            
            total_count += query.count()
            if log_type == "user" or log_type == "all":
                logs = query.order_by(AdminOperationLog.created_at.desc()).offset(skip).limit(limit).all()
                all_logs.extend([to_log_response(log) for log in logs])
        
        if log_type == "all" or log_type == "security":
            # 查询安全日志 (AdminLoginLog)
            query = db.query(AdminLoginLog)
            
            if q:
                query = query.filter(
                    AdminLoginLog.ip_address.ilike(f'%{q}%') |
                    AdminLoginLog.user_agent.ilike(f'%{q}%')
                )
            if user_id:
                query = query.filter(AdminLoginLog.admin_id == user_id)
            if start_date:
                query = query.filter(AdminLoginLog.login_at >= start_date)
            if end_date:
                query = query.filter(AdminLoginLog.login_at <= end_date)
            
            total_count += query.count()
            if log_type == "security" or log_type == "all":
                logs = query.order_by(AdminLoginLog.login_at.desc()).offset(skip).limit(limit).all()
                all_logs.extend([to_log_response(log) for log in logs])
        
        if log_type == "all" or log_type == "api":
            # 查询API日志 (CrawlerTaskLog)
            query = db.query(CrawlerTaskLog)
            
            if q:
                query = query.filter(
                    CrawlerTaskLog.status.ilike(f'%{q}%') |
                    CrawlerTaskLog.error_message.ilike(f'%{q}%')
                )
            if user_id:
                query = query.filter(CrawlerTaskLog.created_by == user_id)
            if start_date:
                query = query.filter(CrawlerTaskLog.started_at >= start_date)
            if end_date:
                query = query.filter(CrawlerTaskLog.started_at <= end_date)
            
            total_count += query.count()
            if log_type == "api" or log_type == "all":
                logs = query.order_by(CrawlerTaskLog.started_at.desc()).offset(skip).limit(limit).all()
                # 转换为LogResponse格式
                result = []
                for log in logs:
                    started_at_dt = log.started_at if log.started_at else datetime.now()
                    created_at_dt = log.created_at if log.created_at else datetime.now()
                    
                    result.append(LogResponse(
                        id=log.id,
                        timestamp=started_at_dt,
                        level='INFO',
                        log_type='api',
                        module='CrawlerTask',
                        message=f"Crawler task {log.task_id}: {log.status}",
                        user_id=log.created_by,
                        ip_address=None,
                        user_agent=None,
                        session_id=None,
                        request_path=f"/crawler/task/{log.task_id}",
                        response_status=200 if log.status == 'success' else 500,
                        duration_ms=int(log.duration_seconds * 1000) if log.duration_seconds else None,
                        extra_data=json.dumps({
                            'status': log.status,
                            'records_processed': log.records_processed,
                            'records_success': log.records_success,
                            'records_failed': log.records_failed,
                            'error_message': log.error_message,
                            'response_time_ms': log.response_time_ms
                        }),
                        created_at=created_at_dt
                    ))
                all_logs.extend(result)
        
        if log_type == "all" or log_type == "ai":
            # 查询AI服务日志 (LogEntry中module包含ai或llm的记录)
            query = db.query(LogEntry).filter(
                LogEntry.module.ilike('%ai%') | LogEntry.module.ilike('%llm%')
            )
            
            # 应用搜索条件
            if q:
                query = query.filter(LogEntry.message.ilike(f'%{q}%'))
            if level:
                query = query.filter(LogEntry.level == level.upper())
            if module:
                query = query.filter(LogEntry.module.ilike(f'%{module}%'))
            if user_id:
                query = query.filter(LogEntry.user_id == user_id)
            if start_date:
                query = query.filter(LogEntry.timestamp >= start_date)
            if end_date:
                query = query.filter(LogEntry.timestamp <= end_date)
            
            total_count += query.count()
            if log_type == "ai" or log_type == "all":
                logs = query.order_by(LogEntry.timestamp.desc()).offset(skip).limit(limit).all()
                all_logs.extend([to_log_response(log) for log in logs])
        
        # 如果是all类型，需要合并并重新排序
        if log_type == "all":
            # 按时间戳降序排序
            all_logs.sort(key=lambda x: x.timestamp, reverse=True)
            # 重新应用分页
            paginated_logs = all_logs[skip:skip+limit]
            total_count = len(all_logs)
        else:
            paginated_logs = all_logs
        
        return {
            "code": 200,
            "message": "日志搜索成功",
            "data": {
                "items": paginated_logs,
                "total": total_count,
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": str(e),
            "data": None
        }
