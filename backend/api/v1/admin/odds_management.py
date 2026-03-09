"""
赔率管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from ....database_async import get_async_db
from ....models.odds import Odds, Bookmaker
from ....models.match import Match
# from ....models.bookmaker import Bookmaker  # 此模块不存在
from ....models.odds import OddsProvider
from ...deps import get_current_admin


# 由于无法确定确切的响应模型位置，此处临时定义所需的基础模型
from pydantic import BaseModel

class UnifiedResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[Dict[str, Any]] = None

router = APIRouter(tags=["admin-odds"])


@router.get("/monitoring", response_model=UnifiedResponse)
async def get_odds_monitoring(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    league_id: Optional[int] = Query(None, description="联赛ID筛选"),
    date_from: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取赔率监控数据
    """
    try:
        from sqlalchemy import select, and_, func, desc
        
        # 构建查询条件
        conditions = []
        if league_id:
            conditions.append(Match.league_id == league_id)
        if date_from:
            from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
            conditions.append(Match.match_date >= from_date)
        if date_to:
            to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
            conditions.append(Match.match_date <= to_date)
        
        # 查询最新的赔率记录
        subquery = select(
            Odds.match_id,
            Odds.bookmaker_id,
            func.max(Odds.last_updated).label("max_update")
        ).group_by(Odds.match_id, Odds.bookmaker_id).subquery()

        query = (
            select(Odds)
            .join(subquery, and_(
                Odds.match_id == subquery.c.match_id,
                Odds.bookmaker_id == subquery.c.bookmaker_id,
                Odds.last_updated == subquery.c.max_update
            ))
            .join(Match, Odds.match_id == Match.id)
        )
        
        if conditions:
            query = query.where(and_(*conditions))
            
        query = query.offset((page - 1) * size).limit(size)
        
        result = await db.execute(query)
        odds_records = result.scalars().all()
        
        # 查询相关的比赛、庄家信息
        match_ids = [record.match_id for record in odds_records]
        bookmaker_ids = [record.bookmaker_id for record in odds_records]
        
        matches_query = select(Match).where(Match.id.in_(match_ids))
        matches_result = await db.execute(matches_query)
        matches_map = {match.id: match for match in matches_result.scalars()}
        
        bookmakers_query = select(Bookmaker).where(Bookmaker.id.in_(bookmaker_ids))
        bookmakers_result = await db.execute(bookmakers_query)
        bookmakers_map = {bm.id: bm for bm in bookmakers_result.scalars()}
        
        # 格式化返回数据
        formatted_odds = []
        for record in odds_records:
            match_obj = matches_map.get(record.match_id)
            bookmaker_obj = bookmakers_map.get(record.bookmaker_id)
            
            if match_obj and bookmaker_obj:
                formatted_odds.append({
                    "matchId": f"M{record.match_id}",
                    "homeTeam": match_obj.home_team.name if match_obj.home_team else "未知",
                    "awayTeam": match_obj.away_team.name if match_obj.away_team else "未知",
                    "league": match_obj.league.name if match_obj.league else "未知",
                    "odds": {
                        "win": record.home_win_odds,
                        "draw": record.draw_odds,
                        "lose": record.away_win_odds
                    },
                    "oddsChanged": {
                        "win": False,  # 简化处理，实际需要比较上次数据
                        "draw": False,
                        "lose": False
                    },
                    "lastUpdate": record.last_updated.strftime('%Y-%m-%d %H:%M:%S') if record.last_updated else ""
                })
        
        # 获取总数
        count_query = select(func.count(subquery.c.match_id))
        if conditions:
            count_query = count_query.select_from(
                subquery.join(Match, subquery.c.match_id == Match.id)
            ).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        return UnifiedResponse(
            success=True,
            data={
            "items": formatted_odds,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        },
            message="获取赔率监控数据成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=UnifiedResponse)
async def get_odds_history(
    match_id: int = Query(..., description="比赛ID"),
    time_from: Optional[str] = Query(None, description="开始时间(YYYY-MM-DD HH:MM:SS)"),
    time_to: Optional[str] = Query(None, description="结束时间(YYYY-MM-DD HH:MM:SS)"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取赔率历史数据
    """
    try:
        from sqlalchemy import select, and_, asc
        
        conditions = [Odds.match_id == match_id]
        if time_from:
            from_time = datetime.strptime(time_from, "%Y-%m-%d %H:%M:%S")
            conditions.append(Odds.last_updated >= from_time)
        if time_to:
            to_time = datetime.strptime(time_to, "%Y-%m-%d %H:%M:%S")
            conditions.append(Odds.last_updated <= to_time)
        
        query = select(Odds).where(and_(*conditions)).order_by(asc(Odds.last_updated))
        result = await db.execute(query)
        odds_records = result.scalars().all()
        
        # 计算变化
        formatted_history = []
        for i, record in enumerate(odds_records):
            prev_record = odds_records[i-1] if i > 0 else None
            change = 0.0
            
            if prev_record and record.home_win_odds and prev_record.home_win_odds:
                change = round(record.home_win_odds - prev_record.home_win_odds, 2)
            
            formatted_history.append({
                "timestamp": record.last_updated.strftime('%Y-%m-%d %H:%M:%S') if record.last_updated else "",
                "winOdds": record.home_win_odds,
                "drawOdds": record.draw_odds,
                "loseOdds": record.away_win_odds,
                "change": change
            })
        
        return UnifiedResponse(
            success=True,
            data={
            "items": formatted_history,
            "matchId": match_id
        },
            message="获取赔率历史数据成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies", response_model=UnifiedResponse)
async def get_anomaly_odds(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    anomaly_type: Optional[str] = Query(None, description="异常类型"),
    severity: Optional[str] = Query(None, description="严重程度"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取异常赔率数据
    """
    try:
        from sqlalchemy import select, func, desc
        
        # 这里为了演示，我们会查询最近的赔率变化较大的记录
        # 在实际应用中，这里应该是经过算法检测出的异常赔率
        query = (
            select(Odds, Match, Bookmaker)
            .join(Match, Odds.match_id == Match.id)
            .join(Bookmaker, Odds.bookmaker_id == Bookmaker.id)
            .order_by(desc(Odds.volatility))
            .offset((page - 1) * size)
            .limit(size)
        )
        
        result = await db.execute(query)
        records = result.fetchall()
        
        formatted_anomalies = []
        for record in records:
            odds, match, bookmaker = record
            formatted_anomalies.append({
                "id": f"A{odds.id}",
                "matchId": f"M{odds.match_id}",
                "homeTeam": match.home_team.name if match.home_team else "未知",
                "awayTeam": match.away_team.name if match.away_team else "未知",
                "type": "volatility_high" if odds.volatility > 0.1 else "sharp_change",
                "severity": "high" if odds.volatility > 0.15 else ("medium" if odds.volatility > 0.1 else "low"),
                "severityText": "高" if odds.volatility > 0.15 else ("中" if odds.volatility > 0.1 else "低"),
                "description": f"赔率波动值达到 {odds.volatility:.3f}",
                "detectedTime": odds.last_updated.strftime('%Y-%m-%d %H:%M:%S') if odds.last_updated else ""
            })
        
        # 获取总数
        count_query = select(func.count(Odds.id)).where(Odds.volatility > 0.05)
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        return UnifiedResponse(
            success=True,
            data={
            "items": formatted_anomalies,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        },
            message="获取异常赔率数据成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=UnifiedResponse)
async def get_odds_stats(
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取赔率统计数据
    """
    try:
        from sqlalchemy import select, func, desc
        from datetime import datetime, timedelta
        
        # 总赔率记录数
        total_odds_result = await db.execute(select(func.count(Odds.id)))
        total_odds = total_odds_result.scalar()
        
        # 获取最近一天的记录
        yesterday = datetime.now() - timedelta(days=1)
        
        # 监控比赛数（最近一天有更新的）
        recent_matches_result = await db.execute(
            select(func.count(func.distinct(Odds.match_id)))
            .where(Odds.last_updated >= yesterday)
        )
        monitored_matches = recent_matches_result.scalar()
        
        # 异常检测数（波动率大于阈值的）
        anomalies_result = await db.execute(
            select(func.count(Odds.id))
            .where(Odds.volatility > 0.1)  # 假设波动率大于0.1为异常
        )
        anomalies_detected = anomalies_result.scalar()
        
        # 今日变动比例
        changes_today_result = await db.execute(
            select(func.avg(Odds.volatility))
            .where(Odds.last_updated >= yesterday)
        )
        changes_today_avg = changes_today_result.scalar() or 0
        changes_today = round(changes_today_avg * 100, 1)
        
        stats = {
            "totalOdds": total_odds or 0,
            "monitoredMatches": monitored_matches or 0,
            "anomaliesDetected": anomalies_detected or 0,
            "changesToday": changes_today
        }
        
        return UnifiedResponse(
            success=True,
            data=stats,
            message="获取统计数据成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alert", response_model=UnifiedResponse)
async def set_odds_alert(
    match_id: int = Query(..., description="比赛ID"),
    bookmaker_id: int = Query(..., description="庄家ID"),
    threshold: float = Query(..., description="阈值"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    设置赔率提醒
    """
    try:
        # 这里只是模拟设置提醒，实际实现可能需要通知服务
        return UnifiedResponse(
            success=True,
            data={
                "match_id": match_id,
                "bookmaker_id": bookmaker_id,
                "threshold": threshold
            },
            message=f"?????? {match_id} ??????????????{threshold}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
