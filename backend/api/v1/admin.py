"""
管理后台API接口
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...models import User, Match, League, Team, Intelligence, IntelligenceType, IntelligenceSource, Permission, Role  # 从共享模型导入
from ...database import get_db
from ...core.auth import get_current_user
from ...schemas.admin import UserResponse, MatchResponse, CreateMatchRequest, UpdateMatchRequest
from ...schemas.user import UserCreate, UserUpdate
from ...schemas.role import RoleResponse, PermissionResponse  # 假设有这些schema
from ...config import settings  # 假设配置在顶层


router = APIRouter(prefix="/admin", tags=["admin"])

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """检查当前用户是否为管理员"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够权限"
        )
    return current_user


# 用户管理
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    username: Optional[str] = Query(None, description="用户名"),
    email: Optional[str] = Query(None, description="邮箱"),
    is_active: Optional[bool] = Query(None, description="是否活跃"),
    is_superuser: Optional[bool] = Query(None, description="是否超级用户"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取用户列表（管理员）
    
    Args:
        username: 用户名
        email: 邮箱
        is_active: 是否活跃
        is_superuser: 是否超级用户
        page: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        List[UserResponse]: 用户列表
    """
    query = db.query(User)
    
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if is_superuser is not None:
        query = query.filter(User.is_superuser == is_superuser)
    
    offset = (page - 1) * page_size
    users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()
    
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int = Path(..., description="用户ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取用户详情（管理员）
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        UserResponse: 用户详情
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    创建用户（管理员）
    
    Args:
        user_data: 用户数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        UserResponse: 创建的用户
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 创建用户
    from ...core.auth import get_password_hash
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    更新用户信息（管理员）
    
    Args:
        user_id: 用户ID
        user_data: 用户更新数据
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        UserResponse: 更新后的用户
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查邮箱是否已被其他用户使用
    if user_data.email and user_data.email != user.email:
        existing_email = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被其他用户使用"
            )
    
    # 更新字段
    for field, value in user_data.dict(exclude_unset=True).items():
        if field == "password" and value:
            from ...core.auth import get_password_hash
            user.hashed_password = get_password_hash(value)
        elif field != "password":
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    删除用户（管理员）
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        None
    """
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 如果是超级用户，需要特殊权限
    if user.is_superuser and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除超级用户"
        )
    
    db.delete(user)
    db.commit()

@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    激活/禁用用户（管理员）
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 操作结果
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能操作自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能操作自己的账户"
        )
    
    user.is_active = not user.is_active
    user.updated_at = datetime.utcnow()
    db.commit()
    
    status_text = "激活" if user.is_active else "禁用"
    return {"message": f"用户已{status_text}"}

# 比赛数据管理
@router.get("/matches/stats")
async def get_matches_stats(
    days: int = Query(30, description="统计天数", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取比赛数据统计（管理员）
    
    Args:
        days: 统计天数
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 比赛统计信息
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # 比赛总数
    total_matches = db.query(Match).filter(
        Match.created_at >= cutoff_date
    ).count()
    
    # 按状态统计
    status_stats = db.query(
        Match.status,
        func.count(Match.id)
    ).filter(
        Match.created_at >= cutoff_date
    ).group_by(Match.status).all()
    
    # 按联赛统计
    league_stats = db.query(
        League.name,
        func.count(Match.id)
    ).join(Match, Match.league_id == League.id).filter(
        Match.created_at >= cutoff_date
    ).group_by(League.name).order_by(
        func.count(Match.id).desc()
    ).all()
    
    # 每日新增统计
    daily_stats = db.query(
        func.date(Match.created_at),
        func.count(Match.id)
    ).filter(
        Match.created_at >= cutoff_date
    ).group_by(
        func.date(Match.created_at)
    ).order_by(
        func.date(Match.created_at).desc()
    ).all()
    
    return {
        "period_days": days,
        "total_matches": total_matches,
        "by_status": [
            {"status": s[0], "count": s[1]} for s in status_stats
        ],
        "by_league": [
            {"league": l[0], "count": l[1]} for l in league_stats
        ],
        "daily_stats": [
            {"date": d[0].isoformat() if d[0] else None, "count": d[1]}
            for d in daily_stats
        ]
    }

@router.post("/matches/batch-import")
async def batch_import_matches(
    matches_data: List[dict] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    批量导入比赛数据（管理员）
    
    Args:
        matches_data: 比赛数据列表
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 导入结果
    """
    imported_count = 0
    error_count = 0
    errors = []
    
    for idx, match_data in enumerate(matches_data):
        try:
            # 检查联赛
            if "league_id" not in match_data:
                errors.append(f"第{idx+1}条: 缺少league_id")
                error_count += 1
                continue
            
            league = db.query(League).filter(League.id == match_data["league_id"]).first()
            if not league:
                errors.append(f"第{idx+1}条: 联赛不存在")
                error_count += 1
                continue
            
            # 检查主队
            if "home_team_id" not in match_data:
                errors.append(f"第{idx+1}条: 缺少home_team_id")
                error_count += 1
                continue
            
            home_team = db.query(Team).filter(Team.id == match_data["home_team_id"]).first()
            if not home_team:
                errors.append(f"第{idx+1}条: 主队不存在")
                error_count += 1
                continue
            
            # 检查客队
            if "away_team_id" not in match_data:
                errors.append(f"第{idx+1}条: 缺少away_team_id")
                error_count += 1
                continue
            
            away_team = db.query(Team).filter(Team.id == match_data["away_team_id"]).first()
            if not away_team:
                errors.append(f"第{idx+1}条: 客队不存在")
                error_count += 1
                continue
            
            # 检查是否已存在
            existing_match = db.query(Match).filter(
                Match.league_id == match_data["league_id"],
                Match.home_team_id == match_data["home_team_id"],
                Match.away_team_id == match_data["away_team_id"],
                Match.match_time == match_data.get("match_time")
            ).first()
            
            if existing_match:
                # 更新现有比赛
                for field, value in match_data.items():
                    if field not in ["league_id", "home_team_id", "away_team_id", "match_time"]:
                        setattr(existing_match, field, value)
                
                existing_match.updated_at = datetime.utcnow()
                existing_match.updated_by = current_user.id
                db.commit()
            else:
                # 创建新比赛
                db_match = Match(
                    **match_data,
                    created_by=current_user.id
                )
                db.add(db_match)
                db.commit()
            
            imported_count += 1
            
        except Exception as e:
            error_count += 1
            errors.append(f"第{idx+1}条: {str(e)}")
    
    return {
        "total": len(matches_data),
        "imported": imported_count,
        "errors": error_count,
        "error_messages": errors[:10]  # 只返回前10个错误
    }

# 情报数据管理
@router.get("/intelligence/stats")
async def get_intelligence_stats(
    days: int = Query(30, description="统计天数", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取情报数据统计（管理员）
    
    Args:
        days: 统计天数
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 情报统计信息
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # 情报总数
    total_intelligence = db.query(Intelligence).filter(
        Intelligence.created_at >= cutoff_date
    ).count()
    
    # 按类型统计
    type_stats = db.query(
        IntelligenceType.name,
        func.count(Intelligence.id)
    ).join(Intelligence, Intelligence.type == IntelligenceType.code).filter(
        Intelligence.created_at >= cutoff_date
    ).group_by(IntelligenceType.name).all()
    
    # 按来源统计
    source_stats = db.query(
        IntelligenceSource.name,
        func.count(Intelligence.id)
    ).join(Intelligence, Intelligence.source == IntelligenceSource.code).filter(
        Intelligence.created_at >= cutoff_date
    ).group_by(IntelligenceSource.name).all()
    
    # 平均权重
    avg_weight = db.query(
        func.avg(Intelligence.weight)
    ).filter(
        Intelligence.created_at >= cutoff_date
    ).scalar() or 0.0
    
    # 有赔率的情报数量
    with_odds = db.query(Intelligence).filter(
        Intelligence.created_at >= cutoff_date,
        Intelligence.odds_data.isnot(None)
    ).count()
    
    return {
        "period_days": days,
        "total_intelligence": total_intelligence,
        "average_weight": round(float(avg_weight), 3),
        "with_odds": with_odds,
        "by_type": [
            {"type": t[0], "count": t[1]} for t in type_stats
        ],
        "by_source": [
            {"source": s[0], "count": s[1]} for s in source_stats
        ]
    }

@router.post("/intelligence/batch-import")
async def batch_import_intelligence(
    intelligence_data: List[dict] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    批量导入情报数据（管理员）
    
    Args:
        intelligence_data: 情报数据列表
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 导入结果
    """
    imported_count = 0
    error_count = 0
    errors = []
    
    for idx, data in enumerate(intelligence_data):
        try:
            # 检查必填字段
            required_fields = ["match_id", "type", "source", "content"]
            for field in required_fields:
                if field not in data:
                    errors.append(f"第{idx+1}条: 缺少{field}")
                    error_count += 1
                    continue
            
            # 检查比赛是否存在
            match = db.query(Match).filter(Match.id == data["match_id"]).first()
            if not match:
                errors.append(f"第{idx+1}条: 比赛不存在")
                error_count += 1
                continue
            
            # 检查类型是否存在
            type_info = db.query(IntelligenceType).filter(
                IntelligenceType.code == data["type"]
            ).first()
            if not type_info:
                errors.append(f"第{idx+1}条: 情报类型不存在")
                error_count += 1
                continue
            
            # 检查来源是否存在
            source_info = db.query(IntelligenceSource).filter(
                IntelligenceSource.code == data["source"]
            ).first()
            if not source_info:
                errors.append(f"第{idx+1}条: 信息来源不存在")
                error_count += 1
                continue
            
            # 检查是否已存在相似情报
            existing = db.query(Intelligence).filter(
                Intelligence.match_id == data["match_id"],
                Intelligence.type == data["type"],
                Intelligence.source == data["source"],
                func.substring(Intelligence.content, 1, 100) == data["content"][:100]
            ).first()
            
            if existing:
                # 更新现有情报
                for field, value in data.items():
                    if field not in ["match_id", "type", "source"]:
                        setattr(existing, field, value)
                
                existing.updated_at = datetime.utcnow()
                existing.updated_by = current_user.id
                db.commit()
            else:
                # 创建新情报
                db_intelligence = Intelligence(
                    **data,
                    created_by=current_user.id
                )
                db.add(db_intelligence)
                db.commit()
            
            imported_count += 1
            
        except Exception as e:
            error_count += 1
            errors.append(f"第{idx+1}条: {str(e)}")
    
    return {
        "total": len(intelligence_data),
        "imported": imported_count,
        "errors": error_count,
        "error_messages": errors[:10]
    }

# 系统配置管理
@router.get("/system/config")
async def get_system_config(
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取系统配置（管理员）
    
    Args:
        current_user: 当前管理员用户
        
    Returns:
        dict: 系统配置信息
    """
    # 返回可配置的系统参数
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "cors_origins": settings.CORS_ORIGINS,
        "database_url": "***" if settings.DATABASE_URL else None,
        "redis_url": "***" if settings.REDIS_URL else None,
        "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "crawler_request_delay": settings.CRAWLER_REQUEST_DELAY,
        "crawler_max_retries": settings.CRAWLER_MAX_RETRIES,
        "password_min_length": settings.PASSWORD_MIN_LENGTH,
        "password_max_length": settings.PASSWORD_MAX_LENGTH,
        "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
        "upload_dir": settings.UPLOAD_DIR,
        "max_upload_size": settings.MAX_UPLOAD_SIZE
    }

@router.get("/system/status")
async def get_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取系统状态（管理员）
    
    Args:
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        dict: 系统状态信息
    """
    from datetime import datetime
    
    # 用户统计
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    superusers = db.query(User).filter(User.is_superuser == True).count()
    
    # 比赛统计
    total_matches = db.query(Match).count()
    scheduled_matches = db.query(Match).filter(Match.status == "scheduled").count()
    finished_matches = db.query(Match).filter(Match.status == "finished").count()
    
    # 情报统计
    total_intelligence = db.query(Intelligence).count()
    today_intelligence = db.query(Intelligence).filter(
        func.date(Intelligence.created_at) == datetime.utcnow().date()
    ).count()
    
    # 联赛统计
    total_leagues = db.query(League).filter(League.is_active == True).count()
    total_teams = db.query(Team).count()
    
    # 数据库状态
    try:
        db_status = "healthy"
        db.execute("SELECT 1")  # 简单查询测试连接
    except Exception:
        db_status = "unhealthy"
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "status": db_status,
            "users": total_users,
            "active_users": active_users,
            "superusers": superusers,
            "matches": total_matches,
            "scheduled_matches": scheduled_matches,
            "finished_matches": finished_matches,
            "intelligence": total_intelligence,
            "today_intelligence": today_intelligence,
            "leagues": total_leagues,
            "teams": total_teams
        },
        "system": {
            "app_name": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        }
    }

# 角色和权限管理（基础实现）
@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取角色列表（管理员）
    
    Args:
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        List[RoleResponse]: 角色列表
    """
    roles = db.query(Role).order_by(Role.name.asc()).all()
    return roles

@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取权限列表（管理员）
    
    Args:
        db: 数据库会话
        current_user: 当前管理员用户
        
    Returns:
        List[PermissionResponse]: 权限列表
    """
    permissions = db.query(Permission).order_by(Permission.name.asc()).all()
    return permissions