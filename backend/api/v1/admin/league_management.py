"""
联赛管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from ....api.deps import get_db
from ....models.match import League, Match
from ....models.team import Team
from ....schemas.match import LeagueCreate, LeagueUpdate, LeagueResponse
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


class LeagueCreateRequest(BaseModel):
    name: str
    country: str
    level: int
    season: str
    status: str
    description: Optional[str] = None


class LeagueUpdateRequest(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    level: Optional[int] = None
    season: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None


router = APIRouter(prefix="/leagues", tags=["admin-leagues"])


@router.get("/", response_model=UnifiedResponse)
async def get_leagues(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    country: Optional[str] = Query(None, description="国家/地区筛选"),
    level: Optional[str] = Query(None, description="联赛级别筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    search_keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取联赛列表
    """
    try:
        from sqlalchemy import select, and_, func, desc, or_
        
        # 构建查询条件
        conditions = []
        
        # 国家筛选
        if country:
            conditions.append(League.country == country)
        
        # 级别筛选
        if level:
            level_mapping = {
                "top": 1,
                "second": 2,
                "youth": 3,
                "women": 4
            }
            if level in level_mapping:
                conditions.append(League.level == level_mapping[level])
        
        # 状态筛选
        if status:
            status_mapping = {
                "active": True,
                "inactive": False,
                "completed": False
            }
            if status in status_mapping:
                conditions.append(League.is_active == status_mapping[status])
        
        # 搜索关键词
        if search_keyword:
            conditions.append(League.name.contains(search_keyword))
        
        # 查询匹配的联赛数据
        query = (
            select(League)
            .where(and_(*conditions))
            .order_by(League.name)
            .offset((page - 1) * size)
            .limit(size)
        )
        
        result = await db.execute(query)
        leagues = result.scalars().all()
        
        # 获取联赛相关的比赛统计信息
        league_ids = [league.id for league in leagues]
        if league_ids:
            matches_query = (
                select(
                    Match.league_id,
                    func.count(Match.id).label('total_matches'),
                    func.sum(case((Match.status == "finished", 1), else_=0)).label('played_matches')
                )
                .where(Match.league_id.in_(league_ids))
                .group_by(Match.league_id)
            )
            matches_result = await db.execute(matches_query)
            matches_stats = {row.league_id: {"total_matches": row.total_matches, "played_matches": row.played_matches or 0} 
                            for row in matches_result.fetchall()}
        else:
            matches_stats = {}
        
        # 格式化返回数据
        formatted_leagues = []
        for league in leagues:
            matches_info = matches_stats.get(league.id, {"total_matches": 0, "played_matches": 0})
            total_matches = matches_info["total_matches"]
            played_matches = matches_info["played_matches"]
            remaining_matches = total_matches - played_matches
            
            # 级别映射
            level_mapping_reverse = {
                1: "top",
                2: "second", 
                3: "youth",
                4: "women"
            }
            
            # 状态映射
            status_mapping_reverse = {
                True: "active",
                False: "inactive"
            }
            
            formatted_league = {
                "id": league.id,
                "name": league.name,
                "country": league.country,
                "level": level_mapping_reverse.get(league.level, "top"),
                "season": league.current_season or "未知",
                "total_matches": total_matches,
                "played_matches": played_matches,
                "remaining_matches": remaining_matches,
                "status": status_mapping_reverse.get(league.is_active, "inactive"),
                "description": league.description or ""
            }
            formatted_leagues.append(formatted_league)
        
        # 获取总数
        count_query = select(func.count(League.id)).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        return UnifiedResponse.success({
            "items": formatted_leagues,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }, "获取联赛列表成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=UnifiedResponse)
async def create_league(
    request: LeagueCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    创建联赛
    """
    try:
        from sqlalchemy import select
        
        # 检查联赛是否已存在
        check_query = select(League).where(League.name == request.name)
        check_result = await db.execute(check_query)
        existing_league = check_result.scalar_one_or_none()
        
        if existing_league:
            raise HTTPException(status_code=400, detail="联赛已存在")
        
        # 级别映射
        level_mapping = {
            "top": 1,
            "second": 2,
            "youth": 3,
            "women": 4
        }
        
        # 状态映射
        status_mapping = {
            "active": True,
            "inactive": False,
            "completed": False
        }
        
        # 创建联赛
        league = League(
            name=request.name,
            code=request.name.lower().replace(" ", "_").replace("-", "_"),
            short_name=request.name[:10],
            country=request.country,
            country_code=request.country[:3].upper(),
            level=level_mapping.get(request.level, 1),
            type="league",
            current_season=request.season,
            is_active=status_mapping.get(request.status, True),
            description=request.description
        )
        
        db.add(league)
        await db.commit()
        await db.refresh(league)
        
        return UnifiedResponse.success({
            "id": league.id,
            "name": league.name,
            "country": league.country,
            "level": request.level,
            "season": request.season,
            "status": request.status,
            "description": request.description
        }, "创建联赛成功")
    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建联赛失败: {str(e)}")


@router.put("/{league_id}", response_model=UnifiedResponse)
async def update_league(
    league_id: int,
    request: LeagueUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    更新联赛
    """
    try:
        from sqlalchemy import select
        
        # 获取联赛
        league_query = select(League).where(League.id == league_id)
        league_result = await db.execute(league_query)
        league = league_result.scalar_one_or_none()
        
        if not league:
            raise HTTPException(status_code=404, detail="联赛不存在")
        
        # 更新字段
        if request.name is not None:
            league.name = request.name
        if request.country is not None:
            league.country = request.country
        if request.level is not None:
            level_mapping = {
                "top": 1,
                "second": 2,
                "youth": 3,
                "women": 4
            }
            league.level = level_mapping.get(request.level, 1)
        if request.season is not None:
            league.current_season = request.season
        if request.status is not None:
            status_mapping = {
                "active": True,
                "inactive": False,
                "completed": False
            }
            league.is_active = status_mapping.get(request.status, False)
        if request.description is not None:
            league.description = request.description
        
        await db.commit()
        await db.refresh(league)
        
        # 级别映射
        level_mapping_reverse = {
            1: "top",
            2: "second", 
            3: "youth",
            4: "women"
        }
        
        # 状态映射
        status_mapping_reverse = {
            True: "active",
            False: "inactive"
        }
        
        return UnifiedResponse.success({
            "id": league.id,
            "name": league.name,
            "country": league.country,
            "level": level_mapping_reverse.get(league.level, "top"),
            "season": league.current_season or "未知",
            "status": status_mapping_reverse.get(league.is_active, "inactive"),
            "description": league.description or ""
        }, "更新联赛成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新联赛失败: {str(e)}")


@router.delete("/{league_id}", response_model=UnifiedResponse)
async def delete_league(
    league_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除联赛
    """
    try:
        from sqlalchemy import select, delete
        
        # 检查联赛是否存在
        league_query = select(League).where(League.id == league_id)
        league_result = await db.execute(league_query)
        league = league_result.scalar_one_or_none()
        
        if not league:
            raise HTTPException(status_code=404, detail="联赛不存在")
        
        # 检查是否有相关比赛数据，如果有则不允许删除
        match_query = select(Match).where(Match.league_id == league_id)
        match_result = await db.execute(match_query)
        matches = match_result.scalars().all()
        
        if matches:
            raise HTTPException(status_code=400, detail="联赛有关联的比赛数据，无法删除")
        
        # 执行删除
        stmt = delete(League).where(League.id == league_id)
        await db.execute(stmt)
        await db.commit()
        
        return UnifiedResponse.success({"id": league_id}, "删除联赛成功")
    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除联赛失败: {str(e)}")


@router.get("/countries", response_model=UnifiedResponse)
async def get_countries(
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有国家/地区列表
    """
    try:
        from sqlalchemy import select, distinct
        
        query = select(distinct(League.country)).where(League.is_active == True)
        result = await db.execute(query)
        countries = [row[0] for row in result.fetchall() if row[0]]
        
        return UnifiedResponse.success({
            "countries": countries
        }, "获取国家/地区列表成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=UnifiedResponse)
async def get_league_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取联赛统计数据
    """
    try:
        from sqlalchemy import select, func, case
        
        # 获取各种统计信息
        stats_query = select(
            func.count(League.id).label('total_leagues'),
            func.count(distinct(League.country)).label('total_countries'),
            func.sum(League.total_teams).label('total_teams'),
            func.sum(League.total_matches).label('total_matches'),
            func.sum(case(
                (League.is_active == True, 1),
                else_=0
            )).label('active_leagues')
        )
        
        result = await db.execute(stats_query)
        row = result.fetchone()
        
        # 计算比赛完成率
        matches_stats_query = select(
            func.sum(case((Match.status == "finished", 1), else_=0)).label('finished_matches'),
            func.count(Match.id).label('total_match_records')
        )
        matches_result = await db.execute(matches_stats_query)
        matches_row = matches_result.fetchone()
        
        finished_matches = matches_row.finished_matches or 0
        total_match_records = matches_row.total_match_records or 1  # 避免除零
        
        completion_rate = (finished_matches / total_match_records) * 100 if total_match_records > 0 else 0
        
        stats = {
            "totalLeagues": row.total_leagues or 0,
            "totalCountries": row.total_countries or 0,
            "activeLeagues": row.active_leagues or 0,
            "totalTeams": row.total_teams or 0,
            "totalMatches": row.total_matches or 0,
            "completionRate": round(completion_rate, 1)
        }
        
        return UnifiedResponse.success(stats, "获取统计数据成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))