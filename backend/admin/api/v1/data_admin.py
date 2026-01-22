"""
数据管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...deps import get_current_admin
from .... import crud
from ....schemas.match import MatchResponse
from ....api.deps import get_db
from ....models.match import Match

router = APIRouter()


@router.get("/matches/", response_model=list[MatchResponse])
async def read_matches(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """
    获取比赛列表
    """
    matches = await crud.match.get_multi(db, skip=skip, limit=limit)
    return matches


@router.get("/matches/{match_id}", response_model=MatchResponse)
async def read_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """
    获取指定比赛信息
    """
    match = await crud.match.get(db, id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail="比赛不存在")
    return match


@router.put("/matches/{match_id}/approve")
async def approve_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """
    审核通过比赛数据
    """
    match = await crud.match.get(db, id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail="比赛不存在")
    
    # 更新审核状态
    match.status = "approved"  # 假设有一个status字段表示审核状态
    await db.commit()
    await db.refresh(match)
    
    return {"message": "比赛数据审核通过"}


@router.delete("/matches/{match_id}")
async def delete_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """
    删除比赛数据
    """
    match = await crud.match.get(db, id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail="比赛不存在")
    await crud.match.remove(db, id=match_id)
    return {"message": "比赛数据删除成功"}