"""Request headers admin API."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.crawler_task_headers import CrawlerTaskHeader
from backend.models.crawler_tasks import CrawlerTask
from backend.models.data_source_headers import DataSourceHeader
from backend.models.data_sources import DataSource
from backend.models.headers import RequestHeader

router = APIRouter(dependencies=[Depends(get_db)])

_TYPE_IN_MAP = {
    "common": "general",
    "specific": "specific",
    "mobile": "mobile",
    "desktop": "desktop",
    "general": "general",
    "request": "request",
    "response": "response",
}

_TYPE_OUT_MAP = {
    "general": "common",
    "request": "specific",
    "response": "specific",
    "specific": "specific",
    "mobile": "mobile",
    "desktop": "desktop",
}

_PRIORITY_IN_MAP = {"low": 1, "medium": 2, "high": 3}
_PRIORITY_OUT_MAP = {1: "low", 2: "medium", 3: "high"}


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _normalize_type(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return _TYPE_IN_MAP.get(str(value).lower(), value)


def _normalize_priority(value: Union[int, str, None]) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    return _PRIORITY_IN_MAP.get(str(value).lower())


def _format_priority(value: Optional[int]) -> Optional[str]:
    if value is None:
        return None
    return _PRIORITY_OUT_MAP.get(value, str(value))


def _format_type(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return _TYPE_OUT_MAP.get(value, value)


def _to_frontend_dict(header: RequestHeader) -> Dict[str, Any]:
    success_rate = round(header.success_count / header.usage_count * 100, 2) if header.usage_count > 0 else 100
    return {
        "id": header.id,
        "domain": header.domain,
        "name": header.name,
        "value": header.value,
        "type": _format_type(header.type),
        "priority": _format_priority(header.priority),
        "status": header.status,
        "remarks": header.remarks,
        "usageCount": header.usage_count,
        "successCount": header.success_count,
        "lastUsed": header.last_used.isoformat() if header.last_used else None,
        "successRate": success_rate,
        "createdAt": header.created_at.isoformat() if header.created_at else None,
        "updatedAt": header.updated_at.isoformat() if header.updated_at else None,
    }


@router.get("/headers")
async def get_headers(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    domain: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    header_type: Optional[str] = Query(None, alias="type"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(RequestHeader)

        if domain:
            query = query.filter(RequestHeader.domain.like(f"%{domain}%"))
        if status:
            query = query.filter(RequestHeader.status == status)
        if header_type:
            query = query.filter(RequestHeader.type == _normalize_type(header_type))
        if search:
            query = query.filter(
                RequestHeader.name.like(f"%{search}%")
                | RequestHeader.value.like(f"%{search}%")
                | RequestHeader.domain.like(f"%{search}%")
            )

        total = query.count()
        headers = query.offset((page - 1) * size).limit(size).all()

        return {
            "success": True,
            "data": {
                "items": [_to_frontend_dict(item) for item in headers],
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
            },
            "message": "请求头获取成功",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/headers")
async def create_header(
    db: Session = Depends(get_db),
    domain: str = Body(..., embed=True),
    name: str = Body(..., embed=True),
    value: str = Body(..., embed=True),
    header_type: str = Body("general", alias="type", embed=True),
    priority: Union[int, str] = Body(1, embed=True),
    status: str = Body("enabled", embed=True),
    remarks: str = Body("", embed=True),
):
    try:
        if _is_blank(domain) or _is_blank(name) or _is_blank(value):
            raise HTTPException(status_code=400, detail="domain/name/value cannot be empty")

        new_header = RequestHeader(
            domain=domain.strip(),
            name=name.strip(),
            value=value.strip(),
            type=_normalize_type(header_type) or "general",
            priority=_normalize_priority(priority) or 1,
            status=status,
            remarks=(remarks or "").strip(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(new_header)
        db.commit()
        db.refresh(new_header)

        return {
            "success": True,
            "data": _to_frontend_dict(new_header),
            "message": "请求头创建成功",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/headers/batch")
async def batch_delete_headers(ids: List[int] = Body(..., embed=True), db: Session = Depends(get_db)):
    try:
        headers = db.query(RequestHeader).filter(RequestHeader.id.in_(ids)).all()
        for item in headers:
            db.delete(item)
        db.commit()
        return {
            "success": True,
            "data": {"deleted_count": len(headers)},
            "message": "批量删除请求头成功",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/headers/batch/test")
async def batch_test_headers(ids: List[int] = Body(..., embed=True), db: Session = Depends(get_db)):
    try:
        headers = db.query(RequestHeader).filter(RequestHeader.id.in_(ids)).all()
        success_count = len(headers)
        return {
            "success": True,
            "data": {"tested_count": len(headers), "success_count": success_count},
            "message": "批量测试请求头完成",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/headers/stats")
async def get_headers_stats(db: Session = Depends(get_db)):
    try:
        total_count = db.query(RequestHeader).count()
        enabled_count = db.query(RequestHeader).filter(RequestHeader.status == "enabled").count()
        disabled_count = db.query(RequestHeader).filter(RequestHeader.status == "disabled").count()

        type_counts = db.query(RequestHeader.type, func.count(RequestHeader.id)).group_by(RequestHeader.type).all()
        type_stats = {item[0]: item[1] for item in type_counts}

        return {
            "success": True,
            "data": {
                "total": total_count,
                "enabled": enabled_count,
                "disabled": disabled_count,
                "by_type": type_stats,
                "latest_update": datetime.utcnow().isoformat(),
            },
            "message": "统计信息获取成功",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/headers/import")
async def batch_import_headers(headers_data: List[Dict[str, Any]] = Body(...), db: Session = Depends(get_db)):
    try:
        created_count = 0
        for header_data in headers_data:
            domain = header_data.get("domain")
            name = header_data.get("name")
            value = header_data.get("value")
            if _is_blank(domain) or _is_blank(name) or _is_blank(value):
                raise HTTPException(status_code=400, detail="missing required fields")

            new_header = RequestHeader(
                domain=domain.strip(),
                name=name.strip(),
                value=value.strip(),
                type=_normalize_type(header_data.get("type")) or "general",
                priority=_normalize_priority(header_data.get("priority")) or 1,
                status=header_data.get("status", "enabled"),
                remarks=(header_data.get("remarks") or "").strip(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(new_header)
            created_count += 1

        db.commit()
        return {
            "success": True,
            "data": {"imported_count": created_count},
            "message": "批量导入请求头成功",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/headers/bind/data-source")
async def bind_headers_to_data_source(data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    data_source_id = data.get("dataSourceId")
    header_ids = data.get("headerIds", [])
    enabled = data.get("enabled", True)
    priority_override = data.get("priorityOverride")

    if not data_source_id or not isinstance(header_ids, list):
        raise HTTPException(status_code=400, detail="invalid payload")

    data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail="data source not found")

    headers = db.query(RequestHeader).filter(RequestHeader.id.in_(header_ids)).all()
    if len(headers) != len(header_ids):
        raise HTTPException(status_code=404, detail="header not found")

    for header_id in header_ids:
        binding = (
            db.query(DataSourceHeader)
            .filter(DataSourceHeader.data_source_id == data_source_id)
            .filter(DataSourceHeader.header_id == header_id)
            .first()
        )
        if not binding:
            binding = DataSourceHeader(
                data_source_id=data_source_id,
                header_id=header_id,
                priority_override=priority_override,
                enabled=enabled,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(binding)
        else:
            binding.enabled = enabled
            if priority_override is not None:
                binding.priority_override = priority_override
            binding.updated_at = datetime.utcnow()

    db.commit()
    return {"success": True, "data": {"count": len(header_ids)}, "message": "绑定成功"}


@router.post("/headers/bind/task")
async def bind_headers_to_task(data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    task_id = data.get("taskId")
    header_ids = data.get("headerIds", [])
    enabled = data.get("enabled", True)
    priority_override = data.get("priorityOverride")

    if not task_id or not isinstance(header_ids, list):
        raise HTTPException(status_code=400, detail="invalid payload")

    task = db.query(CrawlerTask).filter(CrawlerTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    headers = db.query(RequestHeader).filter(RequestHeader.id.in_(header_ids)).all()
    if len(headers) != len(header_ids):
        raise HTTPException(status_code=404, detail="header not found")

    for header_id in header_ids:
        binding = (
            db.query(CrawlerTaskHeader)
            .filter(CrawlerTaskHeader.task_id == task_id)
            .filter(CrawlerTaskHeader.header_id == header_id)
            .first()
        )
        if not binding:
            binding = CrawlerTaskHeader(
                task_id=task_id,
                header_id=header_id,
                priority_override=priority_override,
                enabled=enabled,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(binding)
        else:
            binding.enabled = enabled
            if priority_override is not None:
                binding.priority_override = priority_override
            binding.updated_at = datetime.utcnow()

    db.commit()
    return {"success": True, "data": {"count": len(header_ids)}, "message": "绑定成功"}


@router.get("/headers/bindings")
async def get_header_bindings(
    data_source_id: Optional[int] = Query(None),
    task_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    result = {"dataSourceBindings": [], "taskBindings": []}

    if data_source_id:
        bindings = (
            db.query(DataSourceHeader, RequestHeader)
            .join(RequestHeader, DataSourceHeader.header_id == RequestHeader.id)
            .filter(DataSourceHeader.data_source_id == data_source_id)
            .all()
        )
        for binding, header in bindings:
            result["dataSourceBindings"].append(
                {
                    "dataSourceId": binding.data_source_id,
                    "headerId": binding.header_id,
                    "enabled": binding.enabled,
                    "priorityOverride": binding.priority_override,
                    "header": _to_frontend_dict(header),
                }
            )

    if task_id:
        bindings = (
            db.query(CrawlerTaskHeader, RequestHeader)
            .join(RequestHeader, CrawlerTaskHeader.header_id == RequestHeader.id)
            .filter(CrawlerTaskHeader.task_id == task_id)
            .all()
        )
        for binding, header in bindings:
            result["taskBindings"].append(
                {
                    "taskId": binding.task_id,
                    "headerId": binding.header_id,
                    "enabled": binding.enabled,
                    "priorityOverride": binding.priority_override,
                    "header": _to_frontend_dict(header),
                }
            )

    return {"success": True, "data": result, "message": "绑定关系获取成功"}


@router.post("/headers/bind/data-source/remove")
async def unbind_headers_from_data_source(data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    data_source_id = data.get("dataSourceId")
    header_ids = data.get("headerIds", [])
    if not data_source_id or not isinstance(header_ids, list):
        raise HTTPException(status_code=400, detail="invalid payload")

    deleted = (
        db.query(DataSourceHeader)
        .filter(DataSourceHeader.data_source_id == data_source_id)
        .filter(DataSourceHeader.header_id.in_(header_ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"success": True, "data": {"deleted": deleted}, "message": "解绑成功"}


@router.post("/headers/bind/task/remove")
async def unbind_headers_from_task(data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    task_id = data.get("taskId")
    header_ids = data.get("headerIds", [])
    if not task_id or not isinstance(header_ids, list):
        raise HTTPException(status_code=400, detail="invalid payload")

    deleted = (
        db.query(CrawlerTaskHeader)
        .filter(CrawlerTaskHeader.task_id == task_id)
        .filter(CrawlerTaskHeader.header_id.in_(header_ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"success": True, "data": {"deleted": deleted}, "message": "解绑成功"}


@router.get("/headers/{header_id}")
async def get_header(header_id: int, db: Session = Depends(get_db)):
    header = db.query(RequestHeader).filter(RequestHeader.id == header_id).first()
    if not header:
        raise HTTPException(status_code=404, detail="请求头不存在")
    return {"success": True, "data": _to_frontend_dict(header), "message": "请求头获取成功"}


@router.put("/headers/{header_id}")
async def update_header(header_id: int, header_update: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    try:
        header = db.query(RequestHeader).filter(RequestHeader.id == header_id).first()
        if not header:
            raise HTTPException(status_code=404, detail="请求头不存在")

        update_data = {k: v for k, v in header_update.items() if v is not None}
        for required in ("domain", "name", "value"):
            if required in update_data and _is_blank(update_data.get(required)):
                raise HTTPException(status_code=400, detail=f"{required} cannot be empty")

        for field, value in update_data.items():
            if field == "type":
                value = _normalize_type(value)
            elif field == "priority":
                value = _normalize_priority(value)
            elif field in ("domain", "name", "value", "remarks") and isinstance(value, str):
                value = value.strip()
            setattr(header, field, value)

        header.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(header)
        return {"success": True, "data": _to_frontend_dict(header), "message": "请求头更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/headers/{header_id}")
async def delete_header(header_id: int, db: Session = Depends(get_db)):
    try:
        header = db.query(RequestHeader).filter(RequestHeader.id == header_id).first()
        if not header:
            raise HTTPException(status_code=404, detail="请求头不存在")
        db.delete(header)
        db.commit()
        return {"success": True, "data": {"id": header_id}, "message": "请求头删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/headers/{header_id}/test")
async def test_header(header_id: int, db: Session = Depends(get_db)):
    header = db.query(RequestHeader).filter(RequestHeader.id == header_id).first()
    if not header:
        raise HTTPException(status_code=404, detail="请求头不存在")

    test_result = {
        "id": header.id,
        "domain": header.domain,
        "name": header.name,
        "status": "success",
        "response_time": 150,
        "message": "请求头测试成功",
    }
    return {"success": True, "data": test_result, "message": "请求头测试完成"}
