"""
直接返回数据的lottery API - 最终版本
"""
from fastapi import APIRouter, Query
from typing import Dict, Any, Optional, List
from datetime import timedelta, datetime
from pathlib import Path
import traceback
import logging
import json
import os
import sys

# 使用绝对导入
from backend.schemas.response import UnifiedResponse, PageResponse, ErrorResponse
from backend.scrapers.sporttery_scraper import sporttery_scraper

router = APIRouter(prefix="/lottery", tags=["Sports Lottery"])
logger = logging.getLogger(__name__)


def load_500_com_data_direct(filter_day: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    从debug目录加载500彩票网数据 - 直接返回版本
    """
    try:
        # 打印当前工作目录到控制台
        current_work_dir = Path.cwd()
        logger.debug(f"[DIRECT-LOAD] 当前工作目录: {current_work_dir}")
        
        # 方法1: 使用项目根目录
        project_root = Path.cwd().parent if Path.cwd().name == "backend" else Path.cwd()
        debug_dir = project_root / "debug"
        
        logger.debug(f"[DIRECT-LOAD] 方法1 - project_root: {project_root}")
        logger.debug(f"[DIRECT-LOAD] 方法1 - debug_dir: {debug_dir}")
        logger.debug(f"[DIRECT-LOAD] 方法1 - debug_dir存在: {debug_dir.exists()}")
        
        # 如果方法1失败，尝试方法2
        if not debug_dir.exists():
            # 方法2: 使用绝对路径
            project_root = Path(r"c:\Users\11581\Downloads\sport-lottery-sweeper")
            debug_dir = project_root / "debug"
            logger.debug(f"[DIRECT-LOAD] 方法2 - project_root: {project_root}")
            logger.debug(f"[DIRECT-LOAD] 方法2 - debug_dir: {debug_dir}")
            logger.debug(f"[DIRECT-LOAD] 方法2 - debug_dir存在: {debug_dir.exists()}")
        
        if not debug_dir.exists():
            logger.error(f"[DIRECT-LOAD] debug目录不存在: {debug_dir}")
            return []
        
        # 列出debug目录中的所有文件
        all_files = os.listdir(debug_dir)
        logger.debug(f"[DIRECT-LOAD] debug目录中所有文件: {all_files}")
        
        files = [f for f in all_files if f.startswith("500_com_matches_")]
        logger.debug(f"[DIRECT-LOAD] 匹配文件: {files}")
        
        if not files:
            logger.warning(f"[DIRECT-LOAD] 没有找到500彩票网数据文件")
            return []
        
        # 获取最新文件
        latest_file = sorted(files)[-1]
        file_path = debug_dir / latest_file
        logger.debug(f"[DIRECT-LOAD] 使用文件: {file_path}")
        logger.debug(f"[DIRECT-LOAD] 文件绝对路径: {file_path.absolute()}")
        logger.debug(f"[DIRECT-LOAD] 文件存在: {file_path.exists()}")
        
        if not file_path.exists():
            logger.error(f"[DIRECT-LOAD] 文件不存在: {file_path}")
            return []
        
        # 读取文件
        logger.debug(f"[DIRECT-LOAD] 正在读取文件...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.debug(f"[DIRECT-LOAD] 读取成功，大小: {len(content)} 字节")
        
        # 解析JSON
        matches = json.loads(content)
        logger.debug(f"[DIRECT-LOAD] JSON解析成功，包含 {len(matches)} 条数据")
        
        # 打印前几条数据
        if matches:
            logger.debug(f"[DIRECT-LOAD] 第一条原始数据: {matches[0]}")
        
        # 过滤表头
        matches = [m for m in matches if m.get('match_id') != '编号']
        logger.debug(f"[DIRECT-LOAD] 过滤表头后剩余 {len(matches)} 条数据")
        
        # 按星期筛选
        if filter_day:
            matches = [m for m in matches if m.get('match_id', '').startswith(filter_day)]
            logger.debug(f"[DIRECT-LOAD] 按星期筛选后剩余 {len(matches)} 条数据")
        
        # 格式化数据 - 生成数字ID
        formatted_matches = []
        logger.debug(f"[DIRECT-LOAD] 开始格式化数据...")
        
        for idx, m in enumerate(matches, 1):
            try:
                match_time = m.get("match_time", "")
                match_date = match_time.split(' ')[0] if match_time and ' ' in match_time else match_time
                
                # 确保所有必需字段存在
                match_data = {
                    "id": idx,
                    "match_id": str(m.get("match_id", "")),
                    "league": str(m.get("league", "未知联赛")),
                    "home_team": str(m.get("home_team", "主队")),
                    "away_team": str(m.get("away_team", "客队")),
                    "match_time": str(match_time),
                    "match_date": str(match_date),
                    "odds_home_win": float(m.get("odds_home_win", 0) or 0),
                    "odds_draw": float(m.get("odds_draw", 0) or 0),
                    "odds_away_win": float(m.get("odds_away_win", 0) or 0),
                    "status": str(m.get("status", "scheduled")),
                    "score": str(m.get("score", "-:-")),
                    "popularity": int(m.get("popularity", 70)),
                    "source": "500彩票网"
                }
                formatted_matches.append(match_data)
                
                # 打印前3条格式化后的数据
                if idx <= 3:
                    logger.debug(f"[DIRECT-LOAD] 格式化第{idx}条: ID={match_data['id']}, match_id={match_data['match_id']}")
            except Exception as e:
                logger.debug(f"[DIRECT-LOAD] 格式化第{idx}条失败: {e}")
                logger.debug(f"[DIRECT-LOAD] 原始数据: {m}")
        
        logger.debug(f"[DIRECT-LOAD] 最终返回 {len(formatted_matches)} 条格式化数据")
        return formatted_matches
        
    except Exception as e:
        logger.error(f"[DIRECT-LOAD] 加载数据失败: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.get("/matches-direct", response_model=UnifiedResponse[PageResponse[Dict[str, Any]]])
async def get_lottery_matches_direct(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页大小"),
    source: str = Query("500", description="数据源: 500/sporttery")
):
    """
    直接返回数据的API - 不使用缓存，直接加载
    """
    try:
        logger.debug(f"[DIRECT-API] === 开始处理请求 ===")
        logger.debug(f"[DIRECT-API] source={source}, page={page}, size={size}")
        
        matches = []
        data_source = "unknown"
        
        if source == "500":
            logger.debug(f"[DIRECT-API] 调用load_500_com_data_direct()...")
            matches = load_500_com_data_direct()
            logger.debug(f"[DIRECT-API] load_500_com_data_direct() 返回 {len(matches)} 条数据")
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
                logger.error(f"[DIRECT-API] 竞彩官网爬虫失败: {e}")
                matches = []
        else:
            matches = load_500_com_data_direct()
            if matches:
                data_source = "500彩票网"
        
        # 排序
        matches.sort(key=lambda x: x.get('match_time', ''), reverse=False)
        
        # 分页
        total_matches = len(matches)
        start_idx = (page - 1) * size
        end_idx = min(start_idx + size, total_matches)
        paginated_matches = matches[start_idx:end_idx]
        
        logger.debug(f"[DIRECT-API] 总共 {total_matches} 条，返回 {len(paginated_matches)} 条")
        logger.debug(f"[DIRECT-API] === 请求处理完成 ===")
        
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
        logger.debug(f"[DIRECT-API] === 请求处理失败 ===")
        logger.debug(f"[DIRECT-API] 错误: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"获取数据失败: {str(e)}",
            "error": str(e),
            "data": [],
            "total": 0
        }
