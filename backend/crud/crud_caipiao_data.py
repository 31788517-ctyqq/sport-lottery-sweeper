from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.caipiao_data import CaipiaoData as CaipiaoDataModel
from backend.schemas.caipiao_data import CaipiaoDataCreate, CaipiaoDataUpdate


def get_caipiao_data(db: Session, caipiao_data_id: int) -> Optional[CaipiaoDataModel]:
    """根据ID获取竞彩数据"""
    try:
        return db.query(CaipiaoDataModel).filter(CaipiaoDataModel.id == caipiao_data_id).first()
    except Exception as e:
        db.rollback()
        raise e


def get_caipiao_data_by_line_id(db: Session, line_id: str) -> Optional[CaipiaoDataModel]:
    """根据line_id获取竞彩数据"""
    try:
        return db.query(CaipiaoDataModel).filter(CaipiaoDataModel.line_id == line_id).first()
    except Exception as e:
        db.rollback()
        raise e


def get_caipiao_data_list(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    home_team: Optional[str] = None,
    guest_team: Optional[str] = None,
    game_short_name: Optional[str] = None
) -> List[CaipiaoDataModel]:
    """获取竞彩数据列表，支持分页和筛选"""
    try:
        query = db.query(CaipiaoDataModel)
        
        if home_team:
            query = query.filter(CaipiaoDataModel.home_team.contains(home_team))
        if guest_team:
            query = query.filter(CaipiaoDataModel.guest_team.contains(guest_team))
        if game_short_name:
            query = query.filter(CaipiaoDataModel.game_short_name.contains(game_short_name))
        
        return query.offset(skip).limit(limit).all()
    except Exception as e:
        db.rollback()
        raise e


def get_caipiao_data_count(db: Session) -> int:
    """获取竞彩数据总数量"""
    try:
        return db.query(CaipiaoDataModel).count()
    except Exception as e:
        db.rollback()
        raise e


def create_caipiao_data(db: Session, caipiao_data: CaipiaoDataCreate) -> CaipiaoDataModel:
    """创建竞彩数据"""
    try:
        db_caipiao_data = CaipiaoDataModel(**caipiao_data.dict())
        db.add(db_caipiao_data)
        db.commit()
        db.refresh(db_caipiao_data)
        return db_caipiao_data
    except Exception as e:
        db.rollback()
        raise e


def update_caipiao_data(
    db: Session, 
    caipiao_data_id: int, 
    caipiao_data: CaipiaoDataUpdate
) -> Optional[CaipiaoDataModel]:
    """更新竞彩数据"""
    try:
        db_caipiao_data = get_caipiao_data(db, caipiao_data_id)
        if db_caipiao_data:
            update_data = caipiao_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_caipiao_data, key, value)
            db.commit()
            db.refresh(db_caipiao_data)
        return db_caipiao_data
    except Exception as e:
        db.rollback()
        raise e


def delete_caipiao_data(db: Session, caipiao_data_id: int) -> bool:
    """删除竞彩数据"""
    try:
        db_caipiao_data = get_caipiao_data(db, caipiao_data_id)
        if db_caipiao_data:
            db.delete(db_caipiao_data)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e


def create_caipiao_data_batch(db: Session, caipiao_data_list: List[CaipiaoDataCreate]) -> List[CaipiaoDataModel]:
    """批量创建竞彩数据"""
    try:
        db_caipiao_data_list = [
            CaipiaoDataModel(**caipiao_data.dict()) 
            for caipiao_data in caipiao_data_list
        ]
        db.add_all(db_caipiao_data_list)
        db.commit()
        
        for db_caipiao_data in db_caipiao_data_list:
            db.refresh(db_caipiao_data)
        
        return db_caipiao_data_list
    except Exception as e:
        db.rollback()
        raise e