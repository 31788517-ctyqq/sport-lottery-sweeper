from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, String, cast
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import csv
from io import StringIO
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
    # Some historical rows may have NULL created_at; keep response validation tolerant.
    created_at: Optional[datetime] = None

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
    """Normalize different log models into the unified LogResponse schema."""

    # Determine log_type
    log_type = "system"
    if isinstance(entry, LogEntry):
        log_type = "system"
    elif isinstance(entry, AdminOperationLog):
        log_type = "user"
    elif isinstance(entry, AdminLoginLog):
        log_type = "security"
    elif isinstance(entry, CrawlerTaskLog):
        log_type = "api"

    # System logs
    if isinstance(entry, LogEntry):
        created_at = entry.created_at or entry.timestamp or datetime.utcnow()
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
            created_at=created_at,
        )

    # Admin operation logs
    if isinstance(entry, AdminOperationLog):
        extra = {
            "action": entry.action,
            "resource_type": entry.resource_type,
            "resource_id": entry.resource_id,
            "resource_name": entry.resource_name,
            "method": entry.method,
            "path": entry.path,
            "query_params": entry.query_params,
            "request_body": entry.request_body,
            "response_data": entry.response_data,
            "changes_before": entry.changes_before,
            "changes_after": entry.changes_after,
        }

        level = "INFO" if (entry.status_code or 200) < 400 else "ERROR"
        msg = f"{entry.action} {entry.resource_type} {entry.resource_id or ''}".strip()

        return LogResponse(
            id=entry.id,
            timestamp=entry.created_at,
            level=level,
            log_type=log_type,
            module=entry.resource_type or "admin_operation",
            message=msg,
            user_id=entry.admin_id,
            ip_address=entry.ip_address,
            user_agent=entry.user_agent,
            request_path=entry.path,
            response_status=entry.status_code,
            duration_ms=entry.duration_ms,
            extra_data=json.dumps(extra, ensure_ascii=False),
            created_at=entry.created_at,
        )

    # Admin login logs (security)
    if isinstance(entry, AdminLoginLog):
        level = "INFO" if entry.success else "WARNING"
        msg = "login success" if entry.success else f"login failed: {entry.failure_reason or '-'}"

        extra = {
            "success": entry.success,
            "failure_reason": entry.failure_reason,
            "country": entry.country,
            "region": entry.region,
            "city": entry.city,
            "device_type": entry.device_type,
            "os": entry.os,
            "browser": entry.browser,
            "two_factor_used": entry.two_factor_used,
            "ip_whitelisted": entry.ip_whitelisted,
        }

        return LogResponse(
            id=entry.id,
            timestamp=entry.login_at,
            level=level,
            log_type=log_type,
            module="admin_login",
            message=msg,
            user_id=entry.admin_id,
            ip_address=entry.login_ip,
            user_agent=entry.user_agent,
            extra_data=json.dumps(extra, ensure_ascii=False),
            created_at=entry.login_at,
        )

    # Crawler task logs (API)
    if isinstance(entry, CrawlerTaskLog):
        status_upper = (entry.status or "").upper()
        level = "ERROR" if status_upper in {"FAILED", "TIMEOUT"} else "INFO"

        msg = f"task:{entry.task_id} source:{entry.source_id} status:{entry.status}"
        if entry.error_message:
            msg = f"{msg} error:{entry.error_message}"

        extra = {
            "task_id": entry.task_id,
            "source_id": entry.source_id,
            "status": entry.status,
            "started_at": entry.started_at.isoformat() if entry.started_at else None,
            "completed_at": entry.completed_at.isoformat() if entry.completed_at else None,
            "duration_seconds": entry.duration_seconds,
            "records_processed": entry.records_processed,
            "records_success": entry.records_success,
            "records_failed": entry.records_failed,
            "error_message": entry.error_message,
            "error_details": entry.error_details,
            "response_time_ms": entry.response_time_ms,
            "created_by": entry.created_by,
        }

        duration_ms = None
        if entry.duration_seconds is not None:
            try:
                duration_ms = int(entry.duration_seconds * 1000)
            except Exception:
                duration_ms = None
        elif entry.response_time_ms is not None:
            try:
                duration_ms = int(entry.response_time_ms)
            except Exception:
                duration_ms = None

        timestamp = entry.started_at or entry.created_at or datetime.utcnow()
        created_at = entry.created_at or timestamp

        return LogResponse(
            id=entry.id,
            timestamp=timestamp,
            level=level,
            log_type=log_type,
            module="crawler_task",
            message=msg,
            user_id=entry.created_by,
            duration_ms=duration_ms,
            extra_data=json.dumps(extra, ensure_ascii=False),
            created_at=created_at,
        )

    # Fallback
    ts = getattr(entry, "created_at", None) or getattr(entry, "login_at", None) or datetime.utcnow()
    return LogResponse(
        id=getattr(entry, "id", 0),
        timestamp=ts,
        level="INFO",
        log_type=log_type,
        module=entry.__class__.__name__,
        message=str(entry),
        created_at=ts,
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


@router.get("/logs/db/system", response_model=Dict[str, Any])
async def read_system_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    level: Optional[str] = Query(None, description="日志级别: DEBUG, INFO, WARN, ERROR, CRITICAL"),
    module: Optional[str] = Query(None, description="模块名称"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取系统日志（LogEntry）
    """
    try:
        query = db.query(LogEntry)
        if level:
            query = query.filter(LogEntry.level == level.upper())
        if module:
            query = query.filter(LogEntry.module.ilike(f"%{module}%"))
        if search:
            query = query.filter(
                or_(
                    LogEntry.message.ilike(f"%{search}%"),
                    LogEntry.module.ilike(f"%{search}%")
                )
            )
        if start_date:
            query = query.filter(LogEntry.timestamp >= start_date)
        if end_date:
            query = query.filter(LogEntry.timestamp <= end_date)

        total = query.count()
        logs = query.order_by(LogEntry.timestamp.desc()).offset(skip).limit(limit).all()
        return {
            "code": 200,
            "message": "获取系统日志成功",
            "data": {
                "items": [to_log_response(log) for log in logs],
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


@router.get("/logs/db/security", response_model=Dict[str, Any])
async def read_security_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    search: Optional[str] = Query(None, description="搜索关键词"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取安全日志（AdminLoginLog）
    """
    try:
        query = db.query(AdminLoginLog)
        if search:
            query = query.filter(
                or_(
                    AdminLoginLog.login_ip.ilike(f"%{search}%"),
                    AdminLoginLog.user_agent.ilike(f"%{search}%")
                )
            )
        if start_date:
            query = query.filter(AdminLoginLog.login_at >= start_date)
        if end_date:
            query = query.filter(AdminLoginLog.login_at <= end_date)

        total = query.count()
        logs = query.order_by(AdminLoginLog.login_at.desc()).offset(skip).limit(limit).all()
        
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


@router.get("/logs/export")
async def export_user_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=5000),
    user_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """导出用户操作日志为 CSV。"""
    query = db.query(AdminOperationLog)
    if user_id:
        query = query.filter(AdminOperationLog.admin_id == user_id)
    if search:
        query = query.filter(AdminOperationLog.action.ilike(f'%{search}%'))
    if start_date:
        query = query.filter(AdminOperationLog.created_at >= start_date)
    if end_date:
        query = query.filter(AdminOperationLog.created_at <= end_date)

    logs = query.order_by(AdminOperationLog.created_at.desc()).offset(skip).limit(limit).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "created_at", "admin_id", "action", "resource_type", "resource_id",
        "resource_name", "method", "path", "status_code", "ip_address"
    ])
    for log in logs:
        writer.writerow([
            log.id,
            log.created_at.isoformat() if log.created_at else "",
            log.admin_id,
            log.action,
            log.resource_type,
            log.resource_id or "",
            log.resource_name or "",
            log.method or "",
            log.path or "",
            log.status_code or "",
            log.ip_address or ""
        ])

    output.seek(0)
    filename = f"user_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.delete("/logs/db/user/item/{log_id}")
async def delete_user_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """删除单条用户操作日志。"""
    log = db.query(AdminOperationLog).filter(AdminOperationLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
    return {"code": 200, "message": "删除成功", "data": {"id": log_id}}


@router.delete("/logs/db/user/clear")
async def clear_user_logs(
    beforeDate: Optional[datetime] = Query(None),
    condition: Optional[str] = Query(None),
    days: Optional[int] = Query(None, ge=1),
    count: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """清理用户操作日志，支持 beforeDate / days / count 三种方式。"""
    query = db.query(AdminOperationLog)

    if beforeDate:
        query = query.filter(AdminOperationLog.created_at < beforeDate)
        deleted = query.delete(synchronize_session=False)
        db.commit()
        return {"code": 200, "message": "清理成功", "data": {"deleted": deleted}}

    if condition == "days" and days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = query.filter(AdminOperationLog.created_at < cutoff).delete(synchronize_session=False)
        db.commit()
        return {"code": 200, "message": "清理成功", "data": {"deleted": deleted}}

    if condition == "count" and count:
        keep_ids = [
            x[0]
            for x in db.query(AdminOperationLog.id)
            .order_by(AdminOperationLog.created_at.desc())
            .limit(count)
            .all()
        ]
        if keep_ids:
            deleted = db.query(AdminOperationLog).filter(~AdminOperationLog.id.in_(keep_ids)).delete(synchronize_session=False)
        else:
            deleted = 0
        db.commit()
        return {"code": 200, "message": "清理成功", "data": {"deleted": deleted}}

    raise HTTPException(status_code=422, detail="Invalid cleanup params")


@router.get("/logs/db/api", response_model=Dict[str, Any])
async def read_api_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    search: Optional[str] = Query(None, description="搜索关键词"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取API日志（CrawlerTaskLog）
    """
    try:
        query = db.query(CrawlerTaskLog)
        if search:
            query = query.filter(
                or_(
                    CrawlerTaskLog.status.ilike(f"%{search}%"),
                    CrawlerTaskLog.error_message.ilike(f"%{search}%"),
                    cast(CrawlerTaskLog.task_id, String).ilike(f"%{search}%")
                )
            )
        if start_date:
            query = query.filter(CrawlerTaskLog.started_at >= start_date)
        if end_date:
            query = query.filter(CrawlerTaskLog.started_at <= end_date)

        total = query.count()
        logs = query.order_by(CrawlerTaskLog.started_at.desc()).offset(skip).limit(limit).all()
        
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
    search: Optional[str] = Query(None, description="搜索关键词"),
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
        if search:
            query = query.filter(LogEntry.message.ilike(f'%{search}%'))
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
                    AdminLoginLog.login_ip.ilike(f'%{q}%') |
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
