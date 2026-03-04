from sqlalchemy.orm import Session
from typing import List
from ..models.hedging import HedgingOpportunity, HedgingConfig
from ..schemas.hedging import (
    HedgingOpportunityCreate,
    HedgingConfigCreate,
    HedgingConfig
)


def get_hedging_opportunities_by_date(
    db: Session,
    date: str,
    min_profit_rate: float = 0.02,
    skip: int = 0,
    limit: int = 100
) -> List[HedgingOpportunity]:
    """根据日期获取对冲机会，筛选利润率大于min_profit_rate的记录"""
    return (
        db.query(HedgingOpportunity)
        .filter(HedgingOpportunity.date.like(f"{date}%"))
        .filter(HedgingOpportunity.profit_rate >= min_profit_rate)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_hedging_config(db: Session, config_id: int) -> HedgingConfig:
    """获取对冲配置"""
    return db.query(HedgingConfig).filter(HedgingConfig.id == config_id).first()


def get_default_hedging_config(db: Session) -> HedgingConfig:
    """获取默认对冲配置"""
    config = db.query(HedgingConfig).first()
    if config is None:
        # 如果没有配置，则创建一个默认配置
        config = HedgingConfig(
            min_profit_rate=0.02,
            commission_rate=0.8,
            cost_factor=0.2
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def create_hedging_opportunity(
    db: Session,
    opportunity: HedgingOpportunityCreate
) -> HedgingOpportunity:
    """创建对冲机会记录"""
    db_opportunity = HedgingOpportunity(**opportunity.dict())
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity


def create_hedging_config(
    db: Session,
    config: HedgingConfigCreate
) -> HedgingConfig:
    """创建对冲配置"""
    db_config = HedgingConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def update_hedging_config(
    db: Session,
    config_id: int,
    config: HedgingConfigCreate
) -> HedgingConfig:
    """更新对冲配置"""
    db_config = get_hedging_config(db, config_id)
    if db_config:
        for key, value in config.dict().items():
            setattr(db_config, key, value)
        db.commit()
        db.refresh(db_config)
    return db_config