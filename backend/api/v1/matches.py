"""
比赛数据API端点
提供比赛信息给前端，遵循统一API设计原则
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from backend.api.deps import get_db, get_current_user
from backend.models.user import User
from backend.services.service_registry import get_crawler_service
# 修正导入路径
from backend.schemas.response import UnifiedResponse, PageResponse, ErrorResponse
from backend.schemas.match import MatchResponse
from backend.scrapers.sporttery_scraper import sporttery_scraper


router = APIRouter()


@router.get("/", response_model=UnifiedResponse[List[Dict[str, Any]]])
async def get_matches(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    sort: Optional[str] = Query(None, description="排序字段"),
    order: Optional[str] = Query("desc", description="排序方向 asc/desc"),
    date_from: Optional[str] = Query(None, description="起始日期 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    league: Optional[str] = Query(None, description="联赛过滤"),
    status: Optional[str] = Query(None, description="比赛状态过滤"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取比赛列表 - 从数据库或爬虫服务
    """
    try:
        # 使用爬虫服务获取比赛数据
        crawler_service = get_crawler_service(db)
        matches = await crawler_service.crawl_matches()
        
        # 过滤数据
        filtered_matches = []
        for match in matches:
            match_time = match.match_date
            
            # 日期范围过滤
            if date_from:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                if match_time.date() < from_date.date():
                    continue
                    
            if date_to:
                to_date = datetime.strptime(date_to, "%Y-%m-%d")
                if match_time.date() > to_date.date():
                    continue
            
            # 联赛过滤
            if league and match.league != league:
                continue
                
            # 状态过滤
            if status and match.status != status:
                continue
                
            # 转换数据格式
            match_dict = match.dict()
            match_dict['match_time'] = match_time.strftime('%Y-%m-%d %H:%M')
            filtered_matches.append(match_dict)
        
        # 排序
        if sort:
            reverse_order = order.lower() == "desc"
            filtered_matches.sort(key=lambda x: x.get(sort, ""), reverse=reverse_order)
        
        # 分页
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_matches = filtered_matches[start_idx:end_idx]
        
        # 计算总页数
        total = len(filtered_matches)
        pages = (total + size - 1) // size
        
        page_response = PageResponse(
            data=paginated_matches,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
        return UnifiedResponse(
            code=200,
            message="获取比赛列表成功",
            data=page_response.data,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"获取比赛数据失败: {str(e)}"
        )


@router.get("/{match_id}", response_model=UnifiedResponse[Dict[str, Any]])
async def get_match_by_id(
    match_id: str = Path(..., description="比赛ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取比赛详情 - RESTful风格
    """
    try:
        # 获取所有比赛数据
        crawler_service = get_crawler_service(db)
        all_matches = await crawler_service.crawl_matches()
        
        # 查找指定比赛
        for match in all_matches:
            if str(match.match_id) == match_id:
                # 获取该比赛的赔率历史
                # 注意：这里使用模拟数据，实际应调用真实的服务
                odds_history = []
                
                # 将MatchCreate对象转换为字典
                match_dict = match.dict()
                match_dict["odds_history"] = odds_history
                # 格式化时间
                match_dict['match_time'] = match.match_date.strftime('%Y-%m-%d %H:%M')
                
                return UnifiedResponse(
                    code=200,
                    message="获取比赛详情成功",
                    data=match_dict
                )
        
        raise HTTPException(status_code=404, detail="比赛未找到")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取比赛详情失败: {str(e)}")


@router.post("/", response_model=UnifiedResponse[Dict[str, Any]])
async def create_match(
    match_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建比赛 - RESTful风格
    """
    try:
        # 模拟创建比赛
        match_data["id"] = "mock_id_" + str(hash(str(datetime.now())))
        match_data["created_at"] = datetime.now().isoformat()
        
        return UnifiedResponse(
            code=201,
            message="比赛创建成功",
            data=match_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建比赛失败: {str(e)}")


@router.put("/{match_id}", response_model=UnifiedResponse[Dict[str, Any]])
async def update_match(
    match_id: str,
    match_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新比赛完整信息 - RESTful风格
    """
    try:
        # 模拟更新比赛
        match_data["id"] = match_id
        match_data["updated_at"] = datetime.now().isoformat()
        
        return UnifiedResponse(
            code=200,
            message="比赛更新成功",
            data=match_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新比赛失败: {str(e)}")


@router.patch("/{match_id}", response_model=UnifiedResponse[Dict[str, Any]])
async def partial_update_match(
    match_id: str,
    match_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    部分更新比赛信息 - RESTful风格
    """
    try:
        # 模拟部分更新比赛
        match_data["id"] = match_id
        match_data["updated_at"] = datetime.now().isoformat()
        
        return UnifiedResponse(
            code=200,
            message="比赛部分更新成功",
            data=match_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"部分更新比赛失败: {str(e)}")


@router.delete("/{match_id}", response_model=UnifiedResponse[None])
async def delete_match(
    match_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除比赛 - RESTful风格
    """
    try:
        # 模拟删除比赛
        return UnifiedResponse(
            code=200,
            message="比赛删除成功",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除比赛失败: {str(e)}")


@router.get("/popular", response_model=UnifiedResponse[List[Dict[str, Any]]])
async def get_popular_matches(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取热门比赛 - RESTful风格
    """
    try:
        # 使用爬虫集成服务获取热门比赛
        # 这里暂时使用模拟数据，实际应调用真实服务
        popular_matches = []
        for i in range(limit):
            match = {
                "id": f"popular_match_{i}",
                "home_team": f"主队{i}",
                "away_team": f"客队{i}",
                "league": f"联赛{i}",
                "match_time": (datetime.now() + timedelta(days=i)).isoformat(),
                "popularity": 90 - i
            }
            popular_matches.append(match)
        
        return UnifiedResponse(
            code=200,
            message="获取热门比赛成功",
            data=popular_matches
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门比赛失败: {str(e)}")


@router.get("/trending", response_model=UnifiedResponse[List[Dict[str, Any]]])
async def get_trending_matches(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取趋势比赛 - RESTful风格
    """
    try:
        # 使用爬虫集成服务获取趋势比赛
        # 这里暂时使用模拟数据，实际应调用真实服务
        trending_matches = []
        for i in range(limit):
            match = {
                "id": f"trending_match_{i}",
                "home_team": f"主队{i}",
                "away_team": f"客队{i}",
                "league": f"联赛{i}",
                "match_time": (datetime.now() + timedelta(days=i)).isoformat(),
                "trend_score": 85 + i
            }
            trending_matches.append(match)
        
        return UnifiedResponse(
            code=200,
            message="获取趋势比赛成功",
            data=trending_matches
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取趋势比赛失败: {str(e)}")