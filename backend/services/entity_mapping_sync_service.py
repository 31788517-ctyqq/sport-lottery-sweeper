"""
Periodic DB-driven entity mapping synchronization service.

This service builds team/league mapping records from existing DB entities and
match source attributes, then stores the normalized mapping payload in
`entity_mapping_records`.
"""

from __future__ import annotations

import logging
import re
import threading
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import SessionLocal
from backend.models.entity_mapping_record import EntityMappingRecord, EntityMappingSyncRun
from backend.models.match import League, Match, Team

logger = logging.getLogger(__name__)


class EntityMappingSyncService:
    """Synchronize DB team/league entities into entity mapping records."""

    HOME_NAME_KEYS = ("home_team", "homeTeam", "homeName", "hostName", "host_team")
    AWAY_NAME_KEYS = ("away_team", "awayTeam", "awayName", "guestName", "guest_team")
    LEAGUE_NAME_KEYS = (
        "league",
        "league_name",
        "leagueName",
        "competition",
        "competitionName",
        "tournament",
        "matchName",
    )

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self._started = False
        self._running = False
        self._last_result: Dict[str, Any] = {}
        self._last_started_at: Optional[datetime] = None
        self._last_finished_at: Optional[datetime] = None

    def start(self) -> None:
        if self._started:
            return
        if not bool(getattr(settings, "AUTO_ENTITY_MAPPING_SYNC_ENABLED", True)):
            logger.info("Entity mapping auto sync disabled by configuration")
            return

        interval_minutes = max(10, int(getattr(settings, "AUTO_ENTITY_MAPPING_SYNC_INTERVAL_MINUTES", 180)))
        self._scheduler.add_job(
            self._run_safely,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id="entity_mapping_sync_interval",
            name="Entity mapping sync interval",
            replace_existing=True,
            kwargs={"trigger_type": "scheduler"},
        )

        self._scheduler.start()
        self._started = True
        logger.info("Entity mapping sync scheduler started (interval=%s min)", interval_minutes)

        if bool(getattr(settings, "AUTO_ENTITY_MAPPING_SYNC_RUN_ON_STARTUP", True)):
            self.trigger_run_now(trigger_type="startup")

    def shutdown(self) -> None:
        if not self._started:
            return
        try:
            if self._scheduler.running:
                self._scheduler.shutdown(wait=False)
        finally:
            self._started = False
            logger.info("Entity mapping sync scheduler stopped")

    def trigger_run_now(self, trigger_type: str = "manual") -> Dict[str, Any]:
        if self._running:
            return {"started": False, "message": "sync is already running", "last_result": self._last_result}

        thread = threading.Thread(
            target=self._run_safely,
            kwargs={"trigger_type": trigger_type},
            daemon=True,
            name=f"entity-mapping-sync-{trigger_type}",
        )
        thread.start()
        return {"started": True, "message": "entity mapping sync triggered", "trigger_type": trigger_type}

    def is_running(self) -> bool:
        return self._running

    def get_status_snapshot(self, db: Session) -> Dict[str, Any]:
        latest_run = db.query(EntityMappingSyncRun).order_by(EntityMappingSyncRun.started_at.desc()).first()

        next_run_at: Optional[str] = None
        if self._started and self._scheduler.running:
            jobs = self._scheduler.get_jobs()
            next_times = [job.next_run_time for job in jobs if job.next_run_time is not None]
            if next_times:
                next_run_at = min(next_times).isoformat()

        return {
            "auto_enabled": bool(getattr(settings, "AUTO_ENTITY_MAPPING_SYNC_ENABLED", True)),
            "is_running": self._running,
            "next_sync_at": next_run_at,
            "last_started_at": self._last_started_at.isoformat() if self._last_started_at else None,
            "last_finished_at": self._last_finished_at.isoformat() if self._last_finished_at else None,
            "last_result": self._last_result,
            "last_run": self._serialize_run(latest_run) if latest_run else None,
        }

    def _run_safely(self, trigger_type: str = "scheduler") -> None:
        if not self._lock.acquire(blocking=False):
            logger.info("Entity mapping sync skipped because previous run is still active")
            return

        self._running = True
        self._last_started_at = datetime.utcnow()
        try:
            self._last_result = self._run_once(trigger_type=trigger_type)
        except Exception as exc:
            logger.exception("Entity mapping sync crashed: %s", exc)
            self._last_result = {
                "success": False,
                "trigger_type": trigger_type,
                "message": f"sync crashed: {exc}",
            }
        finally:
            self._last_finished_at = datetime.utcnow()
            self._running = False
            self._lock.release()

    def _run_once(self, trigger_type: str = "scheduler") -> Dict[str, Any]:
        db = SessionLocal()
        run = EntityMappingSyncRun(trigger_type=trigger_type, status="running", started_at=datetime.utcnow())
        db.add(run)
        db.flush()

        try:
            team_alias_index, league_alias_index = self._build_alias_indexes(db)
            scanned_teams, upserted_teams, failed_teams = self._sync_teams(db, team_alias_index)
            scanned_leagues, upserted_leagues, failed_leagues = self._sync_leagues(db, league_alias_index)

            run.status = "success"
            run.scanned_teams = scanned_teams
            run.scanned_leagues = scanned_leagues
            run.upserted_teams = upserted_teams
            run.upserted_leagues = upserted_leagues
            run.failed_count = failed_teams + failed_leagues
            run.finished_at = datetime.utcnow()
            run.summary = {
                "teams": {"scanned": scanned_teams, "upserted": upserted_teams, "failed": failed_teams},
                "leagues": {"scanned": scanned_leagues, "upserted": upserted_leagues, "failed": failed_leagues},
            }
            db.commit()

            return {
                "success": True,
                "trigger_type": trigger_type,
                "scanned_teams": scanned_teams,
                "scanned_leagues": scanned_leagues,
                "upserted_teams": upserted_teams,
                "upserted_leagues": upserted_leagues,
                "failed_count": failed_teams + failed_leagues,
                "run_id": run.id,
            }
        except Exception as exc:
            db.rollback()
            run = db.query(EntityMappingSyncRun).filter(EntityMappingSyncRun.id == run.id).first()
            if run:
                run.status = "failed"
                run.error_message = str(exc)
                run.finished_at = datetime.utcnow()
                db.commit()

            logger.exception("Entity mapping sync failed: %s", exc)
            return {"success": False, "trigger_type": trigger_type, "message": f"sync failed: {exc}"}
        finally:
            db.close()

    def _sync_teams(self, db: Session, alias_index: Dict[int, Dict[str, Set[str]]]) -> Tuple[int, int, int]:
        teams = db.query(Team).all()
        scanned = len(teams)
        upserted = 0
        failed = 0

        for team in teams:
            try:
                zh_names = self._unique_names([team.name, team.short_name, team.full_name])
                source_aliases = self._normalize_alias_map(alias_index.get(int(team.id), {}))
                source_aliases.setdefault("database", [])
                source_aliases["database"] = self._merge_and_sort(source_aliases["database"], zh_names)

                official_info = {}
                if team.website:
                    official_info["website"] = team.website

                changed = self._upsert_mapping_record(
                    db=db,
                    entity_type="team",
                    entity_ref_id=str(team.id),
                    canonical_key=f"team_{team.id}",
                    display_name=team.name or (zh_names[0] if zh_names else f"team_{team.id}"),
                    zh_names=zh_names,
                    en_names=self._extract_en_names(team.config),
                    jp_names=self._extract_jp_names(team.config),
                    source_aliases=source_aliases,
                    official_info=official_info,
                    confidence_score=1.0,
                )
                if changed:
                    upserted += 1
            except Exception as exc:
                failed += 1
                logger.warning("Failed to sync team mapping for team_id=%s: %s", team.id, exc)

        return scanned, upserted, failed

    def _sync_leagues(self, db: Session, alias_index: Dict[int, Dict[str, Set[str]]]) -> Tuple[int, int, int]:
        leagues = db.query(League).all()
        scanned = len(leagues)
        upserted = 0
        failed = 0

        for league in leagues:
            try:
                zh_names = self._unique_names([league.name, league.short_name])
                source_aliases = self._normalize_alias_map(alias_index.get(int(league.id), {}))
                source_aliases.setdefault("database", [])
                source_aliases["database"] = self._merge_and_sort(source_aliases["database"], zh_names)

                official_info = {}
                if league.logo_url:
                    official_info["logo_url"] = league.logo_url

                changed = self._upsert_mapping_record(
                    db=db,
                    entity_type="league",
                    entity_ref_id=str(league.id),
                    canonical_key=f"league_{league.id}",
                    display_name=league.name or (zh_names[0] if zh_names else f"league_{league.id}"),
                    zh_names=zh_names,
                    en_names=self._extract_en_names(league.config),
                    jp_names=self._extract_jp_names(league.config),
                    source_aliases=source_aliases,
                    official_info=official_info,
                    confidence_score=1.0,
                )
                if changed:
                    upserted += 1
            except Exception as exc:
                failed += 1
                logger.warning("Failed to sync league mapping for league_id=%s: %s", league.id, exc)

        return scanned, upserted, failed

    def _build_alias_indexes(
        self, db: Session
    ) -> Tuple[Dict[int, Dict[str, Set[str]]], Dict[int, Dict[str, Set[str]]]]:
        team_alias_index: Dict[int, Dict[str, Set[str]]] = {}
        league_alias_index: Dict[int, Dict[str, Set[str]]] = {}

        max_rows = max(1000, int(getattr(settings, "AUTO_ENTITY_MAPPING_SYNC_MATCH_SCAN_LIMIT", 50000)))
        rows = (
            db.query(
                Match.home_team_id,
                Match.away_team_id,
                Match.league_id,
                Match.data_source,
                Match.external_source,
                Match.source_attributes,
            )
            .order_by(Match.id.desc())
            .limit(max_rows)
            .all()
        )

        for row in rows:
            attrs = self._to_dict(row.source_attributes)
            source = str(row.data_source or row.external_source or "unknown").strip().lower()
            source = source or "unknown"

            if row.home_team_id:
                bucket = team_alias_index.setdefault(int(row.home_team_id), {})
                source_set = bucket.setdefault(source, set())
                self._add_alias_candidates(source_set, self._iter_values(attrs, self.HOME_NAME_KEYS))

            if row.away_team_id:
                bucket = team_alias_index.setdefault(int(row.away_team_id), {})
                source_set = bucket.setdefault(source, set())
                self._add_alias_candidates(source_set, self._iter_values(attrs, self.AWAY_NAME_KEYS))

            if row.league_id:
                bucket = league_alias_index.setdefault(int(row.league_id), {})
                source_set = bucket.setdefault(source, set())
                self._add_alias_candidates(source_set, self._iter_values(attrs, self.LEAGUE_NAME_KEYS))

        return team_alias_index, league_alias_index

    def _upsert_mapping_record(
        self,
        *,
        db: Session,
        entity_type: str,
        entity_ref_id: str,
        canonical_key: str,
        display_name: str,
        zh_names: List[str],
        en_names: List[str],
        jp_names: List[str],
        source_aliases: Dict[str, List[str]],
        official_info: Dict[str, Any],
        confidence_score: float,
    ) -> bool:
        now = datetime.utcnow()
        row = (
            db.query(EntityMappingRecord)
            .filter(
                EntityMappingRecord.entity_type == entity_type,
                EntityMappingRecord.entity_ref_id == entity_ref_id,
            )
            .first()
        )

        if not row:
            row = EntityMappingRecord(
                entity_type=entity_type,
                entity_ref_id=entity_ref_id,
                canonical_key=canonical_key,
                display_name=display_name,
                zh_names=zh_names,
                en_names=en_names,
                jp_names=jp_names,
                source_aliases=source_aliases,
                official_info=official_info,
                confidence_score=confidence_score,
                auto_generated=True,
                last_seen_at=now,
                updated_at=now,
            )
            db.add(row)
            db.flush()
            return True

        changed = False

        changed |= self._set_if_diff(row, "canonical_key", canonical_key)
        changed |= self._set_if_diff(row, "display_name", display_name)
        changed |= self._set_if_diff(row, "zh_names", zh_names)
        changed |= self._set_if_diff(row, "en_names", en_names)
        changed |= self._set_if_diff(row, "jp_names", jp_names)
        changed |= self._set_if_diff(row, "source_aliases", source_aliases)

        merged_official = dict(row.official_info or {})
        merged_official.update(official_info or {})
        changed |= self._set_if_diff(row, "official_info", merged_official)
        changed |= self._set_if_diff(row, "confidence_score", confidence_score)

        row.last_seen_at = now
        row.updated_at = now
        return changed

    @staticmethod
    def _set_if_diff(row: EntityMappingRecord, field_name: str, value: Any) -> bool:
        current = getattr(row, field_name)
        if current == value:
            return False
        setattr(row, field_name, value)
        return True

    @staticmethod
    def _to_dict(value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value
        return {}

    def _iter_values(self, payload: Dict[str, Any], keys: Iterable[str]) -> Iterable[Any]:
        for key in keys:
            if key in payload:
                yield payload.get(key)

    def _add_alias_candidates(self, target: Set[str], values: Iterable[Any]) -> None:
        for value in values:
            for candidate in self._extract_name_candidates(value):
                target.add(candidate)

    def _extract_name_candidates(self, raw: Any) -> List[str]:
        if raw is None:
            return []
        text = str(raw).strip()
        if not text:
            return []

        parts = re.split(r"[,，;；|/]+", text)
        results: List[str] = []
        for part in parts:
            cleaned = self._clean_candidate_name(part)
            if cleaned:
                results.append(cleaned)
        return self._unique_names(results)

    @staticmethod
    def _clean_candidate_name(raw: Any) -> str:
        text = str(raw or "").strip()
        if not text:
            return ""

        text = re.sub(r"\[\d+\]", "", text)
        text = re.sub(r"\(\d+\)", "", text)
        text = re.sub(r"\d+\s*[:：]\s*\d+", "", text)
        text = re.sub(r"\s{2,}", " ", text).strip()

        if not text or len(text) > 80:
            return ""
        if text.isdigit():
            return ""
        return text

    @staticmethod
    def _unique_names(values: Iterable[Any]) -> List[str]:
        seen: Set[str] = set()
        result: List[str] = []
        for value in values:
            text = str(value or "").strip()
            if not text:
                continue
            if text in seen:
                continue
            seen.add(text)
            result.append(text)
        return result

    @staticmethod
    def _merge_and_sort(existing: List[str], incoming: List[str]) -> List[str]:
        merged = list(existing or [])
        for item in incoming or []:
            if item not in merged:
                merged.append(item)
        return sorted(merged, key=lambda x: (len(str(x)), str(x)))

    @staticmethod
    def _normalize_alias_map(alias_map: Dict[str, Set[str]]) -> Dict[str, List[str]]:
        normalized: Dict[str, List[str]] = {}
        for source, names in (alias_map or {}).items():
            cleaned = sorted([name for name in names if name], key=lambda x: (len(str(x)), str(x)))
            if cleaned:
                normalized[str(source)] = cleaned
        return normalized

    @staticmethod
    def _extract_en_names(config: Any) -> List[str]:
        if not isinstance(config, dict):
            return []
        candidates = [
            config.get("en"),
            config.get("en_name"),
            config.get("english_name"),
            config.get("name_en"),
        ]
        return EntityMappingSyncService._unique_names(candidates)

    @staticmethod
    def _extract_jp_names(config: Any) -> List[str]:
        if not isinstance(config, dict):
            return []
        candidates = [
            config.get("jp"),
            config.get("jp_name"),
            config.get("japanese_name"),
            config.get("name_jp"),
        ]
        return EntityMappingSyncService._unique_names(candidates)

    @staticmethod
    def _serialize_run(row: EntityMappingSyncRun) -> Dict[str, Any]:
        return {
            "id": row.id,
            "trigger_type": row.trigger_type,
            "status": row.status,
            "scanned_teams": row.scanned_teams,
            "scanned_leagues": row.scanned_leagues,
            "upserted_teams": row.upserted_teams,
            "upserted_leagues": row.upserted_leagues,
            "failed_count": row.failed_count,
            "error_message": row.error_message,
            "summary": row.summary or {},
            "started_at": row.started_at.isoformat() if row.started_at else None,
            "finished_at": row.finished_at.isoformat() if row.finished_at else None,
        }


entity_mapping_sync_service = EntityMappingSyncService()

