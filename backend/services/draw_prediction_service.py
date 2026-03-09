from datetime import datetime
import json
from typing import Any, List, Optional

from sqlalchemy.orm import Session

from ..models.draw_feature import DrawFeature
from ..models.draw_model_version import DrawModelVersion
from ..models.draw_prediction_result import DrawPredictionResult
from ..models.draw_training_job import DrawTrainingJob, TrainingJobStatus


class TrainingValidationError(ValueError):
    """Raised when a training job request fails strong pre-validation."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        missing_feature_ids: Optional[List[int]] = None,
        inactive_feature_ids: Optional[List[int]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.missing_feature_ids = missing_feature_ids or []
        self.inactive_feature_ids = inactive_feature_ids or []

    def to_detail(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "missing_feature_ids": self.missing_feature_ids,
            "inactive_feature_ids": self.inactive_feature_ids,
        }


def _normalize_feature_ids(raw_feature_ids: Any) -> List[int]:
    if not isinstance(raw_feature_ids, list):
        return []
    result: List[int] = []
    seen = set()
    for raw in raw_feature_ids:
        try:
            value = int(raw)
        except (TypeError, ValueError):
            continue
        if value <= 0 or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def resolve_training_feature_ids(db: Session, raw_feature_ids: Any) -> List[int]:
    """
    Strong validation before training:
    - feature IDs must exist
    - only enabled features can be used
    - if no IDs provided, auto-select all enabled features
    """
    feature_set_ids = _normalize_feature_ids(raw_feature_ids)
    if not feature_set_ids:
        feature_set_ids = [
            int(row[0])
            for row in db.query(DrawFeature.id)
            .filter(DrawFeature.is_active.is_(True))
            .order_by(DrawFeature.id.asc())
            .all()
        ]
        if not feature_set_ids:
            raise TrainingValidationError(
                code="no_active_features",
                message="No active features available for training. Please enable at least one feature.",
            )
        return feature_set_ids

    records = (
        db.query(DrawFeature.id, DrawFeature.is_active)
        .filter(DrawFeature.id.in_(feature_set_ids))
        .all()
    )
    id_to_active = {int(row[0]): bool(row[1]) for row in records}

    missing_feature_ids = sorted([fid for fid in feature_set_ids if fid not in id_to_active])
    if missing_feature_ids:
        raise TrainingValidationError(
            code="missing_feature_ids",
            message="Found non-existent feature IDs. Training request rejected.",
            missing_feature_ids=missing_feature_ids,
        )

    inactive_feature_ids = sorted([fid for fid in feature_set_ids if not id_to_active.get(fid, False)])
    if inactive_feature_ids:
        raise TrainingValidationError(
            code="inactive_feature_ids",
            message="Found disabled feature IDs. Only active features can be trained.",
            inactive_feature_ids=inactive_feature_ids,
        )

    return feature_set_ids


def get_features(db: Session, keyword: Optional[str] = None) -> List[DrawFeature]:
    query = db.query(DrawFeature)
    if keyword:
        query = query.filter(DrawFeature.name.contains(keyword))
    return query.all()


def create_feature(db: Session, data: dict) -> DrawFeature:
    obj = DrawFeature(
        name=data["name"],
        description=data.get("description"),
        source_type=data["source_type"],
        is_active=bool(data.get("is_active", True)),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_feature(db: Session, feature_id: int, data: dict) -> Optional[DrawFeature]:
    obj = db.query(DrawFeature).filter(DrawFeature.id == feature_id).first()
    if not obj:
        return None
    obj.name = data["name"]
    obj.description = data.get("description")
    obj.source_type = data["source_type"]
    if "is_active" in data:
        obj.is_active = bool(data.get("is_active"))
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


def get_training_jobs(db: Session, keyword: Optional[str] = None) -> List[DrawTrainingJob]:
    query = db.query(DrawTrainingJob)
    if keyword:
        query = query.filter(DrawTrainingJob.job_name.contains(keyword))
    return query.order_by(DrawTrainingJob.created_at.desc()).all()


def get_training_job_by_id(db: Session, job_id: int) -> Optional[DrawTrainingJob]:
    return db.query(DrawTrainingJob).filter(DrawTrainingJob.id == job_id).first()


def create_training_job(db: Session, data: dict, created_by: int) -> DrawTrainingJob:
    feature_set_ids = resolve_training_feature_ids(db, data.get("feature_set_ids", []))

    algorithm = data.get("algorithm") or "xgboost"
    hyperparameters = data.get("hyperparameters", data.get("params", {}))
    if isinstance(hyperparameters, str):
        try:
            hyperparameters = json.loads(hyperparameters)
        except Exception:
            hyperparameters = {}
    if not isinstance(hyperparameters, dict):
        hyperparameters = {}

    obj = DrawTrainingJob(
        job_name=data["job_name"],
        feature_set_ids=feature_set_ids,
        algorithm=algorithm,
        hyperparameters=hyperparameters,
        status=TrainingJobStatus.PENDING,
        created_by=created_by,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_training_job_status(
    db: Session,
    job_id: int,
    status: TrainingJobStatus,
    metrics: Optional[dict] = None,
    model_path: Optional[str] = None,
):
    obj = db.query(DrawTrainingJob).filter(DrawTrainingJob.id == job_id).first()
    if not obj:
        return None

    status_value = str(getattr(status, "value", status)).lower()
    obj.status = status_value
    if status_value in ("running", "training"):
        obj.started_at = datetime.utcnow()
    elif status_value in ("success", "failed", "trained", "evaluated"):
        obj.finished_at = datetime.utcnow()
    if metrics is not None:
        obj.metrics = metrics
    db.commit()
    db.refresh(obj)

    if status_value == "success":
        create_model_version_from_job(db, job_id, model_path)

    return obj


def delete_training_job(db: Session, job_id: int) -> bool:
    obj = db.query(DrawTrainingJob).filter(DrawTrainingJob.id == job_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


_training_logs = {}


def append_training_log(job_id: int, message: str):
    _training_logs.setdefault(job_id, []).append(f"{datetime.utcnow().isoformat()} - {message}")


def get_training_logs(job_id: int) -> str:
    return "\n".join(_training_logs.get(job_id, []))


def get_model_versions(db: Session, keyword: Optional[str] = None) -> List[DrawModelVersion]:
    query = db.query(DrawModelVersion)
    if keyword:
        query = query.filter(DrawModelVersion.version_tag.contains(keyword))
    return query.order_by(DrawModelVersion.created_at.desc()).all()


def create_model_version_from_job(
    db: Session, job_id: int, model_path: str = None
) -> Optional[DrawModelVersion]:
    job = db.query(DrawTrainingJob).filter(DrawTrainingJob.id == job_id).first()
    if not job or str(job.status or "").lower() != "success":
        return None

    existing_versions = db.query(DrawModelVersion).filter(
        DrawModelVersion.training_job_id == job_id
    ).count()
    version_tag = f"v{existing_versions + 1}"

    model_version = DrawModelVersion(
        version_tag=version_tag,
        training_job_id=job_id,
        model_path=model_path or f"/models/job_{job_id}/model.pkl",
        performance_metrics=job.metrics,
        status="inactive",
    )
    db.add(model_version)
    db.commit()
    db.refresh(model_version)
    return model_version


def deploy_model_version(db: Session, version_id: int) -> Optional[DrawModelVersion]:
    version = db.query(DrawModelVersion).filter(DrawModelVersion.id == version_id).first()
    if not version:
        return None
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


def get_predictions(
    db: Session,
    match_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[DrawPredictionResult]:
    query = db.query(DrawPredictionResult)
    if match_id:
        query = query.filter(DrawPredictionResult.match_id == match_id)
    if start_date:
        query = query.filter(DrawPredictionResult.predicted_at >= start_date)
    if end_date:
        query = query.filter(DrawPredictionResult.predicted_at <= end_date)
    return query.order_by(DrawPredictionResult.predicted_at.desc()).all()
