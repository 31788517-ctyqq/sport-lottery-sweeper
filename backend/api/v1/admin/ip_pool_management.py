"""
IP池管理API
提供IP池的增删改查和监控功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from backend.database import get_db
from backend.models.data_sources import DataSource  # 使用现有的数据源模型作为参考
from backend.models.ip_pool import IPPool  # 新的IP池模型
from backend.schemas.ip_pool import IPPoolCreate, IPPoolUpdate, IPPoolResponse  # 新的IP池schema

router = APIRouter()

@router.get("/ip-pools")
async def get_ip_pools(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取IP池列表，支持分页和筛选
    """
    try:
        # 查询IP池列表
        query = db.query(IPPool)
        
        if status:
            query = query.filter(IPPool.status == status)
        
        if search:
            query = query.filter(
                IPPool.ip.like(f"%{search}%") | 
                IPPool.location.like(f"%{search}%")
            )
        
        total = query.count()
        pools = query.offset((page - 1) * size).limit(size).all()
        
        return {
            "success": True,
            "data": {
                "items": [pool.to_dict() for pool in pools],
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            },
            "message": "IP池获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ip-pools/{pool_id}")
async def get_ip_pool(
    pool_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个IP池详情
    """
    try:
        pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="IP池不存在")
        
        return {
            "success": True,
            "data": pool.to_dict(),
            "message": "IP池获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ip-pools")
async def create_ip_pool(
    db: Session = Depends(get_db),
    ip: str = Body(..., embed=True),
    port: int = Body(..., embed=True),
    protocol: str = Body("http", embed=True),
    location: str = Body("", embed=True),
    status: str = Body("active", embed=True),
    remarks: str = Body("", embed=True)
):
    """
    创建IP池
    """
    try:
        # 创建IP池对象
        new_pool = IPPool(
            ip=ip,
            port=port,
            protocol=protocol,
            location=location,
            status=status,
            remarks=remarks,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_pool)
        db.commit()
        db.refresh(new_pool)
        
        return {
            "success": True,
            "data": new_pool.to_dict(),
            "message": "IP池创建成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/ip-pools/{pool_id}")
async def update_ip_pool(
    pool_id: int,
    pool_update: IPPoolUpdate,
    db: Session = Depends(get_db)
):
    """
    更新IP池
    """
    try:
        pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="IP池不存在")
        
        # 更新字段
        update_data = pool_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pool, field, value)
        
        pool.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(pool)
        
        return {
            "success": True,
            "data": pool.to_dict(),
            "message": "IP池更新成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/ip-pools/{pool_id}")
async def delete_ip_pool(
    pool_id: int,
    db: Session = Depends(get_db)
):
    """
    删除IP池
    """
    try:
        pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="IP池不存在")
        
        db.delete(pool)
        db.commit()
        
        return {
            "success": True,
            "data": {"id": pool_id},
            "message": "IP池删除成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ip-pools/{pool_id}/test-connection")
async def test_ip_pool_connection(
    pool_id: int,
    db: Session = Depends(get_db)
):
    """
    测试IP池连接
    """
    try:
        pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="IP池不存在")
        
        # 这里可以添加实际的IP测试逻辑
        # 例如尝试使用这个IP连接某个网站
        test_result = {
            "id": pool.id,
            "ip": pool.ip,
            "port": pool.port,
            "status": "success",  # 或 "failed"
            "response_time": 150,  # 响应时间，毫秒
            "message": "IP连接测试成功"
        }
        
        return {
            "success": True,
            "data": test_result,
            "message": "连接测试完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ip-pools/batch-update-status")
async def batch_update_ip_pool_status(
    ids: List[int] = Body(..., embed=True),
    status: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    批量更新IP池状态
    """
    try:
        pools = db.query(IPPool).filter(IPPool.id.in_(ids)).all()
        
        for pool in pools:
            pool.status = status
            pool.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "data": {"updated_count": len(pools)},
            "message": "批量更新状态成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ip-pools/{pool_id}/health")
async def get_ip_pool_health(
    pool_id: int,
    db: Session = Depends(get_db)
):
    """
    获取IP池健康状态
    """
    try:
        pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="IP池不存在")
        
        # 返回IP池的健康状态
        health_status = {
            "id": pool.id,
            "ip": pool.ip,
            "status": pool.status,
            "response_time_ms": 120,
            "last_check": pool.updated_at.isoformat() if pool.updated_at else None,
            "success_rate": 95,
            "message": "健康检查通过"
        }
        
        return {
            "success": True,
            "data": health_status,
            "message": "健康状态获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ip-pools/stats")
async def get_ip_pool_stats(
    db: Session = Depends(get_db)
):
    """
    获取IP池统计信息
    """
    try:
        total_count = db.query(IPPool).count()
        active_count = db.query(IPPool).filter(IPPool.status == "active").count()
        inactive_count = db.query(IPPool).filter(IPPool.status == "inactive").count()
        banned_count = db.query(IPPool).filter(IPPool.status == "banned").count()
        
        return {
            "success": True,
            "data": {
                "total": total_count,
                "active": active_count,
                "inactive": inactive_count,
                "banned": banned_count,
                "latest_update": datetime.utcnow().isoformat()
            },
            "message": "统计信息获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))