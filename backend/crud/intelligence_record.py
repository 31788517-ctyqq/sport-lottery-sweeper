"""
智能分析记录CRUD操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List

from ..models import IntelligenceRecord
from ..schemas import IntelligenceRecordCreate, IntelligenceRecordUpdate


def get(db: Session, id: int) -> Optional[IntelligenceRecord]:
    """根据ID获取智能分析记录"""
    return db.query(IntelligenceRecord).filter(IntelligenceRecord.id == id).first()


def get_by_analysis_type(db: Session, analysis_type: str, skip: int = 0, limit: int = 100) -> List[IntelligenceRecord]:
    """根据分析类型获取智能分析记录"""
    return db.query(IntelligenceRecord).filter(IntelligenceRecord.analysis_type == analysis_type).offset(skip).limit(limit).all()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[IntelligenceRecord]:
    """获取多条智能分析记录"""
    return db.query(IntelligenceRecord).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: IntelligenceRecordCreate) -> IntelligenceRecord:
    """创建智能分析记录"""
    db_obj = IntelligenceRecord(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: IntelligenceRecord, obj_in: IntelligenceRecordUpdate) -> IntelligenceRecord:
    """更新智能分析记录"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, id: int) -> IntelligenceRecord:
    """删除智能分析记录"""
    obj = db.query(IntelligenceRecord).get(id)
    db.delete(obj)
    db.commit()
    return obj