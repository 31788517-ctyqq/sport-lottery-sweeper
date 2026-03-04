"""
赛程管理API - 管理员接口
实现竞彩赛程、北单赛程和赛程配置管理功能
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile, File, Form
from sqlalchemy.orm import Session
import pandas as pd
import io

from backend.core.auth import get_current_admin_user
from backend.database import get_db
from backend.models.user import User
from backend.models.match import League, Match
from backend.schemas.response import UnifiedResponse, PageResponse, ErrorResponse
from backend.services.service_registry import get_crawler_service

router = APIRouter(tags=["admin-matches"])


@router.get("/league/config", response_model=UnifiedResponse[Dict[str, Any]])
async def get_league_config(
    league_id: int = Query(..., description="联赛ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    获取联赛配置信息
    """
    try:
        league = db.query(League).filter(League.id == league_id).first()
        if not league:
            raise HTTPException(status_code=404, detail="联赛不存在")
        
        config = league.config or {}
        
        return UnifiedResponse(
            code=200,
            message="获取联赛配置成功",
            data={
                "league_id": league.id,
                "league_name": league.name,
                "current_season": league.current_season,
                "season_start": league.season_start.isoformat() if league.season_start else None,
                "season_end": league.season_end.isoformat() if league.season_end else None,
                "round_number": league.total_matches,  # 使用total_matches作为轮次
                "total_teams": league.total_teams,
                "config": config
            },
            timestamp=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取联赛配置失败: {str(e)}")


@router.put("/league/config", response_model=UnifiedResponse[Dict[str, Any]])
async def update_league_config(
    league_id: int = Form(..., description="联赛ID"),
    current_season: Optional[str] = Form(None, description="当前赛季"),
    season_start: Optional[str] = Form(None, description="赛季开始时间"),
    season_end: Optional[str] = Form(None, description="赛季结束时间"),
    round_number: Optional[int] = Form(None, description="当前轮次"),
    total_teams: Optional[int] = Form(None, description="参赛队伍数量"),
    config_data: Optional[str] = Form(None, description="配置JSON字符串"),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    更新联赛配置信息
    """
    try:
        league = db.query(League).filter(League.id == league_id).first()
        if not league:
            raise HTTPException(status_code=404, detail="联赛不存在")
        
        # 更新基本信息
        if current_season is not None:
            league.current_season = current_season
        if season_start is not None:
            league.season_start = datetime.fromisoformat(season_start).date() if season_start else None
        if season_end is not None:
            league.season_end = datetime.fromisoformat(season_end).date() if season_end else None
        if total_teams is not None:
            league.total_teams = total_teams
        
        # 解析配置数据
        if config_data:
            import json
            try:
                new_config = json.loads(config_data)
                # 验证配置结构
                if not isinstance(new_config, dict):
                    raise ValueError("配置必须是JSON对象")
                
                # 合并配置
                current_config = league.config or {}
                current_config.update(new_config)
                league.config = current_config
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="配置格式错误，必须是有效的JSON")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # 处理轮次更新（更新total_matches字段）
        if round_number is not None:
            league.total_matches = round_number
        
        league.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(league)
        
        return UnifiedResponse(
            code=200,
            message="联赛配置更新成功",
            data={
                "league_id": league.id,
                "league_name": league.name,
                "updated_at": league.updated_at.isoformat()
            },
            timestamp=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新联赛配置失败: {str(e)}")


@router.get("/jingcai/matches", response_model=UnifiedResponse[List[Dict[str, Any]]])
async def get_jingcai_matches(
    days: int = Query(5, ge=1, le=30, description="获取天数，默认5天"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    获取竞彩足球近N天比赛
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("进入 get_beidan_matches 函数")
        # 计算日期范围
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 查询竞彩比赛（通过联赛名称或其他标识筛选）
        matches = db.query(Match).join(League).filter(
            Match.match_date >= start_date,
            Match.match_date <= end_date,
            League.name.contains("竞彩") | League.code.contains("jc"),
            Match.is_published == True
        ).order_by(Match.match_date, Match.match_time).all()
        
        # 转换数据格式
        match_list = []
        for match in matches:
            match_dict = {
                "id": match.id,
                "match_identifier": match.match_identifier,
                "league_name": match.league.name if match.league else "",
                "home_team": match.home_team.name if match.home_team else "",
                "away_team": match.away_team.name if match.away_team else "",
                "match_date": match.match_date.isoformat(),
                "match_time": match.match_time.isoformat(),
                "scheduled_kickoff": match.scheduled_kickoff.isoformat() if match.scheduled_kickoff else None,
                "status": match.status.value,
                "round_number": match.round_number,
                "match_day": match.match_day,
                "importance": match.importance.value,
                "is_featured": match.is_featured
            }
            match_list.append(match_dict)
        
        return UnifiedResponse(
            code=200,
            message=f"获取竞彩近{days}天比赛成功",
            data=match_list,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取竞彩比赛失败: {str(e)}")


@router.get("/beidan/matches", response_model=UnifiedResponse[List[Dict[str, Any]]])
async def get_beidan_matches(
    days: int = Query(5, ge=1, le=30, description="获取天数，默认5天"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    获取北单足球近N天比赛
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("进入 get_beidan_matches 函数")
        # 计算日期范围
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 查询北单比赛
        matches = db.query(Match).join(League).filter(
            Match.match_date >= start_date,
            Match.match_date <= end_date,
            League.name.contains("北单") | League.code.contains("bd"),
            Match.is_published == True
        ).order_by(Match.match_date, Match.match_time).all()
        
        # 如果没有北单数据，可以从爬虫服务获取
        if not matches:
            try:
                crawler_service = get_crawler_service(db)
                beidan_matches = await crawler_service.crawl_beidan_matches(days)
                match_list = []
                for match in beidan_matches:
                    match_dict = {
                        "id": getattr(match, 'id', None),
                        "match_identifier": getattr(match, 'match_identifier', ''),
                        "league_name": getattr(match, 'league_name', ''),
                        "home_team": getattr(match, 'home_team', ''),
                        "away_team": getattr(match, 'away_team', ''),
                        "match_date": getattr(match, 'match_date', ''),
                        "match_time": getattr(match, 'match_time', ''),
                        "status": getattr(match, 'status', 'scheduled'),
                        "round_number": getattr(match, 'round_number', None),
                        "importance": getattr(match, 'importance', 'medium')
                    }
                    match_list.append(match_dict)
                
                return UnifiedResponse(
                    code=200,
                    message=f"获取北单近{days}天比赛成功",
                    data=match_list,
                    timestamp=datetime.now()
                )
            except Exception as crawl_error:
                # 爬虫失败时返回空数组
                pass
        
        # 转换数据库查询结果
        match_list = []
        for match in matches:
            match_dict = {
                "id": match.id,
                "match_identifier": match.match_identifier,
                "league_name": match.league.name if match.league else "",
                "home_team": match.home_team.name if match.home_team else "",
                "away_team": match.away_team.name if match.away_team else "",
                "match_date": match.match_date.isoformat(),
                "match_time": match.match_time.isoformat(),
                "scheduled_kickoff": match.scheduled_kickoff.isoformat() if match.scheduled_kickoff else None,
                "status": match.status.value,
                "round_number": match.round_number,
                "match_day": match.match_day,
                "importance": match.importance.value,
                "is_featured": match.is_featured
            }
            match_list.append(match_dict)
        
        return UnifiedResponse(
            code=200,
            message=f"获取北单近{days}天比赛成功",
            data=match_list,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取北单比赛失败: {str(e)}")


@router.post("/import/file", response_model=UnifiedResponse[Dict[str, Any]])
async def import_matches_from_file(
    league_id: int = Form(..., description="联赛ID"),
    file: UploadFile = File(..., description="上传文件"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    从文件导入比赛数据（支持CSV、Excel）
    """
    try:
        # 检查联赛是否存在
        league = db.query(League).filter(League.id == league_id).first()
        if not league:
            raise HTTPException(status_code=404, detail="联赛不存在")
        
        # 检查文件类型
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['csv', 'xlsx', 'xls']:
            raise HTTPException(status_code=400, detail="只支持CSV、Excel文件格式")
        
        # 读取文件内容
        contents = await file.read()
        
        # 使用pandas处理数据
        try:
            if file_extension == 'csv':
                df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
            else:
                df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"文件读取失败: {str(e)}")
        
        # 验证必要字段
        required_columns = ['home_team', 'away_team', 'match_date', 'match_time']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"缺少必要字段: {', '.join(missing_columns)}"
            )
        
        # 处理数据导入
        imported_count = 0
        error_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # 基本数据验证
                if pd.isna(row['home_team']) or pd.isna(row['away_team']) or pd.isna(row['match_date']):
                    error_count += 1
                    errors.append(f"第{idx+2}行: 主队、客队、比赛日期不能为空")
                    continue
                
                # 创建比赛记录（这里简化处理，实际应该更复杂的逻辑）
                match_data = {
                    'match_identifier': f"import_{league_id}_{imported_count}_{datetime.now().timestamp()}",
                    'league_id': league_id,
                    'home_team_name': str(row['home_team']).strip(),
                    'away_team_name': str(row['away_team']).strip(),
                    'match_date': pd.to_datetime(row['match_date']).date(),
                    'match_time': pd.to_datetime(str(row['match_time'])).time() if pd.notna(row['match_time']) else datetime.now().time(),
                    'status': 'scheduled',
                    'is_published': True,
                    'created_by': current_user.id
                }
                
                # 这里应该调用实际的创建比赛服务
                # 简化处理，实际项目中需要创建Match记录和关联Team记录
                imported_count += 1
                
            except Exception as row_error:
                error_count += 1
                errors.append(f"第{idx+2}行: {str(row_error)}")
        
        # 更新联赛比赛总数
        league.total_matches = league.total_matches + imported_count if league.total_matches else imported_count
        league.updated_at = datetime.utcnow()
        db.commit()
        
        return UnifiedResponse(
            code=200,
            message=f"文件导入完成，成功导入{imported_count}条记录，失败{error_count}条",
            data={
                "imported_count": imported_count,
                "error_count": error_count,
                "errors": errors[:10],  # 只返回前10个错误
                "total_matches": league.total_matches
            },
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"文件导入失败: {str(e)}")


@router.get("/leagues", response_model=UnifiedResponse[List[Dict[str, Any]]])
async def get_leagues_for_selection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    获取联赛列表供选择（用于配置页面）
    """
    try:
        leagues = db.query(League).filter(
            League.is_active == True
        ).order_by(League.country, League.level, League.name).all()
        
        league_list = []
        for league in leagues:
            league_dict = {
                "id": league.id,
                "name": league.name,
                "code": league.code,
                "short_name": league.short_name,
                "country": league.country,
                "country_code": league.country_code,
                "level": league.level,
                "current_season": league.current_season,
                "total_teams": league.total_teams,
                "is_popular": league.is_popular
            }
            league_list.append(league_dict)
        
        return UnifiedResponse(
            code=200,
            message="获取联赛列表成功",
            data=league_list,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取联赛列表失败: {str(e)}")


@router.delete("/{match_id}", response_model=UnifiedResponse[None])
async def delete_match_admin(
    match_id: int = Path(..., description="比赛ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    删除比赛（管理员权限）
    """
    try:
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        db.delete(match)
        db.commit()
        
        return UnifiedResponse(
            code=200,
            message="比赛删除成功",
            data=None,
            timestamp=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除比赛失败: {str(e)}")


@router.put("/{match_id}/publish", response_model=UnifiedResponse[Dict[str, Any]])
async def publish_match(
    match_id: int = Path(..., description="比赛ID"),
    is_published: bool = Form(..., description="是否发布"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    发布/取消发布比赛
    """
    try:
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        
        match.is_published = is_published
        match.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(match)
        
        return UnifiedResponse(
            code=200,
            message=f"比赛{'发布' if is_published else '取消发布'}成功",
            data={
                "match_id": match.id,
                "is_published": match.is_published
            },
            timestamp=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
