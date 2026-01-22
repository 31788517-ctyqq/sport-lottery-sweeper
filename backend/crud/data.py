"""
数据管理CRUD操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List

from ..models import AdminData
from ..schemas import AdminDataCreate, AdminDataUpdate


def get(db: Session, id: int) -> Optional[AdminData]:
    """根据ID获取数据记录"""
    return db.query(AdminData).filter(AdminData.id == id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[AdminData]:
    """获取多条数据记录"""
    return db.query(AdminData).offset(skip).limit(limit).all()


def get_by_category(db: Session, category: str, skip: int = 0, limit: int = 100) -> List[AdminData]:
    """根据分类获取数据记录"""
    return db.query(AdminData).filter(AdminData.category == category).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: AdminDataCreate) -> AdminData:
    """创建数据记录"""
    db_obj = AdminData(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: AdminData, obj_in: AdminDataUpdate) -> AdminData:
    """更新数据记录"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, id: int) -> AdminData:
    """删除数据记录"""
    obj = db.query(AdminData).get(id)
    db.delete(obj)
    db.commit()
    return obj