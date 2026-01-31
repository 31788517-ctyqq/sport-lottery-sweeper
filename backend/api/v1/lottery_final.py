"""
最终版lottery API - 内联数据加载，确保路径正确
"""
from fastapi import APIRouter, Query
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import logging
import json
import os

from backend.schemas.response import UnifiedResponse, PageResponse

router = APIRouter(prefix="/lottery", tags=["Sports Lottery"])
logger = logging.getLogger(__name__)


def load_500_com_data_direct(filter_day: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    从debug目录加载500彩票网数据 - 最终版本
    使用硬编码路径确保能找到数据文件
    """
    try:
        # 硬编码绝对路径 - 确保能找到
        debug_dir = Path(r"c:\Users\11581\Downloads\sport-lottery-sweeper\debug")
        
        if not debug_dir.exists():
            logger.error(f"[FINAL-LOADER] debug目录不存在: {debug_dir}")
            return []
        
        files = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
        
        if not files:
            logger.warning(f"[FINAL-LOADER] 没有找到500彩票网数据文件")
            return []
        
        latest_file = sorted(files)[-1]
        file_path = debug_dir / latest_file
        
        if not file_path.exists():
            logger.error(f"[FINAL-LOADER] 文件不存在: {file_path}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            matches = json.load(f)
        
        # 过滤表头
        matches = [m for m in matches if m.get('match_id') != '编号']
        
        # 按星期筛选
        if filter_day:
            matches = [m for m in matches if m.get('match_id', '').startswith(filter_day)]
        
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
        
        logger.info(f"[FINAL-LOADER] 成功加载500彩票网数据: {len(formatted_matches)}场比赛")
        return formatted_matches
    except Exception as e:
        logger.error(f"[FINAL-LOADER] 加载500彩票网数据失败: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.get("/matches-final", response_model=UnifiedResponse[PageResponse[Dict[str, Any]]])
async def get_lottery_matches_final(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页大小"),
    source: str = Query("500", description="数据源: 500/sporttery")
):
    """
    最终版API - 内联数据加载，确保路径正确
    """
    try:
        # 硬编码debug目录路径 - 确保能找到
        logger.debug(f"[FINAL-API] === 开始处理 ===")
        logger.debug(f"[FINAL-API] 当前工作目录: {Path.cwd()}")
        logger.debug(f"[FINAL-API] source={source}, page={page}, size={size}")
        
        # 硬编码绝对路径
        debug_dir = Path(r"c:\Users\11581\Downloads\sport-lottery-sweeper\debug")
        logger.debug(f"[FINAL-API] 硬编码debug目录: {debug_dir}")
        logger.debug(f"[FINAL-API] debug目录存在: {debug_dir.exists()}")
        
        matches = []
        data_source = "未知"
        
        if source == "500":
            logger.debug(f"[FINAL-API] 开始加载500彩票数据...")
            
            if debug_dir.exists():
                # 列出所有文件
                all_files = os.listdir(debug_dir)
                logger.debug(f"[FINAL-API] debug目录中文件: {all_files}")
                
                # 查找500彩票数据文件
                files = [f for f in all_files if f.startswith("500_com_matches_")]
                logger.debug(f"[FINAL-API] 匹配文件: {files}")
                
                if files:
                    latest_file = sorted(files)[-1]
                    file_path = debug_dir / latest_file
                    logger.debug(f"[FINAL-API] 使用文件: {file_path}")
                    
                    if file_path.exists():
                        logger.debug(f"[FINAL-API] 读取文件大小: {file_path.stat().st_size} 字节")
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            raw_data = json.load(f)
                        
                        logger.debug(f"[FINAL-API] 加载原始数据: {len(raw_data)} 条")
                        
                        # 过滤和格式化
                        matches = []
                        for idx, item in enumerate(raw_data, 1):
                            if item.get('match_id') == '编号':
                                continue
                            
                            match_time = item.get('match_time', '')
                            match_date = match_time.split(' ')[0] if ' ' in match_time else match_time
                            
                            matches.append({
                                "id": idx,
                                "match_id": str(item.get('match_id', '')),
                                "league": str(item.get('league', '未知联赛')),
                                "home_team": str(item.get('home_team', '主队')),
                                "away_team": str(item.get('away_team', '客队')),
                                "match_time": str(match_time),
                                "match_date": str(match_date),
                                "odds_home_win": float(item.get('odds_home_win', 0) or 0),
                                "odds_draw": float(item.get('odds_draw', 0) or 0),
                                "odds_away_win": float(item.get('odds_away_win', 0) or 0),
                                "status": str(item.get('status', 'scheduled')),
                                "score": str(item.get('score', '-:-')),
                                "popularity": int(item.get('popularity', 70)),
                                "source": "500彩票网"
                            })
                        
                        logger.debug(f"[FINAL-API] 格式化后: {len(matches)} 条数据")
                        data_source = "500彩票网"
                    else:
                        logger.debug(f"[FINAL-API] 错误: 文件不存在")
                else:
                    logger.debug(f"[FINAL-API] 错误: 没有找到匹配文件")
            else:
                logger.debug(f"[FINAL-API] 错误: debug目录不存在")
        elif source == "sporttery":
            # 使用sporttery爬虫
            from backend.scrapers.sporttery_scraper import sporttery_scraper
            try:
                async with sporttery_scraper:
                    raw_matches = await sporttery_scraper.get_recent_matches(7)
                
                for idx, item in enumerate(raw_matches, 1):
                    matches.append({
                        "id": idx,
                        "match_date": str(item.get('match_date', '')),
                        "home_team": str(item.get('home_team', '主队')),
                        "away_team": str(item.get('away_team', '客队')),
                        "league": str(item.get('league', '未知联赛')),
                        "odds_home_win": float(item.get('odds_home_win', 0.0)),
                        "odds_draw": float(item.get('odds_draw', 0.0)),
                        "odds_away_win": float(item.get('odds_away_win', 0.0)),
                        "popularity": int(item.get('popularity', 0)),
                        "status": str(item.get('status', '未开始')),
                        "score": str(item.get('score', '0:0')),
                        "match_time": str(item.get('match_time', '')),
                        "match_id": str(item.get('match_id', '')),
                        "source": "竞彩官网"
                    })
                
                data_source = "竞彩官网"
                logger.debug(f"[FINAL-API] sporttery数据: {len(matches)} 条")
            except Exception as e:
                logger.debug(f"[FINAL-API] sporttery爬虫失败: {e}")
        
        # 排序
        matches.sort(key=lambda x: x.get('match_time', ''), reverse=False)
        
        # 分页
        total = len(matches)
        start = (page - 1) * size
        end = min(start + size, total)
        paginated = matches[start:end]
        
        logger.debug(f"[FINAL-API] 分页: {len(paginated)}/{total} 条 (page={page}, size={size})")
        logger.debug(f"[FINAL-API] === 请求处理完成 ===")
        
        # 计算总页数
        import math
        pages = math.ceil(total / size) if size > 0 else 0
        
        # 构建符合 UnifiedResponse[PageResponse[...]] 模型的响应
        return {
            "code": 200,
            "message": f"成功获取{len(paginated)}场比赛数据",
            "data": {
                "data": paginated,
                "total": total,
                "page": page,
                "size": size,
                "pages": pages,
                "timestamp": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.debug(f"[FINAL-API] === 请求处理失败 ===")
        logger.debug(f"[FINAL-API] 错误: {e}")
        import traceback
        traceback.print_exc()
        # 错误响应也需要符合模型
        return {
            "code": 500,
            "message": f"获取数据失败: {str(e)}",
            "data": {
                "data": [],
                "total": 0,
                "page": page,
                "size": size,
                "pages": 0,
                "timestamp": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
