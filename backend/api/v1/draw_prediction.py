from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from datetime import datetime
import json

# 引入模型和Service
from backend.models.draw_feature import DrawFeature
from backend.models.draw_training_job import TrainingJobStatus
from backend.services.draw_prediction_service import (
    get_features, create_feature, update_feature, delete_feature,
    get_training_jobs, create_training_job, update_training_job_status, delete_training_job,
    get_training_logs, append_training_log,
    get_model_versions, deploy_model_version, rollback_model_version,
    get_predictions,
    get_db
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/draw-prediction", tags=["draw-prediction"])

# ===== Feature 相关接口 =====
@router.get("/features", response_model=List[dict])
async def list_features(keyword: Optional[str] = None, db: Session = Depends(get_db)):
    features = get_features(db, keyword)
    return [
        {
            "id": f.id,
            "name": f.name,
            "description": f.description,
            "source_type": f.source_type,
            "created_at": f.created_at,
            "is_active": f.is_active
        }
        for f in features
    ]

@router.post("/features", response_model=dict)
async def create_feature(data: dict = Body(...), db: Session = Depends(get_db)):
    obj = create_feature(db, data)
    return {"id": obj.id, "name": obj.name}

@router.put("/features/{feature_id}", response_model=dict)
async def update_feature(feature_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    obj = update_feature(db, feature_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"id": obj.id, "name": obj.name}

@router.delete("/features/{feature_id}", response_model=dict)
async def delete_feature(feature_id: int, db: Session = Depends(get_db)):
    ok = delete_feature(db, feature_id)
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
    obj = create_training_job(db, data, created_by)
    append_training_log(obj.id, "训练任务已创建，等待调度")

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
    jobs = get_training_jobs(db, keyword)
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
    logs = get_training_logs(job_id)
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
    
    obj = update_training_job_status(db, job_id, status, metrics_dict, model_path)
    if not obj:
        raise HTTPException(status_code=404, detail="Training job not found")
    append_training_log(job_id, f"状态变更为 {status}")
    if status == TrainingJobStatus.SUCCESS:
        append_training_log(job_id, f"自动创建模型版本")
    return {"id": obj.id, "status": obj.status}

# ===== Model Version 相关接口 =====
@router.get("/models", response_model=List[dict])
async def list_models(keyword: Optional[str] = None, db: Session = Depends(get_db)):
    models = get_model_versions(db, keyword)
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
    obj = deploy_model_version(db, model_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Model version not found")
    return {"id": obj.id, "status": obj.status}

@router.post("/models/{model_id}/rollback", response_model=dict)
async def rollback_model(model_id: int, db: Session = Depends(get_db)):
    obj = rollback_model_version(db, model_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Model version not found")
    return {"id": obj.id, "status": obj.status}

# ===== Prediction 相关接口 =====
@router.get("/predictions", response_model=List[dict])
async def list_predictions(match_id: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, db: Session = Depends(get_db)):
    preds = get_predictions(db, match_id, start_date, end_date)
    return [
        {
            "id": p.id,
            "match_id": p.match_id,
            "predicted_draw_prob": p.predicted_draw_prob,
            "actual_result": p.actual_result,
            "predicted_at": p.predicted_at,
            "match_time": p.match_time
        }
        for p in preds
    ]