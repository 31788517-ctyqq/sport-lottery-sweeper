#!/usr/bin/env python3
"""
Backfill 100qiu raw payload into football_matches.source_attributes.
"""
import argparse
import json
import re
import sys
from typing import Any, Dict, List

import requests

from backend.database import SessionLocal
from backend.models.data_sources import DataSource
from backend.models.matches import FootballMatch


def build_api_url(base_url: str, date_time: str) -> str:
    if "dateTime=" in base_url:
        return re.sub(r"dateTime=\\w+", f"dateTime={date_time}", base_url)
    joiner = "&" if "?" in base_url else "?"
    return f"{base_url}{joiner}dateTime={date_time}"


def extract_matches(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "rows", "results", "items", "matches"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


def fetch_100qiu_matches(url: str) -> List[Dict[str, Any]]:
    session = requests.Session()
    session.trust_env = False
    response = session.get(url, timeout=30)
    response.raise_for_status()
    try:
        data = response.json()
    except json.JSONDecodeError:
        return []
    return extract_matches(data)


def backfill(date_time_override: str | None) -> int:
    session = SessionLocal()
    updated = 0
    skipped = 0
    try:
        sources = session.query(DataSource).all()
        if not sources:
            print("No active 100qiu data sources found.")
            return 1

        for source in sources:
            config = source.config_dict or {}
            status_val = source.status
            is_online = status_val == 1 or status_val == "online"
            is_100qiu = source.type == "100qiu" or config.get("source_type") == "100qiu"
            if not is_100qiu or not is_online:
                continue
            date_time = date_time_override or config.get("date_time")
            if not date_time or str(date_time).lower() == "latest":
                print(f"Skip source {source.id} ({source.name}): date_time missing or latest")
                continue

            if not source.url:
                print(f"Skip source {source.id} ({source.name}): url missing")
                continue

            api_url = build_api_url(source.url, str(date_time))
            matches = fetch_100qiu_matches(api_url)
            if not matches:
                print(f"No matches for source {source.id} ({source.name}) date_time={date_time}")
                continue

            for item in matches:
                line_id = str(item.get("lineId") or "").strip()
                if not line_id:
                    skipped += 1
                    continue
                match = session.query(FootballMatch).filter(FootballMatch.match_id == line_id).first()
                if not match:
                    match_time_str = item.get("matchTimeStr")
                    match_time = None
                    if isinstance(match_time_str, str) and match_time_str:
                        from datetime import datetime
                        try:
                            match_time = datetime.strptime(match_time_str, "%Y-%m-%d")
                        except ValueError:
                            match_time = None
                    if match_time is None:
                        from datetime import datetime
                        match_time = datetime.utcnow()
                    match = FootballMatch(
                        match_id=line_id,
                        home_team=item.get("homeTeam") or "未知主队",
                        away_team=item.get("guestTeam") or "未知客队",
                        league=item.get("gameShortName"),
                        match_time=match_time,
                        status="pending",
                        home_score=None,
                        away_score=None
                    )
                    match.data_source = "100qiu"
                    match.source_attributes = item
                    session.add(match)
                    updated += 1
                    continue
                match.source_attributes = item
                match.data_source = "100qiu"
                if match.home_team == "未知主队" and item.get("homeTeam"):
                    match.home_team = item.get("homeTeam")
                if match.away_team == "未知客队" and item.get("guestTeam"):
                    match.away_team = item.get("guestTeam")
                if not match.league and item.get("gameShortName"):
                    match.league = item.get("gameShortName")
                if not match.match_time:
                    match_time_str = item.get("matchTimeStr")
                    if isinstance(match_time_str, str) and match_time_str:
                        from datetime import datetime
                        try:
                            match.match_time = datetime.strptime(match_time_str, "%Y-%m-%d")
                        except ValueError:
                            pass
                    if not match.match_time:
                        from datetime import datetime
                        match.match_time = datetime.utcnow()
                updated += 1

            session.commit()
            print(f"Backfilled {updated} matches for source {source.id} ({source.name})")
        return 0
    except Exception as exc:
        session.rollback()
        print(f"Backfill failed: {exc}")
        return 1
    finally:
        session.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill 100qiu source_attributes to football_matches.")
    parser.add_argument("--date-time", dest="date_time", help="Override date_time for all sources")
    args = parser.parse_args()
    return backfill(args.date_time)


if __name__ == "__main__":
    sys.exit(main())
