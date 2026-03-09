from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
import json
import re

from sqlalchemy.orm import Session

from backend.models.external_source_mapping import ExternalSourceMapping
from backend.models.match import Match


class DataAdapter:
    @staticmethod
    def to_dict(payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, str) and payload:
            try:
                parsed = json.loads(payload)
                return parsed if isinstance(parsed, dict) else {}
            except Exception:
                return {}
        return {}

    @staticmethod
    def normalize_team_name(name: Any) -> str:
        text = str(name or "").strip().lower()
        if not text:
            return ""
        text = re.sub(r"\s+", "", text)
        text = re.sub(r"[\-_.·•'\"]", "", text)
        return text

    @staticmethod
    def parse_datetime(value: Any) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value
        if not value:
            return None
        text = str(value).strip()
        if not text:
            return None
        patterns = (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        )
        for fmt in patterns:
            try:
                return datetime.strptime(text, fmt)
            except Exception:
                continue
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            return None

    @staticmethod
    def normalize_odds_payload(source: str, payload: Any) -> Dict[str, Any]:
        data = DataAdapter.to_dict(payload)
        odds_draw = data.get("odds_draw")
        if odds_draw is None:
            odds_draw = (
                data.get("odds_nspf_draw")
                or data.get("odds_spf_draw")
                or data.get("drawAward")
                or DataAdapter.to_dict(data.get("odds")).get("draw")
            )

        fixture_id = (
            data.get("fixture_id")
            or data.get("match_id")
            or data.get("source_match_id")
            or data.get("id")
            or data.get("mid")
        )

        return {
            "source": str(source or "500"),
            "fixture_id": str(fixture_id) if fixture_id else None,
            "match_id": data.get("match_id"),
            "home_team": data.get("home_team") or data.get("homeTeam"),
            "away_team": data.get("away_team") or data.get("awayTeam") or data.get("guestTeam"),
            "odds_draw": odds_draw,
            "captured_at": DataAdapter.parse_datetime(data.get("captured_at") or data.get("capture_time") or data.get("odds_update_time")),
            "kickoff_time": DataAdapter.parse_datetime(data.get("kickoff_time") or data.get("match_time") or data.get("matchTimeStr")),
            "raw_payload": data,
        }

    @staticmethod
    def resolve_internal_match_id(
        db: Session,
        source: str,
        normalized_payload: Dict[str, Any],
    ) -> Tuple[Optional[str], float, str]:
        source = str(source or "500")
        external_id = str(normalized_payload.get("fixture_id") or "").strip()

        if external_id:
            mapping = (
                db.query(ExternalSourceMapping)
                .filter(ExternalSourceMapping.source == source)
                .filter(ExternalSourceMapping.external_id == external_id)
                .first()
            )
            if mapping and mapping.internal_match_id:
                return mapping.internal_match_id, float(mapping.confidence_score or 1.0), "mapping_table"

        match_id = normalized_payload.get("match_id")
        if match_id:
            return str(match_id), 1.0, "payload_match_id"

        if external_id:
            by_source_id = (
                db.query(Match)
                .filter(Match.source_match_id == external_id)
                .order_by(Match.id.desc())
                .first()
            )
            if by_source_id and by_source_id.match_identifier:
                return str(by_source_id.match_identifier), 0.98, "source_match_id"

        home_name = DataAdapter.normalize_team_name(normalized_payload.get("home_team"))
        away_name = DataAdapter.normalize_team_name(normalized_payload.get("away_team"))
        kickoff = normalized_payload.get("kickoff_time")

        if home_name and away_name and isinstance(kickoff, datetime):
            start = kickoff - timedelta(hours=6)
            end = kickoff + timedelta(hours=6)
            candidates = (
                db.query(Match)
                .filter(Match.scheduled_kickoff >= start)
                .filter(Match.scheduled_kickoff <= end)
                .order_by(Match.scheduled_kickoff.asc())
                .limit(200)
                .all()
            )
            for candidate in candidates:
                attrs = DataAdapter.to_dict(getattr(candidate, "source_attributes", None))
                c_home = DataAdapter.normalize_team_name(
                    attrs.get("home_team") or attrs.get("homeTeam") or attrs.get("hostName")
                )
                c_away = DataAdapter.normalize_team_name(
                    attrs.get("away_team") or attrs.get("awayTeam") or attrs.get("guestName")
                )
                if c_home == home_name and c_away == away_name:
                    return str(candidate.match_identifier), 0.82, "fuzzy_team_time"

        return None, 0.0, "unresolved"

    @staticmethod
    def upsert_external_mapping(
        db: Session,
        source: str,
        external_id: Optional[str],
        internal_match_id: Optional[str],
        confidence_score: float,
        mapping_meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not external_id or not internal_match_id:
            return

        row = (
            db.query(ExternalSourceMapping)
            .filter(ExternalSourceMapping.source == source)
            .filter(ExternalSourceMapping.external_id == external_id)
            .first()
        )
        if not row:
            row = ExternalSourceMapping(
                source=source,
                external_id=external_id,
                internal_match_id=internal_match_id,
                confidence_score=confidence_score,
                mapping_meta=mapping_meta or {},
                verified=1 if confidence_score >= 0.95 else 0,
            )
            db.add(row)
            return

        row.internal_match_id = internal_match_id
        row.confidence_score = confidence_score
        row.mapping_meta = mapping_meta or row.mapping_meta
        if confidence_score >= 0.95:
            row.verified = 1
