"""
Admin APIs for 500w -> 100qiu automatic synchronization.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.source_sync_service import source_issue_auto_sync_service

router = APIRouter(prefix="/source-sync", tags=["source-sync"])


@router.get("/status")
def get_source_sync_status(db: Session = Depends(get_db)):
    """Get auto-sync health and latest issue state."""
    snapshot = source_issue_auto_sync_service.get_status_snapshot(db)
    return {
        "success": True,
        "message": "source sync status loaded",
        "data": snapshot,
        "error_code": None,
        "trace_id": None,
    }


@router.post("/run-now")
def trigger_source_sync_now():
    """Trigger one manual synchronization run."""
    result = source_issue_auto_sync_service.trigger_run_now()
    return {
        "success": True,
        "message": result.get("message", "sync trigger accepted"),
        "data": result,
        "error_code": None,
        "trace_id": None,
    }


@router.get("/runs")
def list_source_sync_runs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    source_type: str = Query("100qiu"),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List source sync execution history."""
    items, total = source_issue_auto_sync_service.list_runs(
        db,
        page=page,
        size=size,
        source_type=source_type,
        status=status,
    )
    return {
        "success": True,
        "message": "source sync runs loaded",
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

