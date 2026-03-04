from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import json

from sqlalchemy import and_, func, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models.bet_suggestion import BetSuggestion
from backend.models.draw_prediction_result import DrawPredictionResult
from backend.models.match import Match
from backend.models.odds_snapshot import OddsSnapshot
from backend.models.paper_bet import PaperBet
from backend.models.risk_killswitch_state import RiskKillSwitchState
from backend.models.system_config import SystemConfig


DEFAULT_CONFIG: Dict[str, Any] = {
    "draw_suggestion_fee_rate": 0.08,
    "draw_suggestion_rebate_rate": 0.75,
    "draw_suggestion_rebate_mode": "on_win_stake",
    "draw_suggestion_edge_min": 0.03,
    "draw_suggestion_edge_full": 0.10,
    "draw_timing_windows_by_league": {"global": {"min_hours": 2, "max_hours": 6}},
    "killswitch_thresholds": {
        "warn": {"roi_7d": -0.08, "max_drawdown": 0.20},
        "stop": {"roi_7d": -0.15, "rolling_clv_50": 0.0, "max_drawdown": 0.30},
    },
}


class DrawSuggestionCalculator:
    @staticmethod
    def implied_prob(odds_draw: Optional[float]) -> Optional[float]:
        if not odds_draw or odds_draw <= 0:
            return None
        return 1.0 / odds_draw

    @staticmethod
    def edge(base_prob: Optional[float], implied_prob: Optional[float]) -> Optional[float]:
        if base_prob is None or implied_prob is None:
            return None
        return float(base_prob) - float(implied_prob)

    @staticmethod
    def stake_pct(edge: Optional[float], edge_min: float, edge_full: float) -> float:
        if edge is None or edge <= edge_min:
            return 0.0
        if edge >= edge_full:
            return 1.0
        return max(0.0, min(1.0, (edge - edge_min) / max(edge_full - edge_min, 1e-6)))

    @staticmethod
    def calculate_settlement(
        stake: float,
        odds_draw_place: Optional[float],
        fee_rate: float,
        rebate_rate: float,
        actual_result: str,
    ) -> Tuple[float, float, int]:
        stake = float(stake or 1.0)
        if actual_result == "void":
            return 0.0, 0.0, 0

        if actual_result == "draw":
            odds = float(odds_draw_place or 0.0)
            pnl = stake * ((odds - 1.0) * (1.0 - fee_rate) + rebate_rate)
            roi = pnl / stake if stake else 0.0
            return pnl, roi, 1

        pnl = -stake * (1.0 + fee_rate)
        roi = pnl / stake if stake else 0.0
        return pnl, roi, 0


class DrawSuggestionService:
    _config_cache: Dict[str, Tuple[datetime, Any]] = {}
    _config_ttl_seconds: int = 60

    @staticmethod
    def _ensure_killswitch_table(db: Session) -> None:
        bind = db.get_bind()
        if bind is None:
            return
        inspector = inspect(bind)
        if not inspector.has_table(RiskKillSwitchState.__tablename__):
            RiskKillSwitchState.__table__.create(bind=bind, checkfirst=True)

    @staticmethod
    def _ensure_required_tables(db: Session) -> None:
        bind = db.get_bind()
        if bind is None:
            return
        inspector = inspect(bind)
        required_tables = [BetSuggestion.__table__, PaperBet.__table__, OddsSnapshot.__table__]
        for table in required_tables:
            if not inspector.has_table(table.name):
                table.create(bind=bind, checkfirst=True)

    @staticmethod
    def _parse_datetime(value: Any) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value
        if not value:
            return None
        text = str(value).strip()
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ):
            try:
                return datetime.strptime(text, fmt)
            except Exception:
                continue
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            return None

    @staticmethod
    def _get_system_config(db: Session, key: str, default: Any) -> Any:
        now = datetime.utcnow()
        cached = DrawSuggestionService._config_cache.get(key)
        if cached and (now - cached[0]).total_seconds() <= DrawSuggestionService._config_ttl_seconds:
            return cached[1]

        value = default
        cfg = (
            db.query(SystemConfig)
            .filter(SystemConfig.config_key == key)
            .filter(SystemConfig.is_active == True)  # noqa: E712
            .first()
        )
        if cfg and cfg.config_value is not None:
            try:
                if cfg.config_type == "json":
                    value = json.loads(cfg.config_value)
                elif cfg.config_type == "integer":
                    value = int(cfg.config_value)
                elif cfg.config_type == "boolean":
                    value = str(cfg.config_value).strip().lower() in {"1", "true", "yes", "on"}
                elif cfg.config_type in {"float", "number"}:
                    value = float(cfg.config_value)
                else:
                    if isinstance(default, (int, float)):
                        value = type(default)(cfg.config_value)
                    else:
                        value = cfg.config_value
            except Exception:
                value = default

        DrawSuggestionService._config_cache[key] = (now, value)
        return value

    @staticmethod
    def get_runtime_config(db: Session) -> Dict[str, Any]:
        fee_rate = float(DrawSuggestionService._get_system_config(db, "draw_suggestion_fee_rate", DEFAULT_CONFIG["draw_suggestion_fee_rate"]))
        rebate_rate = float(DrawSuggestionService._get_system_config(db, "draw_suggestion_rebate_rate", DEFAULT_CONFIG["draw_suggestion_rebate_rate"]))
        rebate_mode = str(DrawSuggestionService._get_system_config(db, "draw_suggestion_rebate_mode", DEFAULT_CONFIG["draw_suggestion_rebate_mode"]))
        edge_min = float(DrawSuggestionService._get_system_config(db, "draw_suggestion_edge_min", DEFAULT_CONFIG["draw_suggestion_edge_min"]))
        edge_full = float(DrawSuggestionService._get_system_config(db, "draw_suggestion_edge_full", DEFAULT_CONFIG["draw_suggestion_edge_full"]))
        windows = DrawSuggestionService._get_system_config(
            db,
            "draw_timing_windows_by_league",
            DEFAULT_CONFIG["draw_timing_windows_by_league"],
        )
        thresholds = DrawSuggestionService._get_system_config(
            db,
            "killswitch_thresholds",
            DEFAULT_CONFIG["killswitch_thresholds"],
        )

        if not isinstance(windows, dict):
            windows = DEFAULT_CONFIG["draw_timing_windows_by_league"]
        if not isinstance(thresholds, dict):
            thresholds = DEFAULT_CONFIG["killswitch_thresholds"]

        return {
            "fee_rate": max(0.0, min(0.2, fee_rate)),
            "rebate_rate": max(0.0, min(1.0, rebate_rate)),
            "rebate_mode": rebate_mode,
            "edge_min": max(0.0, min(0.2, edge_min)),
            "edge_full": max(edge_min + 0.001, min(0.3, edge_full)),
            "windows": windows,
            "killswitch_thresholds": thresholds,
        }

    @staticmethod
    def _resolve_kickoff(match: Match) -> Optional[datetime]:
        if getattr(match, "scheduled_kickoff", None):
            return match.scheduled_kickoff
        if getattr(match, "match_date", None) is not None and getattr(match, "match_time", None) is not None:
            return datetime.combine(match.match_date, match.match_time)
        return None

    @staticmethod
    def _window_for_match(config: Dict[str, Any], match: Match) -> Tuple[int, int]:
        windows = config.get("windows") or {}
        global_window = windows.get("global") if isinstance(windows, dict) else None
        if isinstance(global_window, dict):
            min_hours = int(global_window.get("min_hours") or 2)
            max_hours = int(global_window.get("max_hours") or 6)
            return min_hours, max_hours
        return 2, 6

    @staticmethod
    def _latest_prediction(db: Session, match_id: str) -> Optional[DrawPredictionResult]:
        return (
            db.query(DrawPredictionResult)
            .filter(DrawPredictionResult.match_id == match_id)
            .order_by(DrawPredictionResult.predicted_at.desc())
            .first()
        )

    @staticmethod
    def _latest_snapshot(db: Session, match_id: str) -> Optional[OddsSnapshot]:
        return (
            db.query(OddsSnapshot)
            .filter(OddsSnapshot.match_id == match_id)
            .order_by(OddsSnapshot.captured_at.desc())
            .first()
        )

    @staticmethod
    def _place_snapshot_in_window(db: Session, match_id: str, kickoff: datetime) -> Optional[OddsSnapshot]:
        start = kickoff - timedelta(hours=10)
        end = kickoff - timedelta(hours=1)
        return (
            db.query(OddsSnapshot)
            .filter(OddsSnapshot.match_id == match_id)
            .filter(and_(OddsSnapshot.captured_at >= start, OddsSnapshot.captured_at <= end))
            .order_by(OddsSnapshot.captured_at.desc())
            .first()
        )

    @staticmethod
    def _decision(
        base_prob: Optional[float],
        odds_draw_place: Optional[float],
        kickoff_time: Optional[datetime],
        now_time: datetime,
        killswitch_state: str,
        edge_min: float,
        edge_full: float,
        min_hours: int,
        max_hours: int,
    ) -> Dict[str, Any]:
        reason_codes: List[str] = []

        if base_prob is None:
            reason_codes.append("missing_base_prob")
        if odds_draw_place is None:
            reason_codes.append("missing_odds_draw_place")
        if kickoff_time is None:
            reason_codes.append("missing_kickoff_time")

        implied = DrawSuggestionCalculator.implied_prob(odds_draw_place)
        edge = DrawSuggestionCalculator.edge(base_prob, implied)
        stake_pct = DrawSuggestionCalculator.stake_pct(edge, edge_min=edge_min, edge_full=edge_full)

        hours_to_kickoff = None
        if kickoff_time:
            hours_to_kickoff = (kickoff_time - now_time).total_seconds() / 3600.0
            if hours_to_kickoff < min_hours or hours_to_kickoff > max_hours:
                reason_codes.append("out_of_window")

        if edge is None or edge < edge_min:
            reason_codes.append("edge_low")

        if killswitch_state == "STOP":
            reason_codes.append("killswitch_stop")

        decision = "BET"
        if reason_codes:
            decision = "SKIP"
            stake_pct = 0.0

        return {
            "decision": decision,
            "implied_prob": implied,
            "edge": edge,
            "stake_pct": stake_pct,
            "hours_to_kickoff": hours_to_kickoff,
            "reason_codes": reason_codes,
        }

    @staticmethod
    def create_suggestion(db: Session, payload: Dict[str, Any], commit: bool = True) -> BetSuggestion:
        config = DrawSuggestionService.get_runtime_config(db)
        now_time = datetime.utcnow()

        kickoff_time = payload.get("kickoff_time")
        if not isinstance(kickoff_time, datetime):
            kickoff_time = DrawSuggestionService._parse_datetime(kickoff_time)

        min_hours, max_hours = DrawSuggestionService._window_for_match(config, payload.get("match") or Match())
        computed = DrawSuggestionService._decision(
            base_prob=payload.get("base_prob"),
            odds_draw_place=payload.get("odds_draw_place"),
            kickoff_time=kickoff_time,
            now_time=now_time,
            killswitch_state=payload.get("killswitch_state") or "RUN",
            edge_min=config["edge_min"],
            edge_full=config["edge_full"],
            min_hours=min_hours,
            max_hours=max_hours,
        )

        row = BetSuggestion(
            match_id=str(payload.get("match_id") or ""),
            decision=computed["decision"],
            stake_pct=computed["stake_pct"],
            edge=computed["edge"],
            base_prob=payload.get("base_prob"),
            implied_prob=computed["implied_prob"],
            odds_draw_place=payload.get("odds_draw_place"),
            odds_draw_close=payload.get("odds_draw_close"),
            clv=(payload.get("odds_draw_close") - payload.get("odds_draw_place")) if payload.get("odds_draw_close") and payload.get("odds_draw_place") else None,
            window_min_hours=min_hours,
            window_max_hours=max_hours,
            hours_to_kickoff=computed["hours_to_kickoff"],
            reason_codes=computed["reason_codes"],
            reason_text=payload.get("reason_text") or ",".join(computed["reason_codes"]),
            features=payload.get("features") if isinstance(payload.get("features"), dict) else {},
            killswitch_state=payload.get("killswitch_state") or "RUN",
            regime_label=payload.get("regime_label"),
            created_at=now_time,
        )
        db.add(row)
        if commit:
            db.commit()
            db.refresh(row)
        return row

    @staticmethod
    def generate_suggestions_for_date(db: Session, target_date: date, force: bool = False) -> Dict[str, Any]:
        DrawSuggestionService._ensure_required_tables(db)
        killswitch_state = DrawSuggestionService.evaluate_and_apply_killswitch(db).get("state", "RUN")

        matches = (
            db.query(Match)
            .filter(Match.match_date == target_date)
            .filter(Match.is_deleted == False)  # noqa: E712
            .all()
        )

        created_ids: List[int] = []
        skipped = 0

        for match in matches:
            match_id = str(match.match_identifier)
            if not force:
                exists = (
                    db.query(BetSuggestion.id)
                    .filter(BetSuggestion.match_id == match_id)
                    .filter(BetSuggestion.created_at >= datetime.combine(target_date, datetime.min.time()))
                    .filter(BetSuggestion.created_at <= datetime.combine(target_date, datetime.max.time()))
                    .first()
                )
                if exists:
                    skipped += 1
                    continue

            kickoff = DrawSuggestionService._resolve_kickoff(match)
            prediction = DrawSuggestionService._latest_prediction(db, match_id)
            place_snapshot = DrawSuggestionService._place_snapshot_in_window(db, match_id, kickoff) if kickoff else None
            close_snapshot = DrawSuggestionService._latest_snapshot(db, match_id)

            base_prob = float(prediction.predicted_draw_prob) if prediction and prediction.predicted_draw_prob is not None else None
            odds_draw_place = float(place_snapshot.odds_draw) if place_snapshot else None
            odds_draw_close = float(close_snapshot.odds_draw) if close_snapshot else None

            row = DrawSuggestionService.create_suggestion(
                db,
                {
                    "match_id": match_id,
                    "base_prob": base_prob,
                    "odds_draw_place": odds_draw_place,
                    "odds_draw_close": odds_draw_close,
                    "kickoff_time": kickoff,
                    "killswitch_state": killswitch_state,
                    "match": match,
                    "features": {
                        "prediction_id": prediction.id if prediction else None,
                        "place_snapshot_id": place_snapshot.id if place_snapshot else None,
                        "close_snapshot_id": close_snapshot.id if close_snapshot else None,
                    },
                },
                commit=False,
            )
            db.flush()
            created_ids.append(int(row.id))

        db.commit()

        return {
            "date": target_date.isoformat(),
            "killswitch_state": killswitch_state,
            "total_matches": len(matches),
            "created_count": len(created_ids),
            "skipped_count": skipped,
            "ids": created_ids,
        }

    @staticmethod
    def list_suggestions(db: Session, date_str: Optional[str] = None, decision: Optional[str] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        DrawSuggestionService._ensure_required_tables(db)
        q = db.query(BetSuggestion)
        if decision:
            q = q.filter(BetSuggestion.decision == decision)
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                q = q.filter(BetSuggestion.created_at >= datetime.combine(target_date, datetime.min.time()))
                q = q.filter(BetSuggestion.created_at < datetime.combine(target_date, datetime.max.time()))
            except Exception:
                pass
        total = q.count()
        rows: List[BetSuggestion] = (
            q.order_by(BetSuggestion.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": [
                {
                    "id": r.id,
                    "match_id": r.match_id,
                    "decision": r.decision,
                    "stake_pct": r.stake_pct,
                    "edge": r.edge,
                    "reason_codes": r.reason_codes or [],
                    "killswitch_state": r.killswitch_state,
                    "created_at": r.created_at,
                }
                for r in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    def get_suggestion(db: Session, suggestion_id: int) -> Optional[BetSuggestion]:
        return db.query(BetSuggestion).filter(BetSuggestion.id == suggestion_id).first()

    @staticmethod
    def create_paper_bets(db: Session, suggestion_ids: List[int]) -> Dict[str, Any]:
        DrawSuggestionService._ensure_required_tables(db)
        created_ids: List[int] = []
        runtime = DrawSuggestionService.get_runtime_config(db)

        suggestions = (
            db.query(BetSuggestion)
            .filter(BetSuggestion.id.in_([int(s) for s in suggestion_ids]))
            .all()
        )
        suggestion_map = {int(s.id): s for s in suggestions}

        for sid in suggestion_ids:
            sid_int = int(sid)
            suggestion = suggestion_map.get(sid_int)
            if not suggestion:
                continue
            if suggestion.decision != "BET":
                continue

            exists = db.query(PaperBet.id).filter(PaperBet.suggestion_id == sid_int).first()
            if exists:
                continue

            pb = PaperBet(
                suggestion_id=sid_int,
                stake=1.0,
                fee_rate=runtime["fee_rate"],
                rebate_rate=runtime["rebate_rate"],
                rebate_mode=runtime["rebate_mode"],
                status="OPEN",
            )
            db.add(pb)
            db.flush()
            created_ids.append(int(pb.id))

        db.commit()
        return {"created_count": len(created_ids), "ids": created_ids}

    @staticmethod
    def settle_paper_bets(
        db: Session,
        target_date: Optional[date] = None,
        overdue_hours: int = 4,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        DrawSuggestionService._ensure_required_tables(db)
        runtime = DrawSuggestionService.get_runtime_config(db)

        q = (
            db.query(PaperBet, BetSuggestion)
            .join(BetSuggestion, BetSuggestion.id == PaperBet.suggestion_id)
            .filter(PaperBet.status == "OPEN")
            .order_by(PaperBet.created_at.asc())
        )
        if target_date:
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date, datetime.max.time())
            q = q.filter(and_(BetSuggestion.created_at >= start, BetSuggestion.created_at <= end))

        rows = q.limit(limit).all()

        settled = 0
        unresolved = 0
        voided = 0

        now = datetime.utcnow()

        for pb, suggestion in rows:
            match = db.query(Match).filter(Match.match_identifier == suggestion.match_id).first()
            if not match:
                unresolved += 1
                continue

            kickoff = DrawSuggestionService._resolve_kickoff(match)
            status_val = getattr(match, "status", None)
            status_text = status_val.value if hasattr(status_val, "value") else str(status_val or "")

            actual_result: Optional[str] = None
            if status_text in {"postponed", "cancelled", "abandoned", "suspended"}:
                actual_result = "void"
            elif match.home_score is not None and match.away_score is not None:
                if int(match.home_score) == int(match.away_score):
                    actual_result = "draw"
                elif int(match.home_score) > int(match.away_score):
                    actual_result = "home"
                else:
                    actual_result = "away"
            elif kickoff and now - kickoff >= timedelta(hours=overdue_hours):
                unresolved += 1
                continue
            else:
                unresolved += 1
                continue

            pnl, roi, is_win = DrawSuggestionCalculator.calculate_settlement(
                stake=float(pb.stake or 1.0),
                odds_draw_place=suggestion.odds_draw_place,
                fee_rate=float(pb.fee_rate if pb.fee_rate is not None else runtime["fee_rate"]),
                rebate_rate=float(pb.rebate_rate if pb.rebate_rate is not None else runtime["rebate_rate"]),
                actual_result=actual_result,
            )

            pb.actual_result = actual_result
            pb.is_win = is_win
            pb.pnl = pnl
            pb.roi = roi
            pb.settled_at = now
            if actual_result == "void":
                pb.status = "VOID"
                voided += 1
            else:
                pb.status = "SETTLED"
            settled += 1

        db.commit()

        return {
            "target_date": target_date.isoformat() if target_date else None,
            "checked": len(rows),
            "settled": settled,
            "voided": voided,
            "unresolved": unresolved,
        }

    @staticmethod
    def _calculate_max_drawdown(pnls: List[float]) -> float:
        peak = 0.0
        cum = 0.0
        max_dd = 0.0
        for p in pnls:
            cum += float(p or 0.0)
            peak = max(peak, cum)
            drawdown = peak - cum
            max_dd = max(max_dd, drawdown)
        return max_dd

    @staticmethod
    def get_metrics_summary(db: Session, days: int = 7) -> Dict[str, Any]:
        DrawSuggestionService._ensure_required_tables(db)
        since = datetime.utcnow() - timedelta(days=days)
        rows = (
            db.query(PaperBet)
            .filter(PaperBet.status.in_(["SETTLED", "VOID"]))
            .filter(PaperBet.settled_at >= since)
            .order_by(PaperBet.settled_at.asc())
            .all()
        )

        pnl_sum = sum(float(r.pnl or 0.0) for r in rows)
        stake_sum = sum(float(r.stake or 1.0) for r in rows)
        roi_7d = (pnl_sum / stake_sum) if stake_sum else 0.0

        settled_non_void = [r for r in rows if r.status == "SETTLED"]
        wins = [r for r in settled_non_void if int(r.is_win or 0) == 1]
        win_rate = (len(wins) / len(settled_non_void)) if settled_non_void else 0.0

        max_drawdown = DrawSuggestionService._calculate_max_drawdown([float(r.pnl or 0.0) for r in rows])

        clv_rows = (
            db.query(BetSuggestion.clv)
            .filter(BetSuggestion.clv.isnot(None))
            .order_by(BetSuggestion.created_at.desc())
            .limit(50)
            .all()
        )
        clv_values = [float(row[0]) for row in clv_rows if row and row[0] is not None]
        clv_50 = (sum(clv_values) / len(clv_values)) if clv_values else 0.0

        state = DrawSuggestionService.evaluate_and_apply_killswitch(db).get("state", "RUN")

        return {
            "roi_7d": round(roi_7d, 6),
            "max_drawdown": round(max_drawdown, 6),
            "win_rate": round(win_rate, 6),
            "clv_50": round(clv_50, 6),
            "rolling_clv_50": round(clv_50, 6),
            "state": state,
            "days": days,
            "settled_count": len(settled_non_void),
        }

    @staticmethod
    def evaluate_and_apply_killswitch(db: Session, force: bool = False) -> Dict[str, Any]:
        try:
            DrawSuggestionService._ensure_killswitch_table(db)
            latest = db.query(RiskKillSwitchState).order_by(RiskKillSwitchState.id.desc()).first()
        except SQLAlchemyError:
            return {
                "state": "RUN",
                "reason": {"mode": "degraded", "message": "killswitch storage unavailable"},
                "manual_override": 0,
                "updated_at": datetime.utcnow(),
            }
        if latest and int(latest.manual_override or 0) == 1 and not force:
            return {
                "state": latest.state,
                "reason": latest.reason_json,
                "manual_override": latest.manual_override,
                "updated_at": latest.created_at,
            }

        runtime = DrawSuggestionService.get_runtime_config(db)
        thresholds = runtime.get("killswitch_thresholds") or DEFAULT_CONFIG["killswitch_thresholds"]
        warn_cfg = thresholds.get("warn") if isinstance(thresholds, dict) else {}
        stop_cfg = thresholds.get("stop") if isinstance(thresholds, dict) else {}

        metrics = DrawSuggestionService.get_metrics_summary_without_state(db, days=7)
        roi_7d = float(metrics.get("roi_7d") or 0.0)
        max_drawdown = float(metrics.get("max_drawdown") or 0.0)
        clv_50 = float(metrics.get("rolling_clv_50") or 0.0)

        new_state = "RUN"
        if (
            roi_7d < float(stop_cfg.get("roi_7d", -0.15))
            or clv_50 < float(stop_cfg.get("rolling_clv_50", 0.0))
            or max_drawdown > float(stop_cfg.get("max_drawdown", 0.30))
        ):
            new_state = "STOP"
        elif (
            roi_7d < float(warn_cfg.get("roi_7d", -0.08))
            or max_drawdown > float(warn_cfg.get("max_drawdown", 0.20))
        ):
            new_state = "WARN"

        if not latest or latest.state != new_state or int(latest.manual_override or 0) == 1:
            row = RiskKillSwitchState(
                state=new_state,
                reason_json={
                    "metrics": metrics,
                    "thresholds": thresholds,
                    "mode": "auto",
                },
                manual_override=0,
                operator=None,
                operator_note=None,
                triggered_at=datetime.utcnow() if new_state == "STOP" else None,
                released_at=datetime.utcnow() if new_state == "RUN" else None,
                created_at=datetime.utcnow(),
            )
            db.add(row)
            db.commit()
            latest = row

        return {
            "state": latest.state if latest else new_state,
            "reason": latest.reason_json if latest else {"metrics": metrics},
            "manual_override": latest.manual_override if latest else 0,
            "updated_at": latest.created_at if latest else datetime.utcnow(),
        }

    @staticmethod
    def get_metrics_summary_without_state(db: Session, days: int = 7) -> Dict[str, Any]:
        DrawSuggestionService._ensure_required_tables(db)
        since = datetime.utcnow() - timedelta(days=days)
        rows = (
            db.query(PaperBet)
            .filter(PaperBet.status.in_(["SETTLED", "VOID"]))
            .filter(PaperBet.settled_at >= since)
            .order_by(PaperBet.settled_at.asc())
            .all()
        )

        pnl_sum = sum(float(r.pnl or 0.0) for r in rows)
        stake_sum = sum(float(r.stake or 1.0) for r in rows)
        roi_7d = (pnl_sum / stake_sum) if stake_sum else 0.0
        max_drawdown = DrawSuggestionService._calculate_max_drawdown([float(r.pnl or 0.0) for r in rows])

        clv_rows = (
            db.query(BetSuggestion.clv)
            .filter(BetSuggestion.clv.isnot(None))
            .order_by(BetSuggestion.created_at.desc())
            .limit(50)
            .all()
        )
        clv_values = [float(row[0]) for row in clv_rows if row and row[0] is not None]
        clv_50 = (sum(clv_values) / len(clv_values)) if clv_values else 0.0

        settled_non_void = [r for r in rows if r.status == "SETTLED"]
        wins = [r for r in settled_non_void if int(r.is_win or 0) == 1]
        win_rate = (len(wins) / len(settled_non_void)) if settled_non_void else 0.0

        return {
            "roi_7d": round(roi_7d, 6),
            "max_drawdown": round(max_drawdown, 6),
            "rolling_clv_50": round(clv_50, 6),
            "clv_50": round(clv_50, 6),
            "win_rate": round(win_rate, 6),
            "days": days,
        }

    @staticmethod
    def get_killswitch_state(db: Session) -> Dict[str, Any]:
        return DrawSuggestionService.evaluate_and_apply_killswitch(db)

    @staticmethod
    def set_killswitch_state(db: Session, state: str, operator: Optional[str], note: Optional[str], manual_override: int = 1) -> Dict[str, Any]:
        DrawSuggestionService._ensure_killswitch_table(db)

        normalized = (state or "RUN").upper()
        if normalized not in {"RUN", "WARN", "STOP"}:
            normalized = "RUN"

        row = RiskKillSwitchState(
            state=normalized,
            reason_json={"note": note, "mode": "manual"} if note else {"mode": "manual"},
            manual_override=manual_override,
            operator=operator,
            operator_note=note,
            triggered_at=datetime.utcnow() if normalized == "STOP" else None,
            released_at=datetime.utcnow() if normalized == "RUN" else None,
            created_at=datetime.utcnow(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return {"ok": True, "state": row.state}
