"""
爬虫配置管理模块
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ....core.database import get_db
from ....crud.crawler_config import get_multi as crud_get_crawler_configs
from ....crud import crawler_config as crud_crawler_config
from ..deps import get_current_admin

router = APIRouter()


@router.get("/crawler-configs", response_model=List[dict])
async def get_crawler_configs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """获取爬虫配置列表"""
    try:
        configs = crud_get_crawler_configs(db=db, skip=0, limit=100)
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawler-configs", response_model=dict)
async def create_crawler_config(
    config_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """创建爬虫配置"""
    try:
        config = crud_crawler_config.create(db, obj_in=config_data)
        return {
            "id": config.id,
            "name": config.name,
            "source_url": config.source_url,
            "enabled": config.enabled,
            "message": "爬虫配置创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建爬虫配置失败: {str(e)}")


@router.delete("/crawler-configs/{config_id}")
async def delete_crawler_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """删除爬虫配置"""
    try:
        success = crud_crawler_config.remove(db, id=config_id)
        if not success:
            raise HTTPException(status_code=404, detail="爬虫配置不存在")
        return {"message": "爬虫配置删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除爬虫配置失败: {str(e)}")