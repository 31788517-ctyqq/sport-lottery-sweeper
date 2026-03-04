"""
请求头管理API适配器
提供请求头的增删改查功能，适配前端请求格式
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from backend.database import get_db
from backend.models.headers import RequestHeader  # 请求头模型
from backend.schemas.headers import RequestHeaderCreate, RequestHeaderUpdate, RequestHeaderResponse  # 请求头schema

def priority_str_to_int(priority_str: str) -> int:
    """将优先级字符串转换为整数"""
    priority_map = {
        "low": 1,
        "medium": 2,
        "high": 3
    }
    return priority_map.get(priority_str.lower(), 2)  # 默认为medium(2)

# 首先定义路由
router = APIRouter(prefix="", tags=["headers-adapter"])


# 定义所有路由处理函数
@router.get("/admin/crawler/headers")
async def get_headers(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    domain: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    header_type: Optional[str] = Query(None, alias="type"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取请求头列表，支持分页和筛选，适配前端格式
    """
    try:
        # 查询请求头列表
        query = db.query(RequestHeader)
        
        if domain:
            query = query.filter(RequestHeader.domain.like(f"%{domain}%"))
        
        if status:
            query = query.filter(RequestHeader.status == status)
        
        if header_type:
            query = query.filter(RequestHeader.type == header_type)
        
        if search:
            query = query.filter(
                RequestHeader.name.like(f"%{search}%") | 
                RequestHeader.value.like(f"%{search}%") |
                RequestHeader.domain.like(f"%{search}%")
            )
        
        total = query.count()
        headers = query.offset((page - 1) * size).limit(size).all()
        
        # 转换为前端需要的格式
        items = []
        for header in headers:
            item = {
                "id": header.id,
                "domain": header.domain,
                "name": header.name,
                "value": header.value,
                "type": header.type,
                "priority": header.priority,
                "status": header.status,
                "lastUsed": header.last_used.isoformat() if header.last_used else "-",
                "usageCount": header.usage_count,
                "successRate": header.success_rate if hasattr(header, 'success_rate') else 
                              (round(header.success_count / header.usage_count * 100, 2) if header.usage_count > 0 else 100),
                "remarks": header.remarks
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
            "message": "请求头获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/crawler/headers/stats")
async def get_headers_stats(
    db: Session = Depends(get_db)
):
    """
    获取请求头统计信息，适配前端格式
    """
    try:
        total_count = db.query(RequestHeader).count()
        enabled_count = db.query(RequestHeader).filter(RequestHeader.status == "enabled").count()
        disabled_count = db.query(RequestHeader).filter(RequestHeader.status == "disabled").count()
        
        # 按类型统计
        from sqlalchemy import func
        type_counts = db.query(RequestHeader.type, func.count(RequestHeader.id)).group_by(RequestHeader.type).all()
        
        type_stats = {item[0]: item[1] for item in type_counts}
        
        return {
            "code": 200,
            "data": {
                "total": total_count,
                "enabled": enabled_count,
                "disabled": disabled_count,
                "by_type": type_stats,
                "latest_update": datetime.utcnow().isoformat()
            },
            "message": "统计信息获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/crawler/headers/{header_id}")
async def get_header(
    header_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个请求头详情，适配前端格式
    """
    header = db.query(RequestHeader).filter(RequestHeader.id == header_id).first()
    if not header:
        raise HTTPException(status_code=404, detail="请求头不存在")
    
    # 转换为前端需要的格式
    item = {
        "id": header.id,
        "domain": header.domain,
        "name": header.name,
        "value": header.value,
        "type": header.type,
        "priority": header.priority,
        "status": header.status,
        "lastUsed": header.last_used.isoformat() if header.last_used else "-",
        "usageCount": header.usage_count,
        "successRate": header.success_rate if hasattr(header, 'success_rate') else 
                      (round(header.success_count / header.usage_count * 100, 2) if header.usage_count > 0 else 100),
        "remarks": header.remarks
    }
    
    return {
        "code": 200,
        "data": item,
        "message": "请求头获取成功"
    }


@router.post("/admin/crawler/headers")
async def create_header(
    domain: str = Body(..., embed=True),
    name: str = Body(..., embed=True),
    value: str = Body(..., embed=True),
    header_type: str = Body("common", alias="type", embed=True),
    priority: str = Body("medium", embed=True),
    status: str = Body("enabled", embed=True),
    remarks: str = Body("", embed=True),
    db: Session = Depends(get_db)
):
    """
    创建请求头，适配前端格式
    """
    try:
        # 将字符串优先级转换为整数
        priority_int = priority_str_to_int(priority)
        
        # 创建请求头对象
        new_header = RequestHeader(
            domain=domain,
            name=name,
            value=value,
            type=header_type,
            priority=priority_int,
            status=status,
            remarks=remarks,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            usage_count=0,
            success_count=0
        )
        
        db.add(new_header)
        db.commit()
        db.refresh(new_header)
        
        # 转换为前端需要的格式
        item = {
            "id": new_header.id,
            "domain": new_header.domain,
            "name": new_header.name,
            "value": new_header.value,
            "type": new_header.type,
            "priority": priority,  # 返回字符串格式给前端
            "status": new_header.status,
            "lastUsed": new_header.last_used.isoformat() if new_header.last_used else "-",
            "usageCount": new_header.usage_count,
            "successRate": 100,  # 新创建的成功率为100
            "remarks": new_header.remarks
        }
        
        return {
            "code": 200,
            "data": item,
            "message": "请求头创建成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/crawler/headers/{header_id}")
async def update_header(
    header_id: int,
    header_update: RequestHeaderUpdate,
    db: Session = Depends(get_db)
):
    """
    更新请求头，适配前端格式
    """
    try:
        header = db.query(RequestHeader).filter(RequestHeader.id == header_id).first()
        if not header:
            raise HTTPException(status_code=404, detail="请求头不存在")
        
        # 更新字段
        update_data = header_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            # 如果是priority字段，需要转换为整数
            if field == 'priority' and isinstance(value, str):
                setattr(header, field, priority_str_to_int(value))
            else:
                setattr(header, field, value)
        
        header.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(header)
        
        # 转换为前端需要的格式
        item = {
            "id": header.id,
            "domain": header.domain,
            "name": header.name,
            "value": header.value,
            "type": header.type,
            "priority": header.priority,  # 返回字符串格式给前端
            "status": header.status,
            "lastUsed": header.last_used.isoformat() if header.last_used else "-",
            "usageCount": header.usage_count,
            "successRate": header.success_rate if hasattr(header, 'success_rate') else 
                          (round(header.success_count / header.usage_count * 100, 2) if header.usage_count > 0 else 100),
            "remarks": header.remarks
        }
        
        return {
            "code": 200,
            "data": item,
            "message": "请求头更新成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/crawler/headers/{header_id}")
async def delete_header(
    header_id: int,
    db: Session = Depends(get_db)
):
    """
    删除请求头，适配前端格式
    """
    try:
        header = db.query(RequestHeader).filter(RequestHeader.id == header_id).first()
        if not header:
            raise HTTPException(status_code=404, detail="请求头不存在")
        
        db.delete(header)
        db.commit()
        
        return {
            "code": 200,
            "data": {"id": header_id},
            "message": "请求头删除成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/crawler/headers/{header_id}/test")
async def test_header(
    header_id: int,
    db: Session = Depends(get_db)
):
    """
    测试请求头，适配前端格式
    """
    try:
        header = db.query(RequestHeader).filter(RequestHeader.id == header_id).first()
        if not header:
            raise HTTPException(status_code=404, detail="请求头不存在")
        
        # 模拟测试结果
        import random
        response_time = random.randint(50, 1000)
        success_rate = random.randint(70, 100)
        
        test_result = {
            "id": header.id,
            "domain": header.domain,
            "name": header.name,
            "status": "success",  # 或 "failed"
            "response_time": response_time,  # 响应时间，毫秒
            "message": "请求头测试成功"
        }
        
        return {
            "code": 200,
            "data": test_result,
            "message": "请求头测试完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/crawler/headers/batch")
async def batch_delete_headers(
    body: dict,
    db: Session = Depends(get_db)
):
    """
    批量删除请求头，适配前端格式
    """
    try:
        ids = body.get('ids', [])
        headers = db.query(RequestHeader).filter(RequestHeader.id.in_(ids)).all()
        
        for header in headers:
            db.delete(header)
        
        db.commit()
        
        return {
            "code": 200,
            "data": {"deleted_count": len(headers)},
            "message": "批量删除请求头成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/crawler/headers/batch/test")
async def batch_test_headers(
    ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    批量测试请求头，适配前端格式
    """
    try:
        headers = db.query(RequestHeader).filter(RequestHeader.id.in_(ids)).all()
        
        success_count = 0
        for header in headers:
            # 这里可以添加实际的请求头测试逻辑
            success_count += 1  # 假设所有测试都成功
        
        return {
            "code": 200,
            "data": {"tested_count": len(headers), "success_count": success_count},
            "message": "批量测试请求头完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/crawler/headers/import")
async def batch_import_headers(
    body: List[dict],
    db: Session = Depends(get_db)
):
    """
    批量导入请求头，适配前端格式
    """
    try:
        created_count = 0
        for header_data in body:
            # 将字符串优先级转换为整数
            priority_int = priority_str_to_int(header_data.get('priority', 'medium'))
            
            new_header = RequestHeader(
                domain=header_data.get('domain'),
                name=header_data.get('name'),
                value=header_data.get('value'),
                type=header_data.get('type', 'common'),
                priority=priority_int,
                status=header_data.get('status', 'enabled'),
                remarks=header_data.get('remarks', ''),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                usage_count=0,
                success_count=0
            )
            db.add(new_header)
            created_count += 1
        
        db.commit()
        
        return {
            "code": 200,
            "data": {"imported_count": created_count},
            "message": "批量导入请求头成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))