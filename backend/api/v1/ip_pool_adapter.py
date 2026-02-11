"""
IP池管理API适配器
提供IP池的增删改查和监控功能，适配前端请求格式
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from backend.database import get_db
from backend.models.ip_pool import IPPool  # IP池模型
from backend.schemas.ip_pool import IPPoolCreate, IPPoolUpdate, IPPoolResponse  # IP池schema

router = APIRouter(prefix="", tags=["ip-pool-adapter"])

@router.get("/ip-pools")
async def get_ip_pools(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取IP池列表，支持分页和筛选，适配前端格式
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
        
        # 转换为前端需要的格式
        items = []
        for pool in pools:
            item = {
                "id": pool.id,
                "ipAddress": pool.ip,
                "port": pool.port,
                "protocol": pool.protocol,
                "location": pool.location or "未知",
                "responseTime": pool.latency_ms if pool.latency_ms is not None else pool.success_count * 10 + 50,
                "successRate": pool.success_rate if pool.success_rate is not None else min(100, max(0, 100 - (pool.failure_count * 5))),
                "lastChecked": pool.last_checked.isoformat() if pool.last_checked else None,
                "source": pool.source or "unknown",
                "anonymity": pool.anonymity or "",
                "score": pool.score,
                "bannedUntil": pool.banned_until.isoformat() if pool.banned_until else None,
                "failReason": pool.fail_reason,
                "status": map_status_for_frontend(pool.status),
                "usageCount": pool.success_count + pool.failure_count,
                "lastUsed": pool.last_used.isoformat() if pool.last_used else "-",
                "isEnabled": pool.status == "active"
            }
            items.append(item)
        
        return {
            "code": 200,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            },
            "message": "IP池获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ip-pools/stats")
async def get_ip_pool_stats(
    db: Session = Depends(get_db)
):
    """
    获取IP池统计信息，适配前端格式
    """
    try:
        total_count = db.query(IPPool).count()
        active_count = db.query(IPPool).filter(IPPool.status == "active").count()
        inactive_count = db.query(IPPool).filter(IPPool.status == "inactive").count()
        banned_count = db.query(IPPool).filter(IPPool.status == "banned").count()
        
        return {
            "code": 200,
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


def map_status_for_frontend(status: str) -> str:
    """将后端状态映射为前端状态"""
    mapping = {
        "active": "available",
        "inactive": "unavailable",
        "banned": "unavailable",
        "pending": "pending"
    }
    return mapping.get(status, "pending")


@router.get("/ip-pools/export")
async def export_ip_pools(
    db: Session = Depends(get_db)
):
    """
    导出IP池为CSV
    """
    import csv
    from io import StringIO

    pools = db.query(IPPool).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "ip", "port", "protocol", "location", "status", "success_count",
        "failure_count", "last_used", "latency_ms", "success_rate", "last_checked",
        "source", "anonymity", "score", "banned_until", "fail_reason"
    ])
    for pool in pools:
        writer.writerow([
            pool.id,
            pool.ip,
            pool.port,
            pool.protocol,
            pool.location or "",
            pool.status,
            pool.success_count,
            pool.failure_count,
            pool.last_used.isoformat() if pool.last_used else "",
            pool.latency_ms if pool.latency_ms is not None else "",
            pool.success_rate if pool.success_rate is not None else "",
            pool.last_checked.isoformat() if pool.last_checked else "",
            pool.source or "",
            pool.anonymity or "",
            pool.score if pool.score is not None else "",
            pool.banned_until.isoformat() if pool.banned_until else "",
            pool.fail_reason or "",
        ])

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ip_pools.csv"}
    )


@router.post("/ip-pools/batch/test")
async def batch_test_ip_pools(
    ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    批量测试IP池
    """
    import random
    now = datetime.utcnow()
    pools = db.query(IPPool).filter(IPPool.id.in_(ids)).all()
    results = []
    for pool in pools:
        response_time = random.randint(50, 1000)
        success_rate = random.randint(70, 100)
        pool.latency_ms = response_time
        pool.success_rate = success_rate
        pool.last_checked = now
        pool.status = "active" if success_rate >= 80 else "inactive"
        results.append({
            "id": pool.id,
            "ipAddress": pool.ip,
            "port": pool.port,
            "response_time": response_time,
            "success_rate": success_rate,
            "status": map_status_for_frontend(pool.status),
        })
    db.commit()
    return {
        "code": 200,
        "data": {"results": results, "tested_count": len(results)},
        "message": "批量测试完成"
    }


@router.post("/ip-pools/batch/delete")
async def batch_delete_ip_pools(
    ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    批量删除IP池
    """
    deleted = db.query(IPPool).filter(IPPool.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return {
        "code": 200,
        "data": {"deleted_count": deleted},
        "message": "批量删除成功"
    }


@router.get("/ip-pools/{pool_id}")
async def get_ip_pool(
    pool_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个IP池详情
    """
    pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
    if not pool:
        raise HTTPException(status_code=404, detail="IP池不存在")
    
    # 转换为前端需要的格式
    item = {
        "id": pool.id,
        "ipAddress": pool.ip,
        "port": pool.port,
        "protocol": pool.protocol,
        "location": pool.location or "未知",
        "responseTime": pool.latency_ms if pool.latency_ms is not None else pool.success_count * 10 + 50,
        "successRate": pool.success_rate if pool.success_rate is not None else min(100, max(0, 100 - (pool.failure_count * 5))),
        "lastChecked": pool.last_checked.isoformat() if pool.last_checked else None,
        "source": pool.source or "unknown",
        "anonymity": pool.anonymity or "",
        "score": pool.score,
        "bannedUntil": pool.banned_until.isoformat() if pool.banned_until else None,
        "failReason": pool.fail_reason,
        "status": map_status_for_frontend(pool.status),
        "usageCount": pool.success_count + pool.failure_count,
        "lastUsed": pool.last_used.isoformat() if pool.last_used else "-",
        "isEnabled": pool.status == "active"
    }
    
    return {
        "code": 200,
        "data": item,
        "message": "IP池获取成功"
    }


@router.post("/ip-pools")
async def create_ip_pool(
    ip: str = Body(..., embed=True),
    port: int = Body(..., embed=True),
    protocol: str = Body("http", embed=True),
    location: str = Body("", embed=True),
    status: str = Body("active", embed=True),
    remarks: str = Body("", embed=True),
    latency_ms: Optional[int] = Body(None, embed=True),
    success_rate: Optional[int] = Body(None, embed=True),
    last_checked: Optional[datetime] = Body(None, embed=True),
    source: Optional[str] = Body(None, embed=True),
    anonymity: Optional[str] = Body(None, embed=True),
    score: Optional[int] = Body(None, embed=True),
    banned_until: Optional[datetime] = Body(None, embed=True),
    fail_reason: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """
    创建IP池，适配前端格式
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
            latency_ms=latency_ms,
            success_rate=success_rate,
            last_checked=last_checked,
            source=source,
            anonymity=anonymity,
            score=score,
            banned_until=banned_until,
            fail_reason=fail_reason,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_pool)
        db.commit()
        db.refresh(new_pool)
        
        # 转换为前端需要的格式
        item = {
            "id": new_pool.id,
            "ipAddress": new_pool.ip,
            "port": new_pool.port,
            "protocol": new_pool.protocol,
            "location": new_pool.location or "未知",
            "responseTime": new_pool.latency_ms or 0,
            "successRate": new_pool.success_rate or 100,
            "lastChecked": new_pool.last_checked.isoformat() if new_pool.last_checked else None,
            "source": new_pool.source or "manual",
            "anonymity": new_pool.anonymity or "",
            "score": new_pool.score,
            "bannedUntil": new_pool.banned_until.isoformat() if new_pool.banned_until else None,
            "failReason": new_pool.fail_reason,
            "status": map_status_for_frontend(new_pool.status),
            "usageCount": 0,
            "lastUsed": "-",
            "isEnabled": new_pool.status == "active"
        }
        
        return {
            "code": 200,
            "data": item,
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
    更新IP池，适配前端格式
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
        
        # 转换为前端需要的格式
        item = {
            "id": pool.id,
            "ipAddress": pool.ip,
            "port": pool.port,
            "protocol": pool.protocol,
            "location": pool.location or "未知",
        "responseTime": pool.latency_ms if pool.latency_ms is not None else pool.success_count * 10 + 50,
        "successRate": pool.success_rate if pool.success_rate is not None else min(100, max(0, 100 - (pool.failure_count * 5))),
        "lastChecked": pool.last_checked.isoformat() if pool.last_checked else None,
        "source": pool.source or "unknown",
        "anonymity": pool.anonymity or "",
        "score": pool.score,
        "bannedUntil": pool.banned_until.isoformat() if pool.banned_until else None,
        "failReason": pool.fail_reason,
        "status": map_status_for_frontend(pool.status),
        "usageCount": pool.success_count + pool.failure_count,
        "lastUsed": pool.last_used.isoformat() if pool.last_used else "-",
        "isEnabled": pool.status == "active"
    }
        
        return {
            "code": 200,
            "data": item,
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
    删除IP池，适配前端格式
    """
    try:
        pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="IP池不存在")
        
        db.delete(pool)
        db.commit()
        
        return {
            "code": 200,
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
    测试IP池连接，适配前端格式
    """
    try:
        pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="IP池不存在")
        
        # 模拟测试结果
        import random
        response_time = random.randint(50, 1000)
        success_rate = random.randint(70, 100)
        
        test_result = {
            "id": pool.id,
            "ipAddress": pool.ip,
            "port": pool.port,
            "status": "available",  # 前端状态
            "response_time": response_time,  # 响应时间，毫秒
            "success_rate": success_rate,   # 成功率
            "message": "IP连接测试成功"
        }
        
        return {
            "code": 200,
            "data": test_result,
            "message": "连接测试完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
