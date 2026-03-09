"""
管理员比赛数据路由 - 临时解决方案
将管理员API调用映射到lottery API
"""
from fastapi import APIRouter, Query, Depends
from typing import Dict, Any, Optional
import logging

# 导入lottery的函数 - 改用最终版
from .lottery_final import load_500_com_data_direct
from backend.scrapers.sporttery_scraper import sporttery_scraper

router = APIRouter(prefix="/admin/matches", tags=["admin-matches"])
logger = logging.getLogger(__name__)

@router.get("")
async def admin_get_matches(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    league_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_start: Optional[str] = Query(None),
    date_end: Optional[str] = Query(None),
    days_range: Optional[str] = Query(None),
    source: str = Query("500", description="数据源: 500/sporttery")
):
    """
    管理员获取比赛数据 - 直接调用数据加载函数
    支持从500彩票网获取数据
    """
    try:
        logger.debug(f"[ADMIN-API] 收到请求，source={source}")
        
        matches = []
        data_source = "unknown"
        
        if source == "500":
            logger.debug(f"[ADMIN-API] 调用 load_500_com_data_direct()...")
            matches = load_500_com_data_direct()
            logger.debug(f"[ADMIN-API] 返回 {len(matches)} 条数据")
            data_source = "500彩票网"
        elif source == "sporttery":
            # 使用sporttery爬虫
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
                logger.debug(f"[ADMIN-API] sporttery爬虫失败: {e}")
                matches = []
        
        # 排序
        matches.sort(key=lambda x: x.get('match_time', ''), reverse=False)
        
        # 分页
        total_matches = len(matches)
        start_idx = (page - 1) * size
        end_idx = min(start_idx + size, total_matches)
        paginated_matches = matches[start_idx:end_idx]
        
        logger.debug(f"[ADMIN-API] 返回分页数据: {len(paginated_matches)}/{total_matches}")
        
        return {
            "code": 200,
            "message": f"成功获取{len(paginated_matches)}场比赛数据",
            "data": paginated_matches,
            "pagination": {
                "page": page,
                "size": size,
                "total": total_matches
            }
        }
        
    except Exception as e:
        logger.error(f"[ADMIN-API] 请求处理失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "code": 500,
            "message": f"获取数据失败: {str(e)}",
            "data": [],
            "pagination": {
                "page": page,
                "size": size,
                "total": 0
            }
        }
