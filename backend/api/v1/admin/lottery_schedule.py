from __future__ import annotations

from datetime import date, datetime, timedelta
import logging
import hashlib
import json
import re
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio

import aiohttp
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, case, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.orm.attributes import flag_modified

from ....database_async import AsyncSessionLocal, get_async_db
from ....models.match import League, Match, MatchStatusEnum, Team
from ...deps import get_current_admin

try:
    from playwright.async_api import async_playwright
except Exception:
    async_playwright = None


logger = logging.getLogger(__name__)


_BD_ISSUE_DATES_CACHE: Dict[str, List[str]] = {}
_BD_ISSUE_BY_DATE_CACHE: Dict[str, tuple[str, List[str]]] = {}
_BD_EXPECT_OPTIONS_CACHE: List[str] = []
_BD_OTHER_ODDS_PREFETCH_RUNNING: set[str] = set()
_BD_OTHER_ODDS_PREFETCH_LAST_AT: Dict[str, datetime] = {}
_BD_OTHER_ODDS_PREFETCH_COOLDOWN_SECONDS = 90
_BD_OTHER_ODDS_PREFETCH_GUARD = threading.Lock()


class UnifiedResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[Dict[str, Any]] = None


class MatchCreateRequest(BaseModel):
    league_name: str
    home_team: str
    away_team: str
    match_time: str  # YYYY-MM-DD HH:mm:ss
    status: str = "pending"
    score: Optional[str] = None
    number: Optional[str] = None
    handicap: Optional[str] = None
    odds_win: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_lose: Optional[float] = None
    source_url: Optional[str] = None


class MatchUpdateRequest(BaseModel):
    league_name: Optional[str] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    match_time: Optional[str] = None
    status: Optional[str] = None
    score: Optional[str] = None
    number: Optional[str] = None
    handicap: Optional[str] = None
    odds_win: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_lose: Optional[float] = None
    source_url: Optional[str] = None


router = APIRouter(tags=["admin-lottery-schedules"])


STATUS_MAP_UI_TO_DB = {
    "pending": MatchStatusEnum.SCHEDULED.value,
    "running": MatchStatusEnum.LIVE.value,
    "finished": MatchStatusEnum.FINISHED.value,
    "cancelled": MatchStatusEnum.CANCELLED.value,
}

STATUS_MAP_DB_TO_UI = {
    MatchStatusEnum.SCHEDULED.value: "pending",
    MatchStatusEnum.LIVE.value: "running",
    MatchStatusEnum.HALFTIME.value: "running",
    MatchStatusEnum.FINISHED.value: "finished",
    MatchStatusEnum.CANCELLED.value: "cancelled",
    MatchStatusEnum.POSTPONED.value: "pending",
    MatchStatusEnum.ABANDONED.value: "cancelled",
    MatchStatusEnum.SUSPENDED.value: "cancelled",
}


_WEEKDAY_CN_LABELS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def _weekday_cn_from_date_str(date_text: Optional[str]) -> Optional[str]:
    raw = str(date_text or "").strip()
    if not raw:
        return None
    try:
        d = datetime.strptime(raw, "%Y-%m-%d").date()
        return _WEEKDAY_CN_LABELS[d.weekday()]
    except Exception:
        return None


def _safe_slug(value: str, default_value: str) -> str:
    base = (value or "").strip().lower()
    base = re.sub(r"[^a-z0-9]+", "_", base)
    base = base.strip("_")
    return base or default_value


def _parse_match_dt(v: str) -> datetime:
    return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


def _score_to_pair(score: Optional[str]) -> tuple[Optional[int], Optional[int]]:
    if not score:
        return None, None
    parts = score.split("-")
    if len(parts) != 2:
        return None, None
    try:
        return int(parts[0]), int(parts[1])
    except Exception:
        return None, None


def _extract_score_pair(text: Optional[str]) -> tuple[Optional[int], Optional[int]]:
    raw = str(text or "").strip()
    if not raw:
        return None, None
    m = re.search(r"(\d+)\s*[-:：]\s*(\d+)", raw)
    if not m:
        return None, None
    try:
        return int(m.group(1)), int(m.group(2))
    except Exception:
        return None, None


def _extract_halftime_text(text: Optional[str]) -> Optional[str]:
    raw = str(text or "").strip()
    if not raw:
        return None
    pairs = re.findall(r"(\d+)\s*[-:：]\s*(\d+)", raw)
    if len(pairs) >= 2:
        return f"{pairs[1][0]}-{pairs[1][1]}"
    return None


def _normalize_status_text(status_value: Any, status_des: Optional[str] = None) -> str:
    status_des_text = str(status_des or "").strip()
    if any(x in status_des_text for x in ["完场", "已结束", "已完成"]):
        return "已完成"
    if any(x in status_des_text for x in ["未开", "待开", "未开赛"]):
        return "未开赛"
    if any(x in status_des_text for x in ["中场", "上半场", "下半场", "进行", "比赛中"]):
        return "比赛中"

    status_text = str(status_value.value if hasattr(status_value, "value") else status_value or "")
    if status_text in [MatchStatusEnum.FINISHED.value]:
        return "已完成"
    if status_text in [
        MatchStatusEnum.CANCELLED.value,
        MatchStatusEnum.ABANDONED.value,
        MatchStatusEnum.SUSPENDED.value,
    ]:
        return "已完成"
    if status_text in [MatchStatusEnum.LIVE.value, MatchStatusEnum.HALFTIME.value]:
        return "比赛中"
    if status_text in [MatchStatusEnum.SCHEDULED.value, MatchStatusEnum.POSTPONED.value]:
        return "未开赛"
    return "-"


def _match_source_attrs(match: Match) -> Dict[str, Any]:
    attrs = match.source_attributes if isinstance(match.source_attributes, dict) else {}
    return {
        "source_match_id": match.source_match_id,
        "number": attrs.get("number"),
        "status_des": attrs.get("status_des"),
        "full_score": attrs.get("full_score") or attrs.get("score"),
        "halftime_score": attrs.get("halftime_score") or attrs.get("half_score"),
        "source_schedule_date": attrs.get("source_schedule_date"),
        "handicap_0": attrs.get("handicap_0"),
        "handicap": attrs.get("handicap"),
        "odds_nspf_win": attrs.get("odds_nspf_win"),
        "odds_nspf_draw": attrs.get("odds_nspf_draw"),
        "odds_nspf_lose": attrs.get("odds_nspf_lose"),
        "odds_spf_win": attrs.get("odds_spf_win"),
        "odds_spf_draw": attrs.get("odds_spf_draw"),
        "odds_spf_lose": attrs.get("odds_spf_lose"),
        "odds_win": attrs.get("odds_win"),
        "odds_draw": attrs.get("odds_draw"),
        "odds_lose": attrs.get("odds_lose"),
        "source_url": attrs.get("source_url"),
    }


async def _resolve_bd_issue_date(db: AsyncSession, issue_no: Optional[str]) -> Optional[str]:
    raw = str(issue_no or "").strip()
    if not raw:
        return None
    normalized = raw.replace("期", "").strip()
    if not normalized:
        return None

    if re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}", normalized):
        return _normalize_yingqiu_date(normalized)
    if re.fullmatch(r"\d{8}", normalized):
        return _normalize_yingqiu_date(f"{normalized[:4]}-{normalized[4:6]}-{normalized[6:8]}")

    # 北单期号简码：yy + 3位期次序号，例如 26026
    if re.fullmatch(r"\d{5}", normalized):
        yy = int(normalized[:2])
        seq = int(normalized[2:])
        if seq <= 0:
            return None
        year = 2000 + yy
        source_date_expr = func.json_extract(Match.source_attributes, "$.source_schedule_date")
        q = (
            select(source_date_expr.label("source_date"))
            .where(
                Match.data_source == "yingqiu_bd",
                source_date_expr.like(f"{year}-%"),
            )
            .distinct()
            .order_by(source_date_expr.asc())
        )
        rows = (await db.execute(q)).all()
        dates = [str(r.source_date or "").strip() for r in rows if str(r.source_date or "").strip()]
        if 1 <= seq <= len(dates):
            return dates[seq - 1]
        return None

    return None


async def _fetch_500_bd_expect_options(limit: int = 300) -> List[str]:
    if _BD_EXPECT_OPTIONS_CACHE and len(_BD_EXPECT_OPTIONS_CACHE) >= limit:
        return _BD_EXPECT_OPTIONS_CACHE[:limit]

    url = "https://trade.500.com/bjdc/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://trade.500.com/bjdc/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
    soup = BeautifulSoup(html, "html.parser")
    options = soup.select("#expect_select option")
    result: List[str] = []
    for opt in options:
        value = str(opt.get("value") or "").strip()
        if re.fullmatch(r"\d{5}", value):
            result.append(value)
        if len(result) >= limit:
            break
    # 去重保序
    dedup: List[str] = []
    seen = set()
    for x in result:
        if x in seen:
            continue
        seen.add(x)
        dedup.append(x)
    if dedup:
        _BD_EXPECT_OPTIONS_CACHE.clear()
        _BD_EXPECT_OPTIONS_CACHE.extend(dedup)
    return dedup


async def _fetch_500_bd_issue_dates(issue_no: str) -> List[str]:
    key = str(issue_no or "").strip()
    if not key:
        return []
    if key in _BD_ISSUE_DATES_CACHE:
        return _BD_ISSUE_DATES_CACHE[key]

    url = f"https://trade.500.com/bjdc/?expect={key}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://trade.500.com/bjdc/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")
    served_expect = str((soup.select_one("input#expect") or {}).get("value") or "").strip()
    if served_expect and served_expect != key:
        # 服务端回退到其它期号时，避免误用
        return []

    vs_table = soup.select_one("#vs_table")
    if not vs_table:
        return []

    dates: List[str] = []
    seen = set()
    for tr in vs_table.select("tr[id^='switch_for_']"):
        tid = str(tr.get("id") or "")
        m = re.match(r"switch_for_(\d{4}-\d{2}-\d{2})", tid)
        if not m:
            continue
        d = m.group(1)
        if d in seen:
            continue
        seen.add(d)
        dates.append(d)
    dates = sorted(dates)
    _BD_ISSUE_DATES_CACHE[key] = dates
    return dates


async def _resolve_bd_issue_dates(db: AsyncSession, issue_no: Optional[str]) -> tuple[Optional[str], List[str]]:
    raw = str(issue_no or "").strip()
    if not raw:
        return None, []
    normalized = raw.replace("期", "").strip()
    if not normalized:
        return None, []

    # 1) 5位北单期号：优先按500规则获取整期覆盖日期
    if re.fullmatch(r"\d{5}", normalized):
        dates = await _fetch_500_bd_issue_dates(normalized)
        if dates:
            return normalized, dates
        # 500失败时回退旧规则（单日）
        fallback = await _resolve_bd_issue_date(db, normalized)
        return normalized, ([fallback] if fallback else [])

    # 2) 日期输入：先尝试反查500期号，再回退单日
    target_date = None
    if re.fullmatch(r"\d{8}", normalized):
        target_date = _normalize_yingqiu_date(f"{normalized[:4]}-{normalized[4:6]}-{normalized[6:8]}")
    elif re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}", normalized):
        target_date = _normalize_yingqiu_date(normalized)
    if target_date:
        if target_date in _BD_ISSUE_BY_DATE_CACHE:
            issue_value, dates = _BD_ISSUE_BY_DATE_CACHE[target_date]
            return issue_value, dates

        yy = target_date[2:4]
        candidates = await _fetch_500_bd_expect_options(limit=240)
        probes = 0
        for issue_value in candidates:
            if not issue_value.startswith(yy):
                continue
            dates = await _fetch_500_bd_issue_dates(issue_value)
            probes += 1
            if target_date in dates:
                _BD_ISSUE_BY_DATE_CACHE[target_date] = (issue_value, dates)
                return issue_value, dates
            if probes >= 120:
                break
        return target_date, [target_date]

    return None, []


async def _get_or_create_league(db: AsyncSession, league_name: str) -> League:
    q = await db.execute(select(League).where(League.name == league_name))
    league = q.scalar_one_or_none()
    if league:
        return league

    h = hashlib.md5(league_name.encode("utf-8")).hexdigest()[:6]
    league = League(
        name=league_name,
        code=f"{_safe_slug(league_name, 'league')}_{h}",
        country="未知",
        country_code="UNKNOWN",
        type="league",
        is_active=True,
        config={},
    )
    db.add(league)
    await db.flush()
    return league


async def _get_or_create_team(db: AsyncSession, team_name: str) -> Team:
    q = await db.execute(select(Team).where(Team.name == team_name))
    team = q.scalar_one_or_none()
    if team:
        return team

    h = hashlib.md5(team_name.encode("utf-8")).hexdigest()[:6]
    code_prefix = _safe_slug(team_name, "tm")[:3]
    team = Team(
        name=team_name,
        short_name=team_name[:20],
        code=f"{code_prefix}{h}",
        country="未知",
        country_code="UNKNOWN",
        is_active=True,
        config={},
    )
    db.add(team)
    await db.flush()
    return team


async def _format_match_rows(db: AsyncSession, rows: List[Any]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for match, league, home_team, away_team in rows:
        attrs = _match_source_attrs(match)
        kickoff = getattr(match, "scheduled_kickoff", None)
        if kickoff is None:
            md = getattr(match, "match_date", None)
            mt = getattr(match, "match_time", None)
            if md is not None and mt is not None:
                kickoff = datetime.combine(md, mt)
        kickoff_str = kickoff.strftime("%Y-%m-%d %H:%M:%S") if kickoff else "-"

        status_raw = getattr(match, "status", None)
        status_value = status_raw.value if hasattr(status_raw, "value") else status_raw
        full_score = (
            f"{match.home_score}-{match.away_score}"
            if match.home_score is not None and match.away_score is not None
            else (attrs.get("full_score") or attrs.get("score"))
        )
        halftime_score = (match.halftime_score or attrs.get("halftime_score") or attrs.get("half_score"))
        result.append(
            {
                "id": match.id,
                "league_name": league.name if league else "未知赛事",
                "home_team": home_team.name if home_team else "未知主队",
                "away_team": away_team.name if away_team else "未知客队",
                "match_time": kickoff_str,
                "status": STATUS_MAP_DB_TO_UI.get(status_value, "pending"),
                "status_text": _normalize_status_text(status_value, attrs.get("status_des")),
                "score": full_score,
                "halftime_score": halftime_score,
                **attrs,
            }
        )
    return result


@router.get("/", response_model=UnifiedResponse)
async def get_lottery_schedules(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    league_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    issue_no: Optional[str] = Query(None, description="北单期号，如26026"),
    schedule_type: Optional[str] = Query(None, description="jczq|bd"),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        conditions = []
        resolved_issue_date: Optional[str] = None
        resolved_issue_dates: List[str] = []
        resolved_issue_no: Optional[str] = None
        bd_prefetch_date: Optional[str] = None
        if schedule_type == "jczq":
            conditions.append(Match.data_source == "500w")
        elif schedule_type == "bd":
            conditions.append(Match.data_source == "yingqiu_bd")
        if league_name:
            conditions.append(League.name.contains(league_name))
        if status and status in STATUS_MAP_UI_TO_DB:
            conditions.append(Match.status == STATUS_MAP_UI_TO_DB[status])
        if schedule_type == "bd":
            # 北单按期次日期过滤，避免把前一期次的次日凌晨比赛并入当前日期
            source_date_expr = func.json_extract(Match.source_attributes, "$.source_schedule_date")
            if issue_no:
                resolved_issue_no, resolved_issue_dates = await _resolve_bd_issue_dates(db, issue_no)
                if resolved_issue_dates:
                    if len(resolved_issue_dates) == 1:
                        conditions.append(source_date_expr == resolved_issue_dates[0])
                        bd_prefetch_date = _normalize_yingqiu_date(resolved_issue_dates[0]) or resolved_issue_dates[0]
                    else:
                        conditions.append(source_date_expr.in_(resolved_issue_dates))
                    resolved_issue_date = resolved_issue_dates[0]
                else:
                    # 期号无效或未导入该期数据时返回空结果
                    conditions.append(Match.id == -1)
            elif date_from and date_to and date_from == date_to:
                conditions.append(source_date_expr == date_from)
                bd_prefetch_date = _normalize_yingqiu_date(date_from) or date_from
            else:
                if date_from:
                    conditions.append(source_date_expr >= date_from)
                if date_to:
                    conditions.append(source_date_expr <= date_to)
                if not date_from and not date_to:
                    bd_prefetch_date = datetime.now().strftime("%Y-%m-%d")
        elif schedule_type == "jczq":
            # 竞彩按源日期过滤；单日查询再叠加“编号周几”限制，避免把下一天分组混入
            source_date_expr = func.json_extract(Match.source_attributes, "$.source_schedule_date")
            number_expr = func.json_extract(Match.source_attributes, "$.number")
            if date_from and date_to and date_from == date_to:
                conditions.append(source_date_expr == date_from)
                weekday_cn = _weekday_cn_from_date_str(date_from)
                if weekday_cn:
                    conditions.append(number_expr.like(f"{weekday_cn}%"))
            else:
                if date_from:
                    conditions.append(source_date_expr >= date_from)
                if date_to:
                    conditions.append(source_date_expr <= date_to)
        else:
            if date_from and date_to and date_from == date_to:
                target_date = datetime.strptime(date_from, "%Y-%m-%d").date()
                conditions.append(
                    or_(
                        Match.match_date == target_date,
                        func.json_extract(Match.source_attributes, "$.source_schedule_date") == date_from,
                    )
                )
            else:
                if date_from:
                    conditions.append(Match.match_date >= datetime.strptime(date_from, "%Y-%m-%d").date())
                if date_to:
                    conditions.append(Match.match_date <= datetime.strptime(date_to, "%Y-%m-%d").date())

        HomeTeam = aliased(Team)
        AwayTeam = aliased(Team)
        base_query = (
            select(Match, League, HomeTeam, AwayTeam)
            .join(League, Match.league_id == League.id, isouter=True)
            .join(HomeTeam, Match.home_team_id == HomeTeam.id, isouter=True)
            .join(AwayTeam, Match.away_team_id == AwayTeam.id, isouter=True)
            .where(and_(*conditions))
        )

        if schedule_type in {"jczq", "bd"}:
            # 强制使用 Python 统一排序，避免不同数据库方言/表达式导致顺序不一致
            all_rows = (await db.execute(base_query)).all()
            sorted_rows = sorted(all_rows, key=lambda r: _match_row_sort_key_by_number(r, schedule_type))
            total = len(sorted_rows)
            start = max(0, (page - 1) * size)
            end = start + size
            page_rows = sorted_rows[start:end]
            items = await _format_match_rows(db, page_rows)
        else:
            query = base_query.order_by(Match.scheduled_kickoff.desc(), Match.id.desc()).offset((page - 1) * size).limit(size)
            rows = (await db.execute(query)).all()
            items = await _format_match_rows(db, rows)
            total_query = (
                select(func.count(Match.id))
                .join(League, Match.league_id == League.id, isouter=True)
                .where(and_(*conditions))
            )
            total = (await db.execute(total_query)).scalar() or 0

        if schedule_type == "bd":
            _trigger_bd_other_odds_prefetch(bd_prefetch_date)

        return UnifiedResponse(
            success=True,
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
                "resolved_issue_date": resolved_issue_date,
                "resolved_issue_dates": resolved_issue_dates,
                "resolved_issue_no": resolved_issue_no,
            },
            message="获取竞彩赛程列表成功",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/issue-options", response_model=UnifiedResponse)
async def get_bd_issue_options(
    count: int = Query(3, ge=1, le=20, description="返回最近多少期号"),
):
    try:
        items = await _fetch_500_bd_expect_options(limit=max(3, count))
        return UnifiedResponse(
            success=True,
            data={"items": items[:count]},
            message="获取北单期号选项成功",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/league-options", response_model=UnifiedResponse)
async def get_lottery_league_options(
    schedule_type: Optional[str] = Query(None, description="jczq|bd"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    issue_no: Optional[str] = Query(None, description="北单期号，如26026"),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        conditions = []
        resolved_issue_date: Optional[str] = None
        resolved_issue_dates: List[str] = []
        resolved_issue_no: Optional[str] = None
        if schedule_type == "jczq":
            conditions.append(Match.data_source == "500w")
        elif schedule_type == "bd":
            conditions.append(Match.data_source == "yingqiu_bd")

        if schedule_type == "bd":
            source_date_expr = func.json_extract(Match.source_attributes, "$.source_schedule_date")
            if issue_no:
                resolved_issue_no, resolved_issue_dates = await _resolve_bd_issue_dates(db, issue_no)
                if resolved_issue_dates:
                    if len(resolved_issue_dates) == 1:
                        conditions.append(source_date_expr == resolved_issue_dates[0])
                    else:
                        conditions.append(source_date_expr.in_(resolved_issue_dates))
                    resolved_issue_date = resolved_issue_dates[0]
                else:
                    conditions.append(Match.id == -1)
            elif date_from and date_to and date_from == date_to:
                conditions.append(source_date_expr == date_from)
            else:
                if date_from:
                    conditions.append(source_date_expr >= date_from)
                if date_to:
                    conditions.append(source_date_expr <= date_to)
        elif schedule_type == "jczq":
            source_date_expr = func.json_extract(Match.source_attributes, "$.source_schedule_date")
            number_expr = func.json_extract(Match.source_attributes, "$.number")
            if date_from and date_to and date_from == date_to:
                conditions.append(source_date_expr == date_from)
                weekday_cn = _weekday_cn_from_date_str(date_from)
                if weekday_cn:
                    conditions.append(number_expr.like(f"{weekday_cn}%"))
            else:
                if date_from:
                    conditions.append(source_date_expr >= date_from)
                if date_to:
                    conditions.append(source_date_expr <= date_to)
        else:
            if date_from and date_to and date_from == date_to:
                target_date = datetime.strptime(date_from, "%Y-%m-%d").date()
                conditions.append(
                    or_(
                        Match.match_date == target_date,
                        func.json_extract(Match.source_attributes, "$.source_schedule_date") == date_from,
                    )
                )
            else:
                if date_from:
                    conditions.append(Match.match_date >= datetime.strptime(date_from, "%Y-%m-%d").date())
                if date_to:
                    conditions.append(Match.match_date <= datetime.strptime(date_to, "%Y-%m-%d").date())

        q = (
            select(League.name)
            .select_from(Match)
            .join(League, Match.league_id == League.id, isouter=True)
            .where(and_(*conditions), League.name.isnot(None))
            .distinct()
            .order_by(League.name.asc())
        )
        rows = (await db.execute(q)).all()
        items = [str(r[0]) for r in rows if r and r[0]]

        return UnifiedResponse(
            success=True,
            data={
                "items": items,
                "resolved_issue_date": resolved_issue_date,
                "resolved_issue_dates": resolved_issue_dates,
                "resolved_issue_no": resolved_issue_no,
            },
            message="获取赛事选项成功",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=UnifiedResponse)
async def get_schedule_stats(db: AsyncSession = Depends(get_async_db)):
    try:
        stats_query = select(
            func.count(Match.id).label("total_matches"),
            func.sum(case((Match.status == MatchStatusEnum.SCHEDULED.value, 1), else_=0)).label("pending_matches"),
            func.sum(case((Match.status.in_([MatchStatusEnum.LIVE.value, MatchStatusEnum.HALFTIME.value]), 1), else_=0)).label("running_matches"),
            func.sum(case((Match.status == MatchStatusEnum.FINISHED.value, 1), else_=0)).label("finished_matches"),
        )
        row = (await db.execute(stats_query)).fetchone()
        data = {
            "totalMatches": row.total_matches or 0,
            "pendingMatches": row.pending_matches or 0,
            "runningMatches": row.running_matches or 0,
            "finishedMatches": row.finished_matches or 0,
        }
        return UnifiedResponse(success=True, data=data, message="获取统计数据成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=UnifiedResponse)
async def create_lottery_schedule(request: MatchCreateRequest, db: AsyncSession = Depends(get_async_db)):
    try:
        league = await _get_or_create_league(db, request.league_name)
        home_team = await _get_or_create_team(db, request.home_team)
        away_team = await _get_or_create_team(db, request.away_team)

        kickoff = _parse_match_dt(request.match_time)
        status_db = STATUS_MAP_UI_TO_DB.get(request.status, MatchStatusEnum.SCHEDULED.value)
        hs, as_ = _score_to_pair(request.score)

        source_match_id = request.number or f"manual-{kickoff.date()}-{request.home_team}-{request.away_team}"
        match_identifier = f"MANUAL-{kickoff.strftime('%Y%m%d%H%M%S')}-{hashlib.md5(source_match_id.encode('utf-8')).hexdigest()[:6]}"

        match = Match(
            match_identifier=match_identifier,
            league_id=league.id,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            match_date=kickoff.date(),
            match_time=kickoff.time(),
            scheduled_kickoff=kickoff,
            status=status_db,
            home_score=hs,
            away_score=as_,
            is_published=True,
            data_source="manual",
            source_match_id=source_match_id,
            source_attributes={
                "number": request.number,
                "handicap": request.handicap,
                "odds_win": request.odds_win,
                "odds_draw": request.odds_draw,
                "odds_lose": request.odds_lose,
                "source_url": request.source_url,
            },
        )

        db.add(match)
        await db.commit()
        await db.refresh(match)

        return UnifiedResponse(success=True, data={"id": match.id}, message="创建竞彩赛程成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建竞彩赛程失败: {str(e)}")


@router.put("/{match_id}", response_model=UnifiedResponse)
async def update_lottery_schedule(match_id: int, request: MatchUpdateRequest, db: AsyncSession = Depends(get_async_db)):
    try:
        q = await db.execute(select(Match).where(Match.id == match_id))
        match = q.scalar_one_or_none()
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")

        if request.league_name:
            league = await _get_or_create_league(db, request.league_name)
            match.league_id = league.id
        if request.home_team:
            home_team = await _get_or_create_team(db, request.home_team)
            match.home_team_id = home_team.id
        if request.away_team:
            away_team = await _get_or_create_team(db, request.away_team)
            match.away_team_id = away_team.id
        if request.match_time:
            kickoff = _parse_match_dt(request.match_time)
            match.match_date = kickoff.date()
            match.match_time = kickoff.time()
            match.scheduled_kickoff = kickoff
        if request.status:
            match.status = STATUS_MAP_UI_TO_DB.get(request.status, match.status)

        if request.score is not None:
            hs, as_ = _score_to_pair(request.score)
            match.home_score = hs
            match.away_score = as_

        attrs = _match_source_attrs(match)
        if request.number is not None:
            attrs["number"] = request.number
        if request.handicap is not None:
            attrs["handicap"] = request.handicap
        if request.odds_win is not None:
            attrs["odds_win"] = request.odds_win
        if request.odds_draw is not None:
            attrs["odds_draw"] = request.odds_draw
        if request.odds_lose is not None:
            attrs["odds_lose"] = request.odds_lose
        if request.source_url is not None:
            attrs["source_url"] = request.source_url
        match.source_attributes = attrs

        await db.commit()
        return UnifiedResponse(success=True, data={"id": match.id}, message="更新竞彩赛程成功")
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新竞彩赛程失败: {str(e)}")


@router.delete("/{match_id}", response_model=UnifiedResponse)
async def delete_lottery_schedule(match_id: int, db: AsyncSession = Depends(get_async_db)):
    try:
        q = await db.execute(select(Match).where(Match.id == match_id))
        match = q.scalar_one_or_none()
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")
        if match.status in [MatchStatusEnum.LIVE.value, MatchStatusEnum.HALFTIME.value]:
            raise HTTPException(status_code=400, detail="进行中的比赛不能删除")

        await db.execute(delete(Match).where(Match.id == match_id))
        await db.commit()
        return UnifiedResponse(success=True, data={"id": match_id}, message="删除竞彩赛程成功")
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除竞彩赛程失败: {str(e)}")


def _extract_cells_text(row) -> List[str]:
    return [c.get_text(" ", strip=True) for c in row.find_all("td")]


def _pick_match_number(cells: List[str], fallback_index: int) -> str:
    for text in cells[:3]:
        m = re.search(r"\d{3,}", text or "")
        if m:
            return m.group(0)
    return f"{fallback_index:03d}"


def _pick_kickoff(cells: List[str], target_date: date) -> datetime:
    for text in cells:
        if not text:
            continue
        hm = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", text)
        if hm:
            return datetime(
                target_date.year,
                target_date.month,
                target_date.day,
                int(hm.group(1)),
                int(hm.group(2)),
                0,
            )
    return datetime.combine(target_date, datetime.min.time())


def _pick_league_teams(cells: List[str]) -> Dict[str, str]:
    league = cells[1] if len(cells) > 1 else "未知赛事"
    home_team = cells[3] if len(cells) > 3 else ""
    away_team = cells[4] if len(cells) > 4 else ""

    if not home_team or not away_team:
        joined = " | ".join(cells)
        m = re.search(r"([^\|]+?)\s*(?:vs|VS|v|V|对)\s*([^\|]+)", joined)
        if m:
            home_team = home_team or m.group(1).strip()
            away_team = away_team or m.group(2).strip()

    return {
        "league_name": league or "未知赛事",
        "home_team": home_team or "未知主队",
        "away_team": away_team or "未知客队",
    }


def _to_float(text: str) -> Optional[float]:
    try:
        return float(str(text).strip())
    except Exception:
        return None


def _to_int(value: Any) -> Optional[int]:
    try:
        if value is None:
            return None
        text = str(value).strip()
        if text == "":
            return None
        return int(float(text))
    except Exception:
        return None


def _pick_handicap_odds(cells: List[str]) -> Dict[str, Any]:
    numeric: List[float] = []
    handicap = None
    for t in cells:
        cleaned = (t or "").strip()
        if handicap is None and re.fullmatch(r"[-+]?\d+(?:\.\d+)?", cleaned):
            handicap = cleaned
        fv = _to_float(cleaned)
        if fv is not None:
            numeric.append(fv)

    odds_win = odds_draw = odds_lose = None
    if len(numeric) >= 3:
        odds_win, odds_draw, odds_lose = numeric[-3], numeric[-2], numeric[-1]

    return {
        "handicap": handicap,
        "odds_win": odds_win,
        "odds_draw": odds_draw,
        "odds_lose": odds_lose,
    }


def _normalize_handicap_text(v: Optional[str], default_value: str = "0") -> str:
    text = (v or "").strip()
    m = re.search(r"[-+]?\d+(?:\.\d+)?", text)
    if m:
        return m.group(0)
    return default_value


async def _fetch_500w_matches(schedule_date: date) -> List[Dict[str, Any]]:
    date_str = schedule_date.strftime("%Y-%m-%d")
    source_url = f"https://trade.500.com/jczq/?date={date_str}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.500.com/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(source_url, headers=headers) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=502, detail=f"抓取500W失败，HTTP {resp.status}")
            raw = await resp.read()
            html = raw.decode("gbk", errors="ignore")

    soup = BeautifulSoup(html, "html.parser")
    # 仅抓取真实比赛行，过滤联赛筛选/让球筛选/日期分组等非比赛行
    rows = soup.select(".jczq_table tbody tr.bet-tb-tr")
    if not rows:
        rows = [r for r in (soup.select(".jczq_table tbody tr") or soup.select("tbody tr")) if r.select_one("td.td-no")]

    result: List[Dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        number = ((row.get("data-matchnum") or "").strip() or None)
        fixture_id = ((row.get("data-fixtureid") or "").strip() or None)
        if not number:
            no_el = row.select_one("td.td-no")
            if no_el:
                number = no_el.get_text(" ", strip=True).replace("点击可隐藏该比赛", "").strip()
        if not number:
            number = f"{idx:03d}"

        league_name = ((row.get("data-simpleleague") or "").strip() or None)
        if not league_name:
            league_el = row.select_one("td.td-evt a")
            league_name = league_el.get_text(" ", strip=True) if league_el else "未知赛事"

        home_team = ((row.get("data-homesxname") or "").strip() or None)
        away_team = ((row.get("data-awaysxname") or "").strip() or None)
        if not home_team:
            home_el = row.select_one("td.td-team .team-l a")
            home_team = home_el.get_text(" ", strip=True) if home_el else "未知主队"
        if not away_team:
            away_el = row.select_one("td.td-team .team-r a")
            away_team = away_el.get_text(" ", strip=True) if away_el else "未知客队"

        # 500W结果页会在队名之间展示比分（如 1:1），从球队单元格抽取
        team_cell_text = row.select_one("td.td-team").get_text(" ", strip=True) if row.select_one("td.td-team") else ""
        home_score, away_score = _extract_score_pair(team_cell_text)
        halftime_score = _extract_halftime_text(team_cell_text)
        if halftime_score:
            hs_ht, as_ht = _extract_score_pair(halftime_score)
            halftime_score = f"{hs_ht}-{as_ht}" if hs_ht is not None and as_ht is not None else None
        else:
            halftime_score = None

        row_classes = set(row.get("class") or [])
        status_attr = str(row.get("data-status") or "").strip().lower()
        if home_score is not None and away_score is not None:
            status = MatchStatusEnum.FINISHED.value
        elif "bet-tb-end" in row_classes or status_attr in {"end", "ended", "finish", "finished"}:
            status = MatchStatusEnum.FINISHED.value
        elif status_attr in {"live", "running", "ing", "halftime"}:
            status = MatchStatusEnum.LIVE.value
        else:
            status = MatchStatusEnum.SCHEDULED.value

        match_date_attr = (row.get("data-matchdate") or "").strip()
        match_time_attr = (row.get("data-matchtime") or "").strip()
        kickoff = None
        if match_date_attr and match_time_attr:
            try:
                kickoff = datetime.strptime(f"{match_date_attr} {match_time_attr}", "%Y-%m-%d %H:%M")
            except ValueError:
                kickoff = None

        if kickoff is None:
            endtime_text = (row.select_one("td.td-endtime").get_text(" ", strip=True) if row.select_one("td.td-endtime") else "")
            hm = re.search(r"(\d{2})-(\d{2})\s+([01]?\d|2[0-3]):([0-5]\d)", endtime_text)
            if hm:
                kickoff = datetime(
                    schedule_date.year,
                    int(hm.group(1)),
                    int(hm.group(2)),
                    int(hm.group(3)),
                    int(hm.group(4)),
                    0,
                )
        if kickoff is None:
            kickoff = datetime.combine(schedule_date, datetime.min.time())

        # 让球：不让球(通常0) + 让球(通常-1/+1)
        handicap_0 = None
        handicap_0_el = row.select_one("td.td-rang .itm-rangA1")
        if handicap_0_el:
            handicap_0 = handicap_0_el.get_text(" ", strip=True)
        handicap = None
        handicap_el = row.select_one("td.td-rang .itm-rangA2")
        if handicap_el:
            handicap = handicap_el.get_text(" ", strip=True)
        handicap_0 = _normalize_handicap_text(handicap_0, "0")
        if not handicap:
            handicap = (row.get("data-rangqiu") or "").strip() or "0"
        handicap = _normalize_handicap_text(handicap, "0")

        def _parse_odds_row(selector: str) -> tuple[Optional[float], Optional[float], Optional[float]]:
            cells = row.select(selector)
            if len(cells) < 3:
                return None, None, None
            return (
                _to_float(cells[0].get("data-sp") or cells[0].get_text(" ", strip=True)),
                _to_float(cells[1].get("data-sp") or cells[1].get_text(" ", strip=True)),
                _to_float(cells[2].get("data-sp") or cells[2].get_text(" ", strip=True)),
            )

        # 不让球 SP（第一行）
        odds_nspf_win, odds_nspf_draw, odds_nspf_lose = _parse_odds_row("td.td-betbtn .itm-rangB1 .betbtn")
        # 让球 SP（第二行）
        odds_spf_win, odds_spf_draw, odds_spf_lose = _parse_odds_row("td.td-betbtn .itm-rangB2 .betbtn")

        # 兼容旧字段：默认返回不让球 SP
        odds_win, odds_draw, odds_lose = odds_nspf_win, odds_nspf_draw, odds_nspf_lose

        if odds_win is None or odds_draw is None or odds_lose is None:
            # 回退到老逻辑，保证容错
            cells = _extract_cells_text(row)
            if len(cells) < 5:
                continue
            fallback_odds = _pick_handicap_odds(cells)
            odds_win = odds_win if odds_win is not None else fallback_odds["odds_win"]
            odds_draw = odds_draw if odds_draw is not None else fallback_odds["odds_draw"]
            odds_lose = odds_lose if odds_lose is not None else fallback_odds["odds_lose"]
            if not handicap:
                handicap = fallback_odds["handicap"]

        if not (home_team and away_team):
            continue

        row_source_schedule_date = _infer_jczq_source_schedule_date(schedule_date, number)
        result.append(
            {
                "number": number,
                "source_match_id": fixture_id or number,
                "league_name": league_name or "未知赛事",
                "home_team": home_team or "未知主队",
                "away_team": away_team or "未知客队",
                "kickoff": kickoff,
                "status": status,
                "home_score": home_score,
                "away_score": away_score,
                "halftime_score": halftime_score,
                "source_schedule_date": row_source_schedule_date.strftime("%Y-%m-%d"),
                "handicap_0": handicap_0,
                "handicap": handicap,
                "odds_nspf_win": odds_nspf_win,
                "odds_nspf_draw": odds_nspf_draw,
                "odds_nspf_lose": odds_nspf_lose,
                "odds_spf_win": odds_spf_win,
                "odds_spf_draw": odds_spf_draw,
                "odds_spf_lose": odds_spf_lose,
                "odds_win": odds_win,
                "odds_draw": odds_draw,
                "odds_lose": odds_lose,
                "source_url": source_url,
            }
        )
    return result


async def _fetch_500w_other_odds(fixture_id: str) -> List[Dict[str, Any]]:
    url = f"https://odds.500.com/fenxi/ouzhi-{fixture_id}.shtml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://trade.500.com/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=502, detail=f"抓取500W其它赔率失败，HTTP {resp.status}")
            raw = await resp.read()
            html = raw.decode("gbk", errors="ignore")

    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("#datatb")
    if not table:
        return []

    result: List[Dict[str, Any]] = []
    for tr in table.select("tr[xls='row']"):
        tds = tr.find_all("td")
        if len(tds) < 9:
            continue
        company = ""
        company_cid = None
        if len(tds) > 1:
            company_td = tds[1]
            name_el = company_td.select_one("span.quancheng")
            if name_el:
                company = name_el.get_text(" ", strip=True)
            if not company:
                company = (company_td.get("title") or "").strip()
            if not company:
                company = company_td.get_text(" ", strip=True)

            link_el = company_td.select_one("a[href*='cid=']")
            if link_el and link_el.get("href"):
                m = re.search(r"cid=(\d+)", link_el.get("href", ""))
                if m:
                    company_cid = m.group(1)
        if not company:
            continue
        result.append(
            {
                "company": company,
                "company_cid": company_cid,
                "updated_at": tr.get("data-time"),
                "init_win": _to_float(tds[3].get_text(" ", strip=True)),
                "init_draw": _to_float(tds[4].get_text(" ", strip=True)),
                "init_lose": _to_float(tds[5].get_text(" ", strip=True)),
                "instant_win": _to_float(tds[6].get_text(" ", strip=True)),
                "instant_draw": _to_float(tds[7].get_text(" ", strip=True)),
                "instant_lose": _to_float(tds[8].get_text(" ", strip=True)),
            }
        )
    return result


_WEEKDAY_ORDER = {
    "周一": 1,
    "周二": 2,
    "周三": 3,
    "周四": 4,
    "周五": 5,
    "周六": 6,
    "周日": 7,
    "周天": 7,
}


def _resolve_match_kickoff(match: Match) -> datetime:
    kickoff = getattr(match, "scheduled_kickoff", None)
    if isinstance(kickoff, datetime):
        return kickoff
    md = getattr(match, "match_date", None)
    mt = getattr(match, "match_time", None)
    if md is not None and mt is not None:
        return datetime.combine(md, mt)
    # 未知时间统一排在最后，避免干扰编号主排序
    return datetime.max


def _extract_match_number_text(match: Match) -> str:
    attrs = match.source_attributes if isinstance(match.source_attributes, dict) else {}
    raw = attrs.get("number")
    if raw in [None, ""]:
        raw = getattr(match, "external_id", None)
    if raw in [None, ""]:
        raw = getattr(match, "source_match_id", None)
    return str(raw or "").strip()


def _number_sort_key(number_text: str, schedule_type: Optional[str]) -> tuple:
    text = str(number_text or "").strip()
    if not text or text == "-":
        return 9, 999999, 999999, text

    # 竞彩常见格式：周X001
    m_week = re.match(r"^(周[一二三四五六日天])\s*0*(\d+)$", text)
    if m_week:
        weekday_rank = _WEEKDAY_ORDER.get(m_week.group(1), 99)
        seq = int(m_week.group(2))
        return 0, weekday_rank, seq, text

    # 纯数字（北单常见）
    if text.isdigit():
        return 1, 0, int(text), text

    # 兜底：提取尾部数字
    m_tail = re.search(r"(\d+)$", text)
    if m_tail:
        return 2, 0, int(m_tail.group(1)), text

    # 最后按文本自然顺序
    return 8, 0, 999999, text


def _match_row_sort_key_by_number(row: Any, schedule_type: Optional[str]) -> tuple:
    match = row[0]
    number_text = _extract_match_number_text(match)
    kickoff = _resolve_match_kickoff(match)
    return (*_number_sort_key(number_text, schedule_type), kickoff, int(getattr(match, "id", 0) or 0))


def _infer_jczq_source_schedule_date(base_date: date, number_text: Optional[str]) -> date:
    text = str(number_text or "").strip()
    m = re.match(r"^(周[一二三四五六日天])", text)
    if not m:
        return base_date
    target_weekday = _WEEKDAY_ORDER.get(m.group(1))
    if not target_weekday:
        return base_date
    base_weekday = base_date.weekday() + 1  # Monday=1 ... Sunday=7
    delta = (target_weekday - base_weekday) % 7
    return base_date + timedelta(days=delta)


def _format_odds_timestamp(ts: Any) -> str:
    tsv = _to_int(ts)
    if tsv is None or tsv <= 0:
        return "-"
    if tsv > 10**12:
        tsv = tsv // 1000
    try:
        return datetime.fromtimestamp(tsv).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "-"


def _pick_latest_yingqiu_odd(odds_rows: Any) -> Dict[str, Any]:
    if not isinstance(odds_rows, list) or not odds_rows:
        return {}
    best_row: Dict[str, Any] = {}
    best_score = -1
    for row in odds_rows:
        if not isinstance(row, dict):
            continue
        score = _to_int(row.get("updateTime")) or _to_int(row.get("createTime")) or _to_int(row.get("number")) or 0
        if score >= best_score:
            best_score = score
            best_row = row
    return best_row


def _map_yingqiu_europe_odds_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = ((payload or {}).get("model") or {}).get("list") or []
    result: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        result.append(
            {
                "company": str(row.get("providerName") or "-"),
                "provider_id": row.get("providerId"),
                "updated_at": _format_odds_timestamp(row.get("createTime")),
                "init_win": _to_float(row.get("firstWinOdds")),
                "init_draw": _to_float(row.get("firstDrawOdds")),
                "init_lose": _to_float(row.get("firstLoseOdds")),
                "instant_win": _to_float(row.get("winOdds")),
                "instant_draw": _to_float(row.get("drawOdds")),
                "instant_lose": _to_float(row.get("loseOdds")),
            }
        )
    return result


def _map_yingqiu_asia_odds_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = (payload or {}).get("list") or []
    result: List[Dict[str, Any]] = []
    for provider in rows:
        if not isinstance(provider, dict):
            continue
        odd = _pick_latest_yingqiu_odd(provider.get("odds"))
        result.append(
            {
                "company": str(provider.get("providerName") or "-"),
                "provider_id": provider.get("providerId"),
                "updated_at": _format_odds_timestamp(odd.get("updateTime") or odd.get("createTime")),
                "init_home": _to_float(odd.get("firstHomeWinOdds")),
                "init_handicap": str(odd.get("firstHandicap") or odd.get("firstHandicapNum") or "-"),
                "init_away": _to_float(odd.get("firstAwayWinOdds")),
                "instant_home": _to_float(odd.get("homeWinOdds")),
                "instant_handicap": str(odd.get("handicap") or odd.get("handicapNum") or "-"),
                "instant_away": _to_float(odd.get("awayWinOdds")),
                "trend": str(odd.get("updown") or "-"),
            }
        )
    return result


def _map_yingqiu_goals_odds_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = (payload or {}).get("list") or []
    result: List[Dict[str, Any]] = []
    for provider in rows:
        if not isinstance(provider, dict):
            continue
        odd = _pick_latest_yingqiu_odd(provider.get("odds"))
        result.append(
            {
                "company": str(provider.get("providerName") or "-"),
                "provider_id": provider.get("providerId"),
                "updated_at": _format_odds_timestamp(odd.get("updateTime") or odd.get("createTime")),
                "init_big": _to_float(odd.get("firstBigOdds")),
                "init_line": str(odd.get("firstHandicap") or odd.get("firstHandicapNum") or "-"),
                "init_small": _to_float(odd.get("firstSmallOdds")),
                "instant_big": _to_float(odd.get("bigOdds")),
                "instant_line": str(odd.get("handicap") or odd.get("handicapNum") or "-"),
                "instant_small": _to_float(odd.get("smallOdds")),
                "trend": str(odd.get("updown") or "-"),
            }
        )
    return result


async def _fetch_yingqiu_europe_odds_direct(match_id: str) -> List[Dict[str, Any]]:
    url = f"https://www.ttyingqiu.com/live/matchDetail/ftAicaiAllEuropeOdds?matchId={match_id}&isPrimary=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://www.ttyingqiu.com/live/zq/matchDetail/oz/{match_id}",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    timeout = aiohttp.ClientTimeout(total=25)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return []
            raw = await resp.read()
            text = ""
            for enc in ("utf-8", "gb18030", "gbk"):
                try:
                    text = raw.decode(enc)
                    if text:
                        break
                except Exception:
                    continue
            if not text:
                text = raw.decode("utf-8", errors="ignore")
            try:
                payload = json.loads(text)
                return _map_yingqiu_europe_odds_payload(payload)
            except Exception:
                return []


async def _fetch_yingqiu_other_odds_settled_via_node(match_id: str) -> Any:
    """
    Fallback: run Playwright via Node.js when python playwright is unavailable.
    """
    repo_root = Path(__file__).resolve().parents[4]
    frontend_dir = repo_root / "frontend"
    if not frontend_dir.exists():
        return None

    node_script = r"""
const mid = process.argv[1];
(async () => {
  let browser = null;
  try {
    const { chromium } = require('playwright');
    browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
    const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
    const detailUrl = `https://www.ttyingqiu.com/live/zq/matchDetail/oz/${mid}`;
    await page.goto(detailUrl, { waitUntil: 'domcontentloaded', timeout: 120000 });
    await page.waitForTimeout(7000);
    const settled = await page.evaluate((m) => new Promise((resolve) => {
      try {
        if (typeof requirejs === 'undefined') {
          resolve({ error: 'requirejs_unavailable' });
          return;
        }
        requirejs(['service/match.service'], function(ms) {
          Promise.allSettled([
            Promise.resolve(ms.getFtAicaiAllEuropeOdds(m, 0)),
            Promise.resolve(ms.getFtRangqiuOdds(m)),
            Promise.resolve(ms.getFtBigsmallAllAicaiOdds(m)),
          ]).then((items) => {
            const normalized = items.map((x) => (
              x.status === 'fulfilled'
                ? { status: 'fulfilled', value: x.value }
                : { status: 'rejected', reason: String(x.reason || '') }
            ));
            resolve(normalized);
          }).catch((e) => resolve({ error: String(e || '') }));
        }, function(err) {
          resolve({ error: String(err || '') });
        });
      } catch (e) {
        resolve({ error: String(e || '') });
      }
    }), String(mid));
    process.stdout.write(JSON.stringify(settled ?? null));
  } catch (e) {
    process.stdout.write(JSON.stringify({ error: String(e || '') }));
    process.exitCode = 1;
  } finally {
    if (browser) {
      try { await browser.close(); } catch (_) {}
    }
  }
})();
"""
    try:
        proc = await asyncio.create_subprocess_exec(
            "node",
            "-e",
            node_script,
            str(match_id),
            cwd=str(frontend_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=150)
        out_text = (stdout or b"").decode("utf-8", errors="ignore").strip()
        if not out_text:
            err_text = (stderr or b"").decode("utf-8", errors="ignore").strip()
            if err_text:
                logger.warning("node兜底抓取输出为空(match_id=%s): %s", match_id, err_text[:300])
            return None
        try:
            return json.loads(out_text)
        except Exception:
            logger.warning("node兜底抓取JSON解析失败(match_id=%s): %s", match_id, out_text[:300])
            return None
    except Exception as e:
        logger.warning("node兜底抓取异常(match_id=%s): %s", match_id, e)
        return None


def _apply_yingqiu_other_odds_settled(
    settled: Any,
    tabs: Dict[str, List[Dict[str, Any]]],
) -> None:
    if not (isinstance(settled, list) and len(settled) >= 3):
        return

    eu_res = settled[0] if isinstance(settled[0], dict) else {}
    asia_res = settled[1] if isinstance(settled[1], dict) else {}
    goals_res = settled[2] if isinstance(settled[2], dict) else {}

    if eu_res.get("status") == "fulfilled" and isinstance(eu_res.get("value"), dict):
        eu_rows = _map_yingqiu_europe_odds_payload(eu_res.get("value") or {})
        if eu_rows:
            tabs["eu"] = eu_rows

    if asia_res.get("status") == "fulfilled" and isinstance(asia_res.get("value"), dict):
        tabs["asia"] = _map_yingqiu_asia_odds_payload(asia_res.get("value") or {})

    if goals_res.get("status") == "fulfilled" and isinstance(goals_res.get("value"), dict):
        tabs["goals"] = _map_yingqiu_goals_odds_payload(goals_res.get("value") or {})


async def _fetch_yingqiu_other_odds_tabs(match_id: str) -> Dict[str, List[Dict[str, Any]]]:
    tabs: Dict[str, List[Dict[str, Any]]] = {
        "eu": [],
        "asia": [],
        "goals": [],
    }

    try:
        # 优先用直接接口抓欧指，兼容性最佳
        tabs["eu"] = await _fetch_yingqiu_europe_odds_direct(match_id)
    except Exception:
        tabs["eu"] = []

    detail_url = f"https://www.ttyingqiu.com/live/zq/matchDetail/oz/{match_id}"
    settled: Any = None

    # 1) Python Playwright path
    if async_playwright is not None:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
                try:
                    page = await browser.new_page(viewport={"width": 1366, "height": 900})
                    await page.goto(detail_url, wait_until="domcontentloaded", timeout=120000)
                    await page.wait_for_timeout(7000)
                    settled = await page.evaluate(
                        """(mid) => new Promise((resolve) => {
                            try {
                                if (typeof requirejs === 'undefined') {
                                    resolve({ error: 'requirejs_unavailable' });
                                    return;
                                }
                                requirejs(['service/match.service'], function(ms) {
                                    Promise.allSettled([
                                        Promise.resolve(ms.getFtAicaiAllEuropeOdds(mid, 0)),
                                        Promise.resolve(ms.getFtRangqiuOdds(mid)),
                                        Promise.resolve(ms.getFtBigsmallAllAicaiOdds(mid)),
                                    ]).then((items) => {
                                        const normalized = items.map((x) => (
                                            x.status === 'fulfilled'
                                                ? { status: 'fulfilled', value: x.value }
                                                : { status: 'rejected', reason: String(x.reason || '') }
                                        ));
                                        resolve(normalized);
                                    }).catch((e) => resolve({ error: String(e || '') }));
                                }, function(err) {
                                    resolve({ error: String(err || '') });
                                });
                            } catch (e) {
                                resolve({ error: String(e || '') });
                            }
                        })""",
                        str(match_id),
                    )
                finally:
                    await browser.close()
        except Exception as e:
            logger.warning("盈球其它赔率抓取(Python Playwright)失败(match_id=%s): %s", match_id, e)

    # 2) Node Playwright fallback path
    if not (isinstance(settled, list) and len(settled) >= 3):
        node_settled = await _fetch_yingqiu_other_odds_settled_via_node(match_id)
        if isinstance(node_settled, list) and len(node_settled) >= 3:
            settled = node_settled

    try:
        _apply_yingqiu_other_odds_settled(settled, tabs)
    except Exception as e:
        logger.warning("盈球其它赔率扩展抓取失败(match_id=%s): %s", match_id, e)

    if not tabs["eu"] and not tabs["asia"] and not tabs["goals"]:
        raise HTTPException(status_code=502, detail="抓取盈球其它赔率失败：未返回有效赔率数据")
    return tabs


async def _fetch_yingqiu_other_odds(match_id: str) -> List[Dict[str, Any]]:
    tabs = await _fetch_yingqiu_other_odds_tabs(match_id)
    return tabs.get("eu", [])


def _extract_json_object_after(source: str, marker: str) -> Optional[Dict[str, Any]]:
    start = source.find(marker)
    if start < 0:
        return None
    brace_start = source.find("{", start)
    if brace_start < 0:
        return None
    level = 0
    brace_end = -1
    for i in range(brace_start, len(source)):
        ch = source[i]
        if ch == "{":
            level += 1
        elif ch == "}":
            level -= 1
            if level == 0:
                brace_end = i
                break
    if brace_end < 0:
        return None
    import json
    return json.loads(source[brace_start:brace_end + 1])


def _map_yingqiu_status(raw_status: Any, status_des: str) -> str:
    status_text = (status_des or "").strip()
    if "完场" in status_text or "已结束" in status_text:
        return MatchStatusEnum.FINISHED.value
    if "未开赛" in status_text or "未开" in status_text:
        return MatchStatusEnum.SCHEDULED.value
    if any(x in status_text for x in ["中场", "上半场", "下半场", "进行", "比赛中"]):
        return MatchStatusEnum.LIVE.value
    try:
        status_int = int(raw_status)
    except Exception:
        status_int = 0
    if status_int <= 0:
        return MatchStatusEnum.SCHEDULED.value
    if status_int in [1, 2, 3, 4, 5]:
        return MatchStatusEnum.LIVE.value
    if status_int in [8, 9, 10]:
        return MatchStatusEnum.FINISHED.value
    return MatchStatusEnum.LIVE.value


def _normalize_yingqiu_date(text: Optional[str]) -> Optional[str]:
    raw = str(text or "").strip()
    if not raw:
        return None
    raw = raw.replace("/", "-").replace(".", "-")
    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", raw)
    if not m:
        return None
    return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"


def _parse_yingqiu_match_datetime(match_date: Optional[str], match_time: Optional[str], schedule_date: str) -> datetime:
    date_text = _normalize_yingqiu_date(match_date) or schedule_date
    time_text = str(match_time or "00:00").strip().replace("：", ":")
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]:
        try:
            return datetime.strptime(f"{date_text} {time_text}", fmt)
        except Exception:
            continue
    return datetime.strptime(f"{schedule_date} 00:00", "%Y-%m-%d %H:%M")


def _map_yingqiu_match(item: Dict[str, Any], source_url: str, schedule_date: str) -> Dict[str, Any]:
    match_date = str(item.get("matchDate") or schedule_date)
    match_time = str(item.get("matchTime") or "00:00")
    kickoff = _parse_yingqiu_match_datetime(match_date, match_time, schedule_date)

    odds_europe = str(item.get("oddsEurope") or "")
    eu_parts = [p.strip() for p in odds_europe.split(";")]
    odds_win = _to_float(eu_parts[0]) if len(eu_parts) > 0 else None
    odds_draw = _to_float(eu_parts[1]) if len(eu_parts) > 1 else None
    odds_lose = _to_float(eu_parts[2]) if len(eu_parts) > 2 else None

    odds_asia = str(item.get("oddsAsia") or "")
    asia_parts = [p.strip() for p in odds_asia.split(";")]
    handicap = asia_parts[1] if len(asia_parts) > 1 else str(item.get("oddsAsiaHandicapDesc") or "0")
    handicap = _normalize_handicap_text(handicap, "0")

    number = str(item.get("matchNoCn") or "")
    source_match_id = str(item.get("qtMatchId") or item.get("matchId") or number)

    home_score_hint = _to_int(item.get("homeScore"))
    away_score_hint = _to_int(item.get("awayScore"))

    raw_score = item.get("score")
    if isinstance(raw_score, list):
        # 盈球score数组常见格式为 [半场, 全场, ...]
        score_list = [str(x or "").strip() for x in raw_score if str(x or "").strip()]
        full_score_raw = ""
        half_score_raw_from_list = ""
        if len(score_list) == 1:
            full_score_raw = score_list[0]
        elif len(score_list) >= 2:
            first_pair = _extract_score_pair(score_list[0])
            second_pair = _extract_score_pair(score_list[1])
            hint_pair = (
                (home_score_hint, away_score_hint)
                if home_score_hint is not None and away_score_hint is not None
                else None
            )
            if hint_pair and second_pair == hint_pair:
                full_score_raw = score_list[1]
                half_score_raw_from_list = score_list[0]
            elif hint_pair and first_pair == hint_pair:
                full_score_raw = score_list[0]
                half_score_raw_from_list = score_list[1]
            else:
                full_score_raw = score_list[1]
                half_score_raw_from_list = score_list[0]
    else:
        full_score_raw = raw_score
        half_score_raw_from_list = ""
    full_score_text = str(
        full_score_raw
        or item.get("fullScore")
        or item.get("matchScore")
        or item.get("scoreFull")
        or ""
    ).strip()
    half_score_text = str(
        item.get("halfScore")
        or item.get("halfTimeScore")
        or item.get("scoreHalf")
        or item.get("half")
        or half_score_raw_from_list
        or ""
    ).strip()
    hs = home_score_hint
    as_ = away_score_hint
    if hs is None or as_ is None:
        hs, as_ = _extract_score_pair(full_score_text)
    if hs is None or as_ is None:
        hs, as_ = _extract_score_pair(str(item.get("statusDes") or ""))
    half_home = _to_int(item.get("homeHalfScore"))
    half_away = _to_int(item.get("awayHalfScore"))
    if half_home is not None and half_away is not None:
        half_score_text = f"{half_home}-{half_away}"
    if not half_score_text:
        half_score_text = _extract_halftime_text(full_score_text)
    if half_score_text:
        hhs, has_ = _extract_score_pair(half_score_text)
        half_score_text = f"{hhs}-{has_}" if hhs is not None and has_ is not None else None
    else:
        half_score_text = None

    return {
        "number": number or source_match_id,
        "source_match_id": source_match_id,
        "league_name": str(item.get("leagueName") or "未知赛事"),
        "home_team": str(item.get("homeName") or "未知主队"),
        "away_team": str(item.get("awayName") or "未知客队"),
        "kickoff": kickoff,
        "status": _map_yingqiu_status(item.get("status"), str(item.get("statusDes") or "")),
        "status_des": str(item.get("statusDes") or ""),
        "home_score": hs,
        "away_score": as_,
        "halftime_score": half_score_text,
        "handicap_0": "0",
        "handicap": handicap,
        "odds_win": odds_win,
        "odds_draw": odds_draw,
        "odds_lose": odds_lose,
        # 静态JSON/源码兜底通常仅提供欧赔，避免误当作北单SP主赔率
        "odds_nspf_win": None,
        "odds_nspf_draw": None,
        "odds_nspf_lose": None,
        "odds_spf_win": None,
        "odds_spf_draw": None,
        "odds_spf_lose": None,
        "source_schedule_date": schedule_date,
        "source_url": source_url,
    }


def _parse_yingqiu_kickoff(kickoff_text: str, schedule_date: str) -> datetime:
    text = (kickoff_text or "").strip()
    m = re.search(r"(\d{2})-(\d{2})\s*(\d{2})[:：](\d{2})", text)
    if not m:
        return datetime.strptime(f"{schedule_date} 00:00", "%Y-%m-%d %H:%M")
    schedule_dt = datetime.strptime(schedule_date, "%Y-%m-%d")
    year = schedule_dt.year
    kickoff = datetime(year, int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
    if (kickoff - schedule_dt).days > 180:
        kickoff = datetime(year - 1, int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
    elif (schedule_dt - kickoff).days > 180:
        kickoff = datetime(year + 1, int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
    return kickoff


def _map_yingqiu_dom_row(row: Dict[str, Any], schedule_date: str, source_url: str) -> Dict[str, Any]:
    source_match_id = str(row.get("source_match_id") or row.get("number") or "").strip()
    home_team = str(row.get("home_team") or "").strip()
    away_team = str(row.get("away_team") or "").strip()
    if not source_match_id:
        source_match_id = f"{schedule_date}-{home_team}-{away_team}"

    kickoff = _parse_yingqiu_kickoff(str(row.get("kickoff_text") or ""), schedule_date)
    odds_win = _to_float(str(row.get("odds_win") or ""))
    odds_draw = _to_float(str(row.get("odds_draw") or ""))
    odds_lose = _to_float(str(row.get("odds_lose") or ""))
    handicap = _normalize_handicap_text(str(row.get("handicap") or ""), "0")
    status_des = str(row.get("status_des") or "")
    score_text = str(row.get("score_text") or "").strip()
    hs, as_ = _extract_score_pair(score_text)

    half_score_text = str(row.get("half_score_text") or "").strip()
    if half_score_text:
        hhs, has_ = _extract_score_pair(half_score_text)
        halftime_score = f"{hhs}-{has_}" if hhs is not None and has_ is not None else None
    else:
        halftime_score = _extract_halftime_text(score_text)

    return {
        "number": str(row.get("number") or source_match_id),
        "source_match_id": source_match_id,
        "league_name": str(row.get("league_name") or "未知赛事"),
        "home_team": home_team or "未知主队",
        "away_team": away_team or "未知客队",
        "kickoff": kickoff,
        "status": _map_yingqiu_status(None, status_des),
        "status_des": status_des,
        "home_score": hs,
        "away_score": as_,
        "halftime_score": halftime_score,
        "handicap_0": "0",
        "handicap": handicap,
        "odds_win": odds_win,
        "odds_draw": odds_draw,
        "odds_lose": odds_lose,
        "odds_nspf_win": odds_win,
        "odds_nspf_draw": odds_draw,
        "odds_nspf_lose": odds_lose,
        "odds_spf_win": None,
        "odds_spf_draw": None,
        "odds_spf_lose": None,
        "source_schedule_date": schedule_date,
        "source_url": source_url,
    }


async def _fetch_yingqiu_bd_matches(schedule_date: date) -> List[Dict[str, Any]]:
    date_str = schedule_date.strftime("%Y-%m-%d")
    source_url = "https://www.ttyingqiu.com/bjdc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.ttyingqiu.com/bjdc",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    ap = async_playwright
    if ap is None:
        try:
            from playwright.async_api import async_playwright as ap
        except Exception:
            ap = None

    static_result: List[Dict[str, Any]] = []
    expected_source_match_ids: set[str] = set()

    # 次选：按日期直连静态JSON，不依赖页面切换（赔率可能为欧赔）
    static_json_url = f"https://www.ttyingqiu.com/static/no_cache/league/zc/jsbf/ttyq2020/bd/jsbf_{date_str}.json"
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(static_json_url, headers=headers) as resp:
                if resp.status == 200:
                    payload = await resp.json(content_type=None)
                    if isinstance(payload, dict):
                        actual_date_raw = str(payload.get("date") or "").strip()
                        actual_date = _normalize_yingqiu_date(actual_date_raw)
                        if actual_date == date_str:
                            raw_list = payload.get("matchList") or []
                            result: List[Dict[str, Any]] = []
                            for item in raw_list:
                                if not isinstance(item, dict):
                                    continue
                                match_id = str(item.get("matchId") or "").strip()
                                if match_id:
                                    expected_source_match_ids.add(match_id)
                                try:
                                    result.append(_map_yingqiu_match(item, static_json_url, date_str))
                                except Exception:
                                    continue
                            static_result = result
    except Exception:
        # 静态JSON失败时继续尝试页面抓取
        pass

    # 优先使用真实页面日期切换并解析完整表格（北单SP）
    if ap is not None:
        try:
            async with ap() as p:
                browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
                page = await browser.new_page(viewport={"width": 1366, "height": 900})
                await page.goto(source_url, wait_until="networkidle", timeout=120000)
                await page.wait_for_timeout(1200)

                get_date_js = """() => {
                    const isVisible = (el) => {
                        const r = el.getBoundingClientRect();
                        const st = getComputedStyle(el);
                        return r.width > 0 && r.height > 0 && r.bottom > 0 &&
                            r.top < window.innerHeight && st.display !== 'none' &&
                            st.visibility !== 'hidden' && st.opacity !== '0';
                    };
                    const btn = Array.from(document.querySelectorAll('.calendarBtn')).find(isVisible);
                    const txt = btn ? (btn.textContent || '') : '';
                    const m = txt.match(/(20\\d{2}-\\d{2}-\\d{2})/);
                    return m ? m[1] : '';
                }"""
                get_table_signature_js = """() => {
                    const toText = (el) => (el ? (el.textContent || '').replace(/\\s+/g, ' ').trim() : '');
                    const trList = Array.from(document.querySelectorAll('tbody[id^="match"] tr.liveMacthLi, tbody[id^="match"] > tr'));
                    for (const tr of trList) {
                        const tds = Array.from(tr.querySelectorAll('td'));
                        if (tds.length < 10) continue;
                        const tbody = tr.closest('tbody[id^="match"]');
                        const tbodyId = tbody ? (tbody.getAttribute('id') || '') : '';
                        const matchIdM = tbodyId.match(/match(\\d+)/);
                        return [
                            matchIdM ? matchIdM[1] : '',
                            toText(tds[0]),
                            toText(tds[2]),
                            toText(tds[4]),
                        ].join('|');
                    }
                    return '';
                }"""
                extract_dom_rows_js = """() => {
                    const toText = (el) => (el ? (el.textContent || '').replace(/\\s+/g, ' ').trim() : '');
                    const rows = [];
                    const trList = Array.from(document.querySelectorAll('tbody[id^="match"] tr.liveMacthLi, tbody[id^="match"] > tr'));
                    for (const tr of trList) {
                        const tds = Array.from(tr.querySelectorAll('td'));
                        if (tds.length < 10) continue;
                        const tbody = tr.closest('tbody[id^="match"]');
                        const tbodyId = tbody ? (tbody.getAttribute('id') || '') : '';
                        const matchIdM = tbodyId.match(/match(\\d+)/);
                        const teamCell = tds[4];
                        const teamNames = teamCell ? Array.from(teamCell.querySelectorAll('.name a')).map((a) => toText(a)) : [];
                        const fullScoreText = toText(teamCell ? teamCell.querySelector('.vs') : null);
                        const halfScoreText = toText(teamCell ? teamCell.querySelector('.nubFont') : null);
                        const oddsCell = tds[9];
                        const odds = oddsCell ? Array.from(oddsCell.querySelectorAll('em')).map((em) => toText(em)) : [];
                        rows.push({
                            source_match_id: matchIdM ? matchIdM[1] : '',
                            number: toText(tds[0]),
                            league_name: toText(tds[1]),
                            kickoff_text: toText(tds[2]),
                            status_des: toText(tds[3]),
                            home_team: teamNames[0] || '',
                            score_text: fullScoreText,
                            half_score_text: halfScoreText,
                            away_team: teamNames[1] || '',
                            handicap: toText(tds[8]),
                            odds_win: odds[0] || '',
                            odds_draw: odds[1] || '',
                            odds_lose: odds[2] || '',
                        });
                    }
                    return rows;
                }"""
                current_date_str = await page.evaluate(get_date_js)
                if not current_date_str:
                    await browser.close()
                    raise HTTPException(status_code=502, detail="盈球页面日期控件解析失败")

                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                current_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
                table_signature = await page.evaluate(get_table_signature_js)
                if current_date != target_date:
                    step = 1 if target_date > current_date else -1
                    selector = ".calendar .after" if step > 0 else ".calendar .before"
                    for _ in range(45):
                        if current_date == target_date:
                            break
                        prev_signature = table_signature
                        await page.evaluate(
                            """(sel) => {
                                const isVisible = (el) => {
                                    const r = el.getBoundingClientRect();
                                    const st = getComputedStyle(el);
                                    return r.width > 0 && r.height > 0 && r.bottom > 0 &&
                                        r.top < window.innerHeight && st.display !== 'none' &&
                                        st.visibility !== 'hidden' && st.opacity !== '0';
                                };
                                const node = Array.from(document.querySelectorAll(sel)).find(isVisible);
                                if (node) node.click();
                            }""",
                            selector,
                        )
                        # 日期按钮会先更新，表格数据异步更新可能滞后；等待表格出现变化
                        for _ in range(12):
                            await page.wait_for_timeout(300)
                            table_signature = await page.evaluate(get_table_signature_js)
                            if table_signature and table_signature != prev_signature:
                                break
                        new_date_str = await page.evaluate(get_date_js)
                        if new_date_str:
                            current_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
                    if current_date != target_date:
                        await browser.close()
                        # 避免误导入非目标日期数据
                        return []

                # 再次等待表格稳定，避免抓到“按钮日期已切换但表格仍是上一期”的数据
                last_signature = await page.evaluate(get_table_signature_js)
                stable_ticks = 0
                for _ in range(20):
                    await page.wait_for_timeout(400)
                    sig = await page.evaluate(get_table_signature_js)
                    if sig and sig == last_signature:
                        stable_ticks += 1
                    else:
                        stable_ticks = 0
                        if sig:
                            last_signature = sig
                    if stable_ticks >= 3:
                        break

                await page.wait_for_selector("tbody[id^='match'] tr", timeout=15000)
                dom_rows = await page.evaluate(extract_dom_rows_js)
                await browser.close()

                result: List[Dict[str, Any]] = []
                for row in dom_rows or []:
                    try:
                        result.append(_map_yingqiu_dom_row(row, date_str, source_url))
                    except Exception:
                        continue
                if expected_source_match_ids and result:
                    parsed_ids = {
                        str(x.get("source_match_id") or "").strip()
                        for x in result
                        if str(x.get("source_match_id") or "").strip()
                    }
                    overlap = len(parsed_ids & expected_source_match_ids)
                    min_overlap = max(1, int(len(expected_source_match_ids) * 0.6))
                    if overlap < min_overlap:
                        logger.warning(
                            "盈球北单表格与目标日期疑似未对齐: date=%s expected=%s parsed=%s overlap=%s",
                            date_str,
                            len(expected_source_match_ids),
                            len(parsed_ids),
                            overlap,
                        )
                        # 对齐失败时宁可返回空，避免误导入上一期次数据
                        return []
                return result
        except Exception as e:
            logger.warning(f"盈球页面抓取失败，改用静态数据或兜底解析: {e}")

    if static_result:
        return static_result

    # 回退逻辑：直接抓取页面源码（部分日期可能不准确）
    source_url = f"https://www.ttyingqiu.com/bjdc?date={date_str}"
    timeout = aiohttp.ClientTimeout(total=25)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(source_url, headers=headers) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=502, detail=f"抓取盈球北单失败，HTTP {resp.status}")
            html = await resp.text()

    payload = _extract_json_object_after(html, "var file =")
    if not payload:
        raise HTTPException(status_code=502, detail="盈球页面解析失败：未找到比赛数据")
    actual_date_raw = str(payload.get("date") or "").strip()
    actual_date = _normalize_yingqiu_date(actual_date_raw)
    if actual_date and actual_date != date_str:
        # 兜底页返回了非请求日期时，不抛错，避免前端400
        return []
    raw_list = payload.get("matchList") or []
    result: List[Dict[str, Any]] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        try:
            result.append(_map_yingqiu_match(item, source_url, date_str))
        except Exception:
            continue
    return result


@router.post("/import/500w", response_model=UnifiedResponse)
async def import_500w_by_date(
    schedule_date: str = Query(..., description="赛程日期，YYYY-MM-DD"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: dict = Depends(get_current_admin),
):
    try:
        target_date = datetime.strptime(schedule_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="schedule_date 格式错误，必须为 YYYY-MM-DD")

    try:
        parsed = await _fetch_500w_matches(target_date)
        if not parsed:
            return UnifiedResponse(
                success=True,
                data={"schedule_date": schedule_date, "total_parsed": 0, "imported_count": 0, "updated_count": 0},
                message="未抓取到比赛数据",
            )

        imported_count = 0
        updated_count = 0

        # 按日期全量替换500W数据，清理旧解析器写入的脏数据/重复数据
        await db.execute(
            delete(Match).where(
                Match.data_source == "500w",
                Match.match_date == target_date,
            )
        )

        for item in parsed:
            league = await _get_or_create_league(db, item["league_name"])
            home_team = await _get_or_create_team(db, item["home_team"])
            away_team = await _get_or_create_team(db, item["away_team"])

            number = str(item["number"])
            source_match_id = str(item.get("source_match_id") or f"{schedule_date}-{number}-{item['home_team']}-{item['away_team']}")
            source_attrs = {
                "number": number,
                "source_schedule_date": item.get("source_schedule_date"),
                "status_des": "完场" if item.get("status") == MatchStatusEnum.FINISHED.value else None,
                "full_score": (
                    f"{item.get('home_score')}-{item.get('away_score')}"
                    if item.get("home_score") is not None and item.get("away_score") is not None
                    else None
                ),
                "halftime_score": item.get("halftime_score"),
                "handicap_0": item.get("handicap_0"),
                "handicap": item.get("handicap"),
                "odds_nspf_win": item.get("odds_nspf_win"),
                "odds_nspf_draw": item.get("odds_nspf_draw"),
                "odds_nspf_lose": item.get("odds_nspf_lose"),
                "odds_spf_win": item.get("odds_spf_win"),
                "odds_spf_draw": item.get("odds_spf_draw"),
                "odds_spf_lose": item.get("odds_spf_lose"),
                "odds_win": item.get("odds_win"),
                "odds_draw": item.get("odds_draw"),
                "odds_lose": item.get("odds_lose"),
                "source_url": item.get("source_url"),
            }

            match_identifier = f"500W-{schedule_date}-{number}-{hashlib.md5(source_match_id.encode('utf-8')).hexdigest()[:6]}"

            # 防止唯一键冲突：先按源ID/标识删除旧记录再写入（幂等导入）
            await db.execute(
                delete(Match).where(
                    Match.data_source == "500w",
                    Match.source_match_id == source_match_id,
                )
            )
            await db.execute(delete(Match).where(Match.match_identifier == match_identifier))

            db.add(
                Match(
                    match_identifier=match_identifier,
                    league_id=league.id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    match_date=item["kickoff"].date(),
                    match_time=item["kickoff"].time(),
                    scheduled_kickoff=item["kickoff"],
                    status=item.get("status") or MatchStatusEnum.SCHEDULED.value,
                    home_score=item.get("home_score"),
                    away_score=item.get("away_score"),
                    halftime_score=item.get("halftime_score"),
                    is_published=True,
                    data_source="500w",
                    source_match_id=source_match_id,
                    source_attributes=source_attrs,
                    external_source="500w",
                    external_id=number,
                )
            )
            imported_count += 1

        await db.commit()
        return UnifiedResponse(
            success=True,
            data={
                "schedule_date": schedule_date,
                "total_parsed": len(parsed),
                "imported_count": imported_count,
                "updated_count": updated_count,
                "source_url": f"https://trade.500.com/jczq/?date={schedule_date}",
            },
            message=f"抓取完成：新增 {imported_count} 场，更新 {updated_count} 场",
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"500W抓取入库失败: {str(e)}")


def _normalize_other_odds_tabs(raw_tabs: Any, fallback_eu: Any = None) -> Dict[str, List[Dict[str, Any]]]:
    tabs: Dict[str, List[Dict[str, Any]]] = {"eu": [], "asia": [], "goals": []}
    if isinstance(raw_tabs, dict):
        for key in tabs.keys():
            rows = raw_tabs.get(key)
            if isinstance(rows, list):
                tabs[key] = rows
    if not tabs["eu"] and isinstance(fallback_eu, list):
        tabs["eu"] = fallback_eu
    return tabs


def _is_bd_other_odds_tabs_complete(tabs: Dict[str, List[Dict[str, Any]]]) -> bool:
    return bool(tabs.get("eu")) and bool(tabs.get("asia")) and bool(tabs.get("goals"))


def _resolve_match_fixture_id(match: Match, attrs: Dict[str, Any]) -> str:
    fixture_id = (match.source_match_id or "").strip()
    if not fixture_id:
        fixture_id = str(attrs.get("source_match_id") or "").strip()
    return fixture_id


def _should_use_other_odds_cache(
    match: Match,
    tabs: Dict[str, List[Dict[str, Any]]],
    force_refresh: bool,
) -> bool:
    if force_refresh:
        return False
    if not any(tabs.values()):
        return False
    if match.data_source != "yingqiu_bd":
        return True
    return _is_bd_other_odds_tabs_complete(tabs)


async def _fetch_and_cache_other_odds_for_match(
    db: AsyncSession,
    match: Match,
    *,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    attrs = dict(match.source_attributes or {}) if isinstance(match.source_attributes, dict) else {}
    cached_items = attrs.get("other_odds")
    cached_tabs = _normalize_other_odds_tabs(attrs.get("other_odds_tabs"), cached_items)
    fixture_id = _resolve_match_fixture_id(match, attrs)

    if _should_use_other_odds_cache(match, cached_tabs, force_refresh):
        eu_rows = cached_tabs.get("eu") or []
        return {
            "match_id": int(match.id),
            "fixture_id": fixture_id,
            "data_source": match.data_source,
            "total": len(eu_rows),
            "items": eu_rows,
            "tabs": cached_tabs,
            "from_cache": True,
            "cache_reason": "cache",
        }

    if not fixture_id:
        raise HTTPException(status_code=400, detail="该场次缺少源ID，无法抓取其它赔率")

    try:
        if match.data_source == "yingqiu_bd":
            tabs = await _fetch_yingqiu_other_odds_tabs(fixture_id)
        else:
            eu_rows = await _fetch_500w_other_odds(fixture_id)
            tabs = {"eu": eu_rows, "asia": [], "goals": []}
    except Exception:
        # 远程抓取失败时，回退已有缓存，提升可用性
        if any(cached_tabs.values()):
            eu_rows = cached_tabs.get("eu") or []
            return {
                "match_id": int(match.id),
                "fixture_id": fixture_id,
                "data_source": match.data_source,
                "total": len(eu_rows),
                "items": eu_rows,
                "tabs": cached_tabs,
                "from_cache": True,
                "cache_reason": "fallback",
            }
        raise

    items = tabs.get("eu") or []

    # 缓存到source_attributes，减少重复解析
    # NOTE: source_attributes is JSON (non-mutable column), so assign a NEW dict
    # and explicitly mark modified to ensure persistence.
    new_attrs = dict(attrs)
    new_attrs["other_odds"] = items
    new_attrs["other_odds_tabs"] = tabs
    new_attrs["other_odds_cached_at"] = datetime.utcnow().isoformat()
    match.source_attributes = new_attrs
    flag_modified(match, "source_attributes")
    await db.commit()

    return {
        "match_id": int(match.id),
        "fixture_id": fixture_id,
        "data_source": match.data_source,
        "total": len(items),
        "items": items,
        "tabs": tabs,
        "from_cache": False,
        "cache_reason": None,
    }


async def _run_bd_other_odds_prefetch_for_date(schedule_date: str) -> None:
    target_date = _normalize_yingqiu_date(schedule_date)
    if not target_date:
        return

    source_date_expr = func.json_extract(Match.source_attributes, "$.source_schedule_date")

    async with AsyncSessionLocal() as session:
        rows = await session.execute(
            select(Match)
            .where(
                and_(
                    Match.data_source == "yingqiu_bd",
                    source_date_expr == target_date,
                )
            )
            .order_by(Match.id.asc())
        )
        matches = rows.scalars().all()
        if not matches:
            logger.info("BD其它赔率预抓取：%s 无比赛，跳过。", target_date)
            return

        refreshed = 0
        skipped = 0
        failed = 0
        for match in matches:
            last_error: Optional[str] = None
            for attempt in range(2):
                try:
                    result = await _fetch_and_cache_other_odds_for_match(session, match, force_refresh=False)
                    if result.get("from_cache"):
                        skipped += 1
                    else:
                        refreshed += 1
                    last_error = None
                    break
                except HTTPException as exc:
                    await session.rollback()
                    if int(exc.status_code) == 400:
                        skipped += 1
                        logger.warning(
                            "BD其它赔率预抓取跳过 match_id=%s：%s",
                            getattr(match, "id", None),
                            exc.detail,
                        )
                        last_error = None
                        break
                    last_error = str(exc.detail)
                    if attempt == 0:
                        await asyncio.sleep(0.8)
                except Exception as exc:
                    await session.rollback()
                    last_error = str(exc)
                    if attempt == 0:
                        await asyncio.sleep(0.8)

            if last_error:
                failed += 1
                logger.warning(
                    "BD其它赔率预抓取失败 match_id=%s：%s",
                    getattr(match, "id", None),
                    last_error,
                )

        logger.info(
            "BD其它赔率预抓取完成：date=%s, total=%s, refreshed=%s, skipped=%s, failed=%s",
            target_date,
            len(matches),
            refreshed,
            skipped,
            failed,
        )


def _trigger_bd_other_odds_prefetch(schedule_date: Optional[str]) -> None:
    target_date = _normalize_yingqiu_date(schedule_date)
    if not target_date:
        return

    now = datetime.utcnow()
    with _BD_OTHER_ODDS_PREFETCH_GUARD:
        for key, ts in list(_BD_OTHER_ODDS_PREFETCH_LAST_AT.items()):
            if (now - ts).total_seconds() >= 24 * 3600:
                _BD_OTHER_ODDS_PREFETCH_LAST_AT.pop(key, None)

        if target_date in _BD_OTHER_ODDS_PREFETCH_RUNNING:
            return

        last_at = _BD_OTHER_ODDS_PREFETCH_LAST_AT.get(target_date)
        if last_at and (now - last_at).total_seconds() < _BD_OTHER_ODDS_PREFETCH_COOLDOWN_SECONDS:
            return

        _BD_OTHER_ODDS_PREFETCH_RUNNING.add(target_date)
        _BD_OTHER_ODDS_PREFETCH_LAST_AT[target_date] = now

    async def _runner() -> None:
        try:
            await _run_bd_other_odds_prefetch_for_date(target_date)
        except Exception:
            logger.exception("BD其它赔率预抓取任务失败: date=%s", target_date)
        finally:
            with _BD_OTHER_ODDS_PREFETCH_GUARD:
                _BD_OTHER_ODDS_PREFETCH_RUNNING.discard(target_date)
                _BD_OTHER_ODDS_PREFETCH_LAST_AT[target_date] = datetime.utcnow()

    asyncio.create_task(_runner())


@router.get("/{match_id}/other-odds", response_model=UnifiedResponse)
async def get_other_odds(
    match_id: int,
    force_refresh: bool = Query(False, description="是否强制刷新远程赔率"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: dict = Depends(get_current_admin),
):
    try:
        q = await db.execute(select(Match).where(Match.id == match_id))
        match = q.scalar_one_or_none()
        if not match:
            raise HTTPException(status_code=404, detail="比赛不存在")

        payload = await _fetch_and_cache_other_odds_for_match(db, match, force_refresh=force_refresh)
        cache_reason = str(payload.get("cache_reason") or "")
        message = "获取其它赔率成功"
        if payload.get("from_cache"):
            message = "远程获取失败，已返回缓存赔率" if cache_reason == "fallback" else "获取其它赔率成功（缓存）"

        return UnifiedResponse(
            success=True,
            data=payload,
            message=message,
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"获取其它赔率失败: {str(e)}")


@router.post("/import/yingqiu-bd-batch", response_model=UnifiedResponse)
async def import_yingqiu_bd_batch_by_year(
    year: int = Query(..., description="年份，例如 2026"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: dict = Depends(get_current_admin),
):
    """
    批量从盈球获取指定年份所有日期的北单赛程
    """
    if year < 2020 or year > 2030:
        raise HTTPException(status_code=400, detail="年份必须在 2020-2030 之间")
    
    try:
        import asyncio
        from datetime import date as date_class
        
        # 生成该年份所有日期
        start_date = date_class(year, 1, 1)
        end_date = date_class(year, 12, 31)
        
        total_dates = (end_date - start_date).days + 1
        current_date = start_date
        
        total_imported = 0
        total_updated = 0
        total_failed = 0
        failed_dates = []
        
        logger.info(f"开始批量抓取 {year} 年北单赛程，共 {total_dates} 天")
        
        # 遍历每一天
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            try:
                # 抓取该日期的比赛
                parsed = await _fetch_yingqiu_bd_matches(current_date)
                
                if parsed:
                    # 清理该日期的旧数据（使用 source_attributes 记录的源日期）
                    await db.execute(
                        delete(Match).where(
                            Match.data_source == "yingqiu_bd",
                            func.json_extract(Match.source_attributes, "$.source_schedule_date") == date_str,
                        )
                    )
                    
                    # 插入新数据
                    imported_count = 0
                    updated_count = 0
                    
                    for item in parsed:
                        source_match_id = str(item.get("source_match_id") or "")
                        if not source_match_id:
                            continue
                        
                        league = await _get_or_create_league(db, item["league_name"])
                        home_team = await _get_or_create_team(db, item["home_team"])
                        away_team = await _get_or_create_team(db, item["away_team"])
                        
                        number = str(item["number"])
                        source_attrs = {
                            "number": number,
                            "source_schedule_date": item.get("source_schedule_date"),
                            "status_des": item.get("status_des"),
                            "full_score": (
                                f"{item.get('home_score')}-{item.get('away_score')}"
                                if item.get("home_score") is not None and item.get("away_score") is not None
                                else None
                            ),
                            "halftime_score": item.get("halftime_score"),
                            "handicap_0": item.get("handicap_0"),
                            "handicap": item.get("handicap"),
                            "odds_nspf_win": item.get("odds_nspf_win"),
                            "odds_nspf_draw": item.get("odds_nspf_draw"),
                            "odds_nspf_lose": item.get("odds_nspf_lose"),
                            "odds_spf_win": item.get("odds_spf_win"),
                            "odds_spf_draw": item.get("odds_spf_draw"),
                            "odds_spf_lose": item.get("odds_spf_lose"),
                            "odds_win": item.get("odds_win"),
                            "odds_draw": item.get("odds_draw"),
                            "odds_lose": item.get("odds_lose"),
                            "source_url": item.get("source_url"),
                        }
                        
                        match_identifier = f"YQBD-{date_str}-{number}-{hashlib.md5(source_match_id.encode('utf-8')).hexdigest()[:6]}"
                        
                        existing = await db.execute(
                            select(Match).where(Match.match_identifier == match_identifier).limit(1)
                        )
                        existing_match = existing.scalar_one_or_none()
                        
                        if existing_match:
                            existing_match.league_id = league.id
                            existing_match.home_team_id = home_team.id
                            existing_match.away_team_id = away_team.id
                            existing_match.match_date = item["kickoff"].date()
                            existing_match.match_time = item["kickoff"].time()
                            existing_match.scheduled_kickoff = item["kickoff"]
                            existing_match.status = item["status"]
                            existing_match.home_score = item.get("home_score")
                            existing_match.away_score = item.get("away_score")
                            existing_match.halftime_score = item.get("halftime_score")
                            existing_match.is_published = True
                            existing_match.data_source = "yingqiu_bd"
                            existing_match.source_match_id = source_match_id
                            existing_match.source_attributes = source_attrs
                            existing_match.external_source = "yingqiu_bd"
                            existing_match.external_id = number
                            existing_match.updated_at = datetime.utcnow()
                            updated_count += 1
                        else:
                            db.add(
                                Match(
                                    match_identifier=match_identifier,
                                    league_id=league.id,
                                    home_team_id=home_team.id,
                                    away_team_id=away_team.id,
                                    match_date=item["kickoff"].date(),
                                    match_time=item["kickoff"].time(),
                                    scheduled_kickoff=item["kickoff"],
                                    status=item["status"],
                                    home_score=item.get("home_score"),
                                    away_score=item.get("away_score"),
                                    halftime_score=item.get("halftime_score"),
                                    is_published=True,
                                    data_source="yingqiu_bd",
                                    source_match_id=source_match_id,
                                    source_attributes=source_attrs,
                                    external_source="yingqiu_bd",
                                    external_id=number,
                                )
                            )
                            imported_count += 1
                    
                    await db.commit()
                    total_imported += imported_count
                    total_updated += updated_count
                    logger.info(f"日期 {date_str}: 新增 {imported_count} 条，更新 {updated_count} 条")
                else:
                    logger.info(f"日期 {date_str}: 无比赛数据")
                
                # 避免请求过快，休眠1秒
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"抓取日期 {date_str} 失败: {str(e)}")
                total_failed += 1
                failed_dates.append(date_str)
                # 继续下一天
            
            current_date += timedelta(days=1)
        
        message = f"批量抓取完成：共 {total_dates} 天，新增 {total_imported} 条，更新 {total_updated} 条，失败 {total_failed} 天"
        
        return UnifiedResponse(
            success=True,
            data={
                "year": year,
                "total_dates": total_dates,
                "imported_count": total_imported,
                "updated_count": total_updated,
                "failed_count": total_failed,
                "failed_dates": failed_dates[:10]  # 只返回前10个失败日期
            },
            message=message,
        )
    
    except Exception as e:
        logger.error(f"批量抓取失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"批量抓取失败: {str(e)}")


@router.post("/import/yingqiu-bd", response_model=UnifiedResponse)
async def import_yingqiu_bd_by_date(
    schedule_date: str = Query(..., description="赛程日期，YYYY-MM-DD"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: dict = Depends(get_current_admin),
):
    try:
        target_date = datetime.strptime(schedule_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="schedule_date 格式错误，必须为 YYYY-MM-DD")

    try:
        parsed = await _fetch_yingqiu_bd_matches(target_date)
        if not parsed:
            return UnifiedResponse(
                success=True,
                data={"schedule_date": schedule_date, "total_parsed": 0, "imported_count": 0},
                message="未抓取到比赛数据",
            )
        imported_count = 0

        # 按源日期清理后重建，保证幂等
        await db.execute(
            delete(Match).where(
                Match.data_source == "yingqiu_bd",
                func.json_extract(Match.source_attributes, "$.source_schedule_date") == schedule_date,
            )
        )

        for item in parsed:
            league = await _get_or_create_league(db, item["league_name"])
            home_team = await _get_or_create_team(db, item["home_team"])
            away_team = await _get_or_create_team(db, item["away_team"])

            number = str(item["number"])
            source_match_id = str(item["source_match_id"])
            source_attrs = {
                "number": number,
                "source_schedule_date": item.get("source_schedule_date"),
                "status_des": item.get("status_des"),
                "full_score": (
                    f"{item.get('home_score')}-{item.get('away_score')}"
                    if item.get("home_score") is not None and item.get("away_score") is not None
                    else None
                ),
                "halftime_score": item.get("halftime_score"),
                "handicap_0": item.get("handicap_0"),
                "handicap": item.get("handicap"),
                "odds_nspf_win": item.get("odds_nspf_win"),
                "odds_nspf_draw": item.get("odds_nspf_draw"),
                "odds_nspf_lose": item.get("odds_nspf_lose"),
                "odds_spf_win": item.get("odds_spf_win"),
                "odds_spf_draw": item.get("odds_spf_draw"),
                "odds_spf_lose": item.get("odds_spf_lose"),
                "odds_win": item.get("odds_win"),
                "odds_draw": item.get("odds_draw"),
                "odds_lose": item.get("odds_lose"),
                "source_url": item.get("source_url"),
            }

            match_identifier = f"YQBD-{schedule_date}-{number}-{hashlib.md5(source_match_id.encode('utf-8')).hexdigest()[:6]}"
            await db.execute(delete(Match).where(Match.match_identifier == match_identifier))
            await db.execute(
                delete(Match).where(
                    Match.data_source == "yingqiu_bd",
                    Match.source_match_id == source_match_id,
                )
            )

            db.add(
                Match(
                    match_identifier=match_identifier,
                    league_id=league.id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    match_date=item["kickoff"].date(),
                    match_time=item["kickoff"].time(),
                    scheduled_kickoff=item["kickoff"],
                    status=item["status"],
                    home_score=item.get("home_score"),
                    away_score=item.get("away_score"),
                    halftime_score=item.get("halftime_score"),
                    is_published=True,
                    data_source="yingqiu_bd",
                    source_match_id=source_match_id,
                    source_attributes=source_attrs,
                    external_source="yingqiu_bd",
                    external_id=number,
                )
            )
            imported_count += 1

        await db.commit()
        return UnifiedResponse(
            success=True,
            data={
                "schedule_date": schedule_date,
                "total_parsed": len(parsed),
                "imported_count": imported_count,
                "source_url": f"https://www.ttyingqiu.com/bjdc?date={schedule_date}",
            },
            message=f"盈球北单抓取完成：新增 {imported_count} 场",
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"盈球北单抓取入库失败: {str(e)}")
