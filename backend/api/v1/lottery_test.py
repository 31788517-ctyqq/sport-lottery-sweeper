"""
工作版lottery API - 基于测试成功的经验，修复实际数据加载
"""
from fastapi import APIRouter, Query
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
import json
import os

from backend.schemas.response import UnifiedResponse, PageResponse
from datetime import datetime

router = APIRouter(prefix="/lottery", tags=["Sports Lottery"])
logger = logging.getLogger(__name__)


def load_500_com_data_working(filter_day: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    工作版数据加载函数 - 基于测试成功的代码
    """
    try:
        # 使用测试成功的硬编码路径
        debug_dir = Path(r"c:\Users\11581\Downloads\sport-lottery-sweeper\debug")
        
        if not debug_dir.exists():
            logger.error(f"[WORKING-LOADER] debug目录不存在: {debug_dir}")
            return []
        
        # 使用测试成功的文件查找方式
        all_files = os.listdir(debug_dir)
        files = [f for f in all_files if f.startswith("500_com_matches_")]
        
        if not files:
            logger.warning(f"[WORKING-LOADER] 没有找到500彩票网数据文件")
            return []
        
        # 按修改时间排序，获取最新的有效文件
        files_with_time = []
        for f in files:
            file_path = debug_dir / f
            try:
                mtime = file_path.stat().st_mtime
                files_with_time.append((f, mtime))
            except Exception:
                continue
        
        if not files_with_time:
            logger.warning(f"[WORKING-LOADER] 无法获取文件时间信息")
            return []
        
        # 按修改时间降序排序
        files_with_time.sort(key=lambda x: x[1], reverse=True)
        
        # 尝试每个文件直到成功
        for f, _ in files_with_time:
            file_path = debug_dir / f
            try:
                if not file_path.exists():
                    logger.warning(f"[WORKING-LOADER] 文件不存在: {file_path}")
                    continue
                    
                if file_path.stat().st_size == 0:
                    logger.warning(f"[WORKING-LOADER] 文件为空: {file_path}")
                    continue
                
                # 读取并解析JSON（测试证明此方法有效）
                with open(file_path, 'r', encoding='utf-8') as file:
                    raw_data = json.load(file)
                
                logger.info(f"[WORKING-LOADER] 成功加载文件: {file_path}, {len(raw_data)} 条数据")
                
                # 过滤和格式化（简化版，减少出错可能）
                matches = []
                for idx, item in enumerate(raw_data, 1):
                    if item.get('match_id') == '编号':
                        continue
                    
                    match_time = item.get('match_time', '')
                    match_date = match_time.split(' ')[0] if ' ' in match_time else match_time
                    
                    # 确保所有字段都有值，避免KeyError
                    matches.append({
                        "id": idx,
                        "match_id": str(item.get('match_id', f'UNKNOWN_{idx}')),
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
                
                logger.info(f"[WORKING-LOADER] 格式化完成，返回 {len(matches)} 条数据")
                return matches
            except json.JSONDecodeError as e:
                logger.warning(f"[WORKING-LOADER] 文件 {f} JSON解析失败: {e}，尝试下一个文件")
                continue
            except Exception as e:
                logger.warning(f"[WORKING-LOADER] 文件 {f} 处理失败: {e}，尝试下一个文件")
                continue
        
        logger.error(f"[WORKING-LOADER] 所有文件都处理失败")
        return []
        
    except Exception as e:
        logger.error(f"[WORKING-LOADER] 加载数据失败: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.get("/matches", response_model=UnifiedResponse[PageResponse[Dict[str, Any]]])
async def get_lottery_matches(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页大小"),
    source: str = Query("500", description="数据源: 500/sporttery")
):
    """
    获取竞彩足球比赛数据 - 工作版本
    """
    try:
        matches = []
        data_source = "未知"
        
        if source == "500":
            matches = load_500_com_data_working()
            data_source = "500彩票网"
        
        # 排序
        matches.sort(key=lambda x: x.get('match_time', ''), reverse=False)
        
        # 分页
        total = len(matches)
        start = (page - 1) * size
        end = min(start + size, total)
        paginated = matches[start:end]
        
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
        logger.error(f"获取数据失败: {e}")
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


@router.get("/test-db")
async def test_debug_directory():
    """
    测试debug目录访问
    """
    import os
    from pathlib import Path
    
    debug_dir = Path(r"c:\Users\11581\Downloads\sport-lottery-sweeper\debug")
    
    result = {
        "debug_dir": str(debug_dir),
        "exists": debug_dir.exists(),
        "files": []
    }
    
    if debug_dir.exists():
        result["files"] = [f for f in os.listdir(debug_dir) if f.startswith("500_com_matches_")]
    
    return result
