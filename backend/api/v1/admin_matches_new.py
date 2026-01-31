"""
管理员比赛数据路由 - 最终版本
直接内联数据加载，不依赖外部函数
"""
from fastapi import APIRouter, Query
from typing import Dict, Any, Optional, List
import logging
import json
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/admin/matches", tags=["admin-matches"])
logger = logging.getLogger(__name__)


def load_500_com_data_inline() -> List[Dict[str, Any]]:
    """
    内联加载500彩票网数据 - 不依赖外部函数
    """
    try:
        # 硬编码绝对路径
        debug_dir = Path(r"c:\Users\11581\Downloads\sport-lottery-sweeper\debug")
        
        if not debug_dir.exists():
            logger.error(f"[INLINE-LOADER] debug目录不存在: {debug_dir}")
            return []
        
        files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
        
        if not files:
            logger.warning(f"[INLINE-LOADER] 没有找到500彩票网数据文件")
            return []
        
        latest_file = sorted(files)[-1]
        file_path = debug_dir / latest_file
        
        if not file_path.exists():
            logger.error(f"[INLINE-LOADER] 文件不存在: {file_path}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            matches = json.load(f)
        
        # 过滤表头
        matches = [m for m in matches if m.get('match_id') != '编号']
        
        # 格式化数据
        formatted_matches = []
        for idx, m in enumerate(matches, 1):
            match_time = m.get("match_time", "")
            match_date = match_time.split(' ')[0] if match_time and ' ' in match_time else match_time
            
            formatted_matches.append({
                "id": idx,
                "match_id": m.get("match_id"),
                "league": m.get("league"),
                "home_team": m.get("home_team"),
                "away_team": m.get("away_team"),
                "match_time": match_time,
                "match_date": match_date,
                "odds_home_win": m.get("odds_home_win", 0),
                "odds_draw": m.get("odds_draw", 0),
                "odds_away_win": m.get("odds_away_win", 0),
                "status": m.get("status", "scheduled"),
                "score": m.get("score", "-:-"),
                "popularity": m.get("popularity", 70),
                "source": "500彩票网"
            })
        
        logger.info(f"[INLINE-LOADER] 成功加载500彩票网数据: {len(formatted_matches)}场比赛")
        return formatted_matches
    except Exception as e:
        logger.error(f"[INLINE-LOADER] 加载500彩票网数据失败: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.get("")
async def admin_get_matches(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    source: str = Query("500", description="数据源: 500/sporttery")
):
    """
    管理员获取比赛数据 - 内联数据加载
    支持从500彩票网获取数据
    """
    try:
        logger.debug(f"[ADMIN-INLINE] 收到请求，source={source}")
        
        matches = []
        
        if source == "500":
            logger.debug(f"[ADMIN-INLINE] 调用内联加载函数...")
            matches = load_500_com_data_inline()
            logger.debug(f"[ADMIN-INLINE] 加载完成，返回 {len(matches)} 条数据")
        elif source == "sporttery":
            # 使用sporttery爬虫
            from backend.scrapers.sporttery_scraper import sporttery_scraper
            try:
                async with sporttery_scraper:
                    raw_matches = await sporttery_scraper.get_recent_matches(7)
                matches = [
                    {
                        "id": idx,
                        "match_id": str(m.get('match_id', '')),
                        "league": str(m.get('league', '未知联赛')),
                        "home_team": str(m.get('home_team', '主队')),
                        "away_team": str(m.get('away_team', '客队')),
                        "match_time": str(m.get('match_time', '')),
                        "match_date": str(m.get('match_date', '')),
                        "odds_home_win": float(m.get('odds_home_win', 0.0)),
                        "odds_draw": float(m.get('odds_draw', 0.0)),
                        "odds_away_win": float(m.get('odds_away_win', 0.0)),
                        "status": str(m.get('status', '未开始')),
                        "score": str(m.get('score', '0:0')),
                        "popularity": int(m.get('popularity', 0)),
                        "source": "竞彩官网"
                    }
                    for idx, m in enumerate(raw_matches, 1)
                ]
                logger.debug(f"[ADMIN-INLINE] sporttery数据: {len(matches)} 条")
            except Exception as e:
                logger.debug(f"[ADMIN-INLINE] sporttery爬虫失败: {e}")
                matches = []
        
        # 排序
        matches.sort(key=lambda x: x.get('match_time', ''), reverse=False)
        
        # 分页
        total_matches = len(matches)
        start_idx = (page - 1) * size
        end_idx = min(start_idx + size, total_matches)
        paginated_matches = matches[start_idx:end_idx]
        
        logger.debug(f"[ADMIN-INLINE] 分页: {len(paginated_matches)}/{total_matches} 条")
        
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
        logger.debug(f"[ADMIN-INLINE] === 请求处理失败 ===")
        logger.debug(f"[ADMIN-INLINE] 错误: {e}")
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
