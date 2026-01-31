"""
竞彩赛程管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, date
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


class MatchCreateRequest(BaseModel):
    league_name: str
    home_team: str
    away_team: str
    match_time: str
    status: str
    score: Optional[str] = None


class MatchUpdateRequest(BaseModel):
    league_name: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    match_time: Optional[str] = None
    status: Optional[str] = None
    score: Optional[str] = None


router = APIRouter(prefix="/lottery-schedules", tags=["admin-lottery-schedules"])


@router.get("/", response_model=UnifiedResponse)
async def get_lottery_schedules(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    league_name: Optional[str] = Query(None, description="联赛名称筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    date_from: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取竞彩赛程列表
    """
    try:
        from sqlalchemy import select, and_, func, desc
        
        # 构建查询条件
        conditions = []
        if league_name:
            conditions.append(League.name.contains(league_name))
        if status:
            # 将前端状态映射到数据库状态
            status_mapping = {
                "pending": MatchStatusEnum.SCHEDULED.value,
                "running": MatchStatusEnum.LIVE.value,
                "finished": MatchStatusEnum.FINISHED.value,
                "cancelled": MatchStatusEnum.CANCELLED.value
            }
            if status in status_mapping:
                conditions.append(Match.status == status_mapping[status])
                
        if date_from:
            from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
            conditions.append(Match.match_date >= from_date)
        if date_to:
            to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
            conditions.append(Match.match_date <= to_date)
        
        # 查询匹配的比赛数据
        query = (
            select(Match, League, Team, Team)
            .join(League, Match.league_id == League.id)
            .join(Team, Match.home_team_id == Team.id, isouter=True)
            .join(Team, Match.away_team_id == Team.id, isouter=True)
            .where(and_(*conditions))
            .order_by(desc(Match.scheduled_kickoff))
            .offset((page - 1) * size)
            .limit(size)
        )
        
        result = await db.execute(query)
        matches = result.all()
        
        # 格式化返回数据
        formatted_matches = []
        for match_row in matches:
            match, league, home_team, away_team = match_row
            
            # 映射数据库状态到前端状态
            status_mapping = {
                MatchStatusEnum.SCHEDULED.value: "pending",
                MatchStatusEnum.LIVE.value: "running",
                MatchStatusEnum.FINISHED.value: "finished",
                MatchStatusEnum.CANCELLED.value: "cancelled",
                MatchStatusEnum.POSTPONED.value: "pending",
                MatchStatusEnum.ABANDONED.value: "cancelled",
                MatchStatusEnum.SUSPENDED.value: "cancelled",
                MatchStatusEnum.HALFTIME.value: "running"
            }
            
            formatted_match = {
                "id": match.id,
                "league_name": league.name,
                "home_team": home_team.name if home_team else "未知",
                "away_team": away_team.name if away_team else "未知",
                "match_time": match.scheduled_kickoff.strftime('%Y-%m-%d %H:%M:%S'),
                "status": status_mapping.get(match.status, "pending"),
                "score": f"{match.home_score}-{match.away_score}" if match.home_score is not None and match.away_score is not None else None
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
        }, "获取竞彩赛程列表成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=UnifiedResponse)
async def get_schedule_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取赛程统计数据
    """
    try:
        from sqlalchemy import select, func, case
        
        # 获取各种状态的比赛数量
        stats_query = select(
            func.count(Match.id).label('total_matches'),
            func.sum(case(
                (Match.status == MatchStatusEnum.SCHEDULED.value, 1),
                else_=0
            )).label('pending_matches'),
            func.sum(case(
                (Match.status.in_([MatchStatusEnum.LIVE.value, MatchStatusEnum.HALFTIME.value]), 1),
                else_=0
            )).label('running_matches'),
            func.sum(case(
                (Match.status == MatchStatusEnum.FINISHED.value, 1),
                else_=0
            )).label('finished_matches')
        )
        
        result = await db.execute(stats_query)
        row = result.fetchone()
        
        stats = {
            "totalMatches": row.total_matches or 0,
            "pendingMatches": row.pending_matches or 0,
            "runningMatches": row.running_matches or 0,
            "finishedMatches": row.finished_matches or 0
        }
        
        return UnifiedResponse.success(stats, "获取统计数据成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=UnifiedResponse)
async def create_lottery_schedule(
    request: MatchCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    创建竞彩赛程
    """
    try:
        from sqlalchemy import select
        
        # 查找或创建联赛
        league_query = select(League).where(League.name == request.league_name)
        league_result = await db.execute(league_query)
        league = league_result.scalar_one_or_none()
        
        if not league:
            # 如果联赛不存在，则创建一个
            from sqlalchemy.dialects.postgresql import insert
            league = League(
                name=request.league_name,
                code=request.league_name.lower().replace(" ", "_"),
                country="未知",
                country_code="UNKNOWN",
                type="league",
                is_active=True
            )
            db.add(league)
            await db.flush()  # 获取ID
        
        # 查找或创建主队
        home_team_query = select(Team).where(Team.name == request.home_team)
        home_team_result = await db.execute(home_team_query)
        home_team = home_team_result.scalar_one_or_none()
        
        if not home_team:
            home_team = Team(
                name=request.home_team,
                short_name=request.home_team[:10],
                code=request.home_team[:3].upper(),
                country="未知",
                country_code="UNKNOWN",
                is_active=True
            )
            db.add(home_team)
            await db.flush()  # 获取ID
        
        # 查找或创建客队
        away_team_query = select(Team).where(Team.name == request.away_team)
        away_team_result = await db.execute(away_team_query)
        away_team = away_team_result.scalar_one_or_none()
        
        if not away_team:
            away_team = Team(
                name=request.away_team,
                short_name=request.away_team[:10],
                code=request.away_team[:3].upper(),
                country="未知",
                country_code="UNKNOWN",
                is_active=True
            )
            db.add(away_team)
            await db.flush()  # 获取ID
        
        # 解析时间
        match_datetime = datetime.strptime(request.match_time, '%Y-%m-%d %H:%M:%S')
        match_date = match_datetime.date()
        match_time = match_datetime.time()
        
        # 状态映射
        status_mapping = {
            "pending": MatchStatusEnum.SCHEDULED.value,
            "running": MatchStatusEnum.LIVE.value,
            "finished": MatchStatusEnum.FINISHED.value,
            "cancelled": MatchStatusEnum.CANCELLED.value
        }
        
        # 创建比赛
        match = Match(
            league_id=league.id,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            match_date=match_date,
            match_time=match_time,
            scheduled_kickoff=match_datetime,
            status=status_mapping.get(request.status, MatchStatusEnum.SCHEDULED.value),
            is_published=True
        )
        
        # 如果有比分信息，解析比分
        if request.score:
            try:
                parts = request.score.split('-')
                if len(parts) == 2:
                    match.home_score = int(parts[0])
                    match.away_score = int(parts[1])
            except ValueError:
                pass  # 分数格式不正确则忽略
        
        db.add(match)
        await db.commit()
        await db.refresh(match)
        
        return UnifiedResponse.success({
            "id": match.id,
            "league_name": league.name,
            "home_team": home_team.name,
            "away_team": away_team.name,
            "match_time": match.scheduled_kickoff.strftime('%Y-%m-%d %H:%M:%S'),
            "status": request.status,
            "score": request.score
        }, "创建竞彩赛程成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建竞彩赛程失败: {str(e)}")


@router.put("/{match_id}", response_model=UnifiedResponse)
async def update_lottery_schedule(
    match_id: int,
    request: MatchUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    更新竞彩赛程
    """
    try:
        from sqlalchemy import select
        
        # 获取比赛
        match_query = select(Match).where(Match.id == match_id)
        match_result = await db.execute(match_query)
        match = match_result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        # 更新字段
        if request.league_name:
            league_query = select(League).where(League.name == request.league_name)
            league_result = await db.execute(league_query)
            league = league_result.scalar_one_or_none()
            
            if not league:
                # 如果联赛不存在，则创建一个
                league = League(
                    name=request.league_name,
                    code=request.league_name.lower().replace(" ", "_"),
                    country="未知",
                    country_code="UNKNOWN",
                    type="league",
                    is_active=True
                )
                db.add(league)
                await db.flush()
            
            match.league_id = league.id
        
        if request.home_team:
            home_team_query = select(Team).where(Team.name == request.home_team)
            home_team_result = await db.execute(home_team_query)
            home_team = home_team_result.scalar_one_or_none()
            
            if not home_team:
                home_team = Team(
                    name=request.home_team,
                    short_name=request.home_team[:10],
                    code=request.home_team[:3].upper(),
                    country="未知",
                    country_code="UNKNOWN",
                    is_active=True
                )
                db.add(home_team)
                await db.flush()
            
            match.home_team_id = home_team.id
        
        if request.away_team:
            away_team_query = select(Team).where(Team.name == request.away_team)
            away_team_result = await db.execute(away_team_query)
            away_team = away_team_result.scalar_one_or_none()
            
            if not away_team:
                away_team = Team(
                    name=request.away_team,
                    short_name=request.away_team[:10],
                    code=request.away_team[:3].upper(),
                    country="未知",
                    country_code="UNKNOWN",
                    is_active=True
                )
                db.add(away_team)
                await db.flush()
            
            match.away_team_id = away_team.id
        
        if request.match_time:
            match_datetime = datetime.strptime(request.match_time, '%Y-%m-%d %H:%M:%S')
            match.match_date = match_datetime.date()
            match.match_time = match_datetime.time()
            match.scheduled_kickoff = match_datetime
        
        if request.status:
            status_mapping = {
                "pending": MatchStatusEnum.SCHEDULED.value,
                "running": MatchStatusEnum.LIVE.value,
                "finished": MatchStatusEnum.FINISHED.value,
                "cancelled": MatchStatusEnum.CANCELLED.value
            }
            match.status = status_mapping.get(request.status, MatchStatusEnum.SCHEDULED.value)
        
        if request.score is not None:
            if request.score:  # 不为空的分数
                try:
                    parts = request.score.split('-')
                    if len(parts) == 2:
                        match.home_score = int(parts[0])
                        match.away_score = int(parts[1])
                except ValueError:
                    pass  # 分数格式不正确则忽略
            else:  # 空字符串则清空分数
                match.home_score = None
                match.away_score = None
        
        await db.commit()
        await db.refresh(match)
        
        # 获取关联的联赛和队伍信息
        league_query = select(League).where(League.id == match.league_id)
        league_result = await db.execute(league_query)
        league = league_result.scalar_one_or_none()
        
        home_team_query = select(Team).where(Team.id == match.home_team_id)
        home_team_result = await db.execute(home_team_query)
        home_team = home_team_result.scalar_one_or_none()
        
        away_team_query = select(Team).where(Team.id == match.away_team_id)
        away_team_result = await db.execute(away_team_query)
        away_team = away_team_result.scalar_one_or_none()
        
        # 状态反向映射
        reverse_status_mapping = {
            MatchStatusEnum.SCHEDULED.value: "pending",
            MatchStatusEnum.LIVE.value: "running",
            MatchStatusEnum.FINISHED.value: "finished",
            MatchStatusEnum.CANCELLED.value: "cancelled",
            MatchStatusEnum.POSTPONED.value: "pending",
            MatchStatusEnum.ABANDONED.value: "cancelled",
            MatchStatusEnum.SUSPENDED.value: "cancelled",
            MatchStatusEnum.HALFTIME.value: "running"
        }
        
        return UnifiedResponse.success({
            "id": match.id,
            "league_name": league.name if league else "未知",
            "home_team": home_team.name if home_team else "未知",
            "away_team": away_team.name if away_team else "未知",
            "match_time": match.scheduled_kickoff.strftime('%Y-%m-%d %H:%M:%S'),
            "status": reverse_status_mapping.get(match.status, "pending"),
            "score": f"{match.home_score}-{match.away_score}" if match.home_score is not None and match.away_score is not None else None
        }, "更新竞彩赛程成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新竞彩赛程失败: {str(e)}")


@router.delete("/{match_id}", response_model=UnifiedResponse)
async def delete_lottery_schedule(
    match_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除竞彩赛程
    """
    try:
        from sqlalchemy import select, delete
        
        # 检查比赛是否存在
        match_query = select(Match).where(Match.id == match_id)
        match_result = await db.execute(match_query)
        match = match_result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        # 检查比赛状态，只有未开始或已取消的比赛才能删除
        if match.status in [MatchStatusEnum.LIVE.value, MatchStatusEnum.HALFTIME.value]:
            raise HTTPException(status_code=400, detail="正在进行中的比赛不能删除")
        
        # 执行删除
        stmt = delete(Match).where(Match.id == match_id)
        await db.execute(stmt)
        await db.commit()
        
        return UnifiedResponse.success({"id": match_id}, "删除竞彩赛程成功")
    except HTTPException as he:
        raise he
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除竞彩赛程失败: {str(e)}")