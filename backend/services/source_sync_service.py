"""
Automatic issue-driven synchronization for 500w -> 100qiu flow.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import threading
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import SessionLocal
from backend.models.data_sources import DataSource
from backend.models.source_issue_fetch_runs import SourceIssueFetchRun
from backend.models.source_issue_state import SourceIssueState

logger = logging.getLogger(__name__)


class SourceIssueAutoSyncService:
    """Manage automatic 500w issue discovery and 100qiu fetch pipeline."""

    STATE_500W = "500w_bjdc"
    STATE_100QIU = "100qiu"

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self._started = False
        self._running = False
        self._last_result: Dict[str, Any] = {}
        self._last_started_at: Optional[datetime] = None
        self._last_finished_at: Optional[datetime] = None

    def start(self) -> None:
        """Start background scheduler."""
        if self._started:
            return
        if not settings.AUTO_100QIU_SYNC_ENABLED:
            logger.info("Auto 500w->100qiu sync is disabled by configuration")
            return

        base_hours = max(1, int(settings.AUTO_100QIU_BASE_INTERVAL_HOURS))
        self._scheduler.add_job(
            self._run_safely,
            trigger=IntervalTrigger(hours=base_hours),
            id="source_sync_base_interval",
            name="500w issue discovery (base interval)",
            replace_existing=True,
        )

        if settings.AUTO_100QIU_WINDOW_ENABLED:
            step = max(5, int(settings.AUTO_100QIU_WINDOW_MINUTE_STEP))
            self._scheduler.add_job(
                self._run_safely,
                trigger=CronTrigger(minute=f"*/{step}", hour=settings.AUTO_100QIU_WINDOW_HOURS),
                id="source_sync_window",
                name="500w issue discovery (window)",
                replace_existing=True,
            )

        self._scheduler.start()
        self._started = True
        logger.info("Auto 500w->100qiu sync scheduler started")

    def shutdown(self) -> None:
        """Stop background scheduler."""
        if not self._started:
            return
        try:
            if self._scheduler.running:
                self._scheduler.shutdown(wait=False)
        finally:
            self._started = False
            logger.info("Auto 500w->100qiu sync scheduler stopped")

    def is_running(self) -> bool:
        return self._running

    def trigger_run_now(self) -> Dict[str, Any]:
        """Run once asynchronously in a daemon thread."""
        if self._running:
            return {
                "started": False,
                "message": "sync is already running",
                "last_result": self._last_result,
            }

        thread = threading.Thread(
            target=self._run_safely,
            kwargs={"trigger_type": "manual"},
            daemon=True,
            name="source-sync-manual",
        )
        thread.start()
        return {
            "started": True,
            "message": "sync triggered",
        }

    def get_status_snapshot(self, db: Session) -> Dict[str, Any]:
        """Build status payload for UI/API."""
        state_500 = self._get_state(db, self.STATE_500W)
        state_100 = self._get_state(db, self.STATE_100QIU)
        latest_run = (
            db.query(SourceIssueFetchRun)
            .filter(SourceIssueFetchRun.source_type == self.STATE_100QIU)
            .order_by(SourceIssueFetchRun.created_at.desc())
            .first()
        )

        next_run_at: Optional[str] = None
        if self._started and self._scheduler.running:
            jobs = self._scheduler.get_jobs()
            next_times = [job.next_run_time for job in jobs if job.next_run_time is not None]
            if next_times:
                next_run_at = min(next_times).isoformat()

        sync_status = "idle"
        if self._running:
            sync_status = "running"
        elif state_100.last_error_message and (
            not state_100.last_success_issue
            or state_100.last_success_issue != state_500.latest_discovered_issue
        ):
            sync_status = "degraded"
        elif state_100.last_success_issue:
            sync_status = "success"

        return {
            "sync_status": sync_status,
            "auto_enabled": bool(settings.AUTO_100QIU_SYNC_ENABLED),
            "is_running": self._running,
            "latest_issue_no": state_500.latest_discovered_issue,
            "last_success_issue_no": state_100.last_success_issue,
            "last_discovered_at": state_500.last_discovered_at.isoformat() if state_500.last_discovered_at else None,
            "last_sync_at": state_100.last_success_at.isoformat() if state_100.last_success_at else None,
            "next_sync_at": next_run_at,
            "last_error": state_100.last_error_message,
            "last_run": self._serialize_run(latest_run) if latest_run else None,
            "last_result": self._last_result,
            "last_started_at": self._last_started_at.isoformat() if self._last_started_at else None,
            "last_finished_at": self._last_finished_at.isoformat() if self._last_finished_at else None,
        }

    def list_runs(
        self,
        db: Session,
        *,
        page: int = 1,
        size: int = 20,
        source_type: str = STATE_100QIU,
        status: Optional[str] = None,
    ) -> Tuple[list[Dict[str, Any]], int]:
        """List synchronization runs for UI/API."""
        page = max(1, int(page))
        size = min(200, max(1, int(size)))
        query = db.query(SourceIssueFetchRun).filter(SourceIssueFetchRun.source_type == source_type)
        if status:
            query = query.filter(SourceIssueFetchRun.status == status)
        total = query.count()
        rows = (
            query.order_by(SourceIssueFetchRun.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return [self._serialize_run(row) for row in rows], total

    def _run_safely(self, trigger_type: str = "scheduler") -> None:
        """Lock-protected run wrapper."""
        if not self._lock.acquire(blocking=False):
            logger.info("Auto source sync skipped because previous run is still active")
            return
        self._running = True
        self._last_started_at = datetime.utcnow()
        try:
            self._last_result = self._run_once(trigger_type=trigger_type)
        except Exception as exc:
            logger.exception("Auto source sync crashed: %s", exc)
            self._last_result = {
                "success": False,
                "message": f"sync crashed: {exc}",
                "trigger_type": trigger_type,
            }
        finally:
            self._last_finished_at = datetime.utcnow()
            self._running = False
            self._lock.release()

    def _run_once(self, trigger_type: str = "scheduler") -> Dict[str, Any]:
        db = SessionLocal()
        try:
            state_500 = self._get_state(db, self.STATE_500W)
            state_100 = self._get_state(db, self.STATE_100QIU)

            latest_issue = self._fetch_latest_issue_from_500w()
            now = datetime.utcnow()
            if not latest_issue:
                state_500.last_error_message = "failed to parse latest issue from 500w"
                state_100.last_error_message = "failed to parse latest issue from 500w"
                db.commit()
                return {
                    "success": False,
                    "trigger_type": trigger_type,
                    "message": "failed to discover latest 500w issue",
                }

            state_500.latest_discovered_issue = latest_issue
            state_500.last_discovered_at = now
            state_500.last_error_message = None
            state_100.latest_discovered_issue = latest_issue
            state_100.last_discovered_at = now
            db.commit()

            if not self._is_new_issue(latest_issue, state_100.last_success_issue):
                return {
                    "success": True,
                    "trigger_type": trigger_type,
                    "status": "skipped",
                    "issue_no": latest_issue,
                    "message": "no new issue",
                }

            data_source, created = self._ensure_100qiu_data_source(db, latest_issue)
            run, action = self._prepare_run_row(
                db,
                issue_no=latest_issue,
                trigger_type=trigger_type,
                source_id=data_source.id,
                request_url=self._build_100qiu_url_for_issue(latest_issue),
            )
            db.commit()

            if action == "already_success":
                return {
                    "success": True,
                    "trigger_type": trigger_type,
                    "status": "skipped",
                    "issue_no": latest_issue,
                    "message": "issue already fetched successfully",
                    "source_id": data_source.id,
                    "source_created": created,
                }
            if action == "already_running":
                return {
                    "success": True,
                    "trigger_type": trigger_type,
                    "status": "skipped",
                    "issue_no": latest_issue,
                    "message": "issue is already running",
                    "source_id": data_source.id,
                    "source_created": created,
                }

            fetch_payload = self._execute_fetch(db, data_source.id)
            run = db.query(SourceIssueFetchRun).filter(SourceIssueFetchRun.id == run.id).first()
            state_100 = self._get_state(db, self.STATE_100QIU)
            finished_at = datetime.utcnow()

            run.response_code = fetch_payload.get("response_code")
            run.records_count = int(fetch_payload.get("total_fetched") or 0)
            run.request_url = fetch_payload.get("request_url") or run.request_url
            run.finished_at = finished_at

            if fetch_payload.get("success"):
                run.status = "success"
                run.error_message = None
                state_100.last_success_issue = latest_issue
                state_100.last_success_at = finished_at
                state_100.last_error_message = None
            else:
                run.status = "failed"
                run.error_message = fetch_payload.get("message")
                state_100.last_error_message = fetch_payload.get("message")

            db.commit()

            return {
                "success": bool(fetch_payload.get("success")),
                "trigger_type": trigger_type,
                "issue_no": latest_issue,
                "source_id": data_source.id,
                "source_created": created,
                "status": run.status,
                "total_fetched": run.records_count,
                "message": fetch_payload.get("message"),
            }
        except Exception as exc:
            db.rollback()
            logger.exception("Auto source sync run failed: %s", exc)
            return {
                "success": False,
                "trigger_type": trigger_type,
                "message": f"sync failed: {exc}",
            }
        finally:
            db.close()

    def _get_state(self, db: Session, source_type: str) -> SourceIssueState:
        row = db.query(SourceIssueState).filter(SourceIssueState.source_type == source_type).first()
        if row:
            return row
        row = SourceIssueState(source_type=source_type)
        db.add(row)
        db.flush()
        return row

    def _is_new_issue(self, latest_issue: str, last_success_issue: Optional[str]) -> bool:
        latest_val = self._to_issue_number(latest_issue)
        last_val = self._to_issue_number(last_success_issue)
        if latest_val is None:
            return False
        if last_val is None:
            return True
        return latest_val > last_val

    @staticmethod
    def _to_issue_number(value: Optional[str]) -> Optional[int]:
        if value is None:
            return None
        match = re.search(r"\d{5,6}", str(value))
        if not match:
            return None
        try:
            return int(match.group(0))
        except (TypeError, ValueError):
            return None

    def _fetch_latest_issue_from_500w(self) -> Optional[str]:
        session = requests.Session()
        session.trust_env = False
        try:
            response = session.get(
                "https://trade.500.com/bjdc/",
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
                    ),
                    "Referer": "https://trade.500.com/bjdc/",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                },
                timeout=20,
            )
            if response.status_code != 200:
                logger.warning("500w issue discovery got status code %s", response.status_code)
                return None

            text = response.text or ""
            selected_match = re.search(
                r"<option[^>]+value=['\"](\d{5,6})['\"][^>]*selected",
                text,
                flags=re.IGNORECASE,
            )
            if selected_match:
                return selected_match.group(1)

            values = re.findall(r"<option[^>]+value=['\"](\d{5,6})['\"]", text, flags=re.IGNORECASE)
            if values:
                return values[0]

            return None
        except Exception as exc:
            logger.warning("500w issue discovery failed: %s", exc)
            return None
        finally:
            session.close()

    def _ensure_100qiu_data_source(self, db: Session, issue_no: str) -> Tuple[DataSource, bool]:
        all_rows = db.query(DataSource).all()
        for row in all_rows:
            config = row.config_dict or {}
            if config.get("source_type") != "100qiu":
                continue
            if str(config.get("date_time") or "").strip() == issue_no:
                return row, False

        config = {
            "source_type": "100qiu",
            "date_time": issue_no,
            "category": "match_data",
            "auto_managed": True,
            "update_frequency": int(settings.AUTO_100QIU_SOURCE_UPDATE_FREQUENCY_MINUTES),
        }
        row = DataSource(
            name=f"100qiu竞彩彩票数据源-{issue_no}",
            type="api",
            status=1,
            url="https://m.100qiu.com/api/dcListBasic",
            config=json.dumps(config, ensure_ascii=False),
            update_frequency=int(settings.AUTO_100QIU_SOURCE_UPDATE_FREQUENCY_MINUTES),
            created_by=1,
        )
        db.add(row)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            all_rows = db.query(DataSource).all()
            for item in all_rows:
                cfg = item.config_dict or {}
                if cfg.get("source_type") == "100qiu" and str(cfg.get("date_time") or "").strip() == issue_no:
                    return item, False
            raise
        return row, True

    def _prepare_run_row(
        self,
        db: Session,
        *,
        issue_no: str,
        trigger_type: str,
        source_id: Optional[int],
        request_url: Optional[str],
    ) -> Tuple[SourceIssueFetchRun, str]:
        run = (
            db.query(SourceIssueFetchRun)
            .filter(SourceIssueFetchRun.source_type == self.STATE_100QIU)
            .filter(SourceIssueFetchRun.issue_no == issue_no)
            .first()
        )
        now = datetime.utcnow()
        if run:
            if run.status == "success":
                return run, "already_success"
            if run.status == "running":
                return run, "already_running"
            run.status = "running"
            run.trigger_type = trigger_type
            run.source_id = source_id
            run.request_url = request_url
            run.error_message = None
            run.response_code = None
            run.records_count = 0
            run.started_at = now
            run.finished_at = None
            return run, "execute"

        run = SourceIssueFetchRun(
            source_type=self.STATE_100QIU,
            issue_no=issue_no,
            status="running",
            trigger_type=trigger_type,
            source_id=source_id,
            request_url=request_url,
            records_count=0,
            started_at=now,
        )
        db.add(run)
        db.flush()
        return run, "execute"

    def _execute_fetch(self, db: Session, source_id: int) -> Dict[str, Any]:
        from backend.api.v1.data_source_100qiu import fetch_100qiu_data

        result = asyncio.run(fetch_100qiu_data(source_id=source_id, compare_update=True, db=db))
        return self._normalize_fetch_result(result)

    def _normalize_fetch_result(self, raw: Any) -> Dict[str, Any]:
        payload: Dict[str, Any]
        if isinstance(raw, dict):
            payload = raw
        elif hasattr(raw, "dict"):
            payload = raw.dict()
        else:
            payload = {"success": False, "message": f"unexpected response type: {type(raw)}"}

        success = bool(payload.get("success"))
        total_fetched = int(payload.get("total_fetched") or 0)
        message = str(payload.get("message") or "")
        request_trace = payload.get("request_trace") if isinstance(payload.get("request_trace"), dict) else {}
        response_code = request_trace.get("status_code") or request_trace.get("response_code")
        request_url = request_trace.get("api_url") or request_trace.get("request_url")

        nested = payload.get("data")
        if isinstance(nested, dict) and "success" in nested and "total_fetched" in nested:
            success = bool(nested.get("success"))
            total_fetched = int(nested.get("total_fetched") or 0)
            message = message or str(nested.get("message") or "")
            nested_trace = nested.get("request_trace")
            if isinstance(nested_trace, dict):
                request_trace = nested_trace
                response_code = request_trace.get("status_code") or request_trace.get("response_code")
                request_url = request_trace.get("api_url") or request_trace.get("request_url")

        if not message:
            message = "fetch completed" if success else "fetch failed"

        return {
            "success": success,
            "total_fetched": total_fetched,
            "message": message,
            "response_code": response_code,
            "request_url": request_url,
        }

    @staticmethod
    def _build_100qiu_url_for_issue(issue_no: str) -> str:
        return f"https://m.100qiu.com/api/dcListBasic?dateTime={issue_no}"

    @staticmethod
    def _serialize_run(row: SourceIssueFetchRun) -> Dict[str, Any]:
        return {
            "id": row.id,
            "source_type": row.source_type,
            "issue_no": row.issue_no,
            "status": row.status,
            "trigger_type": row.trigger_type,
            "source_id": row.source_id,
            "request_url": row.request_url,
            "response_code": row.response_code,
            "records_count": row.records_count,
            "error_message": row.error_message,
            "started_at": row.started_at.isoformat() if row.started_at else None,
            "finished_at": row.finished_at.isoformat() if row.finished_at else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }


source_issue_auto_sync_service = SourceIssueAutoSyncService()

