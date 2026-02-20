from __future__ import annotations

from datetime import date, datetime
import hashlib
import json
import re
from typing import Any, Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, case, delete, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.orm.attributes import flag_modified

from ....database_async import get_async_db
from ....models.match import League, Match, MatchStatusEnum, Team
from ...deps import get_current_admin

try:
    from playwright.async_api import async_playwright
except Exception:
    async_playwright = None


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


router = APIRouter(prefix="/lottery-schedules", tags=["admin-lottery-schedules"])


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
    schedule_type: Optional[str] = Query(None, description="jczq|bd"),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        conditions = []
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
            if date_from and date_to and date_from == date_to:
                conditions.append(source_date_expr == date_from)
            else:
                if date_from:
                    conditions.append(source_date_expr >= date_from)
                if date_to:
                    conditions.append(source_date_expr <= date_to)
        else:
            if date_from and date_to and date_from == date_to:
                target_date = datetime.strptime(date_from, "%Y-%m-%d").date()
                # 竞彩按开赛日期 + 源日期并集，覆盖跨日凌晨场
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

        query = (
            select(Match, League, HomeTeam, AwayTeam)
            .join(League, Match.league_id == League.id, isouter=True)
            .join(HomeTeam, Match.home_team_id == HomeTeam.id, isouter=True)
            .join(AwayTeam, Match.away_team_id == AwayTeam.id, isouter=True)
            .where(and_(*conditions))
            .order_by(desc(Match.scheduled_kickoff))
            .offset((page - 1) * size)
            .limit(size)
        )

        rows = (await db.execute(query)).all()
        items = await _format_match_rows(db, rows)

        total_query = (
            select(func.count(Match.id))
            .join(League, Match.league_id == League.id, isouter=True)
            .where(and_(*conditions))
        )
        total = (await db.execute(total_query)).scalar() or 0

        return UnifiedResponse(
            success=True,
            data={
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
            },
            message="获取竞彩赛程列表成功",
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
                "source_schedule_date": schedule_date.strftime("%Y-%m-%d"),
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


async def _fetch_yingqiu_other_odds(match_id: str) -> List[Dict[str, Any]]:
    def _map_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        rows = ((payload or {}).get("model") or {}).get("list") or []
        result: List[Dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            updated_at = "-"
            ts = row.get("createTime")
            try:
                if ts is not None:
                    tsv = int(ts)
                    if tsv > 10**12:
                        tsv = tsv // 1000
                    updated_at = datetime.fromtimestamp(tsv).strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass
            result.append(
                {
                    "company": str(row.get("providerName") or "-"),
                    "updated_at": updated_at,
                    "init_win": _to_float(row.get("firstWinOdds")),
                    "init_draw": _to_float(row.get("firstDrawOdds")),
                    "init_lose": _to_float(row.get("firstLoseOdds")),
                    "instant_win": _to_float(row.get("winOdds")),
                    "instant_draw": _to_float(row.get("drawOdds")),
                    "instant_lose": _to_float(row.get("loseOdds")),
                }
            )
        return result

    # 先按 match_id 直连接口，适用于已是 leagueMatchId 的场景
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
            if resp.status == 200:
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
                    mapped = _map_payload(payload)
                    if mapped:
                        return mapped
                except Exception:
                    pass

    # 兜底：source_match_id 若是 qtMatchId，则用浏览器打开详情页并拦截真实赔率接口
    if async_playwright is None:
        raise HTTPException(status_code=502, detail="抓取盈球其它赔率失败：直连失败且未安装Playwright")

    detail_url = f"https://www.ttyingqiu.com/live/zq/matchDetail/oz/{match_id}"
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page(viewport={"width": 1366, "height": 900})
            async with page.expect_response(
                lambda r: "ftAicaiAllEuropeOdds?matchId=" in r.url and r.request.method == "GET",
                timeout=40000,
            ) as response_info:
                await page.goto(detail_url, wait_until="networkidle", timeout=120000)
            resp = await response_info.value
            if resp.status != 200:
                await browser.close()
                raise HTTPException(status_code=502, detail=f"抓取盈球其它赔率失败，HTTP {resp.status}")
            payload = await resp.json()
            await browser.close()
            mapped = _map_payload(payload)
            if mapped:
                return mapped
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"抓取盈球其它赔率失败: {str(e)}")

    raise HTTPException(status_code=502, detail="抓取盈球其它赔率失败：未返回有效赔率数据")


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


def _map_yingqiu_match(item: Dict[str, Any], source_url: str, schedule_date: str) -> Dict[str, Any]:
    match_date = str(item.get("matchDate") or schedule_date)
    match_time = str(item.get("matchTime") or "00:00")
    kickoff = datetime.strptime(f"{match_date} {match_time}", "%Y-%m-%d %H:%M")

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

    raw_score = item.get("score")
    if isinstance(raw_score, list):
        full_score_raw = raw_score[0] if len(raw_score) > 0 else ""
        half_score_raw_from_list = raw_score[1] if len(raw_score) > 1 else ""
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
    hs = _to_int(item.get("homeScore"))
    as_ = _to_int(item.get("awayScore"))
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
        "odds_nspf_win": odds_win,
        "odds_nspf_draw": odds_draw,
        "odds_nspf_lose": odds_lose,
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


async def _fetch_yingqiu_bd_matches(schedule_date: date) -> List[Dict[str, Any]]:
    date_str = schedule_date.strftime("%Y-%m-%d")
    source_url = "https://www.ttyingqiu.com/bjdc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.ttyingqiu.com/bjdc",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    # 首选：按日期直连静态JSON，不依赖页面切换
    static_json_url = f"https://www.ttyingqiu.com/static/no_cache/league/zc/jsbf/ttyq2020/bd/jsbf_{date_str}.json"
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(static_json_url, headers=headers) as resp:
                if resp.status == 200:
                    payload = await resp.json(content_type=None)
                    if isinstance(payload, dict):
                        actual_date = str(payload.get("date") or "").strip()
                        if actual_date == date_str:
                            raw_list = payload.get("matchList") or []
                            result: List[Dict[str, Any]] = []
                            for item in raw_list:
                                if not isinstance(item, dict):
                                    continue
                                try:
                                    result.append(_map_yingqiu_match(item, static_json_url, date_str))
                                except Exception:
                                    continue
                            return result
    except Exception:
        # 静态JSON失败时再走页面抓取兜底
        pass

    # 优先使用真实页面日期切换并解析完整表格
    if async_playwright is not None:
        try:
            async with async_playwright() as p:
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
                current_date_str = await page.evaluate(get_date_js)
                if not current_date_str:
                    await browser.close()
                    raise HTTPException(status_code=502, detail="盈球页面日期控件解析失败")

                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                current_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
                if current_date != target_date:
                    step = 1 if target_date > current_date else -1
                    selector = ".calendar .after" if step > 0 else ".calendar .before"
                    for _ in range(45):
                        if current_date == target_date:
                            break
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
                        await page.wait_for_timeout(900)
                        new_date_str = await page.evaluate(get_date_js)
                        if new_date_str:
                            current_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
                    if current_date != target_date:
                        await browser.close()
                        # 避免误导入非目标日期数据
                        return []

                await page.wait_for_timeout(900)
                dom_rows = await page.evaluate(
                    """() => {
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
                            const teamNames = teamCell ? Array.from(teamCell.querySelectorAll('.name a')).map(a => toText(a)) : [];
                            const oddsCell = tds[9];
                            const odds = oddsCell ? Array.from(oddsCell.querySelectorAll('em')).map(em => toText(em)).filter(Boolean) : [];
                            rows.push({
                                source_match_id: matchIdM ? matchIdM[1] : '',
                                number: toText(tds[0]),
                                league_name: toText(tds[1]),
                                kickoff_text: toText(tds[2]),
                                status_des: toText(tds[3]),
                                home_team: teamNames[0] || '',
                                score_text: toText(tds[5]),
                                away_team: teamNames[1] || '',
                                handicap: toText(tds[8]),
                                odds_win: odds[0] || '',
                                odds_draw: odds[1] || '',
                                odds_lose: odds[2] || '',
                            });
                        }
                        return rows;
                    }"""
                )
                await browser.close()

                result: List[Dict[str, Any]] = []
                for row in dom_rows or []:
                    try:
                        source_match_id = str(row.get("source_match_id") or row.get("number") or "").strip()
                        home_team = str(row.get("home_team") or "").strip()
                        away_team = str(row.get("away_team") or "").strip()
                        if not source_match_id:
                            source_match_id = f"{date_str}-{home_team}-{away_team}"
                        kickoff = _parse_yingqiu_kickoff(str(row.get("kickoff_text") or ""), date_str)
                        odds_win = _to_float(str(row.get("odds_win") or ""))
                        odds_draw = _to_float(str(row.get("odds_draw") or ""))
                        odds_lose = _to_float(str(row.get("odds_lose") or ""))
                        handicap = _normalize_handicap_text(str(row.get("handicap") or ""), "0")
                        status_des = str(row.get("status_des") or "")
                        score_text = str(row.get("score_text") or "")
                        hs, as_ = _extract_score_pair(score_text)
                        halftime_score = _extract_halftime_text(score_text)
                        result.append(
                            {
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
                                "source_schedule_date": date_str,
                                "source_url": source_url,
                            }
                        )
                    except Exception:
                        continue
                return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"盈球页面抓取失败: {str(e)}")

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
    actual_date = str(payload.get("date") or "").strip()
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

        attrs = dict(match.source_attributes or {}) if isinstance(match.source_attributes, dict) else {}
        cached_items = attrs.get("other_odds")
        if (
            not force_refresh
            and isinstance(cached_items, list)
            and len(cached_items) > 0
        ):
            return UnifiedResponse(
                success=True,
                data={
                    "match_id": match_id,
                    "fixture_id": str(match.source_match_id or ""),
                    "data_source": match.data_source,
                    "total": len(cached_items),
                    "items": cached_items,
                    "from_cache": True,
                },
                message="获取其它赔率成功（缓存）",
            )

        fixture_id = (match.source_match_id or "").strip()
        if not fixture_id:
            fixture_id = str(attrs.get("source_match_id") or "").strip()
        if not fixture_id:
            raise HTTPException(status_code=400, detail="该场次缺少源ID，无法抓取其它赔率")

        try:
            if match.data_source == "yingqiu_bd":
                items = await _fetch_yingqiu_other_odds(fixture_id)
            else:
                items = await _fetch_500w_other_odds(fixture_id)
        except Exception:
            # 远程抓取失败时，回退已有缓存，提升可用性
            if isinstance(cached_items, list) and len(cached_items) > 0:
                return UnifiedResponse(
                    success=True,
                    data={
                        "match_id": match_id,
                        "fixture_id": fixture_id,
                        "data_source": match.data_source,
                        "total": len(cached_items),
                        "items": cached_items,
                        "from_cache": True,
                    },
                    message="远程获取失败，已返回缓存赔率",
                )
            raise

        # 缓存到source_attributes，减少重复解析
        # NOTE: source_attributes is JSON (non-mutable column), so assign a NEW dict
        # and explicitly mark modified to ensure persistence.
        new_attrs = dict(attrs)
        new_attrs["other_odds"] = items
        new_attrs["other_odds_cached_at"] = datetime.utcnow().isoformat()
        match.source_attributes = new_attrs
        flag_modified(match, "source_attributes")
        await db.commit()

        return UnifiedResponse(
            success=True,
            data={
                "match_id": match_id,
                "fixture_id": fixture_id,
                "data_source": match.data_source,
                "total": len(items),
                "items": items,
                "from_cache": False,
            },
            message="获取其它赔率成功",
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"获取其它赔率失败: {str(e)}")


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
