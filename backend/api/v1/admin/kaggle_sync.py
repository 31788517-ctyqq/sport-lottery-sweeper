"""
Admin APIs for Kaggle sync management.
"""

from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.kaggle_sync_service import kaggle_sync_service

router = APIRouter(prefix="/kaggle-sync", tags=["kaggle-sync"])


@router.get("/status")
def get_kaggle_sync_status(db: Session = Depends(get_db)):
    snapshot = kaggle_sync_service.get_status_snapshot(db)
    return {
        "success": True,
        "message": "kaggle sync status loaded",
        "data": snapshot,
        "error_code": None,
        "trace_id": None,
    }


@router.get("/datasets")
def list_kaggle_datasets(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    enabled: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    items, total = kaggle_sync_service.list_datasets(
        db,
        page=page,
        size=size,
        enabled=enabled,
    )
    return {
        "success": True,
        "message": "kaggle datasets loaded",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size if size else 0,
        },
        "error_code": None,
        "trace_id": None,
    }


@router.post("/datasets")
def create_kaggle_dataset(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    try:
        row = kaggle_sync_service.create_dataset(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "success": True,
        "message": "kaggle dataset created",
        "data": {
            "id": row.id,
            "dataset_slug": row.dataset_slug,
            "enabled": row.enabled,
        },
        "error_code": None,
        "trace_id": None,
    }


@router.patch("/datasets/{dataset_id}")
def update_kaggle_dataset(
    dataset_id: int = Path(..., ge=1),
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    row = kaggle_sync_service.update_dataset(db, dataset_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="dataset not found")
    return {
        "success": True,
        "message": "kaggle dataset updated",
        "data": {
            "id": row.id,
            "dataset_slug": row.dataset_slug,
            "enabled": row.enabled,
            "sync_interval_hours": row.sync_interval_hours,
            "latest_version": row.latest_version,
            "last_synced_version": row.last_synced_version,
        },
        "error_code": None,
        "trace_id": None,
    }


@router.get("/runs")
def list_kaggle_sync_runs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    dataset_slug: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    items, total = kaggle_sync_service.list_runs(
        db,
        page=page,
        size=size,
        dataset_slug=dataset_slug,
        status=status,
    )
    return {
        "success": True,
        "message": "kaggle sync runs loaded",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size if size else 0,
        },
        "error_code": None,
        "trace_id": None,
    }


@router.get("/runs/{run_identifier}")
def get_kaggle_run_detail(
    run_identifier: str = Path(...),
    db: Session = Depends(get_db),
):
    row = kaggle_sync_service.get_run_detail(db, run_identifier)
    if not row:
        raise HTTPException(status_code=404, detail="run not found")
    return {
        "success": True,
        "message": "kaggle sync run detail loaded",
        "data": row,
        "error_code": None,
        "trace_id": None,
    }


@router.get("/runs/{run_identifier}/quality")
def get_kaggle_run_quality(
    run_identifier: str = Path(...),
    db: Session = Depends(get_db),
):
    row = kaggle_sync_service.get_run_quality(db, run_identifier)
    if not row:
        raise HTTPException(status_code=404, detail="run not found")
    return {
        "success": True,
        "message": "kaggle sync run quality loaded",
        "data": row,
        "error_code": None,
        "trace_id": None,
    }


@router.get("/datasets/{dataset_id}/preview")
def get_kaggle_dataset_preview(
    dataset_id: int = Path(..., ge=1),
    version: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    row = kaggle_sync_service.get_dataset_preview(
        db,
        dataset_id,
        version=version,
        limit=limit,
    )
    if not row:
        raise HTTPException(status_code=404, detail="dataset not found")
    return {
        "success": True,
        "message": "kaggle dataset preview loaded",
        "data": row,
        "error_code": None,
        "trace_id": None,
    }


@router.post("/datasets/{dataset_id}/rebuild")
def rebuild_kaggle_dataset(
    dataset_id: int = Path(..., ge=1),
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
):
    row = kaggle_sync_service.rebuild_dataset(db, dataset_id, payload or {})
    if not row:
        raise HTTPException(status_code=404, detail="dataset not found")
    return {
        "success": True,
        "message": "kaggle dataset rebuild accepted",
        "data": row,
        "error_code": None,
        "trace_id": None,
    }


@router.post("/run-now")
def run_kaggle_sync_now(
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
):
    try:
        result = kaggle_sync_service.trigger_run_now(db, payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "success": True,
        "message": "kaggle sync run accepted",
        "data": result,
        "error_code": None,
        "trace_id": None,
    }


@router.post("/merge-backfill-now")
def run_kaggle_merge_backfill_now(
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
):
    try:
        result = kaggle_sync_service.run_merge_backfill_now(db, payload or {})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "success": True,
        "message": "kaggle merge/backfill run accepted",
        "data": result,
        "error_code": None,
        "trace_id": None,
    }
