from sqlalchemy.orm import Session
from ..models.draw_feature import DrawFeature
from ..models.draw_training_job import DrawTrainingJob, TrainingJobStatus
from ..models.draw_model_version import DrawModelVersion
from datetime import datetime
from typing import List, Optional
import json

def get_features(db: Session, keyword: Optional[str] = None) -> List[DrawFeature]:
    query = db.query(DrawFeature)
    if keyword:
        query = query.filter(DrawFeature.name.contains(keyword))
    return query.all()

def create_feature(db: Session, data: dict) -> DrawFeature:
    obj = DrawFeature(
        name=data['name'],
        description=data.get('description'),
        source_type=data['source_type'],
        is_active=bool(data.get('is_active', True))
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_feature(db: Session, feature_id: int, data: dict) -> Optional[DrawFeature]:
    obj = db.query(DrawFeature).filter(DrawFeature.id == feature_id).first()
    if not obj:
        return None
    obj.name = data['name']
    obj.description = data.get('description')
    obj.source_type = data['source_type']
    # Support toggle in UI
    if 'is_active' in data:
        obj.is_active = bool(data.get('is_active'))
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return obj

def delete_feature(db: Session, feature_id: int) -> bool:
    obj = db.query(DrawFeature).filter(DrawFeature.id == feature_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

# ===== TrainingJob 相关 Service =====
def get_training_jobs(db: Session, keyword: Optional[str] = None) -> List[DrawTrainingJob]:
    query = db.query(DrawTrainingJob)
    if keyword:
        query = query.filter(DrawTrainingJob.job_name.contains(keyword))
    return query.order_by(DrawTrainingJob.created_at.desc()).all()

def get_training_job_by_id(db: Session, job_id: int) -> Optional[DrawTrainingJob]:
    """根据ID获取单个训练任务"""
    return db.query(DrawTrainingJob).filter(DrawTrainingJob.id == job_id).first()

def create_training_job(db: Session, data: dict, created_by: int) -> DrawTrainingJob:
    # feature_set_ids 传过来是 list，转 JSON 存库
    obj = DrawTrainingJob(
        job_name=data['job_name'],
        feature_set_ids=data['feature_set_ids'],
        algorithm=data['algorithm'],
        hyperparameters=data.get('hyperparameters', {}),
        status=TrainingJobStatus.PENDING,
        created_by=created_by
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_training_job_status(db: Session, job_id: int, status: TrainingJobStatus, metrics: Optional[dict] = None, model_path: Optional[str] = None):
    obj = db.query(DrawTrainingJob).filter(DrawTrainingJob.id == job_id).first()
    if not obj:
        return None
    obj.status = status
    if status == TrainingJobStatus.RUNNING:
        obj.started_at = datetime.utcnow()
    elif status in (TrainingJobStatus.SUCCESS, TrainingJobStatus.FAILED):
        obj.finished_at = datetime.utcnow()
    if metrics is not None:
        obj.metrics = metrics
    db.commit()
    db.refresh(obj)

    # 当训练成功时，自动创建模型版本
    if status == TrainingJobStatus.SUCCESS:
        create_model_version_from_job(db, job_id, model_path)

    return obj

def delete_training_job(db: Session, job_id: int) -> bool:
    obj = db.query(DrawTrainingJob).filter(DrawTrainingJob.id == job_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

# ===== 日志模拟（实际可对接文件或数据库）=====
_training_logs = {}  # job_id -> list of log strings

def append_training_log(job_id: int, message: str):
    _training_logs.setdefault(job_id, []).append(f"{datetime.utcnow().isoformat()} - {message}")

def get_training_logs(job_id: int) -> str:
    return "\n".join(_training_logs.get(job_id, []))

# ===== ModelVersion 相关 Service =====
def get_model_versions(db: Session, keyword: Optional[str] = None) -> List[DrawModelVersion]:
    query = db.query(DrawModelVersion)
    if keyword:
        query = query.filter(DrawModelVersion.version_tag.contains(keyword))
    return query.order_by(DrawModelVersion.created_at.desc()).all()

def create_model_version_from_job(db: Session, job_id: int, model_path: str = None) -> Optional[DrawModelVersion]:
    """根据训练任务自动创建模型版本"""
    job = db.query(DrawTrainingJob).filter(DrawTrainingJob.id == job_id).first()
    if not job or job.status != TrainingJobStatus.SUCCESS:
        return None

    # 生成版本标签（例如 v1, v2 或基于时间戳）
    existing_versions = db.query(DrawModelVersion).filter(
        DrawModelVersion.training_job_id == job_id
    ).count()
    version_tag = f"v{existing_versions + 1}"

    # 创建模型版本记录
    model_version = DrawModelVersion(
        version_tag=version_tag,
        training_job_id=job_id,
        model_path=model_path or f"/models/job_{job_id}/model.pkl",
        performance_metrics=job.metrics,
        status="inactive"  # 默认不上线
    )
    db.add(model_version)
    db.commit()
    db.refresh(model_version)
    return model_version

def deploy_model_version(db: Session, version_id: int) -> Optional[DrawModelVersion]:
    version = db.query(DrawModelVersion).filter(DrawModelVersion.id == version_id).first()
    if not version:
        return None
    # 先将所有同任务的模型设为 inactive
    db.query(DrawModelVersion).filter(
        DrawModelVersion.training_job_id == version.training_job_id
    ).update({"status": "inactive"})
    version.status = "active"
    version.deployed_at = datetime.utcnow()
    db.commit()
    db.refresh(version)
    return version

def rollback_model_version(db: Session, version_id: int) -> Optional[DrawModelVersion]:
    version = db.query(DrawModelVersion).filter(DrawModelVersion.id == version_id).first()
    if not version:
        return None
    version.status = "active"
    version.deployed_at = datetime.utcnow()
    db.commit()
    db.refresh(version)
    return version

# ===== PredictionResult 相关 Service =====
from ..models.draw_prediction_result import DrawPredictionResult

def get_predictions(db: Session, match_id: Optional[str] = None,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> List[DrawPredictionResult]:
    query = db.query(DrawPredictionResult)
    if match_id:
        query = query.filter(DrawPredictionResult.match_id == match_id)
    if start_date:
        query = query.filter(DrawPredictionResult.predicted_at >= start_date)
    if end_date:
        query = query.filter(DrawPredictionResult.predicted_at <= end_date)
    return query.order_by(DrawPredictionResult.predicted_at.desc()).all()
