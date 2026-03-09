from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Callable

from sqlalchemy import and_, inspect
from sqlalchemy.orm import Session

from backend.models.match import Match
from backend.models.odds_snapshot import OddsSnapshot
from backend.services.data_adapter import DataAdapter


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(str(value).strip().replace(",", "."))
    except Exception:
        return None


class OddsSnapshotService:
    @staticmethod
    def _ensure_snapshot_table(db: Session) -> None:
        bind = db.get_bind()
        if bind is None:
            return
        inspector = inspect(bind)
        if not inspector.has_table(OddsSnapshot.__tablename__):
            OddsSnapshot.__table__.create(bind=bind, checkfirst=True)

    @staticmethod
    def _resolve_kickoff(match: Match, attrs: Dict[str, Any], normalized: Dict[str, Any]) -> Optional[datetime]:
        kickoff = normalized.get("kickoff_time")
        if isinstance(kickoff, datetime):
            return kickoff
        if getattr(match, "scheduled_kickoff", None):
            return match.scheduled_kickoff
        if getattr(match, "match_date", None) is not None and getattr(match, "match_time", None) is not None:
            return datetime.combine(match.match_date, match.match_time)
        return DataAdapter.parse_datetime(attrs.get("kickoff_time") or attrs.get("match_time") or attrs.get("matchTimeStr"))

    @staticmethod
    def _match_query_for_source(db: Session, target_date: date, source: str):
        q = db.query(Match).filter(Match.match_date == target_date)
        q = q.filter(Match.is_deleted == False)  # noqa: E712

        normalized_source = (source or "500").strip().lower()
        if normalized_source in {"500", "500w", "trade500", "bjdc500"}:
            q = q.filter(Match.data_source.like("%500%"))
        elif normalized_source:
            q = q.filter(Match.data_source == normalized_source)
        return q

    @staticmethod
    def _existing_snapshot(
        db: Session,
        match_id: str,
        source: str,
        fixture_id: Optional[str],
        captured_at: datetime,
    ) -> Optional[OddsSnapshot]:
        return (
            db.query(OddsSnapshot)
            .filter(OddsSnapshot.match_id == match_id)
            .filter(OddsSnapshot.source == source)
            .filter(OddsSnapshot.fixture_id == fixture_id)
            .filter(OddsSnapshot.captured_at == captured_at)
            .first()
        )

    @staticmethod
    def create_snapshot(db: Session, payload: Dict[str, Any]) -> OddsSnapshot:
        snapshot = OddsSnapshot(
            match_id=str(payload.get("match_id") or ""),
            source=str(payload.get("source") or "500"),
            fixture_id=payload.get("fixture_id"),
            captured_at=payload.get("captured_at") or datetime.utcnow(),
            kickoff_time=payload.get("kickoff_time") or datetime.utcnow(),
            odds_draw=float(payload.get("odds_draw") or 0),
            raw_payload=payload.get("raw_payload") if isinstance(payload.get("raw_payload"), dict) else payload,
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    @staticmethod
    def fetch_snapshots_for_date(
        db: Session,
        target_date: date,
        source: str = "500",
        overwrite: bool = False,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        OddsSnapshotService._ensure_snapshot_table(db)
        matches = OddsSnapshotService._match_query_for_source(db, target_date, source).all()
        total = len(matches)
        created = 0
        skipped = 0
        mapped = 0

        for idx, match in enumerate(matches, start=1):
            attrs = DataAdapter.to_dict(getattr(match, "source_attributes", None))
            normalized = DataAdapter.normalize_odds_payload(source, attrs)
            odds_draw = _to_float(normalized.get("odds_draw"))
            if odds_draw is None or odds_draw <= 0:
                skipped += 1
                if progress_callback:
                    progress_callback(
                        {
                            "phase": "fetching",
                            "progress": round((idx / max(total, 1)) * 100, 2),
                            "current": idx,
                            "total": total,
                            "message": f"处理中 {idx}/{total}",
                        }
                    )
                continue

            kickoff_time = OddsSnapshotService._resolve_kickoff(match, attrs, normalized)
            if not kickoff_time:
                skipped += 1
                continue

            internal_match_id = str(match.match_identifier)
            fixture_id = normalized.get("fixture_id") or (str(match.source_match_id) if getattr(match, "source_match_id", None) else None)
            captured_at = normalized.get("captured_at") if isinstance(normalized.get("captured_at"), datetime) else datetime.utcnow()

            if not overwrite:
                existing = OddsSnapshotService._existing_snapshot(
                    db=db,
                    match_id=internal_match_id,
                    source=source,
                    fixture_id=fixture_id,
                    captured_at=captured_at,
                )
                if existing:
                    skipped += 1
                    continue

            snapshot = OddsSnapshot(
                match_id=internal_match_id,
                source=source,
                fixture_id=fixture_id,
                captured_at=captured_at,
                kickoff_time=kickoff_time,
                odds_draw=odds_draw,
                raw_payload=normalized.get("raw_payload") if isinstance(normalized.get("raw_payload"), dict) else attrs,
            )
            db.add(snapshot)
            created += 1

            if fixture_id:
                DataAdapter.upsert_external_mapping(
                    db,
                    source=source,
                    external_id=str(fixture_id),
                    internal_match_id=internal_match_id,
                    confidence_score=1.0,
                    mapping_meta={"via": "source_match_id_or_match_record"},
                )
                mapped += 1

            if progress_callback:
                progress_callback(
                    {
                        "phase": "fetching",
                        "progress": round((idx / max(total, 1)) * 100, 2),
                        "current": idx,
                        "total": total,
                        "message": f"处理中 {idx}/{total}",
                    }
                )

        db.commit()

        return {
            "date": target_date.isoformat(),
            "source": source,
            "total_candidates": total,
            "created": created,
            "skipped": skipped,
            "mapped": mapped,
        }

    @staticmethod
    def list_snapshots(
        db: Session,
        match_id: Optional[str] = None,
        date_str: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        OddsSnapshotService._ensure_snapshot_table(db)
        q = db.query(OddsSnapshot)
        if match_id:
            q = q.filter(OddsSnapshot.match_id == match_id)
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                start = datetime.combine(target_date, datetime.min.time())
                end = datetime.combine(target_date, datetime.max.time())
                q = q.filter(and_(OddsSnapshot.kickoff_time >= start, OddsSnapshot.kickoff_time <= end))
            except Exception:
                pass

        total = q.count()
        items: List[OddsSnapshot] = (
            q.order_by(OddsSnapshot.captured_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": [
                {
                    "id": row.id,
                    "match_id": row.match_id,
                    "source": row.source,
                    "fixture_id": row.fixture_id,
                    "captured_at": row.captured_at,
                    "kickoff_time": row.kickoff_time,
                    "odds_draw": row.odds_draw,
                }
                for row in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
