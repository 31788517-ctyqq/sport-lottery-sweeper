"""
Compatibility odds endpoints mounted under /api/v1/admin/odds.
These routes keep admin menu pages working even when legacy odds routers
are not registered in main.py.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, aliased

from backend.database import get_db
from backend.models.match import League, Match, Team
from backend.models.odds import Bookmaker, Odds

logger = logging.getLogger(__name__)
router = APIRouter()


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def _success(data: dict, message: str = "ok") -> dict:
    return {"success": True, "data": data, "message": message}


@router.get("/stats")
def get_odds_stats(db: Session = Depends(get_db)):
    try:
        now = datetime.utcnow()
        since = now - timedelta(days=1)

        total_odds = db.query(func.count(Odds.id)).scalar() or 0
        monitored_matches = (
            db.query(func.count(func.distinct(Odds.match_id)))
            .filter(Odds.last_updated >= since)
            .scalar()
            or 0
        )
        anomalies_detected = (
            db.query(func.count(Odds.id)).filter(Odds.volatility > 0.1).scalar() or 0
        )
        changes_today_avg = (
            db.query(func.avg(Odds.volatility)).filter(Odds.last_updated >= since).scalar()
            or 0
        )

        return _success(
            {
                "totalOdds": int(total_odds),
                "monitoredMatches": int(monitored_matches),
                "anomaliesDetected": int(anomalies_detected),
                "changesToday": round(float(changes_today_avg) * 100, 1),
            },
            "获取赔率统计成功",
        )
    except Exception:
        logger.exception("odds stats query failed; returning fallback")
        return _success(
            {
                "totalOdds": 0,
                "monitoredMatches": 0,
                "anomaliesDetected": 0,
                "changesToday": 0,
            },
            "赔率统计降级返回",
        )


@router.get("/monitoring")
def get_odds_monitoring(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    league: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        home_team = aliased(Team)
        away_team = aliased(Team)

        latest_subquery = (
            db.query(
                Odds.match_id.label("match_id"),
                Odds.bookmaker_id.label("bookmaker_id"),
                func.max(Odds.last_updated).label("max_update"),
            )
            .group_by(Odds.match_id, Odds.bookmaker_id)
            .subquery()
        )

        query = (
            db.query(Odds, Match, League, home_team, away_team, Bookmaker)
            .join(
                latest_subquery,
                and_(
                    Odds.match_id == latest_subquery.c.match_id,
                    Odds.bookmaker_id == latest_subquery.c.bookmaker_id,
                    Odds.last_updated == latest_subquery.c.max_update,
                ),
            )
            .join(Match, Odds.match_id == Match.id)
            .outerjoin(League, Match.league_id == League.id)
            .outerjoin(home_team, Match.home_team_id == home_team.id)
            .outerjoin(away_team, Match.away_team_id == away_team.id)
            .outerjoin(Bookmaker, Odds.bookmaker_id == Bookmaker.id)
        )

        if league:
            trimmed = league.strip()
            if trimmed.isdigit():
                query = query.filter(Match.league_id == int(trimmed))
            else:
                like_pattern = f"%{trimmed}%"
                query = query.filter(
                    (League.name.ilike(like_pattern)) | (League.code.ilike(like_pattern))
                )

        from_date = _parse_date(date_from)
        if from_date:
            query = query.filter(Match.match_date >= from_date.date())
        to_date = _parse_date(date_to)
        if to_date:
            query = query.filter(Match.match_date <= to_date.date())

        total = query.count()
        rows = (
            query.order_by(desc(Odds.last_updated))
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        items = []
        for odds_row, match_row, league_row, home_row, away_row, bookmaker_row in rows:
            items.append(
                {
                    "matchId": f"M{odds_row.match_id}",
                    "homeTeam": getattr(home_row, "name", None) or "未知",
                    "awayTeam": getattr(away_row, "name", None) or "未知",
                    "league": getattr(league_row, "name", None) or "未知",
                    "bookmaker": getattr(bookmaker_row, "name", None) or "未知",
                    "odds": {
                        "win": odds_row.home_win_odds,
                        "draw": odds_row.draw_odds,
                        "lose": odds_row.away_win_odds,
                    },
                    "oddsChanged": {"win": False, "draw": False, "lose": False},
                    "lastUpdate": odds_row.last_updated.strftime("%Y-%m-%d %H:%M:%S")
                    if odds_row.last_updated
                    else "",
                }
            )

        return _success(
            {
                "items": items,
                "total": int(total),
                "page": page,
                "size": size,
                "pages": (int(total) + size - 1) // size if size else 0,
            },
            "获取赔率监控数据成功",
        )
    except Exception:
        logger.exception("odds monitoring query failed; returning fallback")
        return _success(
            {"items": [], "total": 0, "page": page, "size": size, "pages": 0},
            "赔率监控降级返回",
        )


@router.get("/history")
def get_odds_history(
    match_id: Optional[int] = Query(None),
    time_from: Optional[str] = Query(None),
    time_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Odds)

        if match_id:
            query = query.filter(Odds.match_id == match_id)

        from_time = _parse_date(time_from)
        if from_time:
            query = query.filter(Odds.last_updated >= from_time)
        to_time = _parse_date(time_to)
        if to_time:
            query = query.filter(Odds.last_updated <= to_time)

        rows = query.order_by(Odds.last_updated.asc()).limit(500).all()

        items = []
        previous_value = None
        for row in rows:
            current_value = float(row.home_win_odds or 0)
            change = round(current_value - previous_value, 2) if previous_value is not None else 0
            previous_value = current_value
            items.append(
                {
                    "timestamp": row.last_updated.strftime("%Y-%m-%d %H:%M:%S")
                    if row.last_updated
                    else "",
                    "winOdds": row.home_win_odds,
                    "drawOdds": row.draw_odds,
                    "loseOdds": row.away_win_odds,
                    "change": change,
                    "totalStakes": row.volume or 0,
                }
            )

        return _success({"items": items, "matchId": match_id}, "获取赔率历史成功")
    except Exception:
        logger.exception("odds history query failed; returning fallback")
        return _success({"items": [], "matchId": match_id}, "赔率历史降级返回")


@router.get("/anomalies")
def get_odds_anomalies(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    anomaly_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        home_team = aliased(Team)
        away_team = aliased(Team)

        query = (
            db.query(Odds, Match, home_team, away_team)
            .join(Match, Odds.match_id == Match.id)
            .outerjoin(home_team, Match.home_team_id == home_team.id)
            .outerjoin(away_team, Match.away_team_id == away_team.id)
        )

        # Basic anomaly threshold
        query = query.filter(Odds.volatility > 0.05)

        if anomaly_type == "sharp_change":
            query = query.filter(Odds.volatility > 0.1)
        elif anomaly_type == "abnormal_fluctuation":
            query = query.filter(Odds.volatility > 0.08)

        if severity == "high":
            query = query.filter(Odds.volatility > 0.15)
        elif severity == "medium":
            query = query.filter(and_(Odds.volatility > 0.1, Odds.volatility <= 0.15))
        elif severity == "low":
            query = query.filter(and_(Odds.volatility > 0.05, Odds.volatility <= 0.1))

        total = query.count()
        rows = (
            query.order_by(desc(Odds.volatility), desc(Odds.last_updated))
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        items = []
        for odds_row, match_row, home_row, away_row in rows:
            volatility = float(odds_row.volatility or 0)
            if volatility > 0.15:
                sev = "high"
                sev_text = "高"
            elif volatility > 0.1:
                sev = "medium"
                sev_text = "中"
            else:
                sev = "low"
                sev_text = "低"

            detected_type = (
                "sharp_change" if volatility > 0.1 else (anomaly_type or "abnormal_fluctuation")
            )
            items.append(
                {
                    "id": f"A{odds_row.id}",
                    "matchId": f"M{odds_row.match_id}",
                    "homeTeam": getattr(home_row, "name", None) or "未知",
                    "awayTeam": getattr(away_row, "name", None) or "未知",
                    "type": detected_type,
                    "severity": sev,
                    "severityText": sev_text,
                    "description": f"赔率波动值达到 {volatility:.3f}",
                    "detectedTime": odds_row.last_updated.strftime("%Y-%m-%d %H:%M:%S")
                    if odds_row.last_updated
                    else "",
                }
            )

        return _success(
            {
                "items": items,
                "total": int(total),
                "page": page,
                "size": size,
                "pages": (int(total) + size - 1) // size if size else 0,
            },
            "获取异常赔率成功",
        )
    except Exception:
        logger.exception("odds anomalies query failed; returning fallback")
        return _success(
            {"items": [], "total": 0, "page": page, "size": size, "pages": 0},
            "异常赔率降级返回",
        )
