"""
简化版lottery API - 绕过缓存管理器
"""
from fastapi import APIRouter, Query
from typing import Dict, Any, Optional, List
from datetime import timedelta, datetime
from pathlib import Path
import traceback
import logging
import json
import os

# 使用绝对导入
from backend.schemas.response import UnifiedResponse, PageResponse, ErrorResponse
from backend.scrapers.sporttery_scraper import sporttery_scraper

router = APIRouter(prefix="/lottery", tags=["Sports Lottery"])
logger = logging.getLogger(__name__)


def load_500_com_data(filter_day: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    从debug目录加载500彩票网数据 - 使用绝对路径
    """
    try:
        # 使用更可靠的路径计算
        import backend
        backend_dir = Path(backend.__file__).parent
        project_root = backend_dir.parent
        debug_dir = project_root / "debug"
        
        logger.debug(f"[DEBUG] project_root: {project_root}")
        logger.debug(f"[DEBUG] debug_dir: {debug_dir}")
        logger.debug(f"[DEBUG] debug_dir exists: {debug_dir.exists()}")
        
        if not debug_dir.exists():
            logger.warning(f"debug目录不存在: {debug_dir}")
            return []
        
        if not debug_dir.exists():
            logger.error(f"debug目录不存在: {debug_dir}")
            return []
        
        files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
        logger.debug(f"[DEBUG] 找到文件: {files}")
        
        if not files:
            logger.info("没有找到500彩票网数据文件")
            return []
        
        latest_file = sorted(files)[-1]
        file_path = debug_dir / latest_file
        logger.debug(f"[DEBUG] 读取文件: {file_path}")
        logger.debug(f"[DEBUG] 文件存在: {file_path.exists()}")
        
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.debug(f"[DEBUG] 文件大小: {len(content)} 字节")
        
        matches = json.loads(content)
        logger.debug(f"[DEBUG] JSON解析成功，包含 {len(matches)} 条数据")
        
        # 过滤表头
        matches = [m for m in matches if m.get('match_id') != '编号']
        
        # 按星期筛选
        if filter_day:
            matches = [m for m in matches if m.get('match_id', '').startswith(filter_day)]
        
        # 过滤表头
        matches = [m for m in matches if m.get('match_id') != '编号']
        logger.debug(f"[DEBUG] 过滤后剩余 {len(matches)} 条数据")
        
        # 按星期筛选
        if filter_day:
            matches = [m for m in matches if m.get('match_id', '').startswith(filter_day)]
            logger.debug(f"[DEBUG] 按星期筛选后剩余 {len(matches)} 条数据")
        
        # 格式化数据 - 生成数字ID
        formatted_matches = []
        logger.debug(f"[DEBUG] 开始格式化数据...")
        for idx, m in enumerate(matches, 1):
            match_time = m.get("match_time", "")
            match_date = match_time.split(' ')[0] if match_time and ' ' in match_time else match_time
            
            try:
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
            except Exception as e:
                logger.debug(f"[DEBUG] 格式化第 {idx} 条数据失败: {e}")
                logger.debug(f"[DEBUG] 原始数据: {m}")
        
        logger.debug(f"[DEBUG] 最终返回 {len(formatted_matches)} 条格式化数据")
        logger.info(f"成功加载500彩票网数据: {len(formatted_matches)}场比赛")
        return formatted_matches
    except Exception as e:
        logger.error(f"加载500彩票网数据失败: {e}")
        traceback.print_exc()
        return []


@router.get("/matches-simple", response_model=UnifiedResponse[PageResponse[Dict[str, Any]]])
async def get_lottery_matches_simple(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页大小"),
    source: str = Query("500", description="数据源: 500/sporttery"),
    day_filter: Optional[str] = Query(None, description="星期筛选: 周一/周二/周三等")
):
    """
    简化版API - 绕过缓存，直接返回数据
    """
    try:
        logger.info(f"[简化API] 获取竞彩足球数据 (source={source})")
        
        matches = []
        data_source = "unknown"
        
        # 根据数据源选择
        if source == "500":
            matches = load_500_com_data(filter_day=day_filter)
            data_source = "500彩票网"
        elif source == "sporttery":
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
            matches = load_500_com_data(filter_day=day_filter)
            if matches:
                data_source = "500彩票网"
        
        # 排序
        matches.sort(key=lambda x: x.get('match_time', ''), reverse=False)
        
        # 分页
        total_matches = len(matches)
        start_idx = (page - 1) * size
        end_idx = min(start_idx + size, total_matches)
        paginated_matches = matches[start_idx:end_idx]
        
        logger.info(f"[简化API] 返回 {len(paginated_matches)}/{total_matches} 条数据")
        
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
        logger.error(f"[简化API] 获取数据失败: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"获取数据失败: {str(e)}",
            "error": str(e),
            "data": [],
            "total": 0
        }
