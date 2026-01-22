from fastapi import APIRouter, Query
from typing import Dict, Any, Optional, List
from datetime import timedelta, datetime
from pathlib import Path
import traceback
import logging
import json
import os

# 使用绝对导入路径
from backend.schemas.response import UnifiedResponse, PageResponse, ErrorResponse
from backend.core.cache_manager import get_cache_manager
from backend.tasks import sporttery_scraper

router = APIRouter(prefix="/lottery", tags=["Sports Lottery"])

logger = logging.getLogger(__name__)


def load_500_com_data(filter_day: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    从debug目录加载500彩票网数据
    
    Args:
        filter_day: 筛选特定星期的比赛，如 "周一"
    """
    try:
        project_root = Path(__file__).parent.parent.parent.parent
        debug_dir = project_root / "debug"
        
        if not debug_dir.exists():
            logger.warning(f"debug目录不存在: {debug_dir}")
            return []
        
        files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
        
        if not files:
            logger.info("没有找到500彩票网数据文件")
            return []
        
        latest_file = sorted(files)[-1]
        file_path = debug_dir / latest_file
        
        with open(file_path, 'r', encoding='utf-8') as f:
            matches = json.load(f)
        
        # 过滤表头
        matches = [m for m in matches if m.get('match_id') != '编号']
        
        # 按星期筛选
        if filter_day:
            matches = [m for m in matches if m.get('match_id', '').startswith(filter_day)]
        
        # 格式化数据
        formatted_matches = []
        for m in matches:
            formatted_matches.append({
                "id": m.get("match_id"),
                "match_id": m.get("match_id"),
                "league": m.get("league"),
                "home_team": m.get("home_team"),
                "away_team": m.get("away_team"),
                "match_time": m.get("match_time"),
                "match_date": m.get("match_time"),
                "odds_home_win": float(m.get("odds_home_win", 0) or 0),
                "odds_draw": float(m.get("odds_draw", 0) or 0),
                "odds_away_win": float(m.get("odds_away_win", 0) or 0),
                "status": m.get("status", "scheduled"),
                "score": m.get("score", "-:-"),
                "popularity": 70,
                "source": "500彩票网"
            })
        
        logger.info(f"成功加载500彩票网数据: {len(formatted_matches)}场比赛")
        return formatted_matches
    except Exception as e:
        logger.error(f"加载500彩票网数据失败: {e}")
        return []


@router.get("/matches", response_model=UnifiedResponse[PageResponse[Dict[str, Any]]])
async def get_lottery_matches(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页大小"),
    source: str = Query("auto", description="数据源: auto/500/sporttery"),
    date_from: Optional[str] = Query(None, description="起始日期 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    league: Optional[str] = Query(None, description="联赛过滤"),
    day_filter: Optional[str] = Query(None, description="星期筛选: 周一/周二/周三等"),
    sort: Optional[str] = Query("date", description="排序字段: date/popularity"),
    order: Optional[str] = Query("asc", description="排序方向: asc/desc")
) -> Dict[str, Any]:
    """
    获取竞彩足球比赛列表 - 支持多数据源
    
    数据源优先级：
    - auto: 自动选择（优先500.com，回退到sporttery）
    - 500: 强制使用500彩票网数据
    - sporttery: 强制使用竞彩官网数据
    """
    try:
        cache_manager = get_cache_manager()
        cache_key = f"jczq_v2:{source}:{page}:{size}:{date_from}:{date_to}:{league}:{day_filter}:{sort}:{order}"

        # 尝试从缓存获取
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            logger.info(f"[缓存命中] 竞彩足球比赛数据 (source={source})")
            matches = cached_data.get('matches', [])
            data_source = cached_data.get('source', 'cache')
        else:
            logger.info(f"[缓存未命中] 获取新竞彩足球数据 (source={source})")
            matches = []
            data_source = "unknown"
            
            # 根据数据源选择
            if source == "500":
                # 强制使用500彩票网数据
                matches = load_500_com_data(filter_day=day_filter)
                data_source = "500彩票网"
            elif source == "sporttery":
                # 强制使用竞彩官网数据
                try:
                    async with sporttery_scraper:
                        raw_matches = await sporttery_scraper.get_recent_matches(7)
                    matches = [
                        {
                            "id": m.get('id', ''),
                            "match_date": m.get('match_date', ''),
                            "home_team": m.get('home_team', '主队'),
                            "away_team": m.get('away_team', '客队'),
                            "league": m.get('league', '未知联赛'),
                            "odds_home_win": m.get('odds_home_win', 0.0),
                            "odds_draw": m.get('odds_draw', 0.0),
                            "odds_away_win": m.get('odds_away_win', 0.0),
                            "popularity": m.get('popularity', 0),
                            "status": m.get('status', '未开始'),
                            "score": m.get('score', '0:0'),
                            "match_time": m.get('match_time', ''),
                            "match_id": m.get('match_id', ''),
                            "source": "竞彩官网"
                        }
                        for m in raw_matches
                    ]
                    data_source = "竞彩官网"
                except Exception as e:
                    logger.error(f"竞彩官网爬虫失败: {e}")
                    matches = []
            else:
                # auto模式：优先500.com，回退到sporttery
                matches = load_500_com_data(filter_day=day_filter)
                if matches:
                    data_source = "500彩票网"
                else:
                    try:
                        async with sporttery_scraper:
                            raw_matches = await sporttery_scraper.get_recent_matches(7)
                        matches = [
                            {
                                "id": m.get('id', ''),
                                "match_date": m.get('match_date', ''),
                                "home_team": m.get('home_team', '主队'),
                                "away_team": m.get('away_team', '客队'),
                                "league": m.get('league', '未知联赛'),
                                "odds_home_win": m.get('odds_home_win', 0.0),
                                "odds_draw": m.get('odds_draw', 0.0),
                                "odds_away_win": m.get('odds_away_win', 0.0),
                                "popularity": m.get('popularity', 0),
                                "status": m.get('status', '未开始'),
                                "score": m.get('score', '0:0'),
                                "match_time": m.get('match_time', ''),
                                "match_id": m.get('match_id', ''),
                                "source": "竞彩官网"
                            }
                            for m in raw_matches
                        ]
                        data_source = "竞彩官网（回退）"
                    except Exception as e:
                        logger.error(f"所有数据源均失败: {e}")
                        matches = []

            # 应用过滤器
            if league:
                matches = [m for m in matches if m.get('league') == league]
            
            # 排序
            if sort == "popularity":
                matches.sort(key=lambda x: x.get('popularity', 0), reverse=(order == "desc"))
            elif sort == "date":
                matches.sort(key=lambda x: x.get('match_time', ''), reverse=(order == "desc"))

            # 缓存数据
            cache_data = {
                'matches': matches,
                'total': len(matches),
                'source': data_source,
                'timestamp': datetime.now().isoformat()
            }
            await cache_manager.set(cache_key, cache_data, timedelta(minutes=5))

        # 分页处理
        total_matches = len(matches)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_matches = matches[start_idx:end_idx]

        return {
            "success": True,
            "data": paginated_matches,
            "total": total_matches,
            "page": page,
            "size": size,
            "source": data_source,
            "message": f"成功获取{len(paginated_matches)}场比赛数据",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取竞彩足球数据失败: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"获取竞彩足球数据失败: {str(e)}",
            "error": str(e),
            "data": [],
            "total": 0
        }


@router.get("/leagues", summary="Get league list")
async def get_lottery_leagues(
    source: str = Query("auto", description="数据源: auto/500/sporttery")
) -> Dict[str, Any]:
    """获取可用的联赛列表"""
    try:
        # 获取所有比赛
        matches_response = await get_lottery_matches(
            page=1, size=1000, source=source
        )
        
        if not matches_response.get("success"):
            return matches_response
        
        matches = matches_response.get("data", [])
        
        # 提取唯一联赛并统计
        leagues = {}
        for match in matches:
            league_name = match.get("league", "未知")
            if league_name not in leagues:
                leagues[league_name] = {"name": league_name, "count": 0}
            leagues[league_name]["count"] += 1
        
        league_list = sorted(leagues.values(), key=lambda x: x["count"], reverse=True)
        
        return {
            "success": True,
            "data": league_list,
            "total": len(league_list),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取联赛列表失败: {e}")
        return {
            "success": False,
            "message": f"获取联赛列表失败: {str(e)}",
            "data": []
        }


@router.post("/refresh", summary="Refresh data cache")
async def refresh_lottery_cache() -> Dict[str, Any]:
    """清除竞彩足球数据缓存，强制重新获取"""
    try:
        cache_manager = get_cache_manager()
        await cache_manager.invalidate_pattern("jczq_v2:*")
        logger.info("已清除竞彩足球缓存")
        
        return {
            "success": True,
            "message": "缓存已清除，下次请求将重新获取数据",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"刷新缓存失败: {e}")
        return {
            "success": False,
            "message": f"刷新缓存失败: {str(e)}"
        }