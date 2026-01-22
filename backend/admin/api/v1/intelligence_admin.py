"""
智能分析记录管理模块
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ....core.database import get_db
from ....crud.intelligence_record import IntelligenceRecord as crud_intelligence_record
from ..deps import get_current_admin

router = APIRouter()


@router.get("/intelligence-records", response_model=List[dict])
async def get_intelligence_records(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """获取智能分析记录列表"""
    try:
        records = crud_intelligence_record.get_multi(db, limit=100)
        return [
            {
                "id": record.id,
                "analysis_type": record.analysis_type,
                "target_data": record.target_data,
                "result_summary": record.result_summary,
                "confidence_score": record.confidence_score,
                "model_used": record.model_used,
                "processing_time_ms": record.processing_time_ms,
                "status": record.status,
                "created_at": record.created_at.isoformat() if record.created_at else None
            }
            for record in records
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取智能分析记录失败: {str(e)}")


@router.post("/intelligence-records", response_model=dict)
async def create_intelligence_record(
    record_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """创建智能分析记录"""
    try:
        record = crud_intelligence_record.create(db, obj_in=record_data)
        return {
            "id": record.id,
            "analysis_type": record.analysis_type,
            "status": record.status,
            "message": "智能分析记录创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建智能分析记录失败: {str(e)}")


@router.delete("/intelligence-records/{record_id}")
async def delete_intelligence_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """删除智能分析记录"""
    try:
        success = crud_intelligence_record.remove(db, id=record_id)
        if not success:
            raise HTTPException(status_code=404, detail="智能分析记录不存在")
        return {"message": "智能分析记录删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除智能分析记录失败: {str(e)}")