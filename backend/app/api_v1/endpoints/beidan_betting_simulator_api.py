#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北单投注模拟 API"""

import re
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from itertools import combinations
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, aliased

from backend.api.dependencies import get_db, get_current_active_admin_user
import backend.crud.beidan_betting as betting_crud
from backend.models.match import Match, MatchStatusEnum, Team
from backend.schemas.beidan_betting import BettingSchemeCreate, BettingSchemeUpdate
from backend.services.beidan_data_service import BeidanDataService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["beidan-betting"])


def json_attr_text_expr(db: Session, column, key: str):
    """Extract a JSON text attribute in a dialect-safe way."""
    dialect_name = ((db.bind.dialect.name if db.bind and db.bind.dialect else "") or "").lower()
    if dialect_name.startswith("postgres"):
        return column.op("->>")(key)
    return func.json_extract(column, f"$.{key}")


def normalize_match_seq(value: str) -> Optional[str]:
    if value is None:
        return None
    digits = re.findall(r"\d+", str(value))
    if not digits:
        return None
    return str(int(digits[0]))


def normalize_result_text(text: str) -> Optional[str]:
    if text is None:
        return None
    text = str(text).strip()
    if not text:
        return None
    if text in {"胜", "主胜", "3"}:
        return "win"
    if text in {"平", "1"}:
        return "draw"
    if text in {"负", "客胜", "0"}:
        return "lose"
    if "负" in text or "客胜" in text:
        return "lose"
    if "平" in text:
        return "draw"
    if "胜" in text:
        return "win"
    return None


def normalize_attrs(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def extract_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        for key in ("text", "label", "name", "value", "statusDes", "status_des", "status"):
            if key in value and value.get(key) is not None:
                return extract_text(value.get(key))
        for nested in value.values():
            nested_text = extract_text(nested)
            if nested_text:
                return nested_text
        return ""
    if isinstance(value, (list, tuple)):
        parts = [extract_text(v) for v in value]
        parts = [p for p in parts if p]
        return "/".join(parts)
    return str(value).strip()


def normalize_score_text(value: Any) -> str:
    text = extract_text(value)
    if not text:
        return ""
    text = text.replace("：", "-").replace(":", "-")
    m = re.search(r"(\d+)\s*-\s*(\d+)", text)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return text


def normalize_handicap_text(value: Any) -> str:
    text = extract_text(value)
    if not text:
        return ""
    m = re.search(r"[-+]?\d+(?:\.\d+)?", text)
    if not m:
        return text
    try:
        number = float(m.group(0))
    except ValueError:
        return text
    if number.is_integer():
        return str(int(number))
    return str(number).rstrip("0").rstrip(".")


def normalize_odds_value(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            parsed = float(value)
            return parsed if parsed >= 0 else None
        except (TypeError, ValueError):
            return None

    text = extract_text(value)
    if not text:
        return None
    text = text.replace(",", "")
    m = re.search(r"[-+]?\d+(?:\.\d+)?", text)
    if not m:
        return None
    try:
        parsed = float(m.group(0))
        return parsed if parsed >= 0 else None
    except (TypeError, ValueError):
        return None


def first_valid_odds(*values: Any, default: float = 0.0) -> float:
    for value in values:
        parsed = normalize_odds_value(value)
        if parsed is not None:
            return parsed
    return default


def normalize_status_text(value: Any) -> str:
    text = extract_text(value)
    if not text:
        return ""
    raw = text.lower()
    if raw in {"pending", "scheduled", "not_started", "not started"} or "未开" in text:
        return "未开赛"
    if raw in {"running", "live", "inplay", "in_play"} or "进行" in text or "比赛中" in text or "中场" in text:
        return "比赛中"
    if raw in {"finished", "ended", "completed", "ft"} or "完场" in text or "已结束" in text or "已完成" in text:
        return "已完成"
    if raw in {"cancelled", "canceled", "abandoned"} or "取消" in text:
        return "已取消"
    return text


def build_score_display(score: str, half_score: str) -> str:
    full_text = score or ""
    half_text = half_score or ""
    if full_text and half_text:
        return f"{full_text} / {half_text}"
    if full_text:
        return full_text
    if half_text:
        return f"- / {half_text}"
    return "-"


def normalize_schedule_status_text(status_value: Any, status_des: Any = None) -> str:
    status_des_text = extract_text(status_des)
    if any(flag in status_des_text for flag in ("完场", "已结束", "已完成")):
        return "已完成"
    if any(flag in status_des_text for flag in ("未开", "待开", "未开赛")):
        return "未开赛"
    if any(flag in status_des_text for flag in ("中场", "上半场", "下半场", "进行", "比赛中")):
        return "比赛中"

    raw = str(status_value.value if hasattr(status_value, "value") else status_value or "").strip()
    if raw == MatchStatusEnum.FINISHED.value:
        return "已完成"
    if raw in {
        MatchStatusEnum.CANCELLED.value,
        MatchStatusEnum.ABANDONED.value,
        MatchStatusEnum.SUSPENDED.value,
    }:
        return "已完成"
    if raw in {MatchStatusEnum.LIVE.value, MatchStatusEnum.HALFTIME.value}:
        return "比赛中"
    if raw in {MatchStatusEnum.SCHEDULED.value, MatchStatusEnum.POSTPONED.value}:
        return "未开赛"
    return normalize_status_text(status_des_text or raw) or "-"


def normalize_team_name(value: Any) -> str:
    text = extract_text(value).lower()
    return re.sub(r"\s+", "", text)


def parse_match_datetime(value: Any) -> Optional[datetime]:
    text = extract_text(value)
    if not text:
        return None
    normalized = text.replace("T", " ").replace("Z", "").strip()
    normalized = re.sub(r"\.\d+$", "", normalized)
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue
    return None


def build_bd_schedule_candidates(
    db: Session,
    match_rows: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    line_keys = set()
    date_candidates = set()
    for row in match_rows:
        line_key = normalize_match_seq(row.get("lineId") or row.get("line_id") or "")
        if line_key:
            line_keys.add(line_key)
        kickoff = parse_match_datetime(row.get("matchTime"))
        if kickoff:
            date_candidates.add(kickoff.date().isoformat())
            date_candidates.add((kickoff.date() - timedelta(days=1)).isoformat())
            date_candidates.add((kickoff.date() + timedelta(days=1)).isoformat())

    if not line_keys:
        return {}

    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    number_expr = json_attr_text_expr(db, Match.source_attributes, "number")
    source_date_expr = json_attr_text_expr(db, Match.source_attributes, "source_schedule_date")

    query = (
        db.query(Match, HomeTeam, AwayTeam)
        .join(HomeTeam, Match.home_team_id == HomeTeam.id, isouter=True)
        .join(AwayTeam, Match.away_team_id == AwayTeam.id, isouter=True)
        .filter(Match.data_source == "yingqiu_bd")
        .filter(number_expr.in_(list(line_keys)))
    )
    if date_candidates:
        query = query.filter(
            or_(
                source_date_expr.in_(list(date_candidates)),
                func.date(Match.scheduled_kickoff).in_(list(date_candidates)),
            )
        )

    rows = query.all()
    candidates_by_line: Dict[str, List[Dict[str, Any]]] = {}
    for schedule_match, home_team, away_team in rows:
        attrs = normalize_attrs(schedule_match.source_attributes)
        line_key = normalize_match_seq(attrs.get("number") or attrs.get("lineId") or attrs.get("line_id"))
        if not line_key:
            continue

        status_raw = schedule_match.status.value if hasattr(schedule_match.status, "value") else schedule_match.status
        status_text = normalize_schedule_status_text(status_raw, attrs.get("status_des"))
        full_score = (
            f"{schedule_match.home_score}-{schedule_match.away_score}"
            if schedule_match.home_score is not None and schedule_match.away_score is not None
            else normalize_score_text(attrs.get("full_score") or attrs.get("score"))
        )
        halftime_score = normalize_score_text(
            schedule_match.halftime_score or attrs.get("halftime_score") or attrs.get("half_score")
        )
        handicap_text = normalize_handicap_text(attrs.get("handicap") or attrs.get("rq"))
        odds_home_win = normalize_odds_value(attrs.get("odds_nspf_win"))
        odds_draw = normalize_odds_value(attrs.get("odds_nspf_draw"))
        odds_guest_win = normalize_odds_value(attrs.get("odds_nspf_lose"))
        if odds_home_win is None:
            odds_home_win = normalize_odds_value(attrs.get("odds_win"))
        if odds_draw is None:
            odds_draw = normalize_odds_value(attrs.get("odds_draw"))
        if odds_guest_win is None:
            odds_guest_win = normalize_odds_value(attrs.get("odds_lose"))
        kickoff = schedule_match.scheduled_kickoff
        if kickoff is None and schedule_match.match_date and schedule_match.match_time:
            kickoff = datetime.combine(schedule_match.match_date, schedule_match.match_time)

        candidates_by_line.setdefault(line_key, []).append(
            {
                "id": schedule_match.id,
                "home_norm": normalize_team_name(home_team.name if home_team else ""),
                "away_norm": normalize_team_name(away_team.name if away_team else ""),
                "source_date": str(attrs.get("source_schedule_date") or "")[:10],
                "kickoff_date": kickoff.date().isoformat() if kickoff else "",
                "status": status_text or "-",
                "score": full_score or "",
                "half_score": halftime_score or "",
                "handicap": handicap_text or "",
                "odds_home_win": odds_home_win,
                "odds_draw": odds_draw,
                "odds_guest_win": odds_guest_win,
            }
        )

    return candidates_by_line


def pick_bd_schedule_candidate(
    candidates: List[Dict[str, Any]],
    home_team: Any,
    away_team: Any,
    match_time: Any,
) -> Optional[Dict[str, Any]]:
    if not candidates:
        return None

    home_norm = normalize_team_name(home_team)
    away_norm = normalize_team_name(away_team)
    kickoff = parse_match_datetime(match_time)
    target_date = kickoff.date().isoformat() if kickoff else ""
    source_date_preferred = (kickoff.date() - timedelta(days=1)).isoformat() if kickoff else ""

    def candidate_rank(item: Dict[str, Any]) -> tuple:
        team_rank = 0
        if home_norm and away_norm and item.get("home_norm") == home_norm and item.get("away_norm") == away_norm:
            team_rank = 2
        elif home_norm and away_norm and item.get("home_norm") == away_norm and item.get("away_norm") == home_norm:
            team_rank = 1

        date_rank = 0
        if target_date:
            if item.get("source_date") == source_date_preferred:
                date_rank = 3
            elif item.get("source_date") == target_date:
                date_rank = 2
            elif item.get("kickoff_date") == target_date:
                date_rank = 1

        return (team_rank, date_rank, int(item.get("id") or 0))

    return max(candidates, key=candidate_rank)


def fetch_beidan_results(expect: str) -> Dict[str, str]:
    url = f"https://zx.500.com/zqdc/kaijiang.php?playid=1&expect={expect}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results: Dict[str, str] = {}

    rows = soup.find_all("tr")
    for row in rows:
        cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
        if not cells:
            continue

        seq = None
        for cell in cells:
            if re.fullmatch(r"\d{1,3}", cell or ""):
                seq = cell
                break

        if not seq:
            continue

        result_value = None
        for cell in reversed(cells):
            result_value = normalize_result_text(cell)
            if result_value:
                break

        if result_value:
            normalized = normalize_match_seq(seq)
            if normalized:
                results[normalized] = result_value
                results[normalized.zfill(3)] = result_value
            results[seq] = result_value

    return results


def parse_pass_types(pass_types: List[int], total: int) -> List[int]:
    if not pass_types:
        return [total]
    valid = []
    for value in pass_types:
        try:
            size = int(value)
        except (TypeError, ValueError):
            continue
        if 1 < size <= total:
            valid.append(size)
    if not valid:
        return [total]
    return sorted(set(valid))


def parse_pass_type_text(pass_type: str, total: int) -> List[int]:
    if not pass_type or pass_type in {"all", "full", "全串关"}:
        return [total]
    numbers = [int(x) for x in re.findall(r"(\d+)\s*(?:x|串)", pass_type)]
    return parse_pass_types(numbers, total)


def build_selection_groups(selections: List[dict]) -> Dict[str, List[dict]]:
    groups: Dict[str, List[dict]] = {}
    for selection in selections:
        match_seq = str(selection.get("matchSeq") or "")
        if not match_seq:
            continue
        groups.setdefault(match_seq, []).append(selection)
    return groups


def calculate_bet_count(groups: Dict[str, List[dict]], pass_types: List[int]) -> int:
    counts = [len(items) for items in groups.values() if items]
    if not counts:
        return 0
    total = 0
    indices = list(range(len(counts)))
    for size in pass_types:
        for combo in combinations(indices, size):
            product = 1
            for idx in combo:
                product *= counts[idx]
            total += product
    return total


def calculate_display_odds(groups: Dict[str, List[dict]]) -> float:
    total = Decimal("1")
    for items in groups.values():
        if not items:
            continue
        max_odds = max(Decimal(str(item.get("odds") or 0)) for item in items)
        total *= max_odds
    return float(total)


def scheme_to_dict(scheme) -> Dict:
    def format_dt(value):
        if not value:
            return None
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

    return {
        "id": scheme.id,
        "expect": scheme.expect,
        "name": scheme.name,
        "stake": scheme.stake,
        "passType": scheme.pass_type,
        "splitMode": scheme.split_mode,
        "totalOdds": scheme.total_odds or 0.0,
        "status": scheme.status,
        "winAmount": scheme.win_amount or 0.0,
        "profit": scheme.profit or 0.0,
        "ticketed": bool(getattr(scheme, "ticketed", False)),
        "createdAt": format_dt(scheme.created_at),
        "updatedAt": format_dt(scheme.updated_at),
        "items": [
            {
                "id": item.id,
                "matchSeq": item.match_seq,
                "homeTeam": item.home_team,
                "awayTeam": item.away_team,
                "matchTime": item.match_time,
                "selectedResult": item.selected_result,
                "odds": item.odds,
                "result": item.result,
            }
            for item in scheme.items
        ],
    }


@router.get("/expect-options")
async def get_expect_options(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_active_admin_user)
):
    service = BeidanDataService(db)
    options, latest = service.get_latest_date_time_options()
    options = [opt for opt in options if opt.get("value") != "custom"][:5]
    return {"data": {"options": options, "latestPeriod": latest}}


@router.get("/matches")
async def get_matches(
    expect: str = Query(..., description="期号"),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_active_admin_user)
):
    service = BeidanDataService(db)
    matches = await service.get_filtered_matches({"otherConditions": {"dateTime": expect}})
    schedule_candidates = build_bd_schedule_candidates(db, matches)

    result = []
    for match in matches:
        odds = match.get("odds") or {}
        attrs = normalize_attrs(match.get("sourceAttributes"))
        line_key = normalize_match_seq(match.get("lineId") or "")
        schedule_candidate = pick_bd_schedule_candidate(
            schedule_candidates.get(line_key or "", []),
            match.get("homeTeam"),
            match.get("guestTeam"),
            match.get("matchTime"),
        )

        status_raw = (
            match.get("status")
            or attrs.get("statusDes")
            or attrs.get("status_des")
            or attrs.get("status")
            or attrs.get("matchStatus")
            or attrs.get("state")
        )
        status_text = normalize_status_text(status_raw) or "-"
        if schedule_candidate and schedule_candidate.get("status"):
            status_text = schedule_candidate.get("status")

        handicap_raw = (
            match.get("handicap")
            or attrs.get("rq")
            or attrs.get("handicap")
            or attrs.get("letGoal")
            or attrs.get("let_ball")
            or attrs.get("rqValue")
        )
        handicap_text = normalize_handicap_text(handicap_raw) or "0"
        if schedule_candidate and schedule_candidate.get("handicap"):
            handicap_text = normalize_handicap_text(schedule_candidate.get("handicap")) or handicap_text

        score_raw = (
            match.get("score")
            or attrs.get("score")
            or attrs.get("full_score")
            or attrs.get("fullScore")
            or attrs.get("score_full")
        )
        if not score_raw and match.get("homeScore") is not None and match.get("awayScore") is not None:
            score_raw = f"{match.get('homeScore')}-{match.get('awayScore')}"
        score_text = normalize_score_text(score_raw)
        if schedule_candidate and schedule_candidate.get("score"):
            score_text = normalize_score_text(schedule_candidate.get("score"))

        half_score_raw = (
            match.get("halfScore")
            or attrs.get("halfScore")
            or attrs.get("half_score")
            or attrs.get("halftimeScore")
            or attrs.get("halfTimeScore")
        )
        half_score_text = normalize_score_text(half_score_raw)
        if schedule_candidate and schedule_candidate.get("half_score"):
            half_score_text = normalize_score_text(schedule_candidate.get("half_score"))

        # 赔率优先使用北单赛程库（yingqiu_bd）中的SP，原来源赔率仅作兜底
        home_win_odds = first_valid_odds(
            schedule_candidate.get("odds_home_win") if schedule_candidate else None,
            odds.get("homeWin"),
        )
        draw_odds = first_valid_odds(
            schedule_candidate.get("odds_draw") if schedule_candidate else None,
            odds.get("draw"),
        )
        guest_win_odds = first_valid_odds(
            schedule_candidate.get("odds_guest_win") if schedule_candidate else None,
            odds.get("guestWin"),
        )

        result.append({
            "matchSeq": str(match.get("lineId") or ""),
            "homeTeam": match.get("homeTeam") or "",
            "awayTeam": match.get("guestTeam") or "",
            "matchTime": match.get("matchTime") or "",
            "handicap": handicap_text,
            "status": status_text,
            "score": score_text or "-",
            "halfScore": half_score_text or "-",
            "scoreDisplay": build_score_display(score_text, half_score_text),
            "odds": {
                "homeWin": home_win_odds,
                "draw": draw_odds,
                "guestWin": guest_win_odds,
            }
        })

    return {"data": result}


@router.get("/results")
async def get_results(
    expect: str = Query(..., description="期号"),
    current_admin=Depends(get_current_active_admin_user)
):
    try:
        results = fetch_beidan_results(expect)
    except Exception as exc:
        logger.error("获取开奖失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="获取开奖结果失败") from exc

    if not results:
        raise HTTPException(status_code=404, detail="未解析到开奖结果")

    return {"data": results}


@router.post("/schemes")
async def create_scheme(
    payload: BettingSchemeCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_active_admin_user)
):
    if not payload.selections:
        raise HTTPException(status_code=400, detail="请至少选择两场比赛进行串关")

    selections = [item.model_dump() for item in payload.selections]
    groups = build_selection_groups(selections)
    if len(groups) < 2:
        raise HTTPException(status_code=400, detail="请至少选择两场比赛进行串关")

    pass_types = parse_pass_types(payload.passType, len(groups))
    pass_type_text = "all" if pass_types == [len(groups)] else ",".join([f"{x}x1" for x in pass_types])

    bet_count = calculate_bet_count(groups, pass_types)
    if bet_count <= 0:
        raise HTTPException(status_code=400, detail="投注注数为0，请检查选择")

    stake = float(bet_count * 2)
    name = payload.name.strip() if payload.name else f"方案-{payload.expect}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    scheme = betting_crud.create_scheme(
        db,
        admin_user_id=current_admin.id,
        expect=payload.expect,
        name=name,
        stake=stake,
        pass_type=pass_type_text,
        split_mode=payload.splitMode,
        selections=selections
    )

    scheme.total_odds = calculate_display_odds(groups)
    db.commit()
    db.refresh(scheme)

    return {"data": scheme_to_dict(scheme)}


@router.get("/schemes")
async def list_schemes(
    expect: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_active_admin_user)
):
    items, total = betting_crud.list_schemes(db, current_admin.id, expect, page, page_size)
    data = {
        "items": [scheme_to_dict(item) for item in items],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }
    return {"data": data}


@router.get("/schemes/{scheme_id}")
async def get_scheme(
    scheme_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_active_admin_user)
):
    scheme = betting_crud.get_scheme(db, current_admin.id, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="方案不存在")
    return {"data": scheme_to_dict(scheme)}


@router.put("/schemes/{scheme_id}")
async def update_scheme(
    scheme_id: int,
    payload: BettingSchemeUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_active_admin_user)
):
    scheme = betting_crud.get_scheme(db, current_admin.id, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="方案不存在")

    if payload.name is not None:
        scheme.name = payload.name.strip() or scheme.name

    if payload.selections is not None:
        selections = [item.model_dump() for item in payload.selections]
        groups = build_selection_groups(selections)
        if len(groups) < 2:
            raise HTTPException(status_code=400, detail="请至少选择两场比赛进行串关")

        if payload.passType:
            pass_types = parse_pass_types(payload.passType, len(groups))
            scheme.pass_type = "all" if pass_types == [len(groups)] else ",".join([f"{x}x1" for x in pass_types])
        else:
            pass_types = parse_pass_type_text(scheme.pass_type, len(groups))

        bet_count = calculate_bet_count(groups, pass_types)
        if bet_count <= 0:
            raise HTTPException(status_code=400, detail="投注注数为0，请检查选择")

        scheme.stake = float(bet_count * 2)
        if payload.splitMode:
            scheme.split_mode = payload.splitMode

        scheme.total_odds = calculate_display_odds(groups)
        db.commit()
        betting_crud.replace_scheme_items(db, scheme, selections)
        db.refresh(scheme)
    else:
        if payload.passType:
            pass_types = parse_pass_types(payload.passType, len(scheme.items))
            scheme.pass_type = "all" if pass_types == [len(scheme.items)] else ",".join([f"{x}x1" for x in pass_types])
        if payload.splitMode:
            scheme.split_mode = payload.splitMode
        if payload.stake:
            scheme.stake = payload.stake
        db.commit()
        db.refresh(scheme)

    return {"data": scheme_to_dict(scheme)}


@router.post("/schemes/{scheme_id}/ticket")
async def ticket_scheme(
    scheme_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_active_admin_user)
):
    scheme = betting_crud.get_scheme(db, current_admin.id, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="方案不存在")
    if not getattr(scheme, "ticketed", False):
        scheme.ticketed = True
        db.commit()
        db.refresh(scheme)
    return {"data": scheme_to_dict(scheme)}


@router.delete("/schemes/{scheme_id}")
async def delete_scheme(
    scheme_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_active_admin_user)
):
    deleted = betting_crud.delete_scheme(db, current_admin.id, scheme_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="方案不存在")
    return {"data": {"deleted": True}}


@router.post("/schemes/{scheme_id}/simulate")
async def simulate_scheme(
    scheme_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_active_admin_user)
):
    scheme = betting_crud.get_scheme(db, current_admin.id, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="方案不存在")

    try:
        results = fetch_beidan_results(scheme.expect)
    except Exception as exc:
        logger.error("模拟开奖失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="模拟开奖失败") from exc

    if not results:
        raise HTTPException(status_code=404, detail="未解析到开奖结果")

    missing = set()
    normalized_results = {}
    for key, value in results.items():
        norm = normalize_match_seq(key)
        if norm:
            normalized_results[norm] = value
            normalized_results[norm.zfill(3)] = value
        normalized_results[key] = value

    match_groups: Dict[str, List] = {}
    for item in scheme.items:
        norm = normalize_match_seq(item.match_seq)
        result_value = None
        if norm:
            result_value = normalized_results.get(norm) or normalized_results.get(norm.zfill(3))
        if not result_value:
            result_value = normalized_results.get(item.match_seq)
        if not result_value:
            missing.add(item.match_seq)
        else:
            item.result = result_value
        match_key = norm or str(item.match_seq)
        match_groups.setdefault(match_key, []).append(item)

    if missing:
        db.commit()
        raise HTTPException(status_code=400, detail=f"开奖数据缺少场次: {','.join(sorted(missing))}")

    pass_types = parse_pass_type_text(scheme.pass_type, len(match_groups))
    total_bets = calculate_bet_count(match_groups, pass_types)
    if total_bets <= 0:
        raise HTTPException(status_code=400, detail="串关类型无效")

    stake = Decimal(str(scheme.stake or 0))
    stake_per_bet = stake / Decimal(total_bets)

    total_win = Decimal("0")
    group_keys = list(match_groups.keys())
    for size in pass_types:
        for combo in combinations(group_keys, size):
            odds_value = Decimal("1")
            hit = True
            for key in combo:
                items = match_groups.get(key, [])
                matched = next((item for item in items if item.selected_result == item.result), None)
                if not matched:
                    hit = False
                    break
                odds_value *= Decimal(str(matched.odds or 0))
            if hit:
                total_win += stake_per_bet * odds_value

    profit = total_win - stake
    scheme.status = "won" if total_win > 0 else "lost"
    scheme.win_amount = float(total_win)
    scheme.profit = float(profit)

    db.commit()
    db.refresh(scheme)

    return {"data": scheme_to_dict(scheme)}
