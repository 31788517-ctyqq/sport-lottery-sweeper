"""
数据审核API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime

from ....api.deps import get_db
from ....models.data_review import DataReview, DataTypeEnum, ReviewStatusEnum
from ....models.user import User
from ...deps import get_current_admin

# 临时定义UnifiedResponse和PageResponse，因为可能不存在
from pydantic import BaseModel

class UnifiedResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def success(cls, data: Any, message: str = "操作成功"):
        return cls(success=True, data=data, message=message)

    @classmethod
    def error(cls, message: str, error_code: Optional[str] = None):
        return cls(success=False, message=message, error={"code": error_code, "message": message})

class PageResponse(BaseModel):
    data: List[Any]
    total: int
    page: int
    size: int

router = APIRouter(prefix="/reviews", tags=["admin-reviews"])


@router.get("/", response_model=UnifiedResponse)
async def list_pending_reviews(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    data_type: Optional[str] = Query(None, description="数据类型过滤"),
    status: Optional[str] = Query(None, description="审核状态过滤"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取待审核数据列表
    """
    try:
        from sqlalchemy import select, func
        
        # 构建查询条件
        query = select(DataReview).join(User, DataReview.created_by == User.id, isouter=True)
        
        if data_type:
            query = query.where(DataReview.data_type == DataTypeEnum(data_type))
        if status:
            query = query.where(DataReview.review_status == ReviewStatusEnum(status))
        
        # 获取总数
        count_query = select(func.count(DataReview.id))
        if data_type:
            count_query = count_query.where(DataReview.data_type == DataTypeEnum(data_type))
        if status:
            count_query = count_query.where(DataReview.review_status == ReviewStatusEnum(status))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # 分页查询
        offset = (page - 1) * size
        query = query.offset(offset).limit(size).order_by(DataReview.created_at.desc())
        result = await db.execute(query)
        reviews = result.scalars().all()
        
        # 将SQLAlchemy模型转换为字典
        review_list = [
            {
                "id": review.id,
                "data_type": review.data_type.value if hasattr(review.data_type, 'value') else review.data_type,
                "original_data": review.original_data,
                "processed_data": review.processed_data,
                "review_status": review.review_status.value if hasattr(review.review_status, 'value') else review.review_status,
                "review_notes": review.review_notes,
                "is_published": review.is_published,
                "external_id": review.external_id,
                "external_source": review.external_source,
                "created_at": review.created_at.isoformat() if review.created_at else None,
                "updated_at": review.updated_at.isoformat() if review.updated_at else None,
                "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None,
                "published_at": review.published_at.isoformat() if review.published_at else None,
                "created_by": review.created_by,
                "reviewed_by": review.reviewed_by
            }
            for review in reviews
        ]
        
        return UnifiedResponse.success({
            "data": review_list,
            "total": total,
            "page": page,
            "size": size
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{review_id}", response_model=UnifiedResponse)
async def get_review_detail(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取审核详情
    """
    try:
        from sqlalchemy import select
        
        result = await db.execute(
            select(DataReview)
            .where(DataReview.id == review_id)
        )
        review = result.scalar_one_or_none()
        
        if not review:
            raise HTTPException(status_code=404, detail="审核项不存在")
        
        # 构造返回数据
        detail_data = {
            "id": review.id,
            "data_type": review.data_type.value,
            "original_data": review.original_data,
            "processed_data": review.processed_data,
            "review_status": review.review_status.value,
            "review_notes": review.review_notes,
            "is_published": review.is_published,
            "external_id": review.external_id,
            "external_source": review.external_source,
            "created_at": review.created_at.isoformat() if review.created_at else None,
            "updated_at": review.updated_at.isoformat() if review.updated_at else None,
            "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None,
            "published_at": review.published_at.isoformat() if review.published_at else None,
            "creator": {
                "id": review.created_by,
                "username": "unknown"  # 在实际实现中，需要获取创建者信息
            },
            "reviewer": {
                "id": review.reviewed_by,
                "username": "unknown"  # 在实际实现中，需要获取审核者信息
            } if review.reviewed_by else None
        }
        
        return UnifiedResponse.success(detail_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{review_id}/approve", response_model=UnifiedResponse)
async def approve_review(
    review_id: int,
    notes: Optional[str] = Query(None, description="审核备注"),
    db: AsyncSession = Depends(get_db)
):
    """
    批准数据审核
    """
    try:
        from sqlalchemy import select
        
        result = await db.execute(
            select(DataReview).where(DataReview.id == review_id)
        )
        review = result.scalar_one_or_none()
        
        if not review:
            raise HTTPException(status_code=404, detail="审核项不存在")
        
        if review.review_status != "pending":
            raise HTTPException(status_code=400, detail="该数据不是待审核状态")
        
        # 执行批准操作
        review.review_status = "approved"
        review.review_notes = notes
        review.reviewed_at = datetime.utcnow()
        await db.commit()
        
        return UnifiedResponse.success({
            "message": "数据已批准",
            "review_id": review_id,
            "new_status": "approved"
        })
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{review_id}/reject", response_model=UnifiedResponse)
async def reject_review(
    review_id: int,
    notes: str = Query(..., description="拒绝原因"),
    db: AsyncSession = Depends(get_db)
):
    """
    拒绝数据审核
    """
    try:
        from sqlalchemy import select
        
        result = await db.execute(
            select(DataReview).where(DataReview.id == review_id)
        )
        review = result.scalar_one_or_none()
        
        if not review:
            raise HTTPException(status_code=404, detail="审核项不存在")
        
        if review.review_status != "pending":
            raise HTTPException(status_code=400, detail="该数据不是待审核状态")
        
        # 执行拒绝操作
        review.review_status = "rejected"
        review.review_notes = notes
        review.reviewed_at = datetime.utcnow()
        await db.commit()
        
        return UnifiedResponse.success({
            "message": "数据已拒绝",
            "review_id": review_id,
            "new_status": "rejected",
            "notes": notes
        })
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{review_id}/modify", response_model=UnifiedResponse)
async def modify_review(
    review_id: int,
    processed_data: Dict[str, Any] = Body(..., description="处理后的数据"),
    notes: Optional[str] = Query(None, description="修改备注"),
    db: AsyncSession = Depends(get_db)
):
    """
    修改数据并批准
    """
    try:
        from sqlalchemy import select
        
        result = await db.execute(
            select(DataReview).where(DataReview.id == review_id)
        )
        review = result.scalar_one_or_none()
        
        if not review:
            raise HTTPException(status_code=404, detail="审核项不存在")
        
        # 执行修改操作
        review.processed_data = processed_data
        review.review_status = "modified"
        if notes:
            review.review_notes = notes
        review.reviewed_at = datetime.utcnow()
        await db.commit()
        
        return UnifiedResponse.success({
            "message": "数据已修改并批准",
            "review_id": review_id,
            "new_status": "modified"
        })
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))