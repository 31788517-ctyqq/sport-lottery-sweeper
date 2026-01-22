"""
数据提交API端点
允许爬虫或其他数据源提交数据到审核系统
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...database import get_db
from ...models import DataReview
from ...models.data_review import DataTypeEnum, ReviewStatusEnum
from ...schemas.response import UnifiedResponse, PageResponse, ErrorResponse

router = APIRouter(tags=["data-submission"])


@router.post("/", response_model=UnifiedResponse[Dict[str, Any]])
async def submit_data(
    data_type: str = Query(..., description="数据类型"),
    external_source: Optional[str] = Query(None, description="数据来源"),
    external_id: Optional[str] = Query(None, description="外部ID"),
    original_data: Dict[str, Any] = Body(..., description="原始数据"),
    db: AsyncSession = Depends(get_db)
):
    """
    提交数据到审核系统
    """
    try:
        from sqlalchemy import select
        
        # 验证数据类型
        try:
            data_type_enum = DataTypeEnum(data_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的数据类型")
        
        # 检查是否已存在相同外部ID的数据
        if external_id:
            existing_query = select(DataReview).where(
                DataReview.external_id == external_id,
                DataReview.external_source == external_source
            )
            result = await db.execute(existing_query)
            existing = result.scalar_one_or_none()
            
            if existing:
                raise HTTPException(status_code=409, detail="该数据已存在，请勿重复提交")
        
        # 创建数据审核记录
        review = DataReview(
            data_type=data_type_enum,
            original_data=original_data,
            processed_data=original_data,  # 初始处理数据与原始数据相同
            external_source=external_source,
            external_id=external_id,
            review_status=ReviewStatusEnum.PENDING,
            is_published=False
        )
        
        db.add(review)
        await db.commit()
        await db.refresh(review)
        
        return UnifiedResponse.success({
            "message": "数据提交成功，等待审核",
            "review_id": review.id,
            "data_type": data_type_enum.value,
            "submitted_at": review.created_at.isoformat() if review.created_at else None
        })
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"提交数据失败: {str(e)}")


@router.get("/pending/count", response_model=UnifiedResponse[Dict[str, int]])
async def get_pending_count(
    db: AsyncSession = Depends(get_db)
):
    """
    获取待审核数据数量
    """
    try:
        from sqlalchemy import select, func
        
        # 获取各类型待审核数据数量
        pending_query = select(
            DataReview.data_type,
            func.count(DataReview.id).label('count')
        ).where(
            DataReview.review_status == ReviewStatusEnum.PENDING
        ).group_by(DataReview.data_type)
        
        result = await db.execute(pending_query)
        counts = result.all()
        
        # 构建返回数据
        count_dict = {}
        for row in counts:
            count_dict[row[0].value] = row[1]
        
        # 确保所有数据类型都有计数（即使为0）
        for data_type in DataTypeEnum:
            if data_type.value not in count_dict:
                count_dict[data_type.value] = 0
        
        total_pending = sum(count_dict.values())
        count_dict['total'] = total_pending
        
        return UnifiedResponse.success(count_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", response_model=UnifiedResponse[List[Dict[str, Any]]])
async def get_recent_submissions(
    limit: int = Query(10, ge=1, le=100, description="返回数量限制"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取最近提交的数据
    """
    try:
        from sqlalchemy import select
        
        query = select(DataReview).order_by(DataReview.created_at.desc()).limit(limit)
        result = await db.execute(query)
        submissions = result.scalars().all()
        
        submission_list = []
        for sub in submissions:
            submission_list.append({
                "id": sub.id,
                "data_type": sub.data_type.value,
                "review_status": sub.review_status.value,
                "is_published": sub.is_published,
                "external_source": sub.external_source,
                "external_id": sub.external_id,
                "created_at": sub.created_at.isoformat() if sub.created_at else None
            })
        
        return UnifiedResponse.success(submission_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))