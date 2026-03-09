"""
比赛管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date, timezone
import json

from ....api.deps import get_db
from ....models.match import Match, League, MatchStatusEnum
from ...deps import get_current_admin


# 由于无法确定确切的响应模型位置，此处临时定义所需的基础模型
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

router = APIRouter(prefix="/matches", tags=["admin-matches"])


@router.get("/stats", response_model=UnifiedResponse)
async def get_match_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取比赛统计数据
    """
    try:
        from sqlalchemy import select, func, and_
        from datetime import datetime, timedelta
        
        # 总比赛数
        total_matches_result = await db.execute(select(func.count(Match.id)))
        total_matches = total_matches_result.scalar()
        
        # 今日比赛数
        today = datetime.now().date()
        today_matches_result = await db.execute(
            select(func.count(Match.id)).where(
                func.date(Match.match_date) == today
            )
        )
        today_matches = today_matches_result.scalar()
        
        # 进行中比赛数
        live_matches_result = await db.execute(
            select(func.count(Match.id)).where(
                Match.status == MatchStatusEnum.LIVE
            )
        )
        live_matches = live_matches_result.scalar()
        
        # 已完成比赛数
        finished_matches_result = await db.execute(
            select(func.count(Match.id)).where(
                Match.status == MatchStatusEnum.FINISHED
            )
        )
        finished_matches = finished_matches_result.scalar()
        
        # 异常数据数（假设数据质量评分低于0.5为异常）
        anomaly_matches_result = await db.execute(
            select(func.count(Match.id)).where(
                Match.popularity_score < 0.5
            )
        )
        anomaly_count = anomaly_matches_result.scalar()
        
        # 联赛总数
        total_leagues_result = await db.execute(
            select(func.count(League.id))
        )
        total_leagues = total_leagues_result.scalar()
        
        stats = {
            "totalMatches": total_matches,
            "todayMatches": today_matches,
            "liveMatches": live_matches,
            "finishedMatches": finished_matches,
            "anomalyCount": anomaly_count,
            "totalLeagues": total_leagues
        }
        
        return UnifiedResponse.success(stats, "获取统计数据成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=UnifiedResponse)
async def get_matches(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    league_id: Optional[int] = Query(None, description="联赛ID筛选"),
    status: Optional[str] = Query(None, description="比赛状态筛选"),
    search_keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取比赛列表，支持分页、筛选和搜索
    """
    try:
        from sqlalchemy import select, and_, func
        
        # 构建查询条件
        conditions = []
        if league_id:
            conditions.append(Match.league_id == league_id)
        if status:
            conditions.append(Match.status == status)
        if search_keyword:
            search_filter = f"%{search_keyword}%"
            conditions.append(
                Match.home_team.has(Team.name.like(search_filter)) |
                Match.away_team.has(Team.name.like(search_filter))
            )
        
        # 查询比赛总数
        count_query = select(func.count(Match.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 查询比赛列表
        query = select(Match).where(and_(*conditions)).offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        matches = result.scalars().all()
        
        # 查询联赛名称
        league_ids = [match.league_id for match in matches]
        if league_ids:
            league_query = select(League).where(League.id.in_(league_ids))
            league_result = await db.execute(league_query)
            leagues_map = {league.id: league.name for league in league_result.scalars()}
        else:
            leagues_map = {}
        
        # 查询主客队名称
        team_ids = []
        for match in matches:
            team_ids.extend([match.home_team_id, match.away_team_id])
        if team_ids:
            team_query = select(Team).where(Team.id.in_(set(team_ids)))
            team_result = await db.execute(team_query)
            teams_map = {team.id: team.name for team in team_result.scalars()}
        else:
            teams_map = {}
        
        # 格式化返回数据
        formatted_matches = []
        for match in matches:
            formatted_matches.append({
                "id": match.id,
                "league_id": match.league_id,
                "league_name": leagues_map.get(match.league_id, "未知联赛"),
                "home_team": teams_map.get(match.home_team_id, "未知主队"),
                "away_team": teams_map.get(match.away_team_id, "未知客队"),
                "match_date": match.match_date.strftime('%Y-%m-%d') if match.match_date else None,
                "match_time": match.match_time.strftime('%H:%M') if match.match_time else None,
                "status": match.status.value if isinstance(match.status, MatchStatusEnum) else match.status,
                "score": f"{match.home_score}:{match.away_score}" if match.home_score is not None and match.away_score is not None else "",
                "data_quality": "high" if match.popularity_score and match.popularity_score >= 0.7 else ("medium" if match.popularity_score and match.popularity_score >= 0.4 else "low")
            })
        
        return UnifiedResponse.success({
            "items": formatted_matches,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }, "获取比赛列表成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{match_id}", response_model=UnifiedResponse)
async def get_match_by_id(
    match_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取比赛详情
    """
    try:
        from sqlalchemy import select
        
        result = await db.execute(
            select(Match)
            .where(Match.id == match_id)
        )
        match = result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        # 获取联赛和球队信息
        league_result = await db.execute(select(League).where(League.id == match.league_id))
        league = league_result.scalar_one_or_none()
        
        home_team_result = await db.execute(select(Team).where(Team.id == match.home_team_id))
        home_team = home_team_result.scalar_one_or_none()
        
        away_team_result = await db.execute(select(Team).where(Team.id == match.away_team_id))
        away_team = away_team_result.scalar_one_or_none()
        
        formatted_match = {
            "id": match.id,
            "league_id": match.league_id,
            "league_name": league.name if league else "未知联赛",
            "home_team_id": match.home_team_id,
            "home_team": home_team.name if home_team else "未知主队",
            "away_team_id": match.away_team_id,
            "away_team": away_team.name if away_team else "未知客队",
            "match_number": match.match_number,
            "match_day": match.match_day,
            "match_date": match.match_date.strftime('%Y-%m-%d') if match.match_date else None,
            "match_time": match.match_time.strftime('%H:%M') if match.match_time else None,
            "status": match.status.value if isinstance(match.status, MatchStatusEnum) else match.status,
            "match_type": match.match_type,
            "importance": match.importance,
            "venue_name": match.venue_name,
            "city": match.city,
            "country": match.country,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "home_score_ht": match.home_score_ht,
            "away_score_ht": match.away_score_ht,
            "referee": match.referee,
            "attendance": match.attendance,
            "weather_condition": match.weather_condition,
            "temperature": match.temperature,
            "humidity": match.humidity,
            "wind_speed": match.wind_speed,
            "odds_data": match.odds_data,
            "stats_data": match.stats_data,
            "prediction_data": match.prediction_data,
            "popularity_score": match.popularity_score,
            "tags": match.tags,
            "external_id": match.external_id,
            "external_source": match.external_source,
            "created_at": match.created_at.isoformat() if match.created_at else None,
            "updated_at": match.updated_at.isoformat() if match.updated_at else None
        }
        
        return UnifiedResponse.success(formatted_match, "获取比赛详情成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=UnifiedResponse)
async def create_match(
    league_id: int = Query(..., description="联赛ID"),
    home_team_id: int = Query(..., description="主队ID"),
    away_team_id: int = Query(..., description="客队ID"),
    match_date: str = Query(..., description="比赛日期(YYYY-MM-DD)"),
    match_time: str = Query(..., description="比赛时间(HH:MM)"),
    db: AsyncSession = Depends(get_db)
):
    """
    创建比赛
    """
    try:
        from sqlalchemy import select
        from datetime import datetime
        
        # 验证联赛和球队是否存在
        league_result = await db.execute(select(League).where(League.id == league_id))
        league = league_result.scalar_one_or_none()
        if not league:
            raise HTTPException(status_code=404, detail="联赛不存在")
        
        home_team_result = await db.execute(select(Team).where(Team.id == home_team_id))
        home_team = home_team_result.scalar_one_or_none()
        if not home_team:
            raise HTTPException(status_code=404, detail="主队不存在")
        
        away_team_result = await db.execute(select(Team).where(Team.id == away_team_id))
        away_team = away_team_result.scalar_one_or_none()
        if not away_team:
            raise HTTPException(status_code=404, detail="客队不存在")
        
        # 解析日期时间
        match_datetime = datetime.strptime(f"{match_date} {match_time}", "%Y-%m-%d %H:%M")
        
        # 创建比赛
        new_match = Match(
            league_id=league_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            match_date=match_datetime.date(),
            match_time=match_datetime.time(),
            status=MatchStatusEnum.UPCOMING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(new_match)
        await db.commit()
        await db.refresh(new_match)
        
        return UnifiedResponse.success({
            "id": new_match.id,
            "league_id": new_match.league_id,
            "home_team_id": new_match.home_team_id,
            "away_team_id": new_match.away_team_id,
            "match_date": new_match.match_date.strftime('%Y-%m-%d'),
            "match_time": new_match.match_time.strftime('%H:%M'),
            "status": new_match.status.value if isinstance(new_match.status, MatchStatusEnum) else new_match.status
        }, "比赛创建成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{match_id}", response_model=UnifiedResponse)
async def update_match(
    match_id: int,
    league_id: Optional[int] = Query(None, description="联赛ID"),
    home_team_id: Optional[int] = Query(None, description="主队ID"),
    away_team_id: Optional[int] = Query(None, description="客队ID"),
    match_date: Optional[str] = Query(None, description="比赛日期(YYYY-MM-DD)"),
    match_time: Optional[str] = Query(None, description="比赛时间(HH:MM)"),
    status: Optional[str] = Query(None, description="比赛状态"),
    home_score: Optional[int] = Query(None, ge=0, description="主队得分"),
    away_score: Optional[int] = Query(None, ge=0, description="客队得分"),
    db: AsyncSession = Depends(get_db)
):
    """
    更新比赛信息
    """
    try:
        from sqlalchemy import select
        from datetime import datetime
        
        result = await db.execute(select(Match).where(Match.id == match_id))
        match = result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        # 更新字段
        if league_id is not None:
            match.league_id = league_id
        if home_team_id is not None:
            match.home_team_id = home_team_id
        if away_team_id is not None:
            match.away_team_id = away_team_id
        if match_date is not None:
            match.match_date = datetime.strptime(match_date, "%Y-%m-%d").date()
        if match_time is not None:
            match.match_time = datetime.strptime(match_time, "%H:%M").time()
        if status is not None:
            match.status = status
        if home_score is not None:
            match.home_score = home_score
        if away_score is not None:
            match.away_score = away_score
            
        match.updated_at = datetime.now(timezone.utc)
        await db.commit()
        
        return UnifiedResponse.success({
            "id": match.id,
            "league_id": match.league_id,
            "home_team_id": match.home_team_id,
            "away_team_id": match.away_team_id,
            "match_date": match.match_date.strftime('%Y-%m-%d') if match.match_date else None,
            "match_time": match.match_time.strftime('%H:%M') if match.match_time else None,
            "status": match.status.value if isinstance(match.status, MatchStatusEnum) else match.status,
            "home_score": match.home_score,
            "away_score": match.away_score
        }, "比赛更新成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{match_id}", response_model=UnifiedResponse)
async def delete_match(
    match_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除比赛
    """
    try:
        from sqlalchemy import select
        
        result = await db.execute(select(Match).where(Match.id == match_id))
        match = result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        await db.delete(match)
        await db.commit()
        
        return UnifiedResponse.success({"id": match_id}, "比赛删除成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{match_id}/status", response_model=UnifiedResponse)
async def update_match_status(
    match_id: int,
    status: str = Query(..., description="新状态"),
    db: AsyncSession = Depends(get_db)
):
    """
    更新比赛状态
    """
    try:
        from sqlalchemy import select
        
        result = await db.execute(select(Match).where(Match.id == match_id))
        match = result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        old_status = match.status
        match.status = status
        match.updated_at = datetime.now(timezone.utc)
        await db.commit()
        
        return UnifiedResponse.success({
            "message": "比赛状态更新成功",
            "match_id": match_id,
            "old_status": str(old_status),
            "new_status": status
        })
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{match_id}/scores", response_model=UnifiedResponse)
async def update_match_scores(
    match_id: int,
    home_score: Optional[int] = Query(None, ge=0, description="主队得分"),
    away_score: Optional[int] = Query(None, ge=0, description="客队得分"),
    halftime_home_score: Optional[int] = Query(None, ge=0, description="半场主队得分"),
    halftime_away_score: Optional[int] = Query(None, ge=0, description="半场客队得分"),
    db: AsyncSession = Depends(get_db)
):
    """
    更新比赛分数
    """
    try:
        from sqlalchemy import select
        
        result = await db.execute(select(Match).where(Match.id == match_id))
        match = result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        # 更新比分信息
        if home_score is not None:
            match.home_score = home_score
        if away_score is not None:
            match.away_score = away_score
        if halftime_home_score is not None:
            match.home_score_ht = halftime_home_score
        if halftime_away_score is not None:
            match.away_score_ht = halftime_away_score
        
        match.updated_at = datetime.now(timezone.utc)
        await db.commit()
        
        return UnifiedResponse.success({
            "message": "比赛分数更新成功",
            "match_id": match_id,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "home_score_ht": match.home_score_ht,
            "away_score_ht": match.away_score_ht
        })
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{match_id}/cancel", response_model=UnifiedResponse)
async def cancel_match(
    match_id: int,
    reason: str = Query(..., min_length=1, max_length=200, description="取消原因"),
    db: AsyncSession = Depends(get_db)
):
    """
    取消比赛
    """
    try:
        from sqlalchemy import select
        
        result = await db.execute(select(Match).where(Match.id == match_id))
        match = result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        old_status = match.status
        match.status = "cancelled"
        match.updated_at = datetime.now(timezone.utc)
        
        # 保存取消原因到配置中
        if not match.config:
            match.config = {}
        match.config['cancellation_reason'] = reason
        
        await db.commit()
        
        return UnifiedResponse.success({
            "message": "比赛已取消",
            "match_id": match_id,
            "previous_status": str(old_status),
            "new_status": "cancelled",
            "cancellation_reason": reason
        })
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{match_id}/details", response_model=UnifiedResponse)
async def get_match_details(
    match_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取比赛详细信息
    """
    try:
        from sqlalchemy import select
        
        # 查询比赛及关联信息
        result = await db.execute(
            select(Match)
            .join(League, Match.league_id == League.id)
            .join(Team, Match.home_team_id == Team.id)
            .add_columns(League.name.label("league_name"))
            .add_columns(Team.name.label("home_team_name"))
            .where(Match.id == match_id)
        )
        row = result.first()
        
        if not row:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        match = row[0]
        league_name = row[1]
        home_team_name = row[2]
        
        # 获取客队名称
        away_team_result = await db.execute(
            select(Team.name).where(Team.id == match.away_team_id)
        )
        away_team_row = away_team_result.first()
        away_team_name = away_team_row[0] if away_team_row else "未知"
        
        # 构建返回数据
        match_detail = {
            "id": match.id,
            "match_number": match.match_number,
            "match_day": match.match_day,
            "match_date": match.match_date.isoformat() if match.match_date else None,
            "match_time": match.match_time.isoformat() if match.match_time else None,
            "status": str(match.status),
            "match_type": str(match.match_type),
            "importance": str(match.importance),
            "venue_name": match.venue_name,
            "city": match.city,
            "country": match.country,
            "home_team": {
                "id": match.home_team_id,
                "name": home_team_name
            },
            "away_team": {
                "id": match.away_team_id,
                "name": away_team_name
            },
            "league": {
                "id": match.league_id,
                "name": league_name
            },
            "score": {
                "home": match.home_score,
                "away": match.away_score,
                "home_ht": match.home_score_ht,
                "away_ht": match.away_score_ht
            },
            "referee": match.referee,
            "attendance": match.attendance,
            "weather_condition": match.weather_condition,
            "temperature": match.temperature,
            "humidity": match.humidity,
            "wind_speed": match.wind_speed,
            "odds_data": match.odds_data,
            "stats_data": match.stats_data,
            "prediction_data": match.prediction_data,
            "popularity_score": match.popularity_score,
            "tags": match.tags,
            "external_id": match.external_id,
            "external_source": match.external_source,
            "created_at": match.created_at.isoformat() if match.created_at else None,
            "updated_at": match.updated_at.isoformat() if match.updated_at else None
        }
        
        return UnifiedResponse.success(match_detail)
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
        
        result = await db.execute(select(League))
        leagues = result.scalars().all()
        
        formatted_leagues = [
            {
                "id": league.id,
                "name": league.name,
                "country": league.country
            }
            for league in leagues
        ]
        
        return UnifiedResponse.success(formatted_leagues, "获取联赛列表成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))