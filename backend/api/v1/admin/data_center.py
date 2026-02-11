"""
数据中心API
提供数据统计、分析等功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.matches import FootballMatch as Match
from backend.models.odds_companies import OddsCompany as Odds  # 使用正确的Odds模型
from backend.models.data_sources import DataSource
from backend.models.sp_records import SPRecord

router = APIRouter()

@router.get("/data-center/overview")
async def get_data_center_overview(
    db: Session = Depends(get_db)
):
    """
    获取数据中心总览数据
    """
    try:
        # 获取各类数据的统计
        total_matches = db.query(Match).count()
        total_odds = db.query(Odds).count()
        total_sp_records = db.query(SPRecord).count()
        active_sources = db.query(DataSource).filter(DataSource.status == True).count()
        
        # 计算今天新增的数据
        today = datetime.utcnow().date()
        today_matches = db.query(Match).filter(
            Match.created_at >= today
        ).count()
        
        overview_data = {
            "totalMatches": total_matches,
            "totalOdds": total_odds,
            "totalSPRecords": total_sp_records,
            "activeSources": active_sources,
            "todayNewData": today_matches,
            "lastUpdate": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": overview_data,
            "message": "数据中心总览获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-center/data-trend")
async def get_data_trend(
    days: int = Query(30, description="获取过去多少天的数据"),
    db: Session = Depends(get_db)
):
    """
    获取数据趋势（按天统计）
    """
    try:
        # 计算日期范围
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 模拟数据趋势
        trends = []
        current_date = start_date
        base_value = 100
        
        while current_date <= end_date:
            trend = {
                "date": current_date.isoformat(),
                "matches": base_value + (current_date.day % 5) * 10,
                "odds": (base_value + (current_date.day % 5) * 10) * 2,
                "sp_records": (base_value + (current_date.day % 5) * 10) * 3
            }
            trends.append(trend)
            current_date += timedelta(days=1)
            base_value += 5  # 模拟增长趋势
        
        return {
            "success": True,
            "data": {
                "trends": trends,
                "summary": {
                    "totalTrendPoints": len(trends),
                    "startDate": start_date.isoformat(),
                    "endDate": end_date.isoformat()
                }
            },
            "message": "数据趋势获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-center/data-sources")
async def get_data_sources_stats(
    db: Session = Depends(get_db)
):
    """
    获取各数据源的数据统计
    """
    try:
        # 获取所有数据源
        sources = db.query(DataSource).all()
        
        source_stats = []
        for source in sources:
            # 这里应该根据实际的数据关联关系统计每个数据源的数据量
            # 模拟数据
            stat = {
                "id": source.id,
                "name": source.name,
                "type": source.type,
                "status": "active" if source.status else "inactive",
                "dataCount": 120 + source.id * 10,  # 模拟数据量
                "successRate": round(95.0 + source.id * 0.5, 2),  # 模拟成功率
                "lastUpdate": (datetime.utcnow() - timedelta(hours=source.id)).isoformat()
            }
            source_stats.append(stat)
        
        return {
            "success": True,
            "data": {
                "sources": source_stats,
                "summary": {
                    "totalCount": len(source_stats),
                    "activeCount": len([s for s in source_stats if s["status"] == "active"])
                }
            },
            "message": "数据源统计获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-center/detail-data")
async def get_detail_data(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    data_type: Optional[str] = Query(None, description="match, odds, sp_record"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """
    获取详细数据列表
    """
    try:
        # 根据数据类型查询不同的表
        if data_type == "match":
            query = db.query(Match)
            if search:
                query = query.filter(Match.home_team.contains(search) | Match.away_team.contains(search))
            
            total = query.count()
            records = query.offset((page - 1) * size).limit(size).all()
            
            # 转换为字典格式
            items = []
            for record in records:
                item = {
                    "id": record.id,
                    "homeTeam": record.home_team,
                    "awayTeam": record.away_team,
                    "matchTime": record.match_time.isoformat() if record.match_time else None,
                    "league": record.league,
                    "status": record.status,
                    "createdAt": record.created_at.isoformat() if record.created_at else None
                }
                items.append(item)
                
        elif data_type == "odds":
            query = db.query(Odds)
            if search:
                query = query.join(Match).filter(
                    Match.home_team.contains(search) | Match.away_team.contains(search)
                )
            
            total = query.count()
            records = query.offset((page - 1) * size).limit(size).all()
            
            items = []
            for record in records:
                item = {
                    "id": record.id,
                    "matchId": record.match_id,
                    "homeWin": record.home_win_odds,
                    "draw": record.draw_odds,
                    "awayWin": record.away_win_odds,
                    "companyId": record.bookmaker_id,
                    "createdAt": record.created_at.isoformat() if record.created_at else None
                }
                items.append(item)
                
        elif data_type == "sp_record":
            query = db.query(SPRecord)
            if search:
                query = query.join(Match).filter(
                    Match.home_team.contains(search) | Match.away_team.contains(search)
                )
            
            total = query.count()
            records = query.offset((page - 1) * size).limit(size).all()
            
            items = []
            for record in records:
                item = {
                    "id": record.id,
                    "matchId": record.match_id,
                    "playType": record.play_type,
                    "betType": record.bet_type,
                    "spValue": float(record.sp_value) if record.sp_value else 0,
                    "createdAt": record.created_at.isoformat() if record.created_at else None
                }
                items.append(item)
        else:
            # 默认返回比赛数据
            query = db.query(Match)
            if search:
                query = query.filter(Match.home_team.contains(search) | Match.away_team.contains(search))
            
            total = query.count()
            records = query.offset((page - 1) * size).limit(size).all()
            
            items = []
            for record in records:
                item = {
                    "id": record.id,
                    "homeTeam": record.home_team,
                    "awayTeam": record.away_team,
                    "matchTime": record.match_time.isoformat() if record.match_time else None,
                    "league": record.league,
                    "status": record.status,
                    "createdAt": record.created_at.isoformat() if record.created_at else None
                }
                items.append(item)
        
        return {
            "success": True,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            },
            "message": "详细数据获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-center/export-data")
async def export_data(
    data_type: str = Query(..., description="match, odds, sp_record"),
    format: str = Query("json", description="json, csv, excel"),
    db: Session = Depends(get_db)
):
    """
    导出数据
    """
    try:
        # 这里应该实现实际的数据导出逻辑
        # 模拟导出过程
        export_result = {
            "success": True,
            "data": {
                "exportType": data_type,
                "format": format,
                "downloadUrl": f"/api/v1/admin/data-center/download/{data_type}_export_{int(datetime.utcnow().timestamp())}.{format}",
                "fileName": f"{data_type}_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}",
                "recordCount": 1250  # 模拟导出的记录数
            },
            "message": "数据导出任务已启动"
        }
        
        return export_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))