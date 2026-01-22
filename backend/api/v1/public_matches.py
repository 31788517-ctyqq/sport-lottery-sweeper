"""
公共比赛数据API端点
提供无需认证的比赛信息给前端
"""
from typing import List
from fastapi import APIRouter, HTTPException
from ...schemas.match import MatchResponse
from ...services.crawler_integration import crawler_service

router = APIRouter()


@router.get("/", response_model=List[MatchResponse])
async def get_public_matches():
    """
    获取公共比赛数据
    """
    try:
        matches = await crawler_service.get_recent_matches()
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取比赛数据失败: {str(e)}")


@router.get("/popular", response_model=List[MatchResponse])
async def get_popular_matches():
    """
    获取热门比赛数据
    """
    try:
        matches = await crawler_service.get_popular_matches()
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门比赛数据失败: {str(e)}")