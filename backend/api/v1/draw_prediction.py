from fastapi import APIRouter, Depends, HTTPException, Body, Query
from typing import List, Optional
from datetime import datetime
import json

# 引入模型和Service
from backend.models.draw_feature import DrawFeature
from backend.models.draw_training_job import TrainingJobStatus
from backend.models.draw_prediction_result import DrawPredictionResult
from backend.models.match import Match
from backend.services import draw_prediction_service as svc
from backend.services import poisson_11_service
from backend.services import ai_draw_prediction_service
from backend.api.dependencies import get_db, get_current_active_admin_user
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/draw-prediction",
    tags=["draw-prediction"],
    dependencies=[Depends(get_current_active_admin_user)],
)

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
    """创建训练任务并提交到 Celery 异步执行"""
    from ..celery_app import celery_app
    # 假设从请求中获取当前用户 ID（实际应从 JWT / 依赖注入中取）
    created_by = 1  # TODO: 替换为真实用户 ID

    # 1. 在数据库中创建任务记录（状态为 PENDING）
    obj = svc.create_training_job(db, data, created_by)
    svc.append_training_log(obj.id, "训练任务已创建，等待调度")

    # 2. 提交 Celery 异步任务
    task = celery_app.send_task('train_model_task', args=[obj.id])

    # 3. 关联 Celery task_id（可选，可用于查询任务状态）
    obj.celery_task_id = task.id
    db.commit()

    return {
        "id": obj.id,
        "job_name": obj.job_name,
        "status": obj.status,
        "celery_task_id": task.id
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

@router.get("/training-jobs/{job_id}/logs", response_model=dict)
async def get_job_logs(job_id: int):
    logs = svc.get_training_logs(job_id)
    return {"logs": logs}

# 测试用：手动变更任务状态（实际应由后台任务队列完成）
@router.put("/training-jobs/{job_id}/status", response_model=dict)
async def set_job_status(job_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """更新训练任务状态，可选传入模型路径和性能指标"""
    status = data.get('status')
    metrics = data.get('metrics')
    model_path = data.get('model_path')
    
    # 确保 status 是 TrainingJobStatus 枚举类型
    if isinstance(status, str):
        status = TrainingJobStatus(status)
    
    metrics_dict = metrics if isinstance(metrics, dict) else (json.loads(metrics) if metrics else None)
    
    obj = svc.update_training_job_status(db, job_id, status, metrics_dict, model_path)
    if not obj:
        raise HTTPException(status_code=404, detail="Training job not found")
    svc.append_training_log(job_id, f"状态变更为 {status}")
    if status == TrainingJobStatus.SUCCESS:
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

    total = q.count()
    finished_q = q.filter(DrawPredictionResult.actual_result.isnot(None))
    finished = finished_q.count()
    hits = finished_q.filter(DrawPredictionResult.actual_result == "draw").count()
    pending = total - finished
    accuracy = round((hits / finished) * 100, 1) if finished > 0 else 0.0

    preds = (
        q.order_by(DrawPredictionResult.predicted_at.desc(), DrawPredictionResult.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    items = [
        {
            "id": p.id,
            "match_id": p.match_id,
            "predicted_draw_prob": p.predicted_draw_prob,
            "actual_result": p.actual_result,
            "predicted_at": p.predicted_at,
            "match_time": p.match_time,
        }
        for p in preds
    ]

    return {
        "success": True,
        "message": "ok",
        "data": {
            "data": items,
            "total": total,
            "page": page,
            "size": size,
            "stats": {
                "total": total,
                "finished": finished,
                "hits": hits,
                "accuracy": accuracy,
                "pending": pending,
            },
        },
    }

# ===== Poisson 1-1 扫盘接口 =====
@router.post("/poisson-11/fetch", response_model=dict)
async def fetch_poisson_11(
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
async def list_poisson_11(
    date_str: Optional[str] = Query(None, description="比赛日期 YYYY-MM-DD"),
    data_source: str = Query("yingqiu_bd", description="数据源，默认yingqiu_bd"),
    db: Session = Depends(get_db),
):
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
    schedule_source = "yingqiu_bd" if data_source == "yingqiu_bd" else "500w"
    results = poisson_11_service.list_results(db, target_date, data_source=data_source)
    match_ids = [r.match_id for r in results]
    number_map = {}
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

    items = [
        {
            "match_id": r.match_id,
            "match_date": r.match_date,
            "match_time": r.match_time,
            "league": r.league,
            "home_team": r.home_team,
            "away_team": r.away_team,
            "number": (r.input_payload or {}).get("number") or number_map.get(r.match_id),
            "mu_total": r.mu_total,
            "mu_diff": r.mu_diff,
            "mu_home": r.mu_home,
            "mu_away": r.mu_away,
            "prob_11": r.prob_11,
            "rank": r.rank,
            "data_source": r.data_source,
        }
        for r in results
    ]
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
async def get_poisson_11_detail(
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
