"""
北单赛程管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from ....api.deps import get_db
from ....models.match import Match, MatchStatusEnum
from ....models.team import Team
from ....models.league import League
from ....schemas.match import MatchCreate, MatchUpdate, MatchResponse
from ....services.match_service import MatchService
from ...deps import get_current_admin

from pydantic import BaseModel


class UnifiedResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def success(cls, data: Any, message: str = "操作成功"):
        return cls(success=True, data=data, message=message)

    @classmethod
    def error(cls, message: str, error_code: Optional[str] = None):
        return cls(success=False, message=message, error={"code": error_code, "message": message})


router = APIRouter(prefix="/beidan-schedules", tags=["admin-beidan-schedules"])


@router.get("/", response_model=UnifiedResponse)
async def get_beidan_schedules(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    league_id: Optional[int] = Query(None, description="联赛ID筛选"),
    days: Optional[int] = Query(5, description="查询天数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取北单赛程列表
    """
    try:
        from sqlalchemy import select, and_, func, desc, or_
        
        # 构建查询条件
        conditions = []
        
        # 时间范围筛选
        if days:
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=days)
            conditions.append(Match.match_date.between(start_date, end_date))
        
        # 联赛筛选
        if league_id:
            conditions.append(Match.league_id == league_id)
        
        # 关键词搜索
        if keyword:
            conditions.append(or_(
                League.name.contains(keyword),
                Team.name.contains(keyword)
            ))
        
        # 查询匹配的北单比赛数据
        query = (
            select(Match, League, Team, Team)
            .join(League, Match.league_id == League.id)
            .join(Team, Match.home_team_id == Team.id, isouter=True)  # 左外连接主队
            .join(Team, Match.away_team_id == Team.id, isouter=True)  # 左外连接客队
            .where(and_(*conditions))
            .order_by(Match.scheduled_kickoff)
            .offset((page - 1) * size)
            .limit(size)
        )
        
        result = await db.execute(query)
        matches = result.all()
        
        # 格式化返回数据
        formatted_matches = []
        for match_row in matches:
            match, league, home_team, away_team = match_row
            
            # 状态映射
            status_mapping = {
                MatchStatusEnum.SCHEDULED.value: "scheduled",
                MatchStatusEnum.LIVE.value: "live",
                MatchStatusEnum.HALFTIME.value: "halftime",
                MatchStatusEnum.FINISHED.value: "finished",
                MatchStatusEnum.CANCELLED.value: "cancelled",
                MatchStatusEnum.POSTPONED.value: "postponed",
                MatchStatusEnum.ABANDONED.value: "abandoned",
                MatchStatusEnum.SUSPENDED.value: "suspended"
            }
            
            formatted_match = {
                "id": match.id,
                "match_identifier": match.match_identifier,
                "league_name": league.name if league else "未知联赛",
                "league_id": league.id if league else None,
                "scheduled_kickoff": match.scheduled_kickoff.strftime('%Y-%m-%d %H:%M:%S') if match.scheduled_kickoff else None,
                "home_team": home_team.name if home_team else "未知主队",
                "away_team": away_team.name if away_team else "未知客队",
                "status": status_mapping.get(match.status, "scheduled"),
                "match_date": match.match_date.isoformat() if match.match_date else None,
                "is_published": match.is_published
            }
            formatted_matches.append(formatted_match)
        
        # 获取总数
        count_query = (
            select(func.count(Match.id))
            .join(League, Match.league_id == League.id)
            .where(and_(*conditions))
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        return UnifiedResponse.success({
            "items": formatted_matches,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }, "获取北单赛程列表成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leagues", response_model=UnifiedResponse)
async def get_leagues(
    db: AsyncSession = Depends(get_db)
):
    """
    获取联赛列表
    """
    try:
        from sqlalchemy import select
        
        query = select(League).where(League.is_active == True).order_by(League.name)
        result = await db.execute(query)
        leagues = result.scalars().all()
        
        formatted_leagues = [
            {
                "id": league.id,
                "name": league.name,
                "code": league.code,
                "country": league.country
            }
            for league in leagues
        ]
        
        return UnifiedResponse.success({
            "items": formatted_leagues
        }, "获取联赛列表成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{match_id}/publish", response_model=UnifiedResponse)
async def toggle_publish(
    match_id: int,
    publish: bool = Query(..., description="是否发布"),
    db: AsyncSession = Depends(get_db)
):
    """
    切换比赛发布状态
    """
    try:
        from sqlalchemy import select
        
        # 获取比赛
        query = select(Match).where(Match.id == match_id)
        result = await db.execute(query)
        match = result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        # 更新发布状态
        match.is_published = publish
        await db.commit()
        
        return UnifiedResponse.success({
            "id": match.id,
            "is_published": match.is_published
        }, f"{'发布' if match.is_published else '取消发布'}成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{match_id}", response_model=UnifiedResponse)
async def delete_beidan_schedule(
    match_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除北单赛程
    """
    try:
        from sqlalchemy import select, delete
        
        # 检查比赛是否存在
        match_query = select(Match).where(Match.id == match_id)
        match_result = await db.execute(match_query)
        match = match_result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        # 执行删除
        stmt = delete(Match).where(Match.id == match_id)
        await db.execute(stmt)
        await db.commit()
        
        return UnifiedResponse.success({"id": match_id}, "删除北单赛程成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=UnifiedResponse)
async def get_beidan_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取北单赛程统计数据
    """
    try:
        from sqlalchemy import select, func, case
        
        # 获取各种状态的比赛数量
        stats_query = select(
            func.count(Match.id).label('total_matches'),
            func.sum(case(
                (Match.status == MatchStatusEnum.SCHEDULED.value, 1),
                else_=0
            )).label('scheduled_matches'),
            func.sum(case(
                (Match.status.in_([MatchStatusEnum.LIVE.value, MatchStatusEnum.HALFTIME.value]), 1),
                else_=0
            )).label('live_matches'),
            func.sum(case(
                (Match.status == MatchStatusEnum.FINISHED.value, 1),
                else_=0
            )).label('finished_matches'),
            func.sum(case(
                (Match.is_published == True, 1),
                else_=0
            )).label('published_matches')
        )
        
        result = await db.execute(stats_query)
        row = result.fetchone()
        
        stats = {
            "totalMatches": row.total_matches or 0,
            "scheduledMatches": row.scheduled_matches or 0,
            "liveMatches": row.live_matches or 0,
            "finishedMatches": row.finished_matches or 0,
            "publishedMatches": row.published_matches or 0
        }
        
        return UnifiedResponse.success(stats, "获取统计数据成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))