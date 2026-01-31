"""
爬虫配置管理模块
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ....core.database import get_db
from ....crud.crawler_config import get_multi as crud_get_crawler_configs
from ....crud import crawler_config as crud_crawler_config
from ...deps import get_current_admin

router = APIRouter()


@router.get("/crawler-configs", response_model=List[dict])
async def get_crawler_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取爬虫配置列表
    """
    configs, total = crud_get_crawler_configs(db, skip=skip, limit=limit)
    return configs


@router.post("/crawler-configs")
async def create_crawler_config(
    config_data: dict,
    db: Session = Depends(get_db)
):
    """
    创建爬虫配置
    """
    return crud_crawler_config.create(db=db, obj_in=config_data)


@router.put("/crawler-configs/{config_id}")
async def update_crawler_config(
    config_id: int,
    config_data: dict,
    db: Session = Depends(get_db)
):
    """
    更新爬虫配置
    """
    db_config = crud_crawler_config.get(db, id=config_id)
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return crud_crawler_config.update(db=db, db_obj=db_config, obj_in=config_data)


@router.delete("/crawler-configs/{config_id}")
async def delete_crawler_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """
    删除爬虫配置
    """
    db_config = crud_crawler_config.get(db, id=config_id)
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return crud_crawler_config.remove(db=db, id=config_id)