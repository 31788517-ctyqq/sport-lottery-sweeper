"""
比赛管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ....api.deps import get_db
from ....models.match import Match, League, Team, MatchStatusEnum


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

router = APIRouter()


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
        match.updated_at = datetime.utcnow()
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
        
        match.updated_at = datetime.utcnow()
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
        match.updated_at = datetime.utcnow()
        
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
            "match_time": match.match_time.isoformat() if match.match_time else None,
            "match_date": match.match_date.isoformat() if match.match_date else None,
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