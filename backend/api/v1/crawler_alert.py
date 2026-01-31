"""
爬虫告警API接口
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from backend.database import get_db
from backend.services.crawler_alert_service import CrawlerAlertService
from backend.schemas.crawler_alert import (
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse,
    AlertRecordResponse, AlertCheckResult, MetricRecordRequest,
    AlertStats
)
from backend.core.auth import get_current_user
from backend.models.admin_user import AdminUser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crawler-alert", tags=["crawler-alert"])


@router.post("/rules", response_model=dict)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """创建告警规则"""
    try:
        service = CrawlerAlertService(db)
        result = service.create_alert_rule(rule_data, current_user.id)
        
        if result["success"]:
            # 触发告警检查
            background_tasks.add_task(run_alert_check_background, db)
            return {"code": 200, "message": result["message"], "data": {"rule_id": result["rule_id"]}}
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建告警规则API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建告警规则失败: {str(e)}")


@router.put("/rules/{rule_id}", response_model=dict)
async def update_alert_rule(
    rule_id: int,
    rule_data: AlertRuleUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """更新告警规则"""
    try:
        service = CrawlerAlertService(db)
        result = service.update_alert_rule(rule_id, rule_data, current_user.id)
        
        if result["success"]:
            background_tasks.add_task(run_alert_check_background, db)
            return {"code": 200, "message": result["message"], "data": {}}
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新告警规则API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新告警规则失败: {str(e)}")


@router.delete("/rules/{rule_id}", response_model=dict)
async def delete_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """删除告警规则"""
    try:
        service = CrawlerAlertService(db)
        result = service.delete_alert_rule(rule_id)
        
        if result["success"]:
            return {"code": 200, "message": result["message"], "data": {}}
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除告警规则API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除告警规则失败: {str(e)}")


@router.get("/rules", response_model=dict)
async def get_alert_rules(
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """获取告警规则列表"""
    try:
        service = CrawlerAlertService(db)
        rules = service.get_alert_rules(active_only)
        
        return {
            "code": 200,
            "message": "获取告警规则成功",
            "data": {
                "rules": rules,
                "total": len(rules)
            }
        }
        
    except Exception as e:
        logger.error(f"获取告警规则API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取告警规则失败: {str(e)}")


@router.post("/check", response_model=AlertCheckResult)
async def check_alerts(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """手动触发告警检查"""
    try:
        service = CrawlerAlertService(db)
        result = service.check_alerts()
        
        return AlertCheckResult(**result)
        
    except Exception as e:
        logger.error(f"告警检查API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"告警检查失败: {str(e)}")


@router.get("/records", response_model=dict)
async def get_alert_records(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """获取告警记录"""
    try:
        service = CrawlerAlertService(db)
        records = service.get_alert_records(status, limit)
        
        return {
            "code": 200,
            "message": "获取告警记录成功",
            "data": {
                "records": records,
                "total": len(records)
            }
        }
        
    except Exception as e:
        logger.error(f"获取告警记录API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取告警记录失败: {str(e)}")


@router.post("/records/{alert_id}/resolve", response_model=dict)
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """解决告警"""
    try:
        service = CrawlerAlertService(db)
        result = service.resolve_alert(alert_id, current_user.id)
        
        if result["success"]:
            return {"code": 200, "message": result["message"], "data": {}}
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"解决告警API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"解决告警失败: {str(e)}")


@router.post("/metrics", response_model=dict)
async def record_metric(
    metric_data: MetricRecordRequest,
    db: Session = Depends(get_db)
):
    """记录监控指标（无需认证，供内部调用）"""
    try:
        service = CrawlerAlertService(db)
        service.record_metric(
            source_id=metric_data.source_id,
            metric_type=metric_data.metric_type,
            metric_value=metric_data.metric_value,
            tags=metric_data.tags
        )
        
        return {"code": 200, "message": "指标记录成功", "data": {}}
        
    except Exception as e:
        logger.error(f"记录指标API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"记录指标失败: {str(e)}")


@router.get("/stats", response_model=dict)
async def get_alert_stats(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """获取告警统计信息"""
    try:
        service = CrawlerAlertService(db)
        
        # 获取各种状态的告警数量
        all_records = service.get_alert_records(limit=1000)
        active_records = service.get_alert_records(status="active", limit=1000)
        resolved_records = service.get_alert_records(status="resolved", limit=1000)
        
        # 按级别统计
        alerts_by_level = {}
        for record in all_records:
            level = record["alert_level"]
            alerts_by_level[level] = alerts_by_level.get(level, 0) + 1
        
        # 获取故障最多的数据源
        source_failures = {}
        for record in all_records:
            if record["source_id"]:
                source_id = record["source_id"]
                source_failures[source_id] = source_failures.get(source_id, 0) + 1
        
        # 排序获取前5个
        top_failing_sources = sorted(
            [{"source_id": k, "failure_count": v} for k, v in source_failures.items()],
            key=lambda x: x["failure_count"],
            reverse=True
        )[:5]
        
        stats = AlertStats(
            total_alerts=len(all_records),
            active_alerts=len(active_records),
            resolved_alerts=len(resolved_records),
            alerts_by_level=alerts_by_level,
            recent_alerts=[AlertRecordResponse(**record) for record in all_records[:10]],
            top_failing_sources=top_failing_sources
        )
        
        return {
            "code": 200,
            "message": "获取告警统计成功",
            "data": stats.dict()
        }
        
    except Exception as e:
        logger.error(f"获取告警统计API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取告警统计失败: {str(e)}")


def run_alert_check_background(db: Session):
    """后台运行告警检查的辅助函数"""
    try:
        service = CrawlerAlertService(db)
        service.check_alerts()
    except Exception as e:
        logger.error(f"后台告警检查失败: {str(e)}")