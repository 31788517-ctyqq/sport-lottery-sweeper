"""
情报数据API接口
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from ...core.database import get_db
from backend.config import settings
from ...models.intelligence import Intelligence, IntelligenceType, IntelligenceSource
from ...models.match import Match
from ...models.user import User
from ...schemas.intelligence import IntelligenceResponse, IntelligenceCreate, IntelligenceUpdate
from ...core.auth import get_current_user
from ...schemas.intelligence import IntelligenceTypeResponse, IntelligenceSourceResponse
from ...schemas.intelligence import IntelligenceFilter

# 创建情报路由
router = APIRouter()

@router.get("/", response_model=List[IntelligenceResponse])
async def get_intelligence_list(
    league: Optional[str] = Query("all", description="联赛名称"),
    type: Optional[str] = Query("all", description="情报类型"),
    source: Optional[str] = Query("all", description="信息来源"),
    match_id: Optional[int] = Query(None, description="比赛ID"),
    sort_by: str = Query("created_at", description="排序方式: created_at, weight, match_time"),
    sort_order: str = Query("desc", description="排序顺序: asc, desc"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取情报列表
    
    Args:
        league: 联赛名称
        type: 情报类型
        source: 信息来源
        match_id: 比赛ID
        sort_by: 排序方式
        sort_order: 排序顺序
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        List[IntelligenceResponse]: 情报列表
    """
    # 构建基础查询
    query = db.query(Intelligence).options(
        joinedload(Intelligence.match),
        joinedload(Intelligence.type_info),
        joinedload(Intelligence.source_info)
    )
    
    # 应用过滤条件
    if league and league != "all":
        query = query.join(Match).filter(Match.league_id.in_(
            db.query(Intelligence.match_id).filter(Match.league.has(name=league))
        ))
    
    if type and type != "all":
        query = query.filter(Intelligence.type == type)
    
    if source and source != "all":
        query = query.filter(Intelligence.source == source)
    
    if match_id:
        query = query.filter(Intelligence.match_id == match_id)
    
    # 应用排序
    if sort_by == "weight":
        order_field = Intelligence.weight
    elif sort_by == "match_time":
        order_field = Intelligence.match.match_time
    else:
        order_field = Intelligence.created_at
    
    if sort_order == "asc":
        query = query.order_by(order_field.asc())
    else:
        query = query.order_by(order_field.desc())
    
    # 应用分页
    offset = (page - 1) * page_size
    intelligence_list = query.offset(offset).limit(page_size).all()
    
    return intelligence_list

@router.get("/recent", response_model=List[IntelligenceResponse])
async def get_recent_intelligence(
    hours: int = Query(24, description="最近小时数", ge=1, le=168),
    limit: int = Query(50, description="返回数量", ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取最近的情报
    
    Args:
        hours: 最近小时数
        limit: 返回数量
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        List[IntelligenceResponse]: 最近的情报列表
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    intelligence_list = db.query(Intelligence).options(
        joinedload(Intelligence.match),
        joinedload(Intelligence.type_info),
        joinedload(Intelligence.source_info)
    ).filter(
        Intelligence.created_at >= cutoff_time
    ).order_by(
        Intelligence.created_at.desc()
    ).limit(limit).all()
    
    return intelligence_list

@router.get("/high-priority", response_model=List[IntelligenceResponse])
async def get_high_priority_intelligence(
    min_weight: float = Query(0.7, description="最小权重", ge=0.0, le=1.0),
    limit: int = Query(20, description="返回数量", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取高优先级情报
    
    Args:
        min_weight: 最小权重
        limit: 返回数量
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        List[IntelligenceResponse]: 高优先级情报列表
    """
    intelligence_list = db.query(Intelligence).options(
        joinedload(Intelligence.match),
        joinedload(Intelligence.type_info),
        joinedload(Intelligence.source_info)
    ).filter(
        Intelligence.weight >= min_weight,
        Intelligence.match.has(Match.status == "scheduled")
    ).order_by(
        Intelligence.weight.desc(),
        Intelligence.created_at.desc()
    ).limit(limit).all()
    
    return intelligence_list

@router.get("/{intelligence_id}", response_model=IntelligenceResponse)
async def get_intelligence(
    intelligence_id: int = Path(..., description="情报ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取情报详情
    
    Args:
        intelligence_id: 情报ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        IntelligenceResponse: 情报详情
    """
    intelligence = db.query(Intelligence).options(
        joinedload(Intelligence.match),
        joinedload(Intelligence.type_info),
        joinedload(Intelligence.source_info)
    ).filter(Intelligence.id == intelligence_id).first()
    
    if not intelligence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="情报不存在"
        )
    
    return intelligence

@router.post("/", response_model=IntelligenceResponse, status_code=status.HTTP_201_CREATED)
async def create_intelligence(
    intelligence_data: IntelligenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建情报
    
    Args:
        intelligence_data: 情报数据
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        IntelligenceResponse: 创建的情报
    """
    # 检查比赛是否存在
    match = db.query(Match).filter(Match.id == intelligence_data.match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="比赛不存在"
        )
    
    # 检查情报类型是否存在
    type_info = db.query(IntelligenceType).filter(
        IntelligenceType.code == intelligence_data.type
    ).first()
    if not type_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="情报类型不存在"
        )
    
    # 检查信息来源是否存在
    source_info = db.query(IntelligenceSource).filter(
        IntelligenceSource.code == intelligence_data.source
    ).first()
    if not source_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="信息来源不存在"
        )
    
    # 创建情报
    db_intelligence = Intelligence(
        **intelligence_data.dict(exclude_unset=True),
        created_by=current_user.id
    )
    
    db.add(db_intelligence)
    db.commit()
    db.refresh(db_intelligence)
    
    # 重新加载关联数据
    db.refresh(db_intelligence, ["match", "type_info", "source_info"])
    
    return db_intelligence

@router.put("/{intelligence_id}", response_model=IntelligenceResponse)
async def update_intelligence(
    intelligence_id: int,
    intelligence_data: IntelligenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新情报信息
    
    Args:
        intelligence_id: 情报ID
        intelligence_data: 情报更新数据
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        IntelligenceResponse: 更新后的情报
    """
    intelligence = db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
    if not intelligence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="情报不存在"
        )
    
    # 更新字段
    for field, value in intelligence_data.dict(exclude_unset=True).items():
        setattr(intelligence, field, value)
    
    intelligence.updated_at = datetime.utcnow()
    intelligence.updated_by = current_user.id
    
    db.commit()
    db.refresh(intelligence)
    
    # 重新加载关联数据
    db.refresh(intelligence, ["match", "type_info", "source_info"])
    
    return intelligence

@router.delete("/{intelligence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_intelligence(
    intelligence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除情报
    
    Args:
        intelligence_id: 情报ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        None
    """
    intelligence = db.query(Intelligence).filter(Intelligence.id == intelligence_id).first()
    if not intelligence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="情报不存在"
        )
    
    db.delete(intelligence)
    db.commit()

@router.get("/types/", response_model=List[IntelligenceTypeResponse])
async def get_intelligence_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取情报类型列表
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        List[IntelligenceTypeResponse]: 情报类型列表
    """
    types = db.query(IntelligenceType).order_by(IntelligenceType.name.asc()).all()
    return types

@router.get("/sources/", response_model=List[IntelligenceSourceResponse])
async def get_intelligence_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取信息来源列表
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        List[IntelligenceSourceResponse]: 信息来源列表
    """
    sources = db.query(IntelligenceSource).order_by(IntelligenceSource.name.asc()).all()
    return sources

@router.get("/match/{match_id}", response_model=List[IntelligenceResponse])
async def get_match_intelligence(
    match_id: int = Path(..., description="比赛ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取比赛相关情报
    
    Args:
        match_id: 比赛ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        List[IntelligenceResponse]: 比赛相关情报列表
    """
    intelligence_list = db.query(Intelligence).options(
        joinedload(Intelligence.match),
        joinedload(Intelligence.type_info),
        joinedload(Intelligence.source_info)
    ).filter(
        Intelligence.match_id == match_id
    ).order_by(
        Intelligence.weight.desc(),
        Intelligence.created_at.desc()
    ).all()
    
    return intelligence_list

@router.post("/filter", response_model=List[IntelligenceResponse])
async def filter_intelligence(
    filter_data: IntelligenceFilter,
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    高级筛选情报
    
    Args:
        filter_data: 筛选条件
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        List[IntelligenceResponse]: 筛选后的情报列表
    """
    query = db.query(Intelligence).options(
        joinedload(Intelligence.match),
        joinedload(Intelligence.type_info),
        joinedload(Intelligence.source_info)
    )
    
    # 应用筛选条件
    if filter_data.league_ids:
        query = query.filter(
            Intelligence.match.has(Match.league_id.in_(filter_data.league_ids))
        )
    
    if filter_data.match_ids:
        query = query.filter(Intelligence.match_id.in_(filter_data.match_ids))
    
    if filter_data.types:
        query = query.filter(Intelligence.type.in_(filter_data.types))
    
    if filter_data.sources:
        query = query.filter(Intelligence.source.in_(filter_data.sources))
    
    if filter_data.min_weight:
        query = query.filter(Intelligence.weight >= filter_data.min_weight)
    
    if filter_data.max_weight:
        query = query.filter(Intelligence.weight <= filter_data.max_weight)
    
    if filter_data.date_from:
        query = query.filter(Intelligence.created_at >= filter_data.date_from)
    
    if filter_data.date_to:
        query = query.filter(Intelligence.created_at <= filter_data.date_to)
    
    if filter_data.has_odds is not None:
        if filter_data.has_odds:
            query = query.filter(Intelligence.odds_data.isnot(None))
        else:
            query = query.filter(Intelligence.odds_data.is_(None))
    
    # 排序
    if filter_data.sort_by == "weight":
        order_field = Intelligence.weight
    elif filter_data.sort_by == "match_time":
        order_field = Intelligence.match.match_time
    else:
        order_field = Intelligence.created_at
    
    if filter_data.sort_order == "asc":
        query = query.order_by(order_field.asc())
    else:
        query = query.order_by(order_field.desc())
    
    # 分页
    offset = (page - 1) * page_size
    intelligence_list = query.offset(offset).limit(page_size).all()
    
    return intelligence_list

@router.get("/stats/summary")
async def get_intelligence_summary(
    days: int = Query(7, description="统计天数", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取情报统计摘要
    
    Args:
        days: 统计天数
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        dict: 统计摘要
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # 总数量统计
    total_count = db.query(Intelligence).filter(
        Intelligence.created_at >= cutoff_date
    ).count()
    
    # 按类型统计
    type_stats = db.query(
        Intelligence.type,
        IntelligenceType.name,
        db.func.count(Intelligence.id)
    ).join(
        IntelligenceType, Intelligence.type == IntelligenceType.code
    ).filter(
        Intelligence.created_at >= cutoff_date
    ).group_by(
        Intelligence.type, IntelligenceType.name
    ).all()
    
    # 按来源统计
    source_stats = db.query(
        Intelligence.source,
        IntelligenceSource.name,
        db.func.count(Intelligence.id)
    ).join(
        IntelligenceSource, Intelligence.source == IntelligenceSource.code
    ).filter(
        Intelligence.created_at >= cutoff_date
    ).group_by(
        Intelligence.source, IntelligenceSource.name
    ).all()
    
    # 平均权重
    avg_weight = db.query(
        db.func.avg(Intelligence.weight)
    ).filter(
        Intelligence.created_at >= cutoff_date
    ).scalar() or 0.0
    
    # 每日统计
    daily_stats = db.query(
        db.func.date(Intelligence.created_at),
        db.func.count(Intelligence.id)
    ).filter(
        Intelligence.created_at >= cutoff_date
    ).group_by(
        db.func.date(Intelligence.created_at)
    ).order_by(
        db.func.date(Intelligence.created_at).desc()
    ).all()
    
    return {
        "period_days": days,
        "total_count": total_count,
        "average_weight": round(float(avg_weight), 3),
        "by_type": [
            {"type": t[0], "type_name": t[1], "count": t[2]}
            for t in type_stats
        ],
        "by_source": [
            {"source": s[0], "source_name": s[1], "count": s[2]}
            for s in source_stats
        ],
        "daily_stats": [
            {"date": d[0].isoformat() if d[0] else None, "count": d[1]}
            for d in daily_stats
        ]
    }