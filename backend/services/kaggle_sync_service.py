"""
Kaggle sync service with real Kaggle download/clean/staging upsert flow.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import logging
import os
import re
import shutil
import threading
import time
import uuid
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models.draw_feature import DrawFeature
from backend.models.external_source_mapping import ExternalSourceMapping
from backend.models.kaggle_dataset_registry import KaggleDatasetRegistry
from backend.models.kaggle_file_manifest import KaggleFileManifest
from backend.models.kaggle_league_staging import KaggleLeagueStaging
from backend.models.kaggle_match_staging import KaggleMatchStaging
from backend.models.kaggle_sync_runs import KaggleSyncRun
from backend.models.kaggle_sync_state import KaggleSyncState
from backend.models.kaggle_team_staging import KaggleTeamStaging
from backend.models.match import League, Match, MatchStatusEnum, Team

logger = logging.getLogger(__name__)
KAGGLE_API_BASE = "https://www.kaggle.com/api/v1"
KAGGLE_VIEW_URL = KAGGLE_API_BASE + "/datasets/view/{owner}/{dataset}"
KAGGLE_DOWNLOAD_URL = KAGGLE_API_BASE + "/datasets/download/{owner}/{dataset}"


class KaggleSyncService:
    """Registry and run-state management for Kaggle sync."""

    MATCH_HOME_KEYS = (
        "home_team",
        "team_home",
        "home_name",
        "hometeam",
        "home_club",
        "home_team_id",
        "hometeamid",
        "homeid",
        "home_id",
    )
    MATCH_AWAY_KEYS = (
        "away_team",
        "team_away",
        "away_name",
        "awayteam",
        "away_club",
        "away_team_id",
        "awayteamid",
        "awayid",
        "away_id",
    )
    MATCH_LEAGUE_KEYS = (
        "league",
        "league_name",
        "competition",
        "tournament",
        "division",
        "event",
        "league_id",
        "leagueid",
        "competition_id",
        "competitionid",
    )
    MATCH_TIME_KEYS = ("match_time", "match_date", "date", "kickoff", "datetime", "utc_date", "time")
    MATCH_ID_KEYS = ("match_id", "id", "fixture_id", "game_id", "event_id", "gameid", "eventid")

    TEAM_NAME_KEYS = ("team_name", "team", "name", "club", "squad", "displayname")
    TEAM_COUNTRY_KEYS = ("country", "nation", "country_name")
    TEAM_ID_KEYS = ("team_id", "id", "club_id", "squad_id", "teamid")

    LEAGUE_NAME_KEYS = (
        "league_name",
        "league",
        "competition",
        "tournament",
        "name",
        "midsizename",
        "understatnotation",
        "leagueshortname",
    )
    LEAGUE_COUNTRY_KEYS = ("country", "nation", "country_name", "region")
    LEAGUE_ID_KEYS = ("league_id", "id", "competition_id", "tournament_id", "leagueid")
    MERGE_SOURCE_LEAGUE = "kaggle_league"
    MERGE_SOURCE_TEAM = "kaggle_team"
    MERGE_SOURCE_MATCH = "kaggle_match"

    DRAW_FEATURE_DEFINITIONS = (
        {
            "name": "kaggle_entity_coverage",
            "description": "Kaggle实体映射覆盖度(0~1)，映射到联赛/主队/客队的比例",
        },
        {
            "name": "kaggle_country_consistency",
            "description": "Kaggle主客队国家一致性(1同国/0异国或未知)",
        },
        {
            "name": "kaggle_enriched_flag",
            "description": "Kaggle增强标记(1=已完成实体合并与特征回填)",
        },
        {
            "name": "kaggle_source_freshness_hours",
            "description": "Kaggle数据新鲜度(小时)，基于同步完成时间与比赛时间差",
        },
    )

    def __init__(self) -> None:
        self._started = False
        self._lock = threading.Lock()
        self._project_root = Path(__file__).resolve().parents[2]
        self._storage_root = self._project_root / "data" / "external" / "kaggle"
        self._stop_event = threading.Event()
        self._scheduler_thread: Optional[threading.Thread] = None
        self._scheduler_tick_seconds = 60

    def start(self) -> None:
        if self._started:
            return
        self._storage_root.mkdir(parents=True, exist_ok=True)
        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True,
            name="kaggle-sync-scheduler",
        )
        self._scheduler_thread.start()
        self._started = True
        logger.info("Kaggle sync service started")

    def shutdown(self) -> None:
        if not self._started:
            return
        self._stop_event.set()
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=2)
        self._started = False
        logger.info("Kaggle sync service stopped")

    def get_status_snapshot(self, db: Session) -> Dict[str, Any]:
        total_datasets = db.query(KaggleDatasetRegistry).count()
        enabled_datasets = db.query(KaggleDatasetRegistry).filter(KaggleDatasetRegistry.enabled == True).count()
        latest_run = db.query(KaggleSyncRun).order_by(KaggleSyncRun.created_at.desc()).first()
        running_count = (
            db.query(KaggleSyncRun)
            .filter(KaggleSyncRun.status.in_(["pending", "running", "queued"]))
            .count()
        )
        failed_count = db.query(KaggleSyncRun).filter(KaggleSyncRun.status == "failed").count()
        kaggle_team_count = db.query(Team).filter(Team.external_source == "kaggle").count()
        kaggle_league_count = db.query(League).filter(League.external_source == "kaggle").count()
        kaggle_match_count = db.query(Match).filter(Match.data_source == "kaggle").count()
        mapped_match_count = (
            db.query(Match)
            .filter(
                Match.data_source == "kaggle",
                Match.home_team_id.isnot(None),
                Match.away_team_id.isnot(None),
                Match.league_id.isnot(None),
            )
            .count()
        )
        mapping_coverage_rate = round((mapped_match_count / kaggle_match_count) * 100, 2) if kaggle_match_count else 0.0

        recent_runs = (
            db.query(KaggleSyncRun.status)
            .order_by(KaggleSyncRun.created_at.desc())
            .limit(100)
            .all()
        )
        success_status = {"success", "succeeded", "completed"}
        quality_score = 0.0
        if recent_runs:
            success_count = sum(1 for (status,) in recent_runs if str(status or "").lower() in success_status)
            quality_score = round((success_count / len(recent_runs)) * 100, 2)

        latest_run_meta = latest_run.run_meta if latest_run and isinstance(latest_run.run_meta, dict) else {}
        latest_merge = latest_run_meta.get("entity_merge", {}) if isinstance(latest_run_meta, dict) else {}
        latest_backfill = latest_run_meta.get("feature_backfill", {}) if isinstance(latest_run_meta, dict) else {}

        return {
            "service_started": self._started,
            "total_datasets": total_datasets,
            "enabled_datasets": enabled_datasets,
            "running_runs": running_count,
            "failed_runs": failed_count,
            "latest_run": self._serialize_run(latest_run) if latest_run else None,
            "kaggle_team_count": kaggle_team_count,
            "kaggle_league_count": kaggle_league_count,
            "kaggle_match_count": kaggle_match_count,
            "mapping_coverage_rate": mapping_coverage_rate,
            "quality_score": quality_score,
            "latest_entity_merge": latest_merge,
            "latest_feature_backfill": latest_backfill,
        }

    def list_datasets(
        self,
        db: Session,
        *,
        page: int = 1,
        size: int = 20,
        enabled: Optional[bool] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        page = max(1, int(page))
        size = min(200, max(1, int(size)))

        query = db.query(KaggleDatasetRegistry)
        if enabled is not None:
            query = query.filter(KaggleDatasetRegistry.enabled == enabled)

        total = query.count()
        rows = (
            query.order_by(KaggleDatasetRegistry.updated_at.desc(), KaggleDatasetRegistry.id.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return [self._serialize_dataset(row) for row in rows], total

    def create_dataset(self, db: Session, payload: Dict[str, Any]) -> KaggleDatasetRegistry:
        dataset_slug = str(payload.get("dataset_slug", "")).strip()
        if not dataset_slug:
            raise ValueError("dataset_slug is required")
        if "/" not in dataset_slug:
            raise ValueError("dataset_slug must be owner/dataset")

        exists = (
            db.query(KaggleDatasetRegistry)
            .filter(KaggleDatasetRegistry.dataset_slug == dataset_slug)
            .first()
        )
        if exists:
            raise ValueError("dataset_slug already exists")

        owner_name = dataset_slug.split("/", 1)[0] if "/" in dataset_slug else None

        obj = KaggleDatasetRegistry(
            dataset_slug=dataset_slug,
            display_name=str(payload.get("display_name") or dataset_slug),
            owner_name=str(payload.get("owner_name") or owner_name or ""),
            enabled=bool(payload.get("enabled", True)),
            sync_interval_hours=max(1, int(payload.get("sync_interval_hours", 6))),
            latest_version=self._normalize_optional_str(payload.get("latest_version")),
            last_synced_version=self._normalize_optional_str(payload.get("last_synced_version")),
            license_name=self._normalize_optional_str(payload.get("license_name")),
            import_mode=self._normalize_optional_str(payload.get("import_mode")) or "incremental",
            mapping_strategy=self._normalize_optional_str(payload.get("mapping_strategy")) or "alias_first",
            config=payload.get("config") if isinstance(payload.get("config"), dict) else {},
        )
        db.add(obj)
        db.flush()

        self._ensure_state_row(db, dataset_slug=dataset_slug)
        db.commit()
        db.refresh(obj)
        return obj

    def update_dataset(self, db: Session, dataset_id: int, payload: Dict[str, Any]) -> Optional[KaggleDatasetRegistry]:
        obj = db.query(KaggleDatasetRegistry).filter(KaggleDatasetRegistry.id == dataset_id).first()
        if not obj:
            return None

        if "display_name" in payload:
            obj.display_name = self._normalize_optional_str(payload.get("display_name"))
        if "enabled" in payload:
            obj.enabled = bool(payload.get("enabled"))
        if "sync_interval_hours" in payload:
            obj.sync_interval_hours = max(1, int(payload.get("sync_interval_hours") or 1))
        if "latest_version" in payload:
            obj.latest_version = self._normalize_optional_str(payload.get("latest_version"))
        if "last_synced_version" in payload:
            obj.last_synced_version = self._normalize_optional_str(payload.get("last_synced_version"))
        if "license_name" in payload:
            obj.license_name = self._normalize_optional_str(payload.get("license_name"))
        if "import_mode" in payload:
            obj.import_mode = self._normalize_optional_str(payload.get("import_mode")) or obj.import_mode
        if "mapping_strategy" in payload:
            obj.mapping_strategy = (
                self._normalize_optional_str(payload.get("mapping_strategy")) or obj.mapping_strategy
            )
        if "config" in payload and isinstance(payload.get("config"), dict):
            obj.config = payload.get("config")

        db.commit()
        db.refresh(obj)

        self._ensure_state_row(db, dataset_slug=obj.dataset_slug)
        return obj

    def list_runs(
        self,
        db: Session,
        *,
        page: int = 1,
        size: int = 20,
        dataset_slug: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        page = max(1, int(page))
        size = min(200, max(1, int(size)))

        query = db.query(KaggleSyncRun)
        if dataset_slug:
            query = query.filter(KaggleSyncRun.dataset_slug == dataset_slug)
        if status:
            query = query.filter(KaggleSyncRun.status == status)

        total = query.count()
        rows = (
            query.order_by(KaggleSyncRun.created_at.desc(), KaggleSyncRun.id.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return [self._serialize_run(row) for row in rows], total

    def trigger_run_now(self, db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
        dataset_slug = self._normalize_optional_str(payload.get("dataset_slug"))
        if dataset_slug:
            dataset = (
                db.query(KaggleDatasetRegistry)
                .filter(KaggleDatasetRegistry.dataset_slug == dataset_slug)
                .first()
            )
            if not dataset:
                raise ValueError("dataset_slug not found")
        else:
            dataset = (
                db.query(KaggleDatasetRegistry)
                .filter(KaggleDatasetRegistry.enabled == True)
                .order_by(KaggleDatasetRegistry.id.asc())
                .first()
            )
            if not dataset:
                raise ValueError("no enabled dataset found")
            dataset_slug = dataset.dataset_slug

        with self._lock:
            run_id = f"kaggle-{uuid.uuid4().hex[:16]}"
            now = datetime.utcnow()
            run = KaggleSyncRun(
                run_id=run_id,
                dataset_slug=dataset_slug,
                task_type="kaggle_sync",
                trigger_type="manual",
                status="queued",
                version=dataset.latest_version,
                run_meta={},
                started_at=now,
            )
            db.add(run)
            db.flush()

            state = self._ensure_state_row(db, dataset_slug=dataset_slug)
            state.sync_status = "running"
            state.last_run_id = run.id
            state.last_started_at = now
            state.latest_detected_version = dataset.latest_version

            db.commit()
            db.refresh(run)

        force = bool(payload.get("force", False))
        sync_mode = bool(payload.get("sync", False))
        if sync_mode:
            self._execute_run(run.id, force=force)
        else:
            thread = threading.Thread(
                target=self._execute_run,
                kwargs={"run_db_id": run.id, "force": force},
                daemon=True,
                name=f"kaggle-sync-{run.run_id}",
            )
            thread.start()

        db.expire_all()
        refreshed_run = db.query(KaggleSyncRun).filter(KaggleSyncRun.id == run.id).first()
        return {
            "accepted": True,
            "execution_mode": "sync" if sync_mode else "async",
            "run": self._serialize_run(refreshed_run or run),
        }

    def get_run_detail(self, db: Session, run_identifier: str) -> Optional[Dict[str, Any]]:
        run = self._get_run_by_identifier(db, run_identifier)
        if not run:
            return None
        return self._serialize_run(run)

    def get_run_quality(self, db: Session, run_identifier: str) -> Optional[Dict[str, Any]]:
        run = self._get_run_by_identifier(db, run_identifier)
        if not run:
            return None

        version = run.version or ""
        dataset_slug = run.dataset_slug
        if not version:
            return {
                "run_id": run.run_id,
                "dataset_slug": dataset_slug,
                "version": None,
                "quality_score": 0.0,
                "message": "run has no version yet",
            }

        match_total = (
            db.query(KaggleMatchStaging)
            .filter(
                KaggleMatchStaging.dataset_slug == dataset_slug,
                KaggleMatchStaging.version == version,
            )
            .count()
        )
        match_invalid = (
            db.query(KaggleMatchStaging)
            .filter(
                KaggleMatchStaging.dataset_slug == dataset_slug,
                KaggleMatchStaging.version == version,
                KaggleMatchStaging.is_valid == False,  # noqa: E712
            )
            .count()
        )
        team_total = (
            db.query(KaggleTeamStaging)
            .filter(
                KaggleTeamStaging.dataset_slug == dataset_slug,
                KaggleTeamStaging.version == version,
            )
            .count()
        )
        team_invalid = (
            db.query(KaggleTeamStaging)
            .filter(
                KaggleTeamStaging.dataset_slug == dataset_slug,
                KaggleTeamStaging.version == version,
                KaggleTeamStaging.is_valid == False,  # noqa: E712
            )
            .count()
        )
        league_total = (
            db.query(KaggleLeagueStaging)
            .filter(
                KaggleLeagueStaging.dataset_slug == dataset_slug,
                KaggleLeagueStaging.version == version,
            )
            .count()
        )
        league_invalid = (
            db.query(KaggleLeagueStaging)
            .filter(
                KaggleLeagueStaging.dataset_slug == dataset_slug,
                KaggleLeagueStaging.version == version,
                KaggleLeagueStaging.is_valid == False,  # noqa: E712
            )
            .count()
        )

        total_rows = match_total + team_total + league_total
        invalid_rows = match_invalid + team_invalid + league_invalid
        quality_score = 0.0
        if total_rows > 0:
            quality_score = round((1 - (invalid_rows / total_rows)) * 100, 2)

        return {
            "run_id": run.run_id,
            "dataset_slug": dataset_slug,
            "version": version,
            "quality_score": quality_score,
            "rows_total": total_rows,
            "rows_invalid": invalid_rows,
            "match": {"total": match_total, "invalid": match_invalid},
            "team": {"total": team_total, "invalid": team_invalid},
            "league": {"total": league_total, "invalid": league_invalid},
        }

    def get_dataset_preview(
        self,
        db: Session,
        dataset_id: int,
        *,
        version: Optional[str] = None,
        limit: int = 20,
    ) -> Optional[Dict[str, Any]]:
        dataset = db.query(KaggleDatasetRegistry).filter(KaggleDatasetRegistry.id == dataset_id).first()
        if not dataset:
            return None
        target_version = version or dataset.last_synced_version or dataset.latest_version
        if not target_version:
            return {
                "dataset_id": dataset.id,
                "dataset_slug": dataset.dataset_slug,
                "version": None,
                "message": "no synced version yet",
                "match_samples": [],
                "team_samples": [],
                "league_samples": [],
            }

        cap = min(100, max(1, int(limit)))
        match_rows = (
            db.query(KaggleMatchStaging)
            .filter(
                KaggleMatchStaging.dataset_slug == dataset.dataset_slug,
                KaggleMatchStaging.version == target_version,
            )
            .order_by(KaggleMatchStaging.updated_at.desc(), KaggleMatchStaging.id.desc())
            .limit(cap)
            .all()
        )
        team_rows = (
            db.query(KaggleTeamStaging)
            .filter(
                KaggleTeamStaging.dataset_slug == dataset.dataset_slug,
                KaggleTeamStaging.version == target_version,
            )
            .order_by(KaggleTeamStaging.updated_at.desc(), KaggleTeamStaging.id.desc())
            .limit(cap)
            .all()
        )
        league_rows = (
            db.query(KaggleLeagueStaging)
            .filter(
                KaggleLeagueStaging.dataset_slug == dataset.dataset_slug,
                KaggleLeagueStaging.version == target_version,
            )
            .order_by(KaggleLeagueStaging.updated_at.desc(), KaggleLeagueStaging.id.desc())
            .limit(cap)
            .all()
        )

        return {
            "dataset_id": dataset.id,
            "dataset_slug": dataset.dataset_slug,
            "version": target_version,
            "match_samples": [self._serialize_match_staging(row) for row in match_rows],
            "team_samples": [self._serialize_team_staging(row) for row in team_rows],
            "league_samples": [self._serialize_league_staging(row) for row in league_rows],
        }

    def rebuild_dataset(self, db: Session, dataset_id: int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        dataset = db.query(KaggleDatasetRegistry).filter(KaggleDatasetRegistry.id == dataset_id).first()
        if not dataset:
            return None
        trigger_payload: Dict[str, Any] = {
            "dataset_slug": dataset.dataset_slug,
            "force": bool(payload.get("force", True)),
            "sync": bool(payload.get("sync", False)),
        }
        return self.trigger_run_now(db, trigger_payload)

    def run_merge_backfill_now(self, db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
        dataset_slug = self._normalize_optional_str(payload.get("dataset_slug"))
        target_version = self._normalize_optional_str(payload.get("version"))

        if dataset_slug:
            dataset = (
                db.query(KaggleDatasetRegistry)
                .filter(KaggleDatasetRegistry.dataset_slug == dataset_slug)
                .first()
            )
            if not dataset:
                raise ValueError("dataset_slug not found")
        else:
            dataset = (
                db.query(KaggleDatasetRegistry)
                .filter(KaggleDatasetRegistry.enabled == True)  # noqa: E712
                .order_by(KaggleDatasetRegistry.id.asc())
                .first()
            )
            if not dataset:
                raise ValueError("no enabled dataset found")
            dataset_slug = dataset.dataset_slug

        if not target_version:
            target_version = (
                self._normalize_optional_str(dataset.last_synced_version)
                or self._normalize_optional_str(dataset.latest_version)
                or self._resolve_latest_staging_version(db, dataset_slug)
            )
        if not target_version:
            raise ValueError("no staging version found for merge/backfill")

        with self._lock:
            run_id = f"kaggle-merge-{uuid.uuid4().hex[:12]}"
            now = datetime.utcnow()
            run = KaggleSyncRun(
                run_id=run_id,
                dataset_slug=dataset_slug,
                task_type="kaggle_merge_entities",
                trigger_type="manual",
                status="queued",
                version=str(target_version),
                run_meta={"mode": "merge_backfill_only", "version": str(target_version)},
                started_at=now,
            )
            db.add(run)
            db.flush()

            state = self._ensure_state_row(db, dataset_slug=dataset_slug)
            state.sync_status = "running"
            state.last_run_id = run.id
            state.last_started_at = now
            db.commit()

            worker = threading.Thread(
                target=self._execute_merge_backfill_run,
                kwargs={"run_db_id": run.id},
                daemon=True,
                name=f"kaggle-merge-backfill-{run.run_id}",
            )
            worker.start()

        return {
            "run_id": run.run_id,
            "dataset_slug": dataset_slug,
            "version": target_version,
            "status": run.status,
        }

    def _execute_run(self, run_db_id: int, *, force: bool = False) -> None:
        db = SessionLocal()
        try:
            run = db.query(KaggleSyncRun).filter(KaggleSyncRun.id == run_db_id).first()
            if not run:
                return
            dataset = (
                db.query(KaggleDatasetRegistry)
                .filter(KaggleDatasetRegistry.dataset_slug == run.dataset_slug)
                .first()
            )
            if not dataset:
                self._mark_failed(db, run, "dataset_not_found", "dataset not found")
                return

            state = self._ensure_state_row(db, dataset_slug=dataset.dataset_slug)
            started_at = datetime.utcnow()
            run.status = "running"
            run.started_at = started_at
            run.error_code = None
            run.error_message = None
            state.sync_status = "running"
            state.last_run_id = run.id
            state.last_started_at = started_at
            db.commit()

            version = self._discover_latest_version(dataset)
            if not version:
                version = dataset.latest_version or started_at.strftime("%Y%m%d%H%M%S")
            run.version = str(version)
            state.latest_detected_version = str(version)
            dataset.latest_version = str(version)
            db.commit()

            if not force and dataset.last_synced_version and str(dataset.last_synced_version) == str(version):
                now = datetime.utcnow()
                run.status = "success"
                run.finished_at = now
                run.duration_ms = self._duration_ms(run.started_at, now)
                run.rows_raw = 0
                run.rows_curated = 0
                run.rows_upserted = 0
                run.run_meta = {"skipped_reason": "version_already_synced"}

                state.sync_status = "idle"
                state.last_finished_at = now
                state.last_success_version = str(version)
                state.consecutive_failures = 0
                state.last_error_message = None
                db.commit()
                return

            summary = self._run_download_transform_stage(
                db=db,
                dataset=dataset,
                version=str(version),
                run_id=run.run_id,
            )

            finished_at = datetime.utcnow()
            run.status = "success"
            run.rows_raw = summary["rows_raw"]
            run.rows_curated = summary["rows_curated"]
            run.rows_upserted = summary["rows_upserted"]
            run.duration_ms = self._duration_ms(run.started_at, finished_at)
            run.finished_at = finished_at
            run.error_code = None
            run.error_message = None
            run.run_meta = summary

            dataset.last_synced_version = str(version)
            dataset.last_sync_at = finished_at
            dataset.last_error_message = None

            state.sync_status = "idle"
            state.last_finished_at = finished_at
            state.last_success_version = str(version)
            state.consecutive_failures = 0
            state.last_error_message = None
            db.commit()
        except Exception as exc:
            logger.exception("Kaggle sync run failed: %s", exc)
            run = db.query(KaggleSyncRun).filter(KaggleSyncRun.id == run_db_id).first()
            if run:
                self._mark_failed(
                    db,
                    run,
                    "run_failed",
                    str(exc),
                )
        finally:
            db.close()

    def _execute_merge_backfill_run(self, run_db_id: int) -> None:
        db = SessionLocal()
        try:
            run = db.query(KaggleSyncRun).filter(KaggleSyncRun.id == run_db_id).first()
            if not run:
                return
            dataset = (
                db.query(KaggleDatasetRegistry)
                .filter(KaggleDatasetRegistry.dataset_slug == run.dataset_slug)
                .first()
            )
            if not dataset:
                self._mark_failed(db, run, "dataset_not_found", "dataset not found")
                return

            state = self._ensure_state_row(db, dataset_slug=run.dataset_slug)
            started_at = datetime.utcnow()
            run.status = "running"
            run.started_at = started_at
            run.error_code = None
            run.error_message = None
            state.sync_status = "running"
            state.last_run_id = run.id
            state.last_started_at = started_at
            db.commit()

            version = self._normalize_optional_str(run.version) or self._resolve_latest_staging_version(db, run.dataset_slug)
            if not version:
                raise RuntimeError("no staging version found for merge/backfill run")
            run.version = version
            db.commit()

            summary = self._merge_entities_and_backfill_features(
                db=db,
                dataset_slug=run.dataset_slug,
                version=version,
            )

            finished_at = datetime.utcnow()
            run.status = "success"
            run.rows_raw = int(summary.get("rows_raw", 0) or 0)
            run.rows_curated = int(summary.get("rows_curated", 0) or 0)
            run.rows_upserted = int(summary.get("rows_upserted", 0) or 0)
            run.duration_ms = self._duration_ms(run.started_at, finished_at)
            run.finished_at = finished_at
            run.error_code = None
            run.error_message = None
            run.run_meta = summary

            state.sync_status = "idle"
            state.last_finished_at = finished_at
            state.last_success_version = version
            state.consecutive_failures = 0
            state.last_error_message = None
            db.commit()
        except Exception as exc:
            logger.exception("Kaggle merge/backfill run failed: %s", exc)
            run = db.query(KaggleSyncRun).filter(KaggleSyncRun.id == run_db_id).first()
            if run:
                self._mark_failed(db, run, "merge_backfill_failed", str(exc))
        finally:
            db.close()

    def _scheduler_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._run_scheduled_once()
            except Exception as exc:
                logger.warning("Kaggle scheduler tick failed: %s", exc)
            self._stop_event.wait(self._scheduler_tick_seconds)

    def _run_scheduled_once(self) -> None:
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            datasets = (
                db.query(KaggleDatasetRegistry)
                .filter(KaggleDatasetRegistry.enabled == True)  # noqa: E712
                .order_by(KaggleDatasetRegistry.id.asc())
                .all()
            )
            for dataset in datasets:
                hours = max(1, int(dataset.sync_interval_hours or 6))
                due = (
                    dataset.last_sync_at is None
                    or (now - dataset.last_sync_at) >= timedelta(hours=hours)
                )
                if not due:
                    continue

                running_exists = (
                    db.query(KaggleSyncRun)
                    .filter(
                        KaggleSyncRun.dataset_slug == dataset.dataset_slug,
                        KaggleSyncRun.status.in_(["queued", "running", "pending"]),
                    )
                    .count()
                )
                if running_exists:
                    continue

                run_id = f"kaggle-{uuid.uuid4().hex[:16]}"
                run = KaggleSyncRun(
                    run_id=run_id,
                    dataset_slug=dataset.dataset_slug,
                    task_type="kaggle_sync",
                    trigger_type="scheduler",
                    status="queued",
                    version=dataset.latest_version,
                    run_meta={"reason": "scheduled_due"},
                    started_at=now,
                )
                db.add(run)
                db.flush()

                state = self._ensure_state_row(db, dataset_slug=dataset.dataset_slug)
                state.sync_status = "running"
                state.last_run_id = run.id
                state.last_started_at = now
                state.next_scheduled_at = now + timedelta(hours=hours)
                db.commit()

                worker = threading.Thread(
                    target=self._execute_run,
                    kwargs={"run_db_id": run.id, "force": False},
                    daemon=True,
                    name=f"kaggle-sync-scheduled-{run.run_id}",
                )
                worker.start()
        finally:
            db.close()

    def _run_download_transform_stage(
        self,
        *,
        db: Session,
        dataset: KaggleDatasetRegistry,
        version: str,
        run_id: str,
    ) -> Dict[str, Any]:
        slug_path = self._safe_slug(dataset.dataset_slug)
        version_root = self._storage_root / slug_path / version
        raw_dir = version_root / "raw"
        curated_dir = version_root / "curated"
        reject_dir = version_root / "rejects"
        raw_dir.mkdir(parents=True, exist_ok=True)
        curated_dir.mkdir(parents=True, exist_ok=True)
        reject_dir.mkdir(parents=True, exist_ok=True)

        config = dataset.config or {}
        downloaded_path = self._prepare_raw_dataset(
            dataset_slug=dataset.dataset_slug,
            version=version,
            raw_dir=raw_dir,
            config=config,
        )
        lookup_context = self._build_dataset_lookup_context(raw_dir)

        file_paths = self._collect_supported_files(raw_dir, config=config)
        if not file_paths:
            raise RuntimeError("no supported dataset files found after download/extract")

        db.query(KaggleFileManifest).filter(KaggleFileManifest.run_id == run_id).delete(synchronize_session=False)

        total_rows_raw = 0
        total_rows_curated = 0
        total_rows_upserted = 0
        staged_match_rows: List[Dict[str, Any]] = []
        staged_team_rows: List[Dict[str, Any]] = []
        staged_league_rows: List[Dict[str, Any]] = []
        processed_files = 0

        for path in file_paths:
            df = self._load_dataframe(path)
            if df is None or df.empty:
                continue
            processed_files += 1
            source_file = str(path.relative_to(raw_dir)).replace("\\", "/")

            rows_raw = int(len(df))
            total_rows_raw += rows_raw

            normalized_df = self._normalize_columns(df)
            rows_curated = int(len(normalized_df))
            total_rows_curated += rows_curated
            curated_file = curated_dir / f"{path.stem}.curated.csv"
            normalized_df.to_csv(curated_file, index=False, encoding="utf-8")

            schema_hash = self._hash_text("|".join(sorted(normalized_df.columns.tolist())))
            manifest = KaggleFileManifest(
                run_id=run_id,
                dataset_slug=dataset.dataset_slug,
                version=version,
                file_path=str(path.relative_to(version_root)),
                file_name=path.name,
                file_size_bytes=path.stat().st_size if path.exists() else None,
                file_sha256=self._hash_file(path),
                row_count=rows_raw,
                schema_hash=schema_hash,
                manifest_meta={"curated_file": str(curated_file.relative_to(version_root))},
            )
            db.add(manifest)

            file_type = self._classify_dataframe(normalized_df.columns.tolist())
            records = normalized_df.to_dict("records")
            if file_type == "match":
                staged_match_rows.extend(
                    self._build_match_rows(
                        dataset.dataset_slug,
                        version,
                        records,
                        source_file=source_file,
                        config=config,
                        lookup_context=lookup_context,
                    )
                )
            elif file_type == "team":
                staged_team_rows.extend(
                    self._build_team_rows(dataset.dataset_slug, version, records, source_file=source_file)
                )
            elif file_type == "league":
                staged_league_rows.extend(
                    self._build_league_rows(dataset.dataset_slug, version, records, source_file=source_file)
                )
            else:
                reject_file = reject_dir / f"{path.stem}.unknown_type.jsonl"
                with reject_file.open("w", encoding="utf-8") as fp:
                    for row in records[:200]:
                        fp.write(json.dumps(row, ensure_ascii=False) + "\n")

        total_rows_upserted += self._upsert_match_staging(db, staged_match_rows)
        total_rows_upserted += self._upsert_team_staging(db, staged_team_rows)
        total_rows_upserted += self._upsert_league_staging(db, staged_league_rows)
        db.commit()

        merge_backfill_summary = self._merge_entities_and_backfill_features(
            db=db,
            dataset_slug=dataset.dataset_slug,
            version=version,
        )

        return {
            "version": version,
            "downloaded_path": str(downloaded_path),
            "files_processed": processed_files,
            "rows_raw": total_rows_raw,
            "rows_curated": total_rows_curated,
            "rows_upserted": total_rows_upserted,
            "staging_counts": {
                "match": len(staged_match_rows),
                "team": len(staged_team_rows),
                "league": len(staged_league_rows),
            },
            "entity_merge": merge_backfill_summary.get("entity_merge", {}),
            "feature_backfill": merge_backfill_summary.get("feature_backfill", {}),
            "rows_merged": int(merge_backfill_summary.get("rows_upserted", 0) or 0),
        }

    def _prepare_raw_dataset(
        self,
        *,
        dataset_slug: str,
        version: str,
        raw_dir: Path,
        config: Dict[str, Any],
    ) -> Path:
        local_source_dir = self._normalize_optional_str(config.get("local_source_dir"))
        if local_source_dir:
            source_dir = Path(local_source_dir)
            if not source_dir.is_absolute():
                source_dir = self._project_root / source_dir
            if not source_dir.exists():
                raise RuntimeError(f"local_source_dir not found: {source_dir}")
            self._copy_dir(source_dir, raw_dir)
            return source_dir

        owner, dataset = dataset_slug.split("/", 1)
        auth = self._build_kaggle_auth(config)
        if not auth:
            raise RuntimeError("Kaggle credentials are required (KAGGLE_USERNAME/KAGGLE_KEY)")

        zip_path = raw_dir / f"{dataset}-{version}.zip"
        self._download_dataset_zip(owner=owner, dataset=dataset, version=version, auth=auth, output_path=zip_path)
        if zipfile.is_zipfile(zip_path):
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(raw_dir)
        return zip_path

    def _discover_latest_version(self, dataset: KaggleDatasetRegistry) -> Optional[str]:
        config = dataset.config or {}
        owner, ds_name = dataset.dataset_slug.split("/", 1)
        auth = self._build_kaggle_auth(config)
        if not auth:
            return dataset.latest_version

        try:
            response = requests.get(
                KAGGLE_VIEW_URL.format(owner=owner, dataset=ds_name),
                auth=auth,
                timeout=20,
            )
            if response.status_code >= 400:
                logger.warning(
                    "Kaggle version discovery failed for %s: %s %s",
                    dataset.dataset_slug,
                    response.status_code,
                    response.text[:200],
                )
                return dataset.latest_version
            payload = response.json() if response.text else {}
            for key in (
                "currentVersionNumber",
                "versionNumber",
                "latestVersionNumber",
                "currentVersion",
            ):
                value = payload.get(key)
                if value is not None and str(value).strip():
                    return str(value).strip()
        except Exception as exc:
            logger.warning("Kaggle version discovery error for %s: %s", dataset.dataset_slug, exc)

        return dataset.latest_version

    @staticmethod
    def _build_kaggle_auth(config: Dict[str, Any]) -> Optional[Tuple[str, str]]:
        username = (
            str(config.get("kaggle_username")).strip()
            if config.get("kaggle_username")
            else os.getenv("KAGGLE_USERNAME", "").strip()
        )
        key = (
            str(config.get("kaggle_key")).strip()
            if config.get("kaggle_key")
            else os.getenv("KAGGLE_KEY", "").strip()
        )
        if username and key:
            return (username, key)
        return None

    def _download_dataset_zip(
        self,
        *,
        owner: str,
        dataset: str,
        version: str,
        auth: Tuple[str, str],
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        params = {"datasetVersionNumber": str(version)}
        with requests.get(
            KAGGLE_DOWNLOAD_URL.format(owner=owner, dataset=dataset),
            params=params,
            auth=auth,
            timeout=120,
            stream=True,
        ) as response:
            if response.status_code >= 400:
                body = response.text[:300]
                raise RuntimeError(f"Kaggle download failed {response.status_code}: {body}")
            with output_path.open("wb") as fp:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        fp.write(chunk)

    @staticmethod
    def _copy_dir(source_dir: Path, target_dir: Path) -> None:
        for item in source_dir.rglob("*"):
            if item.is_dir():
                continue
            rel = item.relative_to(source_dir)
            dest = target_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)

    def _collect_supported_files(self, raw_dir: Path, *, config: Dict[str, Any]) -> List[Path]:
        include_globs = config.get("file_globs") if isinstance(config.get("file_globs"), list) else None
        supported_ext = {
            ".csv",
            ".tsv",
            ".txt",
            ".json",
            ".jsonl",
            ".ndjson",
            ".xlsx",
            ".xls",
            ".parquet",
        }
        files: List[Path] = []
        for path in raw_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in supported_ext:
                continue
            if include_globs:
                rel_path = str(path.relative_to(raw_dir)).replace("\\", "/")
                matched = any(
                    fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(rel_path, pattern)
                    for pattern in include_globs
                )
                if not matched:
                    continue
            files.append(path)
        files.sort(key=lambda p: str(p))
        return files

    @staticmethod
    def _load_dataframe(path: Path) -> Optional[pd.DataFrame]:
        suffix = path.suffix.lower()
        try:
            if suffix == ".csv":
                return pd.read_csv(path, low_memory=False)
            if suffix == ".tsv":
                return pd.read_csv(path, sep="\t", low_memory=False)
            if suffix == ".txt":
                return pd.read_csv(path, sep=None, engine="python", low_memory=False)
            if suffix in (".jsonl", ".ndjson"):
                return pd.read_json(path, lines=True)
            if suffix == ".json":
                try:
                    return pd.read_json(path)
                except ValueError:
                    return pd.read_json(path, lines=True)
            if suffix in (".xlsx", ".xls"):
                return pd.read_excel(path)
            if suffix == ".parquet":
                return pd.read_parquet(path)
        except Exception as exc:
            logger.warning("Failed to load dataset file %s: %s", path, exc)
            return None
        return None

    @staticmethod
    def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        cloned = df.copy()
        renamed = {col: str(col).strip().lower().replace("-", "_").replace(" ", "_") for col in cloned.columns}
        cloned.rename(columns=renamed, inplace=True)
        return cloned

    def _classify_dataframe(self, columns: List[str]) -> str:
        names = set(c.lower() for c in columns)
        has_home = self._contains_any(names, self.MATCH_HOME_KEYS)
        has_away = self._contains_any(names, self.MATCH_AWAY_KEYS)
        if has_home and has_away:
            return "match"
        if self._contains_any(names, self.TEAM_NAME_KEYS):
            return "team"
        if self._contains_any(names, self.LEAGUE_NAME_KEYS):
            return "league"
        return "unknown"

    @staticmethod
    def _contains_any(columns: List[str] | set[str], candidates: Tuple[str, ...]) -> bool:
        colset = set(columns)
        for key in candidates:
            if key.lower().replace(" ", "_") in colset:
                return True
        return False

    def _build_dataset_lookup_context(self, raw_dir: Path) -> Dict[str, Any]:
        context: Dict[str, Any] = {
            "team_name_by_id": {},
            "league_name_by_id": {},
            "league_code_by_id": {},
            "league_year_by_id_and_season": {},
        }

        team_sources = [raw_dir / "base_data" / "teams.csv", raw_dir / "teams.csv"]
        for team_path in team_sources:
            if not team_path.exists():
                continue
            df = self._load_dataframe(team_path)
            if df is None or df.empty:
                continue
            normalized = self._normalize_columns(df)
            for _, row in normalized.iterrows():
                row_map = self._row_to_lookup(row.to_dict())
                team_id = self._pick_value(row_map, ("teamid", "team_id", "id"))
                if not team_id:
                    continue
                team_name = self._pick_value(row_map, ("displayname", "shortdisplayname", "name", "team_name"))
                if not team_name:
                    continue
                context["team_name_by_id"][self._normalize_id_key(team_id)] = team_name

        league_sources = [raw_dir / "base_data" / "leagues.csv", raw_dir / "leagues.csv"]
        for league_path in league_sources:
            if not league_path.exists():
                continue
            df = self._load_dataframe(league_path)
            if df is None or df.empty:
                continue
            normalized = self._normalize_columns(df)
            for _, row in normalized.iterrows():
                row_map = self._row_to_lookup(row.to_dict())
                league_id = self._pick_value(row_map, ("leagueid", "league_id", "id"))
                if not league_id:
                    continue
                league_id_key = self._normalize_id_key(league_id)
                league_name = self._pick_value(
                    row_map,
                    ("leaguename", "leagueshortname", "name", "league_name", "competition"),
                )
                if league_name:
                    context["league_name_by_id"][league_id_key] = league_name

                league_code = self._pick_value(
                    row_map,
                    ("midsizename", "understatnotation", "seasonslug", "short_name", "code"),
                )
                if league_code:
                    context["league_code_by_id"][league_id_key] = league_code

                season_type = self._pick_value(row_map, ("seasontype", "season_type"))
                year_text = self._pick_value(row_map, ("year", "season", "season_year"))
                year_value = self._to_int_or_none(year_text)
                if season_type and year_value is not None:
                    context["league_year_by_id_and_season"][
                        (league_id_key, self._normalize_id_key(season_type))
                    ] = year_value

        return context

    @staticmethod
    def _normalize_id_key(value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            return ""
        if text.endswith(".0"):
            text = text[:-2]
        return text

    @staticmethod
    def _looks_numeric_like_id(value: Optional[str]) -> bool:
        text = str(value or "").strip()
        if not text:
            return False
        return bool(re.fullmatch(r"\d+(?:\.0+)?", text))

    @staticmethod
    def _to_int_or_none(value: Any) -> Optional[int]:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        try:
            return int(float(text))
        except Exception:
            return None

    @staticmethod
    def _normalize_competition_code(value: Any) -> str:
        text = str(value or "").strip().upper()
        if not text:
            return ""
        text = text.replace("_", ".").replace(" ", "")
        text = re.sub(r"[^A-Z0-9.]+", "", text)
        return text

    @staticmethod
    def _extract_league_code_from_source_file(source_file: str) -> Optional[str]:
        name = Path(source_file or "").name.upper()
        # e.g. commentary_2025_ENG.1.csv / lineup_2025_UEFA.CHAMPIONS.csv
        match = re.search(r"_(\d{4})_([A-Z0-9.]+)\.(?:CSV|PARQUET|XLSX|XLS)$", name)
        if match:
            return match.group(2)
        return None

    @staticmethod
    def _extract_year_from_source_file(source_file: str) -> Optional[int]:
        name = Path(source_file or "").name
        match = re.search(r"(20\d{2})", name)
        if not match:
            return None
        try:
            return int(match.group(1))
        except Exception:
            return None

    def _should_keep_match_record(
        self,
        *,
        config: Dict[str, Any],
        source_file: str,
        league_name: Optional[str],
        league_code: Optional[str],
        season_year: Optional[int],
    ) -> bool:
        league_code_allow = {
            self._normalize_competition_code(item)
            for item in (config.get("league_code_allow") or [])
            if self._normalize_competition_code(item)
        }
        league_name_allow = {
            self._normalize_entity_key(item)
            for item in (config.get("league_name_allow") or [])
            if self._normalize_entity_key(item)
        }
        season_year_allow = {
            self._to_int_or_none(item)
            for item in (config.get("season_year_allow") or [])
            if self._to_int_or_none(item) is not None
        }
        season_year_min = self._to_int_or_none(config.get("season_year_min"))
        season_year_max = self._to_int_or_none(config.get("season_year_max"))

        code_candidates = set()
        if league_code:
            code_candidates.add(self._normalize_competition_code(league_code))
        code_from_file = self._extract_league_code_from_source_file(source_file)
        if code_from_file:
            code_candidates.add(self._normalize_competition_code(code_from_file))
        code_candidates = {item for item in code_candidates if item}

        if league_code_allow and not code_candidates.intersection(league_code_allow):
            return False

        if league_name_allow:
            name_key = self._normalize_entity_key(league_name)
            if not name_key or name_key not in league_name_allow:
                return False

        effective_year = season_year if season_year is not None else self._extract_year_from_source_file(source_file)
        if season_year_allow and (effective_year is None or effective_year not in season_year_allow):
            return False
        if season_year_min is not None and (effective_year is None or effective_year < season_year_min):
            return False
        if season_year_max is not None and (effective_year is None or effective_year > season_year_max):
            return False

        return True

    def _build_match_rows(
        self,
        dataset_slug: str,
        version: str,
        records: List[Dict[str, Any]],
        *,
        source_file: str,
        config: Optional[Dict[str, Any]] = None,
        lookup_context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        cfg = config or {}
        context = lookup_context or {}
        team_name_by_id = context.get("team_name_by_id", {})
        league_name_by_id = context.get("league_name_by_id", {})
        league_code_by_id = context.get("league_code_by_id", {})
        league_year_by_id_and_season = context.get("league_year_by_id_and_season", {})
        for row in records:
            row_map = self._row_to_lookup(row)
            league = self._pick_value(row_map, self.MATCH_LEAGUE_KEYS)
            home = self._pick_value(row_map, self.MATCH_HOME_KEYS)
            away = self._pick_value(row_map, self.MATCH_AWAY_KEYS)
            match_time = self._pick_value(row_map, self.MATCH_TIME_KEYS)
            external_id = self._pick_value(row_map, self.MATCH_ID_KEYS)
            league_id = self._pick_value(row_map, ("leagueid", "league_id", "competitionid", "competition_id"))
            season_type = self._pick_value(row_map, ("seasontype", "season_type"))
            season_year_raw = self._pick_value(row_map, ("year", "season", "seasonyear", "season_year"))
            home_id = self._pick_value(row_map, ("hometeamid", "home_team_id", "homeid", "home_id"))
            away_id = self._pick_value(row_map, ("awayteamid", "away_team_id", "awayid", "away_id"))

            league_id_key = self._normalize_id_key(league_id)
            if (not league or self._looks_numeric_like_id(league)) and league_id_key:
                mapped_league_name = league_name_by_id.get(league_id_key)
                if mapped_league_name:
                    league = mapped_league_name

            home_id_key = self._normalize_id_key(home_id if home_id is not None else home)
            if (not home or self._looks_numeric_like_id(home)) and home_id_key:
                mapped_home = team_name_by_id.get(home_id_key)
                if mapped_home:
                    home = mapped_home

            away_id_key = self._normalize_id_key(away_id if away_id is not None else away)
            if (not away or self._looks_numeric_like_id(away)) and away_id_key:
                mapped_away = team_name_by_id.get(away_id_key)
                if mapped_away:
                    away = mapped_away

            league_code = None
            if league_id_key:
                league_code = league_code_by_id.get(league_id_key)

            season_year = self._to_int_or_none(season_year_raw)
            if season_year is None and league_id_key:
                season_type_key = self._normalize_id_key(season_type)
                if season_type_key:
                    season_year = self._to_int_or_none(league_year_by_id_and_season.get((league_id_key, season_type_key)))

            if not self._should_keep_match_record(
                config=cfg,
                source_file=source_file,
                league_name=league,
                league_code=league_code,
                season_year=season_year,
            ):
                continue

            if not external_id:
                if self._normalize_optional_str(row_map.get("eventid")):
                    external_id = self._normalize_optional_str(row_map.get("eventid"))
                elif self._normalize_optional_str(row_map.get("gameid")):
                    external_id = self._normalize_optional_str(row_map.get("gameid"))
                else:
                    external_id = self._hash_text(f"{league}|{home}|{away}|{match_time}")[:24]

            rows.append(
                {
                    "dataset_slug": dataset_slug,
                    "version": version,
                    "external_id": external_id,
                    "league_name_raw": league,
                    "home_team_name_raw": home,
                    "away_team_name_raw": away,
                    "match_time_raw": match_time,
                    "normalized_hash": self._hash_text(f"{league}|{home}|{away}|{match_time}"),
                    "payload_json": {"source_file": source_file, "raw": row},
                    "is_valid": bool(home and away),
                    "reject_reason": None if (home and away) else "missing home/away team",
                }
            )
        return rows

    def _build_team_rows(
        self,
        dataset_slug: str,
        version: str,
        records: List[Dict[str, Any]],
        *,
        source_file: str,
    ) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for row in records:
            row_map = self._row_to_lookup(row)
            team_name = self._pick_value(row_map, self.TEAM_NAME_KEYS)
            country = self._pick_value(row_map, self.TEAM_COUNTRY_KEYS)
            external_id = self._pick_value(row_map, self.TEAM_ID_KEYS)
            if not external_id:
                external_id = self._hash_text(f"{team_name}|{country}")[:24]
            rows.append(
                {
                    "dataset_slug": dataset_slug,
                    "version": version,
                    "external_id": external_id,
                    "team_name_raw": team_name,
                    "country_raw": country,
                    "normalized_hash": self._hash_text(f"{team_name}|{country}"),
                    "payload_json": {"source_file": source_file, "raw": row},
                    "is_valid": bool(team_name),
                    "reject_reason": None if team_name else "missing team name",
                }
            )
        return rows

    def _build_league_rows(
        self,
        dataset_slug: str,
        version: str,
        records: List[Dict[str, Any]],
        *,
        source_file: str,
    ) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for row in records:
            row_map = self._row_to_lookup(row)
            league_name = self._pick_value(row_map, self.LEAGUE_NAME_KEYS)
            country = self._pick_value(row_map, self.LEAGUE_COUNTRY_KEYS)
            external_id = self._pick_value(row_map, self.LEAGUE_ID_KEYS)
            if not external_id:
                external_id = self._hash_text(f"{league_name}|{country}")[:24]
            rows.append(
                {
                    "dataset_slug": dataset_slug,
                    "version": version,
                    "external_id": external_id,
                    "league_name_raw": league_name,
                    "country_raw": country,
                    "normalized_hash": self._hash_text(f"{league_name}|{country}"),
                    "payload_json": {"source_file": source_file, "raw": row},
                    "is_valid": bool(league_name),
                    "reject_reason": None if league_name else "missing league name",
                }
            )
        return rows

    def _upsert_match_staging(self, db: Session, rows: List[Dict[str, Any]]) -> int:
        return self._upsert_staging_generic(
            db=db,
            model=KaggleMatchStaging,
            rows=rows,
            identity_keys=("dataset_slug", "version", "external_id"),
        )

    def _upsert_team_staging(self, db: Session, rows: List[Dict[str, Any]]) -> int:
        return self._upsert_staging_generic(
            db=db,
            model=KaggleTeamStaging,
            rows=rows,
            identity_keys=("dataset_slug", "version", "external_id"),
        )

    def _upsert_league_staging(self, db: Session, rows: List[Dict[str, Any]]) -> int:
        return self._upsert_staging_generic(
            db=db,
            model=KaggleLeagueStaging,
            rows=rows,
            identity_keys=("dataset_slug", "version", "external_id"),
        )

    @staticmethod
    def _upsert_staging_generic(
        *,
        db: Session,
        model: Any,
        rows: List[Dict[str, Any]],
        identity_keys: Tuple[str, str, str],
    ) -> int:
        if not rows:
            return 0

        dedup: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        for row in rows:
            key = tuple(str(row.get(k) or "") for k in identity_keys)
            dedup[key] = row

        keys = list(dedup.keys())
        existing_map: Dict[Tuple[str, str, str], Any] = {}
        chunk_size = 300
        for i in range(0, len(keys), chunk_size):
            chunk = keys[i : i + chunk_size]
            conditions = [
                and_(
                    getattr(model, identity_keys[0]) == k[0],
                    getattr(model, identity_keys[1]) == k[1],
                    getattr(model, identity_keys[2]) == k[2],
                )
                for k in chunk
            ]
            if not conditions:
                continue
            found = db.query(model).filter(or_(*conditions)).all()
            for item in found:
                map_key = tuple(str(getattr(item, id_key)) for id_key in identity_keys)
                existing_map[map_key] = item

        for key, payload in dedup.items():
            existing = existing_map.get(key)
            if existing:
                for field, value in payload.items():
                    setattr(existing, field, value)
            else:
                db.add(model(**payload))
        return len(dedup)

    def _resolve_latest_staging_version(self, db: Session, dataset_slug: str) -> Optional[str]:
        candidates: List[str] = []
        for model in (KaggleMatchStaging, KaggleTeamStaging, KaggleLeagueStaging):
            row = (
                db.query(model.version)
                .filter(model.dataset_slug == dataset_slug)
                .order_by(model.updated_at.desc(), model.id.desc())
                .first()
            )
            if row and row[0]:
                candidates.append(str(row[0]))
        return candidates[0] if candidates else None

    @staticmethod
    def _normalize_entity_key(value: Any) -> str:
        text = str(value or "").strip().lower()
        if not text:
            return ""
        text = re.sub(r"\s+", "", text)
        text = re.sub(r"[\-_.·•/\\'\"`~()（）\[\]{}]+", "", text)
        return text

    @staticmethod
    def _country_code(country: Optional[str]) -> str:
        text = str(country or "").strip()
        if not text:
            return "UN"
        letters = "".join(ch for ch in text if ch.isalpha()).upper()
        if len(letters) >= 2:
            return letters[:2]
        return "UN"

    @staticmethod
    def _parse_match_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value.replace(tzinfo=None)
        text = str(value or "").strip()
        if not text:
            return datetime.utcnow()

        if text.isdigit() and len(text) in (10, 13):
            stamp = int(text)
            if len(text) == 13:
                stamp = int(stamp / 1000)
            try:
                return datetime.utcfromtimestamp(stamp)
            except Exception:
                pass

        cleaned = text.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(cleaned)
            return dt.replace(tzinfo=None)
        except Exception:
            pass

        patterns = (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%d/%m/%Y %H:%M",
            "%m/%d/%Y %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d",
        )
        for fmt in patterns:
            try:
                return datetime.strptime(text, fmt)
            except Exception:
                continue
        return datetime.utcnow()

    def _upsert_external_mapping_row(
        self,
        db: Session,
        *,
        source: str,
        external_id: Optional[str],
        internal_id: Optional[str],
        confidence: float,
        mapping_meta: Optional[Dict[str, Any]] = None,
    ) -> int:
        ext_id = self._normalize_optional_str(external_id)
        in_id = self._normalize_optional_str(internal_id)
        if not ext_id or not in_id:
            return 0

        row = (
            db.query(ExternalSourceMapping)
            .filter(ExternalSourceMapping.source == source, ExternalSourceMapping.external_id == ext_id)
            .first()
        )
        if not row:
            row = ExternalSourceMapping(
                source=source,
                external_id=ext_id,
                internal_match_id=in_id,
                confidence_score=confidence,
                mapping_meta=mapping_meta or {},
                verified=1 if confidence >= 0.95 else 0,
            )
            db.add(row)
            return 1

        row.internal_match_id = in_id
        row.confidence_score = confidence
        row.mapping_meta = mapping_meta or (row.mapping_meta or {})
        if confidence >= 0.95:
            row.verified = 1
        return 1

    def _merge_entities_and_backfill_features(
        self,
        *,
        db: Session,
        dataset_slug: str,
        version: str,
    ) -> Dict[str, Any]:
        league_rows = (
            db.query(KaggleLeagueStaging)
            .filter(
                KaggleLeagueStaging.dataset_slug == dataset_slug,
                KaggleLeagueStaging.version == version,
                KaggleLeagueStaging.is_valid == True,  # noqa: E712
            )
            .all()
        )
        team_rows = (
            db.query(KaggleTeamStaging)
            .filter(
                KaggleTeamStaging.dataset_slug == dataset_slug,
                KaggleTeamStaging.version == version,
                KaggleTeamStaging.is_valid == True,  # noqa: E712
            )
            .all()
        )
        match_rows = (
            db.query(KaggleMatchStaging)
            .filter(
                KaggleMatchStaging.dataset_slug == dataset_slug,
                KaggleMatchStaging.version == version,
                KaggleMatchStaging.is_valid == True,  # noqa: E712
            )
            .all()
        )

        entity_merge = {
            "dataset_slug": dataset_slug,
            "version": version,
            "leagues_created": 0,
            "leagues_updated": 0,
            "teams_created": 0,
            "teams_updated": 0,
            "matches_created": 0,
            "matches_updated": 0,
            "mapping_rows_upserted": 0,
        }
        feature_backfill = {
            "matches_backfilled": 0,
            "draw_features_ensured": 0,
        }

        league_name_map: Dict[str, League] = {}
        league_external_map: Dict[str, League] = {}
        team_name_map: Dict[str, Team] = {}
        team_external_map: Dict[str, Team] = {}
        touched_match_ids: List[int] = []

        all_leagues = db.query(League).all()
        used_league_codes = {str(row.code or "").upper() for row in all_leagues if row.code}
        for row in all_leagues:
            name_key = self._normalize_entity_key(row.name)
            if name_key and name_key not in league_name_map:
                league_name_map[name_key] = row
            if row.external_source == "kaggle" and row.external_id:
                league_external_map[str(row.external_id)] = row

        for row in league_rows:
            league_name = self._normalize_optional_str(row.league_name_raw)
            if not league_name:
                continue
            ext_id = self._normalize_optional_str(row.external_id) or self._hash_text(f"league|{league_name}")[:24]
            name_key = self._normalize_entity_key(league_name)
            country = self._normalize_optional_str(row.country_raw) or "Unknown"
            country_code = self._country_code(country)

            league = league_external_map.get(ext_id) or league_name_map.get(name_key)
            if league:
                changed = False
                if not league.external_id:
                    league.external_id = ext_id
                    changed = True
                if not league.external_source:
                    league.external_source = "kaggle"
                    changed = True
                if not league.country or str(league.country).strip() in {"", "Unknown", "未知"}:
                    league.country = country
                    changed = True
                if not league.country_code or str(league.country_code).strip() in {"", "UN"}:
                    league.country_code = country_code
                    changed = True
                config = league.config.copy() if isinstance(league.config, dict) else {}
                kaggle_meta = config.get("kaggle", {}) if isinstance(config.get("kaggle"), dict) else {}
                kaggle_meta.update(
                    {
                        "dataset_slug": dataset_slug,
                        "version": version,
                        "external_id": ext_id,
                        "last_merged_at": datetime.utcnow().isoformat(),
                    }
                )
                config["kaggle"] = kaggle_meta
                league.config = config
                if changed:
                    entity_merge["leagues_updated"] += 1
            else:
                base_code = f"KG{self._hash_text(f'league|{league_name}|{ext_id}')[:8].upper()}"
                code = base_code
                suffix = 1
                while code.upper() in used_league_codes:
                    code = f"{base_code[:8]}{suffix:02d}"[:10]
                    suffix += 1
                used_league_codes.add(code.upper())

                league = League(
                    name=league_name,
                    short_name=league_name[:50],
                    code=code,
                    country=country,
                    country_code=country_code,
                    type="national",
                    format="round_robin",
                    level=1,
                    is_active=True,
                    is_popular=False,
                    external_id=ext_id,
                    external_source="kaggle",
                    config={
                        "kaggle": {
                            "dataset_slug": dataset_slug,
                            "version": version,
                            "external_id": ext_id,
                            "last_merged_at": datetime.utcnow().isoformat(),
                        }
                    },
                )
                db.add(league)
                db.flush()
                entity_merge["leagues_created"] += 1

            league_name_map[name_key] = league
            if ext_id:
                league_external_map[ext_id] = league
                entity_merge["mapping_rows_upserted"] += self._upsert_external_mapping_row(
                    db,
                    source=self.MERGE_SOURCE_LEAGUE,
                    external_id=ext_id,
                    internal_id=str(league.id),
                    confidence=1.0,
                    mapping_meta={"entity_type": "league", "dataset_slug": dataset_slug, "version": version},
                )

        all_teams = db.query(Team).all()
        used_team_codes = {str(row.code or "").upper() for row in all_teams if row.code}
        for row in all_teams:
            name_key = self._normalize_entity_key(row.name)
            if name_key and name_key not in team_name_map:
                team_name_map[name_key] = row
            if row.external_source == "kaggle" and row.external_id:
                team_external_map[str(row.external_id)] = row

        for row in team_rows:
            team_name = self._normalize_optional_str(row.team_name_raw)
            if not team_name:
                continue

            ext_id = self._normalize_optional_str(row.external_id) or self._hash_text(f"team|{team_name}")[:24]
            name_key = self._normalize_entity_key(team_name)
            country = self._normalize_optional_str(row.country_raw) or "Unknown"
            country_code = self._country_code(country)
            payload_raw = row.payload_json.get("raw") if isinstance(row.payload_json, dict) else {}
            payload_lookup = self._row_to_lookup(payload_raw if isinstance(payload_raw, dict) else {})
            payload_league_name = self._pick_value(payload_lookup, self.LEAGUE_NAME_KEYS)
            payload_league_key = self._normalize_entity_key(payload_league_name)
            linked_league = league_name_map.get(payload_league_key) if payload_league_key else None

            team = team_external_map.get(ext_id) or team_name_map.get(name_key)
            if team:
                changed = False
                if not team.external_id:
                    team.external_id = ext_id
                    changed = True
                if not team.external_source:
                    team.external_source = "kaggle"
                    changed = True
                if linked_league and not team.league_id:
                    team.league_id = linked_league.id
                    changed = True
                if not team.country or str(team.country).strip() in {"", "Unknown", "未知"}:
                    team.country = country
                    changed = True
                if not team.country_code or str(team.country_code).strip() in {"", "UN"}:
                    team.country_code = country_code
                    changed = True
                config = team.config.copy() if isinstance(team.config, dict) else {}
                kaggle_meta = config.get("kaggle", {}) if isinstance(config.get("kaggle"), dict) else {}
                kaggle_meta.update(
                    {
                        "dataset_slug": dataset_slug,
                        "version": version,
                        "external_id": ext_id,
                        "last_merged_at": datetime.utcnow().isoformat(),
                    }
                )
                config["kaggle"] = kaggle_meta
                team.config = config
                if changed:
                    entity_merge["teams_updated"] += 1
            else:
                base_code = f"KT{self._hash_text(f'team|{team_name}|{ext_id}')[:8].upper()}"
                code = base_code
                suffix = 1
                while code.upper() in used_team_codes:
                    code = f"{base_code[:8]}{suffix:02d}"[:10]
                    suffix += 1
                used_team_codes.add(code.upper())

                team = Team(
                    name=team_name,
                    short_name=team_name[:50],
                    full_name=team_name,
                    code=code,
                    country=country,
                    country_code=country_code,
                    league_id=linked_league.id if linked_league else None,
                    is_active=True,
                    is_popular=False,
                    external_id=ext_id,
                    external_source="kaggle",
                    config={
                        "kaggle": {
                            "dataset_slug": dataset_slug,
                            "version": version,
                            "external_id": ext_id,
                            "last_merged_at": datetime.utcnow().isoformat(),
                        }
                    },
                )
                db.add(team)
                db.flush()
                entity_merge["teams_created"] += 1

            team_name_map[name_key] = team
            if ext_id:
                team_external_map[ext_id] = team
                entity_merge["mapping_rows_upserted"] += self._upsert_external_mapping_row(
                    db,
                    source=self.MERGE_SOURCE_TEAM,
                    external_id=ext_id,
                    internal_id=str(team.id),
                    confidence=1.0,
                    mapping_meta={"entity_type": "team", "dataset_slug": dataset_slug, "version": version},
                )

        for row in match_rows:
            ext_id = self._normalize_optional_str(row.external_id) or self._hash_text(
                f"{row.league_name_raw}|{row.home_team_name_raw}|{row.away_team_name_raw}|{row.match_time_raw}"
            )[:24]
            home_name = self._normalize_optional_str(row.home_team_name_raw)
            away_name = self._normalize_optional_str(row.away_team_name_raw)
            league_name = self._normalize_optional_str(row.league_name_raw)
            if not home_name or not away_name:
                continue

            home_team = team_name_map.get(self._normalize_entity_key(home_name))
            away_team = team_name_map.get(self._normalize_entity_key(away_name))
            league = league_name_map.get(self._normalize_entity_key(league_name))
            kickoff = self._parse_match_datetime(row.match_time_raw)
            match_date = kickoff.date()
            match_time = kickoff.time().replace(microsecond=0)

            existing = (
                db.query(Match)
                .filter(
                    Match.data_source == "kaggle",
                    Match.source_match_id == ext_id,
                )
                .first()
            )
            if not existing and home_team and away_team:
                existing = (
                    db.query(Match)
                    .filter(
                        Match.home_team_id == home_team.id,
                        Match.away_team_id == away_team.id,
                        Match.scheduled_kickoff >= kickoff - timedelta(hours=12),
                        Match.scheduled_kickoff <= kickoff + timedelta(hours=12),
                    )
                    .order_by(Match.scheduled_kickoff.desc(), Match.id.desc())
                    .first()
                )

            attrs = {}
            if existing and isinstance(existing.source_attributes, dict):
                attrs = existing.source_attributes.copy()
            elif existing and isinstance(existing.source_attributes, str):
                try:
                    attrs = json.loads(existing.source_attributes)
                except Exception:
                    attrs = {}

            coverage_parts = [
                1 if league else 0,
                1 if home_team else 0,
                1 if away_team else 0,
            ]
            entity_coverage = round(sum(coverage_parts) / 3.0, 4)
            attrs["kaggle"] = {
                "dataset_slug": dataset_slug,
                "version": version,
                "external_id": ext_id,
                "league_name_raw": league_name,
                "home_team_name_raw": home_name,
                "away_team_name_raw": away_name,
                "normalized_hash": row.normalized_hash,
                "entity_coverage": entity_coverage,
                "merged_at": datetime.utcnow().isoformat(),
            }

            if existing:
                changed = False
                if home_team and not existing.home_team_id:
                    existing.home_team_id = home_team.id
                    changed = True
                if away_team and not existing.away_team_id:
                    existing.away_team_id = away_team.id
                    changed = True
                if league and not existing.league_id:
                    existing.league_id = league.id
                    changed = True
                if existing.data_source in {"", "default", "kaggle"}:
                    if existing.data_source != "kaggle":
                        existing.data_source = "kaggle"
                        changed = True
                    if not existing.source_match_id:
                        existing.source_match_id = ext_id
                        changed = True
                if not existing.external_source:
                    existing.external_source = "kaggle"
                    changed = True
                if not existing.external_id:
                    existing.external_id = ext_id
                    changed = True
                existing.source_attributes = attrs
                changed = True
                if changed:
                    entity_merge["matches_updated"] += 1
                db.flush()
                target_match = existing
            else:
                target_match = Match(
                    match_identifier=f"KG{uuid.uuid4().hex[:12].upper()}",
                    home_team_id=home_team.id if home_team else None,
                    away_team_id=away_team.id if away_team else None,
                    league_id=league.id if league else None,
                    match_date=match_date,
                    match_time=match_time,
                    scheduled_kickoff=kickoff,
                    status=MatchStatusEnum.SCHEDULED,
                    data_source="kaggle",
                    source_match_id=ext_id,
                    source_attributes=attrs,
                    external_id=ext_id,
                    external_source="kaggle",
                )
                db.add(target_match)
                db.flush()
                entity_merge["matches_created"] += 1

            touched_match_ids.append(target_match.id)
            entity_merge["mapping_rows_upserted"] += self._upsert_external_mapping_row(
                db,
                source=self.MERGE_SOURCE_MATCH,
                external_id=ext_id,
                internal_id=str(target_match.match_identifier),
                confidence=entity_coverage,
                mapping_meta={
                    "entity_type": "match",
                    "dataset_slug": dataset_slug,
                    "version": version,
                    "home_team_id": target_match.home_team_id,
                    "away_team_id": target_match.away_team_id,
                    "league_id": target_match.league_id,
                },
            )

        if touched_match_ids:
            now = datetime.utcnow()
            matches = db.query(Match).filter(Match.id.in_(touched_match_ids)).all()
            for match in matches:
                attrs = match.source_attributes.copy() if isinstance(match.source_attributes, dict) else {}
                if not attrs:
                    try:
                        attrs = json.loads(match.source_attributes) if isinstance(match.source_attributes, str) else {}
                    except Exception:
                        attrs = {}
                coverage = round(
                    (
                        (1 if match.league_id else 0)
                        + (1 if match.home_team_id else 0)
                        + (1 if match.away_team_id else 0)
                    ) / 3.0,
                    4,
                )
                home_country = getattr(match.home_team, "country", None) if match.home_team else None
                away_country = getattr(match.away_team, "country", None) if match.away_team else None
                country_consistency = 1 if home_country and away_country and home_country == away_country else 0
                freshness_hours = 0.0
                if match.scheduled_kickoff:
                    freshness_hours = round(abs((now - match.scheduled_kickoff.replace(tzinfo=None)).total_seconds()) / 3600, 2)

                attrs["kaggle_entity_coverage"] = coverage
                attrs["kaggle_country_consistency"] = country_consistency
                attrs["kaggle_enriched_flag"] = 1
                attrs["kaggle_source_freshness_hours"] = freshness_hours
                attrs["kaggle_feature_backfilled_at"] = now.isoformat()
                match.source_attributes = attrs
                feature_backfill["matches_backfilled"] += 1

        feature_backfill["draw_features_ensured"] = self._ensure_draw_feature_definitions(db)
        db.flush()

        rows_raw = len(league_rows) + len(team_rows) + len(match_rows)
        rows_upserted = (
            entity_merge["leagues_created"]
            + entity_merge["leagues_updated"]
            + entity_merge["teams_created"]
            + entity_merge["teams_updated"]
            + entity_merge["matches_created"]
            + entity_merge["matches_updated"]
        )
        return {
            "dataset_slug": dataset_slug,
            "version": version,
            "rows_raw": rows_raw,
            "rows_curated": rows_raw,
            "rows_upserted": rows_upserted,
            "entity_merge": entity_merge,
            "feature_backfill": feature_backfill,
        }

    def _ensure_draw_feature_definitions(self, db: Session) -> int:
        names = [item["name"] for item in self.DRAW_FEATURE_DEFINITIONS]
        existing_names = {
            row[0]
            for row in db.query(DrawFeature.name)
            .filter(DrawFeature.name.in_(names))
            .all()
        }
        created = 0
        for item in self.DRAW_FEATURE_DEFINITIONS:
            if item["name"] in existing_names:
                continue
            db.add(
                DrawFeature(
                    name=item["name"],
                    description=item["description"],
                    source_type="kaggle",
                    is_active=True,
                    meta={
                        "auto_created": True,
                        "category": "kaggle_enrichment",
                        "created_by": "kaggle_sync_service",
                    },
                )
            )
            created += 1
        return created

    def _mark_failed(self, db: Session, run: KaggleSyncRun, code: str, message: str) -> None:
        now = datetime.utcnow()
        dataset = (
            db.query(KaggleDatasetRegistry)
            .filter(KaggleDatasetRegistry.dataset_slug == run.dataset_slug)
            .first()
        )
        state = self._ensure_state_row(db, dataset_slug=run.dataset_slug)

        run.status = "failed"
        run.error_code = code
        run.error_message = (message or "")[:2000]
        run.finished_at = now
        run.duration_ms = self._duration_ms(run.started_at, now)

        state.sync_status = "failed"
        state.last_finished_at = now
        state.consecutive_failures = int(state.consecutive_failures or 0) + 1
        state.last_error_message = run.error_message
        if dataset:
            dataset.last_error_message = run.error_message
        db.commit()

    def _get_run_by_identifier(self, db: Session, run_identifier: str) -> Optional[KaggleSyncRun]:
        run = db.query(KaggleSyncRun).filter(KaggleSyncRun.run_id == run_identifier).first()
        if run:
            return run
        if str(run_identifier).isdigit():
            run = db.query(KaggleSyncRun).filter(KaggleSyncRun.id == int(run_identifier)).first()
        return run

    def _ensure_state_row(self, db: Session, *, dataset_slug: str) -> KaggleSyncState:
        row = db.query(KaggleSyncState).filter(KaggleSyncState.dataset_slug == dataset_slug).first()
        if row:
            return row
        row = KaggleSyncState(dataset_slug=dataset_slug, sync_status="idle")
        db.add(row)
        db.flush()
        return row

    @staticmethod
    def _normalize_optional_str(value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _row_to_lookup(row: Dict[str, Any]) -> Dict[str, Any]:
        lookup: Dict[str, Any] = {}
        for key, value in row.items():
            normalized = str(key).strip().lower().replace("-", "_").replace(" ", "_")
            lookup[normalized] = value
        return lookup

    def _pick_value(self, row: Dict[str, Any], keys: Tuple[str, ...]) -> Optional[str]:
        for key in keys:
            normalized = key.lower().replace(" ", "_")
            if normalized in row and row[normalized] is not None:
                val = str(row[normalized]).strip()
                if val:
                    return val
        return None

    @staticmethod
    def _hash_text(text: str) -> str:
        return hashlib.sha256((text or "").encode("utf-8")).hexdigest()

    @staticmethod
    def _hash_file(path: Path) -> Optional[str]:
        if not path.exists():
            return None
        hasher = hashlib.sha256()
        with path.open("rb") as fp:
            for chunk in iter(lambda: fp.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def _safe_slug(dataset_slug: str) -> str:
        return dataset_slug.replace("/", "__").replace("\\", "__")

    @staticmethod
    def _duration_ms(started_at: Optional[datetime], finished_at: Optional[datetime]) -> Optional[int]:
        if not started_at or not finished_at:
            return None
        return int((finished_at - started_at).total_seconds() * 1000)

    @staticmethod
    def _serialize_dataset(row: KaggleDatasetRegistry) -> Dict[str, Any]:
        safe_config = row.config.copy() if isinstance(row.config, dict) else {}
        if "kaggle_key" in safe_config:
            key_text = str(safe_config.get("kaggle_key") or "")
            safe_config["kaggle_key"] = "***" if key_text else ""
        return {
            "id": row.id,
            "dataset_slug": row.dataset_slug,
            "display_name": row.display_name,
            "owner_name": row.owner_name,
            "enabled": row.enabled,
            "sync_interval_hours": row.sync_interval_hours,
            "latest_version": row.latest_version,
            "last_synced_version": row.last_synced_version,
            "license_name": row.license_name,
            "import_mode": row.import_mode,
            "mapping_strategy": row.mapping_strategy,
            "config": safe_config,
            "last_sync_at": row.last_sync_at.isoformat() if row.last_sync_at else None,
            "last_error_message": row.last_error_message,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    @staticmethod
    def _serialize_run(row: KaggleSyncRun) -> Dict[str, Any]:
        return {
            "id": row.id,
            "run_id": row.run_id,
            "dataset_slug": row.dataset_slug,
            "task_type": row.task_type,
            "trigger_type": row.trigger_type,
            "status": row.status,
            "version": row.version,
            "rows_raw": row.rows_raw,
            "rows_curated": row.rows_curated,
            "rows_upserted": row.rows_upserted,
            "duration_ms": row.duration_ms,
            "error_code": row.error_code,
            "error_message": row.error_message,
            "run_meta": row.run_meta or {},
            "started_at": row.started_at.isoformat() if row.started_at else None,
            "finished_at": row.finished_at.isoformat() if row.finished_at else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    @staticmethod
    def _serialize_match_staging(row: KaggleMatchStaging) -> Dict[str, Any]:
        return {
            "id": row.id,
            "external_id": row.external_id,
            "league_name_raw": row.league_name_raw,
            "home_team_name_raw": row.home_team_name_raw,
            "away_team_name_raw": row.away_team_name_raw,
            "match_time_raw": row.match_time_raw,
            "is_valid": row.is_valid,
            "reject_reason": row.reject_reason,
            "payload_json": row.payload_json or {},
        }

    @staticmethod
    def _serialize_team_staging(row: KaggleTeamStaging) -> Dict[str, Any]:
        return {
            "id": row.id,
            "external_id": row.external_id,
            "team_name_raw": row.team_name_raw,
            "country_raw": row.country_raw,
            "is_valid": row.is_valid,
            "reject_reason": row.reject_reason,
            "payload_json": row.payload_json or {},
        }

    @staticmethod
    def _serialize_league_staging(row: KaggleLeagueStaging) -> Dict[str, Any]:
        return {
            "id": row.id,
            "external_id": row.external_id,
            "league_name_raw": row.league_name_raw,
            "country_raw": row.country_raw,
            "is_valid": row.is_valid,
            "reject_reason": row.reject_reason,
            "payload_json": row.payload_json or {},
        }


kaggle_sync_service = KaggleSyncService()
