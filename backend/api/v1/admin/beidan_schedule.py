"""
彩票赛程管理API端点
提供彩票赛程管理功能，遵循统一API设计原则
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, func, desc, asc
from datetime import datetime, timedelta
import logging

from ....database import get_db
from ....models.user import User
from ....models.match import Match, League, Team  # 修改导入路径
from ....schemas.response import UnifiedResponse, PageResponse
from ....schemas.match import MatchCreateUpdate, MatchFilter
from ....services.match_service import MatchService
# 修改logger导入
logger = logging.getLogger(__name__)

# 假设MatchStatusEnum是一个枚举类
from enum import Enum

class MatchStatusEnum(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    HALFTIME = "halftime"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"
    ABANDONED = "abandoned"
    SUSPENDED = "suspended"


router = APIRouter()

@router.get("/", response_model=PageResponse)
async def get_beidan_schedules(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    league_id: Optional[int] = Query(None, description="联赛ID筛选"),
    days: Optional[int] = Query(5, description="查询天数"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """
    获取北单赛程列表
    """
    try:
        from sqlalchemy import and_, or_
        
        # 构建查询条件
        conditions = []
        
        # 时间范围筛选
        if days:
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=days)
            # 假设Match模型有match_date字段
            from ....models.match import Match as MatchModel
            conditions.append(MatchModel.match_date.between(start_date, end_date))
        
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
        home_team = aliased(Team)
        away_team = aliased(Team)
        query = (
            select(Match, League, home_team, away_team)
            .join(League, Match.league_id == League.id)
            .join(home_team, Match.home_team_id == home_team.id, isouter=True)  # 左外连接主队
            .join(away_team, Match.away_team_id == away_team.id, isouter=True)  # 左外连接客队
            .where(and_(*conditions))
            .order_by(Match.scheduled_kickoff)
            .offset((page - 1) * size)
            .limit(size)
        )
        
        result = db.execute(query)
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
        total_result = db.execute(count_query)
        total = total_result.scalar()
        
        return PageResponse(
            code=200,
            message="OK",
            data=formatted_matches,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leagues", response_model=UnifiedResponse)
async def get_leagues(
    db: Session = Depends(get_db)
):
    """
    ??????
    """
    try:
        # ????
        query = select(League).where(League.is_active == True).order_by(League.name)
        result = db.execute(query)
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

        return UnifiedResponse(
            code=200,
            message="????????",
            data={
                "items": formatted_leagues
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{match_id}/publish", response_model=UnifiedResponse)
async def toggle_publish(
    match_id: int,
    publish: bool = Query(..., description="????"),
    db: Session = Depends(get_db)
):
    """
    ????????
    """
    try:
        # ????
        query = select(Match).where(Match.id == match_id)
        result = db.execute(query)
        match = result.scalar_one_or_none()

        if not match:
            raise HTTPException(status_code=404, detail="?????")

        # ??????
        match.is_published = publish
        db.commit()

        publish_message = "????" if match.is_published else "??????"
        return UnifiedResponse(
            code=200,
            message=publish_message,
            data={
                "id": match.id,
                "is_published": match.is_published
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{match_id}", response_model=UnifiedResponse)
async def delete_beidan_schedule(
    match_id: int,
    db: Session = Depends(get_db)
):
    """
    删除北单赛程
    """
    try:
        from sqlalchemy import delete
        
        # 检查比赛是否存在
        match_query = select(Match).where(Match.id == match_id)
        match_result = db.execute(match_query)
        match = match_result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        # 执行删除
        stmt = delete(Match).where(Match.id == match_id)
        db.execute(stmt)
        db.commit()
        
        return UnifiedResponse(
            code=200,
            message="????????",
            data={"id": match_id}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=UnifiedResponse)
async def get_beidan_stats(
    db: Session = Depends(get_db)
):
    """
    获取北单赛程统计数据
    """
    try:
        from sqlalchemy import case
        
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
        
        result = db.execute(stats_query)
        row = result.fetchone()
        
        stats = {
            "totalMatches": row.total_matches or 0,
            "scheduledMatches": row.scheduled_matches or 0,
            "liveMatches": row.live_matches or 0,
            "finishedMatches": row.finished_matches or 0,
            "publishedMatches": row.published_matches or 0
        }
        
        return UnifiedResponse(
            code=200,
            message="获取统计数据成功",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
