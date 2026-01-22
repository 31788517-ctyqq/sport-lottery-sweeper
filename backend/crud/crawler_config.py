"""
爬虫配置CRUD操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List

from ..models import CrawlerConfig
from ..schemas import CrawlerConfigCreate, CrawlerConfigUpdate


def get(db: Session, id: int) -> Optional[CrawlerConfig]:
    """根据ID获取爬虫配置"""
    return db.query(CrawlerConfig).filter(CrawlerConfig.id == id).first()


def get_by_name(db: Session, name: str) -> Optional[CrawlerConfig]:
    """根据名称获取爬虫配置"""
    return db.query(CrawlerConfig).filter(CrawlerConfig.name == name).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[CrawlerConfig]:
    """获取多条爬虫配置"""
    return db.query(CrawlerConfig).offset(skip).limit(limit).all()


def get_enabled_configs(db: Session) -> List[CrawlerConfig]:
    """获取启用的爬虫配置"""
    return db.query(CrawlerConfig).filter(CrawlerConfig.enabled == True).all()


def create(db: Session, *, obj_in: CrawlerConfigCreate) -> CrawlerConfig:
    """创建爬虫配置"""
    db_obj = CrawlerConfig(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: CrawlerConfig, obj_in: CrawlerConfigUpdate) -> CrawlerConfig:
    """更新爬虫配置"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, id: int) -> CrawlerConfig:
    """删除爬虫配置"""
    obj = db.query(CrawlerConfig).get(id)
    db.delete(obj)
    db.commit()
    return obj