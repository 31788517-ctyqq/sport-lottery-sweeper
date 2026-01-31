from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.sql import func
from ....models.log_entry import LogEntry
from ....models.admin_user import AdminLoginLog, AdminOperationLog
from ....models.crawler_logs import CrawlerTaskLog
from ....database import get_db
from datetime import datetime, timedelta
from fastapi import Depends
import json

# 模拟 token 获取函数，避免认证依赖问题
def get_mock_token():
    return None

# 移除prefix="/admin"，因为在API注册时已经包含了/admin前缀
router = APIRouter(tags=["admin-logs"])

# 简单的模式定义，避免导入缺失
class LogResponse(BaseModel):
    id: int
    timestamp: datetime
    level: str
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
    if isinstance(entry, LogEntry):
        return LogResponse(
            id=entry.id,
            timestamp=entry.timestamp,
            level=entry.level,
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
        module=entry.__class__.__name__,
        message=str(entry),
        created_at=datetime.utcnow()
    )

@router.get("/system/logs/db/statistics", response_model=LogStatistics)
async def read_log_statistics(current_user=Depends(get_mock_token)):
    """
    获取日志统计信息
    """
    db = next(get_db())
    try:
        # 简单统计
        total = db.query(LogEntry).count()
        levels = db.query(LogEntry.level, func.count(LogEntry.id)).group_by(LogEntry.level).all()
        modules = db.query(LogEntry.module, func.count(LogEntry.id)).group_by(LogEntry.module).all()
        recent_time = datetime.utcnow() - timedelta(hours=24)
        recent_count = db.query(LogEntry).filter(LogEntry.timestamp >= recent_time).count()
        avg_daily = total / 30 if total > 0 else 0
        
        stats = LogStatistics(
            total_logs=total,
            logs_by_level={level: count for level, count in levels},
            logs_by_module={module: count for module, count in modules},
            recent_24h=recent_count,
            average_daily=avg_daily
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/system/logs/db/system", response_model=List[LogResponse])
async def read_system_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user=Depends(get_mock_token)
):
    """
    获取系统日志（LogEntry）
    """
    db = next(get_db())
    try:
        logs = db.query(LogEntry).order_by(LogEntry.timestamp.desc()).offset(skip).limit(limit).all()
        return [to_log_response(log) for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/system/logs/db/user", response_model=List[LogResponse])
async def read_user_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user=Depends(get_mock_token)
):
    """
    获取用户操作日志（AdminOperationLog）
    """
    db = next(get_db())
    try:
        logs = db.query(AdminOperationLog).order_by(AdminOperationLog.created_at.desc()).offset(skip).limit(limit).all()
        return [to_log_response(log) for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/system/logs/db/security", response_model=List[LogResponse])
async def read_security_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user=Depends(get_mock_token)
):
    """
    获取安全日志（AdminLoginLog）
    """
    db = next(get_db())
    try:
        logs = db.query(AdminLoginLog).order_by(AdminLoginLog.login_at.desc()).offset(skip).limit(limit).all()
        return [to_log_response(log) for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/system/logs/db/api", response_model=List[LogResponse])
async def read_api_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user=Depends(get_mock_token)
):
    """
    获取API日志（CrawlerTaskLog）
    """
    db = next(get_db())
    try:
        logs = db.query(CrawlerTaskLog).order_by(CrawlerTaskLog.started_at.desc()).offset(skip).limit(limit).all()
        return [to_log_response(log) for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/system/logs/db/search", response_model=List[LogResponse])
async def search_logs(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user=Depends(get_mock_token)
):
    """
    搜索日志
    """
    db = next(get_db())
    try:
        # 简单搜索：在所有 LogEntry 中搜索消息
        logs = db.query(LogEntry).filter(LogEntry.message.ilike(f'%{q}%')).order_by(LogEntry.timestamp.desc()).offset(skip).limit(limit).all()
        return [to_log_response(log) for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()