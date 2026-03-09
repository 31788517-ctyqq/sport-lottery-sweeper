from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.crawler_tasks import CrawlerTask
from backend.models.crawler_logs import CrawlerTaskLog

router = APIRouter(prefix="/task-monitor", tags=["task-monitor"])

# Pydantic模型
class Execution(BaseModel):
    id: int
    task_id: int
    task_name: str
    status: str  # RUNNING, SUCCESS, FAILED, CANCELLED, PENDING
    progress: float
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration: Optional[float] = None  # in seconds
    error_message: Optional[str] = None
    records_processed: Optional[int] = 0
    records_success: Optional[int] = 0
    records_failed: Optional[int] = 0


class ExecutionDetail(Execution):
    config: Optional[Dict[str, Any]] = {}
    logs: Optional[List[Dict[str, Any]]] = []


class Statistics(BaseModel):
    success_rate: float
    avg_execution_time: float
    failure_rate: float


class DailyStatistics(BaseModel):
    date: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_duration: float


class TopIssue(BaseModel):
    issue_type: str
    count: int
    description: str


class RealtimeOverview(BaseModel):
    running_tasks: int
    today_total: int
    today_success: int
    success_rate: float
    avg_duration: float
    hourly_error_rate: float


@router.get("/executions")
async def get_executions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    task_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取任务执行列表 - 从真实数据库获取数据
    """
    # 获取任务日志作为执行记录
    query = db.query(CrawlerTaskLog).join(CrawlerTask, CrawlerTask.id == CrawlerTaskLog.task_id)
    
    if status:
        query = query.filter(CrawlerTaskLog.status.ilike(f"%{status}%"))
    
    if task_id:
        query = query.filter(CrawlerTaskLog.task_id == task_id)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    start_idx = (page - 1) * page_size
    execution_logs = query.order_by(CrawlerTaskLog.id.desc()).offset(start_idx).limit(page_size).all()
    
    # 转换为Execution对象
    items = []
    for log in execution_logs:
        # 获取对应的task信息
        task = db.query(CrawlerTask).filter(CrawlerTask.id == log.task_id).first()
        
        # 计算持续时间
        duration = None
        if log.started_at and log.completed_at:
            duration = (log.completed_at - log.started_at).total_seconds()
        elif log.started_at:
            duration = (datetime.utcnow() - log.started_at).total_seconds()
        
        execution = Execution(
            id=log.id,
            task_id=log.task_id,
            task_name=task.name if task else f"Task {log.task_id}",
            status=log.status or "UNKNOWN",
            progress=0.0,  # 任务进度暂时设为0，因为没有实时进度信息
            started_at=log.started_at,
            finished_at=log.completed_at,
            duration=duration,
            error_message=log.error_message,
            records_processed=log.records_processed or 0,
            records_success=log.records_success or 0,
            records_failed=log.records_failed or 0
        )
        items.append(execution)
    
    return {
        "code": 200,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "size": page_size,
            "pages": (total + page_size - 1) // page_size
        },
        "message": "获取任务执行列表成功"
    }


@router.get("/executions/{execution_id}")
async def get_execution_detail(execution_id: int, db: Session = Depends(get_db)):
    """
    获取单个执行详情
    """
    # 通过日志ID获取日志记录
    log = db.query(CrawlerTaskLog).filter(CrawlerTaskLog.id == execution_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="执行记录未找到")
    
    # 获取对应的task信息
    task = db.query(CrawlerTask).filter(CrawlerTask.id == log.task_id).first()
    
    # 计算持续时间
    duration = None
    if log.started_at and log.completed_at:
        duration = (log.completed_at - log.started_at).total_seconds()
    elif log.started_at:
        duration = (datetime.utcnow() - log.started_at).total_seconds()
    
    # 构建ExecutionDetail对象
    detail = ExecutionDetail(
        id=log.id,
        task_id=log.task_id,
        task_name=task.name if task else f"Task {log.task_id}",
        status=log.status or "UNKNOWN",
        progress=0.0,
        started_at=log.started_at,
        finished_at=log.completed_at,
        duration=duration,
        error_message=log.error_message,
        records_processed=log.records_processed or 0,
        records_success=log.records_success or 0,
        records_failed=log.records_failed or 0,
        config=task.config if task and task.config else {},
        logs=[{
            "timestamp": log.created_at.isoformat() if log.created_at else "",
            "level": "INFO",
            "message": log.error_message or f"Log entry for task {log.task_id}"
        }]
    )
    
    return {
        "code": 200,
        "data": detail,
        "message": "获取执行详情成功"
    }


@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: int, db: Session = Depends(get_db)):
    """
    取消正在执行的任务
    """
    # 实际上无法取消已完成的日志记录，所以返回错误
    log = db.query(CrawlerTaskLog).filter(CrawlerTaskLog.id == execution_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="执行记录未找到")
    
    # 通过task_id获取任务并尝试停止
    from backend.services.task_scheduler_service import TaskSchedulerService
    scheduler_service = TaskSchedulerService(db)
    result = scheduler_service.stop_task(log.task_id)
    
    if result["success"]:
        return {
            "code": 200,
            "data": {"id": log.task_id, "status": "CANCELLED"},
            "message": "任务已成功取消"
        }
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@router.get("/executions/{execution_id}/logs")
async def get_execution_logs(execution_id: int, db: Session = Depends(get_db)):
    """
    获取任务执行日志
    """
    log = db.query(CrawlerTaskLog).filter(CrawlerTaskLog.id == execution_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="执行记录未找到")
    
    # 返回该任务的最近日志记录
    task_logs = db.query(CrawlerTaskLog).filter(
        CrawlerTaskLog.task_id == log.task_id
    ).order_by(CrawlerTaskLog.created_at.desc()).limit(50).all()
    
    logs = [
        {
            "id": log_record.id,
            "timestamp": log_record.created_at.isoformat() if log_record.created_at else "",
            "level": log_record.status.upper() if log_record.status else "INFO",
            "message": log_record.error_message or 
                      f"Processed {log_record.records_processed or 0} records, " +
                      f"success: {log_record.records_success or 0}, " +
                      f"failed: {log_record.records_failed or 0}"
        }
        for log_record in task_logs
    ]
    
    return {
        "code": 200,
        "data": logs,
        "message": "获取日志成功"
    }


@router.get("/statistics/daily")
async def get_daily_statistics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取每日统计
    """
    # 获取任务日志统计信息
    logs = db.query(CrawlerTaskLog).all()
    
    # 按日期分组统计
    daily_stats = {}
    for log in logs:
        if not log.created_at:
            continue
            
        date_str = log.created_at.strftime("%Y-%m-%d")
        if date_str not in daily_stats:
            daily_stats[date_str] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "durations": []
            }
        
        daily_stats[date_str]["total_executions"] += 1
        
        if log.status and "success" in log.status.lower():
            daily_stats[date_str]["successful_executions"] += 1
        elif log.status and ("fail" in log.status.lower() or "error" in log.status.lower()):
            daily_stats[date_str]["failed_executions"] += 1
            
        if log.started_at and log.completed_at:
            duration = (log.completed_at - log.started_at).total_seconds()
            daily_stats[date_str]["durations"].append(duration)
    
    # 转换为DailyStatistics对象列表
    stats_list = []
    for date_str, data in daily_stats.items():
        avg_duration = sum(data["durations"]) / len(data["durations"]) if data["durations"] else 0
        stat = DailyStatistics(
            date=date_str,
            total_executions=data["total_executions"],
            successful_executions=data["successful_executions"],
            failed_executions=data["failed_executions"],
            avg_duration=avg_duration
        )
        stats_list.append(stat)
    
    # 按日期排序
    stats_list.sort(key=lambda x: x.date, reverse=True)
    
    return {
        "code": 200,
        "data": stats_list,
        "message": "获取每日统计成功"
    }


@router.get("/statistics/top-issues")
async def get_top_issues(db: Session = Depends(get_db)):
    """
    获取主要问题排行
    """
    # 获取错误日志
    error_logs = db.query(CrawlerTaskLog).filter(
        CrawlerTaskLog.error_message.isnot(None),
        CrawlerTaskLog.error_message != ""
    ).all()
    
    # 统计错误类型
    error_counts = {}
    for log in error_logs:
        error_msg = log.error_message
        if error_msg in error_counts:
            error_counts[error_msg] += 1
        else:
            error_counts[error_msg] = 1
    
    # 按计数排序并取前几位
    sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    issues = [
        TopIssue(
            issue_type=error_msg[:50] + "..." if len(error_msg) > 50 else error_msg,  # 限制长度
            count=count,
            description=error_msg
        )
        for error_msg, count in sorted_errors
    ]
    
    return {
        "code": 200,
        "data": issues,
        "message": "获取问题排行成功"
    }


@router.get("/realtime/overview")
async def get_realtime_overview(db: Session = Depends(get_db)):
    """
    获取实时概览
    """
    # 获取所有任务
    all_tasks = db.query(CrawlerTask).all()
    
    # 获取今天的日志
    today = datetime.utcnow().date()
    today_logs = db.query(CrawlerTaskLog).filter(
        func.date(CrawlerTaskLog.created_at) == today
    ).all()
    
    # 统计数据
    running_tasks = len([task for task in all_tasks if task.status and task.status.lower() == "running"])
    today_total = len(today_logs)
    today_success = len([log for log in today_logs if log.status and "success" in log.status.lower()])
    success_rate = (today_success / today_total * 100) if today_total > 0 else 0
    
    # 计算平均执行时间
    durations = [
        (log.completed_at - log.started_at).total_seconds() 
        for log in today_logs 
        if log.started_at and log.completed_at
    ]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # 计算每小时错误率（过去24小时）
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    recent_logs = db.query(CrawlerTaskLog).filter(
        CrawlerTaskLog.created_at >= twenty_four_hours_ago
    ).all()
    
    total_recent = len(recent_logs)
    failed_recent = len([log for log in recent_logs if log.status and "fail" in log.status.lower()])
    hourly_error_rate = (failed_recent / total_recent * 100) / 24 if total_recent > 0 else 0
    
    overview = RealtimeOverview(
        running_tasks=running_tasks,
        today_total=today_total,
        today_success=today_success,
        success_rate=round(success_rate, 2),
        avg_duration=round(avg_duration, 2),
        hourly_error_rate=round(hourly_error_rate, 2)
    )
    
    return {
        "code": 200,
        "data": overview,
        "message": "获取实时概览成功"
    }