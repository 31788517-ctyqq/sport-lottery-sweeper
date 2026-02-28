from fastapi import APIRouter, Depends, HTTPException, Body, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import json
import threading
import socket
import os
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from urllib.parse import urlparse

# 引入模型和Service
from backend.models.draw_feature import DrawFeature
from backend.models.draw_training_job import TrainingJobStatus, DrawTrainingJob
from backend.models.draw_model_version import DrawModelVersion
from backend.models.draw_prediction_result import DrawPredictionResult
from backend.models.match import Match
from backend.models.admin_user import AdminUser
from backend.services import draw_prediction_service as svc
from backend.services import poisson_11_service
from backend.services import ai_draw_prediction_service
from backend.services.draw_suggestion_service import DrawSuggestionService
from backend.services.odds_snapshot_service import OddsSnapshotService
from backend.services.llm_content_service import LLMContentService
from backend.models.async_task import AsyncTask
from backend.api.dependencies import get_db, get_current_active_admin_user
from backend.database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/draw-prediction",
    tags=["draw-prediction"],
    dependencies=[Depends(get_current_active_admin_user)],
)


_FETCH_TASK_TTL_MINUTES = 30
_FETCH_TASKS: Dict[str, Dict[str, Any]] = {}
_FETCH_TASKS_LOCK = threading.Lock()
_FETCH_TASK_EXECUTOR = ThreadPoolExecutor(max_workers=3, thread_name_prefix="draw_prediction_fetch")
_TRAINING_TASK_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="draw_prediction_train")
_RETRAIN_DRAFTS: Dict[str, Dict[str, Any]] = {}
_RETRAIN_DRAFTS_LOCK = threading.Lock()
_ENABLE_CELERY_DISPATCH = os.getenv("DRAW_PREDICTION_ENABLE_CELERY", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def _utcnow() -> datetime:
    return datetime.utcnow()


def _is_broker_endpoint_reachable(broker_url: str, timeout_seconds: float = 1.0) -> bool:
    """Fast TCP probe to avoid blocking Celery send_task when broker is unavailable."""
    try:
        parsed = urlparse(str(broker_url or ""))
        host = parsed.hostname
        port = parsed.port
        if not host:
            return False
        if port is None:
            if parsed.scheme.startswith("redis"):
                port = 6379
            elif parsed.scheme.startswith("amqp"):
                port = 5672
            else:
                return False
        with socket.create_connection((host, int(port)), timeout=timeout_seconds):
            return True
    except Exception:
        return False


def _serialize_task(task: Dict[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    for key, value in task.items():
        if isinstance(value, datetime):
            payload[key] = value.isoformat()
        else:
            payload[key] = value
    return payload


def _cleanup_fetch_tasks_locked(now: datetime) -> None:
    expired_ids: List[str] = []
    for task_id, task in _FETCH_TASKS.items():
        if task.get("status") in {"success", "failed", "cancelled"}:
            updated_at = task.get("updated_at")
            if isinstance(updated_at, datetime) and now - updated_at >= timedelta(minutes=_FETCH_TASK_TTL_MINUTES):
                expired_ids.append(task_id)
    for task_id in expired_ids:
        _FETCH_TASKS.pop(task_id, None)


def _save_task_to_db(task: Dict[str, Any]) -> None:
    db = SessionLocal()
    try:
        row = db.query(AsyncTask).filter(AsyncTask.task_id == task.get("task_id")).first()
        if not row:
            row = AsyncTask(
                task_id=str(task.get("task_id")),
                task_type=str(task.get("type") or task.get("task_type") or "generic"),
                status=str(task.get("status") or "PENDING").upper(),
                payload=task.get("params") if isinstance(task.get("params"), dict) else {},
                result=task.get("result") if isinstance(task.get("result"), dict) else None,
                error_message=task.get("error"),
                progress=float(task.get("progress") or 0.0),
            )
            db.add(row)
        else:
            row.status = str(task.get("status") or row.status or "PENDING").upper()
            row.payload = task.get("params") if isinstance(task.get("params"), dict) else row.payload
            row.result = task.get("result") if isinstance(task.get("result"), dict) else row.result
            row.error_message = task.get("error") or row.error_message
            row.progress = float(task.get("progress") or row.progress or 0.0)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def _create_fetch_task(task_type: str, params: Optional[Dict[str, Any]] = None) -> str:
    now = _utcnow()
    task_id = f"{task_type}_{now.strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:8]}"
    task = {
        "task_id": task_id,
        "type": task_type,
        "status": "pending",
        "phase": "pending",
        "progress": 0.0,
        "current": 0,
        "total": 0,
        "message": "任务已创建，等待执行",
        "error": None,
        "result": None,
        "params": params or {},
        "created_at": now,
        "started_at": None,
        "completed_at": None,
        "updated_at": now,
    }
    with _FETCH_TASKS_LOCK:
        _cleanup_fetch_tasks_locked(now)
        _FETCH_TASKS[task_id] = task
    _save_task_to_db(task)
    return task_id


def _update_fetch_task(task_id: str, **kwargs: Any) -> None:
    with _FETCH_TASKS_LOCK:
        task = _FETCH_TASKS.get(task_id)
        if not task:
            return
        for key, value in kwargs.items():
            task[key] = value
        task["updated_at"] = _utcnow()
        task_copy = dict(task)
    _save_task_to_db(task_copy)


def _get_fetch_task(task_id: str) -> Optional[Dict[str, Any]]:
    now = _utcnow()
    with _FETCH_TASKS_LOCK:
        _cleanup_fetch_tasks_locked(now)
        task = _FETCH_TASKS.get(task_id)
        if task:
            return _serialize_task(dict(task))

    db = SessionLocal()
    try:
        row = db.query(AsyncTask).filter(AsyncTask.task_id == task_id).first()
        if not row:
            return None
        return {
            "task_id": row.task_id,
            "type": row.task_type,
            "status": str(row.status or "").lower(),
            "progress": row.progress,
            "result": row.result,
            "error": row.error_message,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }
    finally:
        db.close()



def _run_poisson_fetch_task(task_id: str, target_date: date, data_source: str) -> None:
    db = SessionLocal()
    started_at = _utcnow()
    _update_fetch_task(
        task_id,
        status="running",
        phase="prepare",
        started_at=started_at,
        message="开始抓取并计算",
        progress=1.0,
    )
    try:
        def _on_progress(progress_payload: Dict[str, Any]) -> None:
            _update_fetch_task(
                task_id,
                phase=str(progress_payload.get("phase") or "running"),
                progress=float(progress_payload.get("progress") or 0.0),
                current=int(progress_payload.get("current") or 0),
                total=int(progress_payload.get("total") or 0),
                message=str(progress_payload.get("message") or "处理中"),
            )

        results = poisson_11_service.scan_for_date(
            db,
            target_date,
            data_source=data_source,
            overwrite=True,
            progress_callback=_on_progress,
        )
        _update_fetch_task(
            task_id,
            status="success",
            phase="finished",
            progress=100.0,
            current=len(results),
            total=len(results),
            message=f"处理完成，共 {len(results)} 场",
            result={
                "date": target_date.isoformat(),
                "data_source": data_source,
                "total": len(results),
            },
            completed_at=_utcnow(),
            error=None,
        )
    except Exception as exc:
        try:
            db.rollback()
        except Exception:
            pass
        _update_fetch_task(
            task_id,
            status="failed",
            phase="failed",
            message="抓取任务失败",
            error=str(exc),
            completed_at=_utcnow(),
        )
    finally:
        db.close()


def _run_ai_draw_fetch_task(task_id: str, target_date: date) -> None:
    db = SessionLocal()
    started_at = _utcnow()
    _update_fetch_task(
        task_id,
        status="running",
        phase="compute",
        started_at=started_at,
        message="开始计算 AI 平局预测",
        progress=5.0,
    )
    try:
        items = ai_draw_prediction_service.list_for_date(db, target_date, data_source="yingqiu_bd")
        _update_fetch_task(
            task_id,
            status="success",
            phase="finished",
            progress=100.0,
            current=len(items),
            total=len(items),
            message=f"处理完成，共 {len(items)} 场",
            result={
                "date": target_date.isoformat(),
                "data_source": "yingqiu_bd",
                "total": len(items),
            },
            completed_at=_utcnow(),
            error=None,
        )
    except Exception as exc:
        try:
            db.rollback()
        except Exception:
            pass
        _update_fetch_task(
            task_id,
            status="failed",
            phase="failed",
            message="抓取任务失败",
            error=str(exc),
            completed_at=_utcnow(),
        )
    finally:
        db.close()


def _run_draw_suggestion_snapshot_fetch_task(task_id: str, target_date: date, source: str) -> None:
    db = SessionLocal()
    _update_fetch_task(
        task_id,
        status="running",
        phase="fetch_snapshots",
        started_at=_utcnow(),
        message="开始采集赔率快照",
        progress=2.0,
    )
    try:
        result = OddsSnapshotService.fetch_snapshots_for_date(
            db,
            target_date=target_date,
            source=source,
            overwrite=False,
            progress_callback=lambda p: _update_fetch_task(
                task_id,
                phase=str(p.get("phase") or "fetch_snapshots"),
                progress=float(p.get("progress") or 0.0),
                current=int(p.get("current") or 0),
                total=int(p.get("total") or 0),
                message=str(p.get("message") or "处理中"),
            ),
        )
        _update_fetch_task(
            task_id,
            status="success",
            phase="finished",
            progress=100.0,
            message="快照采集完成",
            result=result,
            completed_at=_utcnow(),
            error=None,
        )
    except Exception as exc:
        try:
            db.rollback()
        except Exception:
            pass
        _update_fetch_task(
            task_id,
            status="failed",
            phase="failed",
            message="快照采集失败",
            error=str(exc),
            completed_at=_utcnow(),
        )
    finally:
        db.close()


def _run_draw_suggestion_generate_task(task_id: str, target_date: date, force: bool) -> None:
    db = SessionLocal()
    _update_fetch_task(
        task_id,
        status="running",
        phase="generate_suggestions",
        started_at=_utcnow(),
        message="开始生成下注建议",
        progress=3.0,
    )
    try:
        result = DrawSuggestionService.generate_suggestions_for_date(db, target_date=target_date, force=force)
        _update_fetch_task(
            task_id,
            status="success",
            phase="finished",
            progress=100.0,
            message="建议生成完成",
            result=result,
            completed_at=_utcnow(),
            error=None,
        )
    except Exception as exc:
        try:
            db.rollback()
        except Exception:
            pass
        _update_fetch_task(
            task_id,
            status="failed",
            phase="failed",
            message="建议生成失败",
            error=str(exc),
            completed_at=_utcnow(),
        )
    finally:
        db.close()


def _run_draw_suggestion_settle_task(task_id: str, target_date: Optional[date]) -> None:
    db = SessionLocal()
    _update_fetch_task(
        task_id,
        status="running",
        phase="settle_paper_bets",
        started_at=_utcnow(),
        message="开始结算模拟下注",
        progress=5.0,
    )
    try:
        settle_result = DrawSuggestionService.settle_paper_bets(db, target_date=target_date)
        ks_state = DrawSuggestionService.evaluate_and_apply_killswitch(db)
        _update_fetch_task(
            task_id,
            status="success",
            phase="finished",
            progress=100.0,
            message="结算完成",
            result={"settlement": settle_result, "killswitch": ks_state},
            completed_at=_utcnow(),
            error=None,
        )
    except Exception as exc:
        try:
            db.rollback()
        except Exception:
            pass
        _update_fetch_task(
            task_id,
            status="failed",
            phase="failed",
            message="结算失败",
            error=str(exc),
            completed_at=_utcnow(),
        )
    finally:
        db.close()


def _normalize_meta(raw_meta: Any) -> Dict[str, Any]:

    if isinstance(raw_meta, dict):
        return raw_meta
    if isinstance(raw_meta, str) and raw_meta:
        try:
            parsed = json.loads(raw_meta)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _extract_model_version_id(meta: Dict[str, Any]) -> Optional[int]:
    value = meta.get("model_version_id")
    try:
        if value is None:
            return None
        return int(value)
    except Exception:
        return None


def _calc_prediction_stats(items: List[DrawPredictionResult]) -> Dict[str, Any]:
    total = len(items)
    finished = [p for p in items if p.actual_result is not None]
    hits = [p for p in finished if p.actual_result == "draw"]
    pending = total - len(finished)
    accuracy = round((len(hits) / len(finished)) * 100, 1) if finished else 0.0
    return {
        "total": total,
        "finished": len(finished),
        "hits": len(hits),
        "pending": pending,
        "accuracy": accuracy,
    }


def _serialize_retrain_draft(draft: Dict[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    for key, value in draft.items():
        if isinstance(value, datetime):
            payload[key] = value.isoformat()
        else:
            payload[key] = value
    return payload


def _resolve_created_by_id(db: Session) -> int:
    first_admin = db.query(AdminUser.id).order_by(AdminUser.id.asc()).first()
    if first_admin and first_admin[0]:
        return int(first_admin[0])
    return 1


def _bootstrap_draw_prediction_mock_data(db: Session) -> Dict[str, Any]:
    now = _utcnow()
    created: Dict[str, Optional[Dict[str, Any]]] = {
        "training_job": None,
        "model_version": None,
        "prediction": None,
    }

    feature_count = db.query(DrawFeature).count()
    feature_ids = [row[0] for row in db.query(DrawFeature.id).order_by(DrawFeature.id.asc()).limit(5).all()]
    created_by = _resolve_created_by_id(db)

    training_count = db.query(DrawTrainingJob).count()
    if training_count == 0:
        job = DrawTrainingJob(
            job_name=f"Mock平局训练_{now.strftime('%Y%m%d')}",
            feature_set_ids=feature_ids,
            algorithm="xgboost",
            hyperparameters={
                "epochs": 120,
                "batch_size": 32,
                "learning_rate": 0.001,
                "validation_split": 0.2,
            },
            status="success",
            started_at=now - timedelta(hours=2),
            finished_at=now - timedelta(hours=1, minutes=30),
            metrics={
                "accuracy": 0.62,
                "precision": 0.58,
                "recall": 0.55,
                "f1_score": 0.56,
                "auc": 0.67,
            },
            created_by=created_by,
            created_at=now - timedelta(hours=2),
        )
        db.add(job)
        db.flush()
        created["training_job"] = {
            "id": job.id,
            "job_name": job.job_name,
            "status": job.status,
        }

    seed_job = (
        db.query(DrawTrainingJob)
        .order_by(DrawTrainingJob.created_at.desc(), DrawTrainingJob.id.desc())
        .first()
    )

    model_count = db.query(DrawModelVersion).count()
    if model_count == 0 and seed_job:
        metrics = seed_job.metrics if isinstance(seed_job.metrics, dict) else {
            "accuracy": 0.60,
            "precision": 0.56,
            "recall": 0.53,
            "f1_score": 0.54,
            "auc": 0.65,
        }
        model = DrawModelVersion(
            version_tag=f"v{now.strftime('%Y.%m.%d')}-mock",
            training_job_id=seed_job.id,
            model_path=f"/models/mock/job_{seed_job.id}/model.pkl",
            performance_metrics=metrics,
            status="active",
            deployed_at=now - timedelta(minutes=20),
            created_at=now - timedelta(minutes=25),
        )
        db.add(model)
        db.flush()
        created["model_version"] = {
            "id": model.id,
            "version_tag": model.version_tag,
            "status": model.status,
        }

    seed_model = (
        db.query(DrawModelVersion)
        .order_by(DrawModelVersion.created_at.desc(), DrawModelVersion.id.desc())
        .first()
    )

    prediction_count = db.query(DrawPredictionResult).count()
    if prediction_count == 0:
        pred = DrawPredictionResult(
            match_id=f"MOCK-{now.strftime('%Y%m%d')}-001",
            predicted_draw_prob=0.41,
            actual_result="draw",
            prediction_meta={
                "model_version_id": seed_model.id if seed_model else None,
                "model_version_tag": seed_model.version_tag if seed_model else None,
                "source": "mock_bootstrap",
            },
            predicted_at=now - timedelta(minutes=10),
            match_time=now + timedelta(hours=2),
        )
        db.add(pred)
        db.flush()
        created["prediction"] = {
            "id": pred.id,
            "match_id": pred.match_id,
        }

    db.commit()

    after_counts = {
        "features": db.query(DrawFeature).count(),
        "training_jobs": db.query(DrawTrainingJob).count(),
        "model_versions": db.query(DrawModelVersion).count(),
        "predictions": db.query(DrawPredictionResult).count(),
    }
    return {
        "created": created,
        "counts": after_counts,
        "feature_count_before": feature_count,
        "feature_count_keep": feature_count == after_counts["features"],
    }

# ===== Feature 相关接口 =====
@router.get("/features", response_model=dict)
async def list_features(
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=200),
    db: Session = Depends(get_db),
):
    # DB-level pagination to keep UI paging accurate.
    q = db.query(DrawFeature)
    if keyword:
        q = q.filter(DrawFeature.name.contains(keyword))

    total = q.count()
    features = (
        q.order_by(DrawFeature.created_at.desc(), DrawFeature.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    items = [
        {
            "id": f.id,
            "name": f.name,
            "description": f.description,
            "source_type": f.source_type,
            "created_at": f.created_at,
            "is_active": f.is_active,
        }
        for f in features
    ]

    # Compatible with frontend `request` interceptor: it returns `res.data`.
    return {
        "success": True,
        "message": "ok",
        "data": {
            "data": items,
            "total": total,
            "page": page,
            "size": size,
        },
    }

@router.post("/features", response_model=dict)
async def create_feature(data: dict = Body(...), db: Session = Depends(get_db)):
    obj = svc.create_feature(db, data)
    return {"id": obj.id, "name": obj.name}

@router.put("/features/{feature_id}", response_model=dict)
async def update_feature(feature_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    obj = svc.update_feature(db, feature_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"id": obj.id, "name": obj.name}

@router.delete("/features/{feature_id}", response_model=dict)
async def delete_feature(feature_id: int, db: Session = Depends(get_db)):
    ok = svc.delete_feature(db, feature_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"msg": "deleted"}

# ===== TrainingJob 相关接口 =====
@router.post("/training-jobs", response_model=dict)
async def create_training_job(data: dict = Body(...), db: Session = Depends(get_db)):
    """Create training job and dispatch to async executor."""
    from ...celery_app import celery_app, run_training_job_local

    created_by = _resolve_created_by_id(db)
    try:
        obj = svc.create_training_job(db, data, created_by)
    except svc.TrainingValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.to_detail())

    svc.append_training_log(obj.id, "Training job created and waiting for dispatch.")

    task_id = None
    queue_warning = None
    dispatch_mode = "celery"
    broker_url = str(getattr(celery_app.conf, "broker_url", "") or "")
    queue_available = _ENABLE_CELERY_DISPATCH and _is_broker_endpoint_reachable(
        broker_url, timeout_seconds=1.0
    )
    if not _ENABLE_CELERY_DISPATCH:
        queue_warning = "Queue dispatch disabled by runtime config, switched to local async training."
        dispatch_mode = "local_async_fallback"
        svc.append_training_log(obj.id, queue_warning)
        try:
            _TRAINING_TASK_EXECUTOR.submit(run_training_job_local, obj.id)
            svc.append_training_log(obj.id, "Local async training has started.")
        except Exception as local_exc:
            queue_warning = f"{queue_warning}; local fallback start failed: {local_exc}"
            dispatch_mode = "dispatch_failed"
            svc.append_training_log(obj.id, queue_warning)
    elif not queue_available:
        queue_warning = "Queue broker unreachable, switched to local async training."
        dispatch_mode = "local_async_fallback"
        svc.append_training_log(obj.id, queue_warning)
        try:
            _TRAINING_TASK_EXECUTOR.submit(run_training_job_local, obj.id)
            svc.append_training_log(obj.id, "Local async training has started.")
        except Exception as local_exc:
            queue_warning = f"{queue_warning}; local fallback start failed: {local_exc}"
            dispatch_mode = "dispatch_failed"
            svc.append_training_log(obj.id, queue_warning)
    else:
        try:
            task = celery_app.send_task("train_model_task", args=[obj.id])
            task_id = task.id
            obj.celery_task_id = task_id
            svc.append_training_log(obj.id, f"Task dispatched to queue, task_id={task_id}")
        except Exception as exc:
            queue_warning = f"Queue dispatch failed, switched to local async training: {exc}"
            dispatch_mode = "local_async_fallback"
            svc.append_training_log(obj.id, queue_warning)
            try:
                _TRAINING_TASK_EXECUTOR.submit(run_training_job_local, obj.id)
                svc.append_training_log(obj.id, "Local async training has started.")
            except Exception as local_exc:
                queue_warning = f"{queue_warning}; local fallback start failed: {local_exc}"
                dispatch_mode = "dispatch_failed"
                svc.append_training_log(obj.id, queue_warning)

    db.commit()

    return {
        "id": obj.id,
        "job_name": obj.job_name,
        "status": obj.status,
        "celery_task_id": task_id,
        "queue_warning": queue_warning,
        "dispatch_mode": dispatch_mode,
    }

@router.get("/training-jobs", response_model=List[dict])
async def list_training_jobs(keyword: Optional[str] = None, db: Session = Depends(get_db)):
    jobs = svc.get_training_jobs(db, keyword)
    return [
        {
            "id": j.id,
            "job_name": j.job_name,
            "status": j.status,
            "started_at": j.started_at,
            "finished_at": j.finished_at,
            "metrics": j.metrics
        }
        for j in jobs
    ]

@router.get("/training-jobs/summary", response_model=dict)
async def get_training_jobs_summary(db: Session = Depends(get_db)):
    jobs = svc.get_training_jobs(db)
    summary = {
        "pending": 0,
        "running": 0,
        "success": 0,
        "failed": 0,
        "total": len(jobs),
    }
    for job in jobs:
        status = str(job.status or "").lower()
        if status == "pending":
            summary["pending"] += 1
        elif status in {"running", "training"}:
            summary["running"] += 1
        elif status in {"success", "trained", "evaluated"}:
            summary["success"] += 1
        elif status == "failed":
            summary["failed"] += 1
    return {
        "success": True,
        "message": "ok",
        "data": summary,
    }

@router.get("/training-jobs/{job_id}/logs", response_model=dict)
async def get_job_logs(job_id: int):
    logs = svc.get_training_logs(job_id)
    return {"logs": logs}

# 测试用：手动变更任务状态（实际应由后台任务队列完成）
@router.put("/training-jobs/{job_id}/status", response_model=dict)
async def set_job_status(job_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """更新训练任务状态，可选传入模型路径和性能指标"""
    status = str(data.get('status') or '').lower()
    metrics = data.get('metrics')
    model_path = data.get('model_path')
    if status not in {"pending", "running", "training", "success", "failed", "trained", "evaluated"}:
        raise HTTPException(status_code=422, detail="invalid status")
    
    metrics_dict = metrics if isinstance(metrics, dict) else (json.loads(metrics) if metrics else None)
    
    obj = svc.update_training_job_status(db, job_id, status, metrics_dict, model_path)
    if not obj:
        raise HTTPException(status_code=404, detail="Training job not found")
    svc.append_training_log(job_id, f"状态变更为 {status}")
    if status == "success":
        svc.append_training_log(job_id, "自动创建模型版本")
    return {"id": obj.id, "status": obj.status}

# ===== Model Version 相关接口 =====
@router.get("/models", response_model=List[dict])
async def list_models(keyword: Optional[str] = None, db: Session = Depends(get_db)):
    models = svc.get_model_versions(db, keyword)
    return [
        {
            "id": m.id,
            "version_tag": m.version_tag,
            "training_job_id": m.training_job_id,
            "performance_metrics": m.performance_metrics,
            "status": m.status,
            "deployed_at": m.deployed_at
        }
        for m in models
    ]

@router.get("/models/{model_id}/trace", response_model=dict)
async def get_model_trace(model_id: int, db: Session = Depends(get_db)):
    model = db.query(DrawModelVersion).filter(DrawModelVersion.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found")

    job = db.query(DrawTrainingJob).filter(DrawTrainingJob.id == model.training_job_id).first()
    feature_ids = []
    feature_items: List[Dict[str, Any]] = []
    if job and isinstance(job.feature_set_ids, list):
        feature_ids = job.feature_set_ids
    if feature_ids:
        features = (
            db.query(DrawFeature)
            .filter(DrawFeature.id.in_(feature_ids))
            .order_by(DrawFeature.id.asc())
            .all()
        )
        feature_items = [
            {
                "id": f.id,
                "name": f.name,
                "source_type": f.source_type,
                "is_active": f.is_active,
            }
            for f in features
        ]

    return {
        "success": True,
        "message": "ok",
        "data": {
            "model_id": model.id,
            "version_tag": model.version_tag,
            "model_status": model.status,
            "deployed_at": model.deployed_at,
            "training_job": {
                "id": job.id if job else model.training_job_id,
                "job_name": job.job_name if job else None,
                "status": job.status if job else None,
                "algorithm": job.algorithm if job else None,
                "metrics": job.metrics if job else None,
            },
            "feature_set": {
                "ids": feature_ids,
                "items": feature_items,
            },
        },
    }

@router.post("/models/{model_id}/deploy", response_model=dict)
async def deploy_model(model_id: int, db: Session = Depends(get_db)):
    obj = svc.deploy_model_version(db, model_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Model version not found")
    return {"id": obj.id, "status": obj.status}

@router.post("/models/{model_id}/rollback", response_model=dict)
async def rollback_model(model_id: int, db: Session = Depends(get_db)):
    obj = svc.rollback_model_version(db, model_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Model version not found")
    return {"id": obj.id, "status": obj.status}

# ===== Prediction 相关接口 =====
@router.get("/predictions", response_model=dict)
async def list_predictions(
    match_id: Optional[str] = Query(None),
    model_version_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    预测监控数据（带分页 + 统计），返回结构与前端 request 拦截器兼容：{success, message, data: {...}}。
    """
    q = db.query(DrawPredictionResult)
    if match_id:
        q = q.filter(DrawPredictionResult.match_id == match_id)
    if start_date:
        q = q.filter(DrawPredictionResult.predicted_at >= start_date)
    if end_date:
        q = q.filter(DrawPredictionResult.predicted_at <= end_date)

    if model_version_id is not None:
        all_candidates = q.order_by(DrawPredictionResult.predicted_at.desc(), DrawPredictionResult.id.desc()).all()
        filtered_candidates = []
        for row in all_candidates:
            meta = _normalize_meta(row.prediction_meta)
            if _extract_model_version_id(meta) == model_version_id:
                filtered_candidates.append(row)
        total = len(filtered_candidates)
        stats = _calc_prediction_stats(filtered_candidates)
        preds = filtered_candidates[(page - 1) * size : page * size]
    else:
        total = q.count()
        finished_q = q.filter(DrawPredictionResult.actual_result.isnot(None))
        finished = finished_q.count()
        hits = finished_q.filter(DrawPredictionResult.actual_result == "draw").count()
        pending = total - finished
        accuracy = round((hits / finished) * 100, 1) if finished > 0 else 0.0
        stats = {
            "total": total,
            "finished": finished,
            "hits": hits,
            "accuracy": accuracy,
            "pending": pending,
        }
        preds = (
            q.order_by(DrawPredictionResult.predicted_at.desc(), DrawPredictionResult.id.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

    items = []
    for p in preds:
        meta = _normalize_meta(p.prediction_meta)
        items.append(
            {
                "id": p.id,
                "match_id": p.match_id,
                "predicted_draw_prob": p.predicted_draw_prob,
                "actual_result": p.actual_result,
                "predicted_at": p.predicted_at,
                "match_time": p.match_time,
                "prediction_meta": meta,
                "model_version_id": _extract_model_version_id(meta),
            }
        )

    return {
        "success": True,
        "message": "ok",
        "data": {
            "data": items,
            "total": total,
            "page": page,
            "size": size,
            "stats": stats,
        },
    }


@router.get("/predictions/summary", response_model=dict)
async def get_prediction_summary(
    model_version_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(DrawPredictionResult)
    if start_date:
        q = q.filter(DrawPredictionResult.predicted_at >= start_date)
    if end_date:
        q = q.filter(DrawPredictionResult.predicted_at <= end_date)
    rows = q.order_by(DrawPredictionResult.predicted_at.desc(), DrawPredictionResult.id.desc()).all()
    if model_version_id is not None:
        rows = [
            row
            for row in rows
            if _extract_model_version_id(_normalize_meta(row.prediction_meta)) == model_version_id
        ]
    return {
        "success": True,
        "message": "ok",
        "data": _calc_prediction_stats(rows),
    }


@router.post("/retrain-drafts", response_model=dict)
async def create_retrain_draft(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    model_version_id = payload.get("model_version_id")
    reason = payload.get("reason") or "监控指标下降，建议再训练"
    if not model_version_id:
        raise HTTPException(status_code=422, detail="model_version_id is required")

    model = db.query(DrawModelVersion).filter(DrawModelVersion.id == int(model_version_id)).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found")

    job = db.query(DrawTrainingJob).filter(DrawTrainingJob.id == model.training_job_id).first()
    feature_set_ids = []
    algorithm = "xgboost"
    hyperparameters = {"epochs": 120, "batch_size": 32, "learning_rate": 0.001}
    if job:
        if isinstance(job.feature_set_ids, list):
            feature_set_ids = job.feature_set_ids
        if isinstance(job.algorithm, str) and job.algorithm:
            algorithm = job.algorithm
        if isinstance(job.hyperparameters, dict):
            hyperparameters = job.hyperparameters

    draft_id = f"retrain_{_utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:6]}"
    draft = {
        "draft_id": draft_id,
        "status": "draft",
        "reason": reason,
        "model_version_id": int(model_version_id),
        "source_training_job_id": model.training_job_id,
        "suggestion": {
            "job_name": f"再训练_{model.version_tag}_{_utcnow().strftime('%Y%m%d')}",
            "algorithm": algorithm,
            "feature_set_ids": feature_set_ids,
            "hyperparameters": hyperparameters,
        },
        "created_at": _utcnow(),
        "submitted_training_job_id": None,
        "submitted_at": None,
    }
    with _RETRAIN_DRAFTS_LOCK:
        _RETRAIN_DRAFTS[draft_id] = draft
    return {
        "success": True,
        "message": "ok",
        "data": _serialize_retrain_draft(draft),
    }


@router.get("/retrain-drafts/{draft_id}", response_model=dict)
async def get_retrain_draft(draft_id: str):
    with _RETRAIN_DRAFTS_LOCK:
        draft = _RETRAIN_DRAFTS.get(draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        return {
            "success": True,
            "message": "ok",
            "data": _serialize_retrain_draft(draft),
        }


@router.post("/retrain-drafts/{draft_id}/submit", response_model=dict)
async def submit_retrain_draft(
    draft_id: str,
    db: Session = Depends(get_db),
):
    with _RETRAIN_DRAFTS_LOCK:
        draft = _RETRAIN_DRAFTS.get(draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        if draft.get("status") == "submitted":
            return {
                "success": True,
                "message": "ok",
                "data": _serialize_retrain_draft(draft),
            }

    suggestion = draft.get("suggestion") or {}
    created_by = _resolve_created_by_id(db)
    try:
        job = svc.create_training_job(
            db,
            {
                "job_name": suggestion.get("job_name") or f"retrain_job_{_utcnow().strftime('%Y%m%d%H%M%S')}",
                "feature_set_ids": suggestion.get("feature_set_ids") or [],
                "algorithm": suggestion.get("algorithm") or "xgboost",
                "hyperparameters": suggestion.get("hyperparameters") or {},
            },
            created_by=created_by,
        )
    except svc.TrainingValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.to_detail())
    svc.append_training_log(job.id, f"Created from retrain draft {draft_id}")

    with _RETRAIN_DRAFTS_LOCK:
        latest = _RETRAIN_DRAFTS.get(draft_id)
        if latest:
            latest["status"] = "submitted"
            latest["submitted_training_job_id"] = job.id
            latest["submitted_at"] = _utcnow()
            draft = latest

    return {
        "success": True,
        "message": "ok",
        "data": _serialize_retrain_draft(draft),
    }


@router.post("/mock/bootstrap", response_model=dict)
async def bootstrap_draw_prediction_mock_data(db: Session = Depends(get_db)):
    result = _bootstrap_draw_prediction_mock_data(db)
    return {
        "success": True,
        "message": "ok",
        "data": result,
    }


@router.get("/mock/bootstrap/status", response_model=dict)
async def get_bootstrap_status(db: Session = Depends(get_db)):
    counts = {
        "features": db.query(DrawFeature).count(),
        "training_jobs": db.query(DrawTrainingJob).count(),
        "model_versions": db.query(DrawModelVersion).count(),
        "predictions": db.query(DrawPredictionResult).count(),
    }
    return {
        "success": True,
        "message": "ok",
        "data": {
            "counts": counts,
            "page_ready": {
                "data_features": counts["features"] >= 17,
                "training_evaluation": counts["training_jobs"] >= 1,
                "model_deployment": counts["model_versions"] >= 1,
                "prediction_monitoring": counts["predictions"] >= 1,
            },
            "feature_count_keep": counts["features"] >= 17,
        },
    }

# ===== 通用抓取任务状态 =====
@router.get("/tasks/{task_id}", response_model=dict)
def get_fetch_task_status(task_id: str):
    task = _get_fetch_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或已过期")
    return {
        "success": True,
        "message": "ok",
        "data": task,
    }


# ===== 形态B：draw-suggestion 接口 =====
@router.post("/draw-suggestion/odds-snapshots/fetch-async", response_model=dict)
def draw_suggestion_fetch_snapshots_async(
    date_str: Optional[str] = Query(None, description="比赛日期 YYYY-MM-DD"),
    source: str = Query("500", description="数据源"),
):
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
    except Exception:
        raise HTTPException(status_code=400, detail="INVALID_DATE")

    task_id = _create_fetch_task("draw_suggestion_snapshot_fetch", params={"date": target_date.isoformat(), "source": source})
    _FETCH_TASK_EXECUTOR.submit(_run_draw_suggestion_snapshot_fetch_task, task_id, target_date, source)
    return {
        "success": True,
        "message": "任务已提交",
        "data": {"task_id": task_id, "status": "pending", "polling_interval_ms": 1200},
    }


@router.get("/draw-suggestion/odds-snapshots", response_model=dict)
def draw_suggestion_list_snapshots(
    match_id: Optional[str] = Query(None),
    date_str: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    data = OddsSnapshotService.list_snapshots(db, match_id=match_id, date_str=date_str, page=page, page_size=page_size)
    return {"success": True, "message": "ok", "data": data}


@router.post("/draw-suggestion/suggestions/generate-async", response_model=dict)
def draw_suggestion_generate_async(payload: dict = Body(default={})):
    req = payload or {}
    date_value = req.get("date") or req.get("date_str")
    force = bool(req.get("force") or False)

    try:
        target_date = datetime.strptime(str(date_value), "%Y-%m-%d").date() if date_value else datetime.now().date()
    except Exception:
        raise HTTPException(status_code=400, detail="INVALID_DATE")

    task_id = _create_fetch_task(
        "draw_suggestion_generate",
        params={"date": target_date.isoformat(), "force": force},
    )
    _FETCH_TASK_EXECUTOR.submit(_run_draw_suggestion_generate_task, task_id, target_date, force)
    return {
        "success": True,
        "message": "任务已提交",
        "data": {"task_id": task_id, "status": "pending", "polling_interval_ms": 1200},
    }


@router.get("/draw-suggestion/suggestions", response_model=dict)
def draw_suggestion_list(
    date_str: Optional[str] = Query(None),
    decision: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    data = DrawSuggestionService.list_suggestions(db, date_str=date_str, decision=decision, page=page, page_size=page_size)
    return {"success": True, "message": "ok", "data": data}


@router.get("/draw-suggestion/suggestions/{suggestion_id}", response_model=dict)
def draw_suggestion_detail(suggestion_id: int, db: Session = Depends(get_db)):
    row = DrawSuggestionService.get_suggestion(db, suggestion_id)
    if not row:
        raise HTTPException(status_code=404, detail="suggestion not found")
    return {
        "success": True,
        "message": "ok",
        "data": {
            "id": row.id,
            "match_id": row.match_id,
            "decision": row.decision,
            "stake_pct": row.stake_pct,
            "edge": row.edge,
            "reason_codes": row.reason_codes or [],
            "reason_text": row.reason_text,
            "features": row.features or {},
            "killswitch_state": row.killswitch_state,
            "created_at": row.created_at,
        },
    }


@router.post("/draw-suggestion/paper-bets/create", response_model=dict)
def draw_suggestion_create_paper_bets(payload: dict = Body(...), db: Session = Depends(get_db)):
    suggestion_ids = payload.get("suggestion_ids") if isinstance(payload, dict) else []
    if not isinstance(suggestion_ids, list) or not suggestion_ids:
        raise HTTPException(status_code=422, detail="suggestion_ids is required")
    data = DrawSuggestionService.create_paper_bets(db, suggestion_ids)
    return {"success": True, "message": "ok", "data": data}


@router.post("/draw-suggestion/paper-bets/settle-async", response_model=dict)
def draw_suggestion_settle_async(payload: dict = Body(default={})):
    req = payload or {}
    date_value = req.get("date") or req.get("date_str")
    target_date: Optional[date] = None
    if date_value:
        try:
            target_date = datetime.strptime(str(date_value), "%Y-%m-%d").date()
        except Exception:
            raise HTTPException(status_code=400, detail="INVALID_DATE")

    task_id = _create_fetch_task(
        "draw_suggestion_settle",
        params={"date": target_date.isoformat() if target_date else None},
    )
    _FETCH_TASK_EXECUTOR.submit(_run_draw_suggestion_settle_task, task_id, target_date)
    return {
        "success": True,
        "message": "任务已提交",
        "data": {"task_id": task_id, "status": "pending", "polling_interval_ms": 1200},
    }


@router.get("/draw-suggestion/metrics/summary", response_model=dict)
def draw_suggestion_metrics_summary(days: int = Query(7, ge=1, le=180), db: Session = Depends(get_db)):
    data = DrawSuggestionService.get_metrics_summary(db, days=days)
    return {"success": True, "message": "ok", "data": data}


@router.get("/draw-suggestion/killswitch/state", response_model=dict)
def draw_suggestion_killswitch_state(db: Session = Depends(get_db)):
    try:
        data = DrawSuggestionService.get_killswitch_state(db)
        return {"success": True, "message": "ok", "data": data}
    except Exception as exc:
        return {
            "success": True,
            "message": f"killswitch degraded: {exc}",
            "data": {
                "state": "RUN",
                "reason": {"mode": "degraded", "message": "killswitch endpoint fallback"},
                "manual_override": 0,
                "updated_at": datetime.utcnow().isoformat(),
            },
        }



@router.post("/draw-suggestion/killswitch/manual-stop", response_model=dict)
def draw_suggestion_killswitch_stop(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    data = DrawSuggestionService.set_killswitch_state(
        db,
        state="STOP",
        operator=(payload or {}).get("operator"),
        note=(payload or {}).get("note"),
        manual_override=1,
    )
    return {"success": True, "message": "ok", "data": data}


@router.post("/draw-suggestion/killswitch/manual-release", response_model=dict)
def draw_suggestion_killswitch_release(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    data = DrawSuggestionService.set_killswitch_state(
        db,
        state="RUN",
        operator=(payload or {}).get("operator"),
        note=(payload or {}).get("note"),
        manual_override=1,
    )
    return {"success": True, "message": "ok", "data": data}


# ===== LLM 文案接口 =====
@router.post("/llm/explain", response_model=dict)
def llm_explain(payload: dict = Body(...)):
    result = LLMContentService.explain(payload or {})
    return result


@router.post("/llm/alert-summary", response_model=dict)
def llm_alert_summary(payload: dict = Body(...)):
    result = LLMContentService.alert_summary(payload or {})
    return result


@router.post("/llm/report", response_model=dict)
def llm_report(payload: dict = Body(...)):
    result = LLMContentService.report(payload or {})
    return result


# ===== Poisson 1-1 扫盘接口 =====
@router.post("/poisson-11/fetch-async", response_model=dict)
def fetch_poisson_11_async(
    date_str: Optional[str] = Query(None, description="比赛日期 YYYY-MM-DD"),
    data_source: str = Query("yingqiu_bd", description="数据源，默认yingqiu_bd"),
):
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
    task_id = _create_fetch_task(
        "poisson11_fetch",
        params={"date": target_date.isoformat(), "data_source": data_source},
    )
    _FETCH_TASK_EXECUTOR.submit(_run_poisson_fetch_task, task_id, target_date, data_source)
    return {
        "success": True,
        "message": "任务已提交",
        "data": {
            "task_id": task_id,
            "status": "pending",
            "polling_interval_ms": 1200,
        },
    }


@router.post("/poisson-11/fetch", response_model=dict)
def fetch_poisson_11(
    date_str: Optional[str] = Query(None, description="比赛日期 YYYY-MM-DD"),
    data_source: str = Query("yingqiu_bd", description="数据源，默认yingqiu_bd"),
    db: Session = Depends(get_db),
):
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
    schedule_source = "yingqiu_bd" if data_source == "yingqiu_bd" else "500w"
    results = poisson_11_service.scan_for_date(db, target_date, data_source=data_source, overwrite=True)
    return {
        "success": True,
        "message": "ok",
        "data": {
            "date": target_date.isoformat(),
            "data_source": data_source,
            "schedule_source": schedule_source,
            "total": len(results),
        },
    }


@router.get("/poisson-11/list", response_model=dict)
def list_poisson_11(
    date_str: Optional[str] = Query(None, description="比赛日期 YYYY-MM-DD"),
    data_source: str = Query("yingqiu_bd", description="数据源，默认yingqiu_bd"),
    db: Session = Depends(get_db),
):
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
    schedule_source = "yingqiu_bd" if data_source == "yingqiu_bd" else "500w"
    results = poisson_11_service.list_results(db, target_date, data_source=data_source)
    match_ids = [r.match_id for r in results]
    number_map = {}
    odds_11_map = {}
    odds_11_source_map = {}
    if match_ids:
        rows = (
            db.query(Match.match_identifier, Match.source_attributes, Match.source_match_id)
            .filter(Match.match_identifier.in_(match_ids))
            .filter(Match.data_source == schedule_source)
            .all()
        )
        for match_identifier, source_attrs, source_match_id in rows:
            attrs = {}
            if isinstance(source_attrs, dict):
                attrs = source_attrs
            elif isinstance(source_attrs, str) and source_attrs:
                try:
                    attrs = json.loads(source_attrs)
                except json.JSONDecodeError:
                    attrs = {}
            number_map[match_identifier] = attrs.get("number") or source_match_id
            odds_11_map[match_identifier] = (
                attrs.get("odds_score_11")
                or attrs.get("score_odds_11")
                or attrs.get("odds_11")
                or attrs.get("odds11")
            )
            odds_11_source_map[match_identifier] = attrs.get("odds_score_11_source")

    items = []
    for r in results:
        payload = r.input_payload or {}
        number_value = payload.get("number") or number_map.get(r.match_id)

        items.append(
            {
                "match_id": r.match_id,
                "match_date": r.match_date,
                "match_time": r.match_time,
                "league": r.league,
                "home_team": r.home_team,
                "away_team": r.away_team,
                "number": number_value,
                "mu_total": r.mu_total,
                "mu_diff": r.mu_diff,
                "mu_home": r.mu_home,
                "mu_away": r.mu_away,
                "prob_11": r.prob_11,
                "odds_11": payload.get("odds_score_11") or odds_11_map.get(r.match_id),
                "odds_11_source": payload.get("odds_score_11_source") or odds_11_source_map.get(r.match_id),
                "rank": r.rank,
                "data_source": r.data_source,
            }
        )
    return {
        "success": True,
        "message": "ok",
        "data": {
            "date": target_date.isoformat(),
            "data_source": data_source,
            "schedule_source": schedule_source,
            "total": len(items),
            "items": items,
        },
    }


@router.get("/poisson-11/detail/{match_id}", response_model=dict)
def get_poisson_11_detail(
    match_id: str,
    data_source: str = Query("yingqiu_bd", description="数据源，默认yingqiu_bd"),
    db: Session = Depends(get_db),
):
    result = poisson_11_service.get_detail(db, match_id, data_source=data_source)
    if not result:
        raise HTTPException(status_code=404, detail="模型数据不存在")
    number = (result.input_payload or {}).get("number")
    if not number:
        schedule_source = "yingqiu_bd" if data_source == "yingqiu_bd" else "500w"
        match = (
            db.query(Match)
            .filter(Match.match_identifier == match_id, Match.data_source == schedule_source)
            .first()
        )
        if match:
            attrs = match.source_attributes if isinstance(match.source_attributes, dict) else {}
            if not attrs and isinstance(match.source_attributes, str):
                try:
                    attrs = json.loads(match.source_attributes)
                except json.JSONDecodeError:
                    attrs = {}
            number = attrs.get("number") or match.source_match_id
    return {
        "success": True,
        "message": "ok",
        "data": {
            "match_id": result.match_id,
            "match_date": result.match_date,
            "match_time": result.match_time,
            "league": result.league,
            "home_team": result.home_team,
            "away_team": result.away_team,
            "number": number,
            "mu_total": result.mu_total,
            "mu_diff": result.mu_diff,
            "mu_home": result.mu_home,
            "mu_away": result.mu_away,
            "prob_11": result.prob_11,
            "odds_11": (result.input_payload or {}).get("odds_score_11"),
            "odds_11_source": (result.input_payload or {}).get("odds_score_11_source"),
            "rank": result.rank,
            "data_source": result.data_source,
            "input_payload": result.input_payload,
        },
    }


# ===== AI 平局预测扫盘接口（北单/盈球） =====
@router.get("/ai-draw/rules", response_model=dict)
async def get_ai_draw_rules(db: Session = Depends(get_db)):
    rules = ai_draw_prediction_service.get_rules(db)
    return {
        "success": True,
        "message": "ok",
        "data": {"rules": rules},
    }


@router.put("/ai-draw/rules", response_model=dict)
async def save_ai_draw_rules(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    rules = payload.get("rules") if isinstance(payload, dict) else None
    if rules is None:
        rules = payload
    saved = ai_draw_prediction_service.save_rules(db, rules or {})
    return {
        "success": True,
        "message": "ok",
        "data": {"rules": saved},
    }


@router.get("/ai-draw/rules/{match_id}", response_model=dict)
async def get_ai_draw_match_rules(
    match_id: str,
    db: Session = Depends(get_db),
):
    rules = ai_draw_prediction_service.get_match_rules(db, match_id)
    return {
        "success": True,
        "message": "ok",
        "data": {"rules": rules},
    }


@router.put("/ai-draw/rules/{match_id}", response_model=dict)
async def save_ai_draw_match_rules(
    match_id: str,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    rules = payload.get("rules") if isinstance(payload, dict) else None
    if rules is None:
        rules = payload
    saved = ai_draw_prediction_service.save_match_rules(db, match_id, rules or {})
    return {
        "success": True,
        "message": "ok",
        "data": {"rules": saved},
    }


@router.get("/ai-draw/overrides/{match_id}", response_model=dict)
async def get_ai_draw_match_overrides(
    match_id: str,
    db: Session = Depends(get_db),
):
    overrides = ai_draw_prediction_service.get_match_overrides(db, match_id)
    return {
        "success": True,
        "message": "ok",
        "data": {"overrides": overrides},
    }


@router.put("/ai-draw/overrides/{match_id}", response_model=dict)
async def save_ai_draw_match_overrides(
    match_id: str,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    overrides = payload.get("overrides") if isinstance(payload, dict) else None
    if overrides is None:
        overrides = payload
    saved = ai_draw_prediction_service.save_match_overrides(db, match_id, overrides or {})
    return {
        "success": True,
        "message": "ok",
        "data": {"overrides": saved},
    }


@router.post("/ai-draw/fetch", response_model=dict)
async def fetch_ai_draw(
    date_str: Optional[str] = Query(None, description="比赛日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
    items = ai_draw_prediction_service.list_for_date(db, target_date, data_source="yingqiu_bd")
    return {
        "success": True,
        "message": "ok",
        "data": {
            "date": target_date.isoformat(),
            "data_source": "yingqiu_bd",
            "total": len(items),
        },
    }


@router.post("/ai-draw/fetch-async", response_model=dict)
def fetch_ai_draw_async(
    date_str: Optional[str] = Query(None, description="比赛日期 YYYY-MM-DD"),
):
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
    task_id = _create_fetch_task(
        "ai_draw_fetch",
        params={"date": target_date.isoformat(), "data_source": "yingqiu_bd"},
    )
    _FETCH_TASK_EXECUTOR.submit(_run_ai_draw_fetch_task, task_id, target_date)
    return {
        "success": True,
        "message": "任务已提交",
        "data": {
            "task_id": task_id,
            "status": "pending",
            "polling_interval_ms": 1200,
        },
    }


@router.get("/ai-draw/list", response_model=dict)
async def list_ai_draw(
    date_str: Optional[str] = Query(None, description="比赛日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
    items = ai_draw_prediction_service.list_for_date(db, target_date, data_source="yingqiu_bd")
    return {
        "success": True,
        "message": "ok",
        "data": {
            "date": target_date.isoformat(),
            "data_source": "yingqiu_bd",
            "total": len(items),
            "items": items,
        },
    }


@router.get("/ai-draw/detail/{match_id}", response_model=dict)
async def get_ai_draw_detail(
    match_id: str,
    db: Session = Depends(get_db),
):
    result = ai_draw_prediction_service.get_detail(db, match_id)
    if not result:
        raise HTTPException(status_code=404, detail="模型数据不存在")
    return {
        "success": True,
        "message": "ok",
        "data": result,
    }
