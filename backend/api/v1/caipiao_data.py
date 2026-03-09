from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas.caipiao_data import CaipiaoData, CaipiaoDataCreate, CaipiaoDataUpdate
from backend.crud.crud_caipiao_data import (
    get_caipiao_data, 
    get_caipiao_data_list, 
    get_caipiao_data_count,
    create_caipiao_data, 
    update_caipiao_data, 
    delete_caipiao_data,
    create_caipiao_data_batch
)
from backend.services.caipiao_data_service import CaipiaoDataService

router = APIRouter(prefix="/caipiao-data", tags=["caipiao-data"])


@router.post("/", response_model=CaipiaoData)
def create_single_caipiao_data(caipiao_data: CaipiaoDataCreate, db: Session = Depends(get_db)):
    """
    创建单条竞彩数据
    """
    try:
        return create_caipiao_data(db=db, caipiao_data=caipiao_data)
    except Exception as e:
        print(f"Error in create_single_caipiao_data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"创建数据失败: {str(e)}")


@router.get("/{caipiao_data_id}", response_model=CaipiaoData)
def get_single_caipiao_data(caipiao_data_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单条竞彩数据
    """
    try:
        caipiao_data = get_caipiao_data(db=db, caipiao_data_id=caipiao_data_id)
        if not caipiao_data:
            raise HTTPException(status_code=404, detail="竞彩数据不存在")
        return caipiao_data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_single_caipiao_data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.put("/{caipiao_data_id}", response_model=CaipiaoData)
def update_single_caipiao_data(
    caipiao_data_id: int, 
    caipiao_data: CaipiaoDataUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新单条竞彩数据
    """
    try:
        updated_caipiao_data = update_caipiao_data(
            db=db, 
            caipiao_data_id=caipiao_data_id, 
            caipiao_data=caipiao_data
        )
        if not updated_caipiao_data:
            raise HTTPException(status_code=404, detail="竞彩数据不存在")
        return updated_caipiao_data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_single_caipiao_data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"更新数据失败: {str(e)}")


@router.delete("/{caipiao_data_id}")
def delete_single_caipiao_data(caipiao_data_id: int, db: Session = Depends(get_db)):
    """
    删除单条竞彩数据
    """
    try:
        deleted = delete_caipiao_data(db=db, caipiao_data_id=caipiao_data_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="竞彩数据不存在")
        return {"message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_single_caipiao_data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"删除数据失败: {str(e)}")


@router.get("/")
def get_caipiao_data_list_simple(
    skip: int = 0, 
    limit: int = 100, 
    home_team: str = None,
    guest_team: str = None,
    game_short_name: str = None,
    db: Session = Depends(get_db)
):
    """
    获取竞彩数据列表
    """
    try:
        # 查询数据列表
        data = get_caipiao_data_list(
            db=db, 
            skip=skip, 
            limit=limit,
            home_team=home_team,
            guest_team=guest_team,
            game_short_name=game_short_name
        )
        
        # 获取总数
        total = get_caipiao_data_count(db)
        
        # 计算总页数
        pages = (total + limit - 1) // limit if limit > 0 else 1
        
        return {
            "code": 200,
            "message": "Success",
            "data": data,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "pages": pages
        }
    except Exception as e:
        print(f"Error in get_caipiao_data_list: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.post("/sync-from-api/")
def sync_caipiao_data_from_api(date_time: str = "26011", db: Session = Depends(get_db)):
    """
    从API同步竞彩数据到数据库
    """
    try:
        service = CaipiaoDataService(db)
        count = service.sync_data_from_api(date_time)
        return {"message": f"成功同步 {count} 条数据", "count": count}
    except Exception as e:
        print(f"Error in sync_caipiao_data_from_api: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"同步数据失败: {str(e)}")


@router.post("/batch/", response_model=List[CaipiaoData])
def batch_create_caipiao_data(caipiao_data_list: List[CaipiaoDataCreate], db: Session = Depends(get_db)):
    """
    批量创建竞彩数据
    """
    return create_caipiao_data_batch(db=db, caipiao_data_list=caipiao_data_list)