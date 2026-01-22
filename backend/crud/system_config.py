"""
系统配置CRUD操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List

from ..models import SystemConfig
from ..schemas import SystemConfigCreate, SystemConfigUpdate


def get(db: Session, id: int) -> Optional[SystemConfig]:
    """根据ID获取系统配置"""
    return db.query(SystemConfig).filter(SystemConfig.id == id).first()


def get_by_key(db: Session, config_key: str) -> Optional[SystemConfig]:
    """根据键名获取系统配置"""
    return db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[SystemConfig]:
    """获取多条系统配置"""
    return db.query(SystemConfig).offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: SystemConfigCreate) -> SystemConfig:
    """创建系统配置"""
    db_obj = SystemConfig(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: SystemConfig, obj_in: SystemConfigUpdate) -> SystemConfig:
    """更新系统配置"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, id: int) -> SystemConfig:
    """删除系统配置"""
    obj = db.query(SystemConfig).get(id)
    db.delete(obj)
    db.commit()
    return obj