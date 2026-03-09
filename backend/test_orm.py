#!/usr/bin/env python3
"""
Legacy ORM quick check script.
"""

from __future__ import annotations

from datetime import datetime

from database import SessionLocal
from models.matches import FootballMatch

__test__ = False


def run_orm_check() -> int:
    db = SessionLocal()
    try:
        matches = db.query(FootballMatch).all()
        print(f"ORM query - total records: {len(matches)}")

        new_match = FootballMatch(
            match_id="test_orm_002",
            home_team="ORM Home",
            away_team="ORM Away",
            match_time=datetime(2026, 2, 7, 21, 0, 0),
            league="ORM League",
            status="pending",
        )
        db.add(new_match)
        db.commit()
        print("ORM insert successful")
    except Exception as exc:  # pragma: no cover - diagnostic script
        db.rollback()
        print(f"ORM error: {exc}")
        return 1
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(run_orm_check())
