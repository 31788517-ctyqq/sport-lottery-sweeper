"""
公开赛程API端点 - 无需认证的赛程查询
为前端赛程展示页面提供数据接口
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Query

# AI_WORKING: coder1 @2026-01-25T00:00:00 - 修复public_matches.py导入路径错误
from backend.services.service_registry import get_crawler_service
from backend.schemas.response import UnifiedResponse
# AI_DONE: coder1 @2026-01-25T00:00:00

router = APIRouter()

@router.get("/lottery/matches", response_model=UnifiedResponse[List[Dict[str, Any]]])
async def get_lottery_matches(
    days: int = Query(3, ge=1, le=30, description="天数范围"),
    league: Optional[str] = Query(None, description="联赛过滤"),
    sort_by: Optional[str] = Query("date", description="排序字段: date/popularity/odds"),
    order: Optional[str] = Query("desc", description="排序方向: asc/desc"),
    source: Optional[str] = Query("500", description="数据源: 500/sporttery"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),

) -> Dict[str, Any]:
    """
    获取彩票赛程数据 - 公开接口，无需认证
    直接从爬虫服务获取数据，支持多数据源
    """
    try:
        # 使用服务注册表获取爬虫服务
        crawler_service = get_crawler_service()
        matches = await crawler_service.crawl_matches()
        
        # 过滤未来days天的比赛
        cutoff_date = datetime.now() + timedelta(days=days)
        filtered_matches = []
        
        for match in matches:
            match_time = match.match_date
            
            # 只显示未来比赛
            if match_time <= datetime.now():
                continue
                
            # 日期范围过滤
            if match_time > cutoff_date:
                continue
                
            # 联赛过滤
            if league and match.league != league:
                continue
                
            # 转换数据格式适配前端
            match_dict = {
                "id": match.match_id,
                "match_id": match.match_id,
                "league": match.league,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "match_date": match_time.isoformat(),
                "match_time": match_time.strftime('%m-%d %H:%M'),
                "odds_home_win": float(match.odds_home_win) if match.odds_home_win else 0,
                "odds_draw": float(match.odds_draw) if match.odds_draw else 0,
                "odds_away_win": float(match.odds_away_win) if match.odds_away_win else 0,
                "status": match.status,
                "score": f"{match.home_score}:{match.away_score}" if match.home_score is not None else "-:-",
                "popularity": getattr(match, 'popularity', 50),
                "source": source,
                "venue": getattr(match, 'venue', ''),
                "round_number": getattr(match, 'round_number', '')
            }
            filtered_matches.append(match_dict)
        
        # 排序
        if sort_by:
            reverse_order = order.lower() == "desc"
            if sort_by == "date":
                filtered_matches.sort(key=lambda x: x.get('match_date', ''), reverse=reverse_order)
            elif sort_by == "popularity":
                filtered_matches.sort(key=lambda x: x.get('popularity', 0), reverse=reverse_order)
            elif sort_by == "odds":
                filtered_matches.sort(key=lambda x: x.get('odds_home_win', 0), reverse=reverse_order)
        
        # 分页
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_matches = filtered_matches[start_idx:end_idx]
        
        # 计算统计信息
        total = len(filtered_matches)
        pages = (total + size - 1) // size
        
        return UnifiedResponse(
            code=200,
            message="获取赛程数据成功",
            data=paginated_matches,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        return UnifiedResponse(
            code=500,
            message=f"获取赛程数据失败: {str(e)}",
            data=[],
            timestamp=datetime.now()
        )

@router.get("/lottery/matches/popular", response_model=UnifiedResponse[List[Dict[str, Any]]])
async def get_popular_matches(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),

):
    """
    获取热门比赛 - 公开接口
    """
    try:
        # 获取所有比赛并排序
        crawler_service = get_crawler_service()
        matches = await crawler_service.crawl_matches()
        
        # 过滤未来比赛并按热度排序
        future_matches = [m for m in matches if m.match_date > datetime.now()]
        popular_matches = sorted(future_matches, key=lambda x: getattr(x, 'popularity', 50), reverse=True)
        
        # 转换格式并返回前limit个
        result = []
        for match in popular_matches[:limit]:
            match_dict = {
                "id": match.match_id,
                "match_id": match.match_id,
                "league": match.league,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "match_date": match.match_date.isoformat(),
                "match_time": match.match_date.strftime('%m-%d %H:%M'),
                "odds_home_win": float(match.odds_home_win) if match.odds_home_win else 0,
                "odds_draw": float(match.odds_draw) if match.odds_draw else 0,
                "odds_away_win": float(match.odds_away_win) if match.odds_away_win else 0,
                "status": match.status,
                "popularity": getattr(match, 'popularity', 50),
                "venue": getattr(match, 'venue', '')
            }
            result.append(match_dict)
        
        return UnifiedResponse(
            code=200,
            message="获取热门比赛成功",
            data=result,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        return UnifiedResponse(
            code=500,
            message=f"获取热门比赛失败: {str(e)}",
            data=[],
            timestamp=datetime.now()
        )

@router.get("/lottery/matches/leagues", response_model=UnifiedResponse[List[Dict[str, Any]]])
async def get_leagues(

):
    """
    获取联赛列表 - 公开接口
    """
    try:
        crawler_service = get_crawler_service()
        matches = await crawler_service.crawl_matches()
        future_matches = [m for m in matches if m.match_date > datetime.now()]
        
        # 提取唯一联赛并统计
        league_stats = {}
        for match in future_matches:
            league = match.league
            if league not in league_stats:
                league_stats[league] = {
                    "name": league,
                    "match_count": 0,
                    "avg_odds": []
                }
            league_stats[league]["match_count"] += 1
            if match.odds_home_win:
                league_stats[league]["avg_odds"].append(float(match.odds_home_win))
        
        # 计算平均赔率
        result = []
        for league, stats in league_stats.items():
            avg_odds = sum(stats["avg_odds"]) / len(stats["avg_odds"]) if stats["avg_odds"] else 0
            result.append({
                "name": league,
                "match_count": stats["match_count"],
                "avg_odds": round(avg_odds, 2)
            })
        
        # 按比赛数量排序
        result.sort(key=lambda x: x["match_count"], reverse=True)
        
        return UnifiedResponse(
            code=200,
            message="获取联赛列表成功",
            data=result,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        return UnifiedResponse(
            code=500,
            message=f"获取联赛列表失败: {str(e)}",
            data=[],
            timestamp=datetime.now()
        )