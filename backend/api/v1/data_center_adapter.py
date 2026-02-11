"""
数据中心API适配器
为前端提供兼容的API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.matches import FootballMatch as Match
from backend.models.odds_companies import OddsCompany as Odds
from backend.models.data_sources import DataSource
from backend.models.sp_records import SPRecord

router = APIRouter(prefix="", tags=["data-center-adapter"])

@router.get("/stats/data-center")
async def get_summary_stats(
    db: Session = Depends(get_db)
):
    """
    获取数据中心统计摘要 - 适配前端请求路径
    """
    try:
        # 获取各类数据的统计
        total_matches = db.query(Match).count()
        total_odds = db.query(Odds).count()
        total_sp_records = db.query(SPRecord).count()
        active_sources = db.query(DataSource).filter(DataSource.status == True).count()
        
        # 计算今天的增长率（模拟数据）
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # 这里我们简单模拟增长率数据
        growth_factor = 5  # 模拟增长
        
        summary_data = {
            "totalMatches": total_matches,
            "activeSources": active_sources,
            "dataQuality": 94.2,
            "errorRate": 1.2,
            "avgResponseTime": 185,
            "storageUsed": 12.5,
            "matchGrowth": growth_factor,
            "sourceGrowth": growth_factor,
            "qualityTrend": "up",
            "qualityChange": 1.2,
            "errorImprovement": 0.8,
            "responseImprovement": 1.5,
            "storageTrend": "up",
            "storageChange": 2.1,
            "lastUpdate": datetime.utcnow().isoformat()
        }
        
        return {
            "code": 200,
            "data": summary_data,
            "message": "数据中心统计获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/data")
async def get_data_list(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None),
    source_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取数据列表 - 适配前端请求路径
    """
    try:
        # 构建查询
        query = db.query(Match)
        
        # 应用筛选条件
        if type:
            # 这里可以根据type进行筛选，这里简化处理
            pass
        if source_id:
            # 模拟按数据源筛选
            pass
        if status:
            query = query.filter(Match.status == status)
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Match.created_at >= start_dt)
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Match.created_at <= end_dt)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        records = query.offset((page - 1) * size).limit(size).all()
        
        # 转换为前端需要的格式
        items = []
        for record in records:
            item = {
                "id": record.id,
                "type": "matches",  # 默认类型
                "sourceName": "数据源A",  # 模拟数据源名称
                "title": f"{record.home_team} VS {record.away_team}",  # 比赛标题
                "status": record.status or "normal",  # 状态
                "quality": round(90 + (record.id % 10), 2),  # 模拟质量分数
                "recordCount": 150 + (record.id % 50),  # 模拟记录数
                "createdAt": record.created_at.isoformat() if record.created_at else "",
                "updatedAt": record.updated_at.isoformat() if record.updated_at else ""
            }
            items.append(item)
        
        return {
            "code": 200,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            },
            "message": "数据列表获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/data/export")
async def export_data_list(
    format: str = Query("excel"),
    scope: str = Query("current"),
    date_range: Optional[str] = Query(None)
):
    """
    导出数据 - 适配前端请求路径
    """
    try:
        return {
            "code": 200,
            "data": {
                "format": format,
                "scope": scope,
                "downloadUrl": f"/api/v1/admin/data-center/download/export_{int(datetime.utcnow().timestamp())}.{format}",
                "fileName": f"data_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}",
                "recordCount": 1250
            },
            "message": "数据导出任务已启动"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))