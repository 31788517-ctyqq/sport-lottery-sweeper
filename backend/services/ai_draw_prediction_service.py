import json
import math
import time
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, aliased, joinedload

from backend.models.match import League, Match, Team
from backend.models.matches import FootballMatch


def _to_float(value: Any) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _safe_attrs(source_attributes: Any) -> Dict[str, Any]:
    if isinstance(source_attributes, dict):
        return source_attributes
    if isinstance(source_attributes, str) and source_attributes:
        try:
            return json.loads(source_attributes)
        except json.JSONDecodeError:
            return {}
    return {}


def _json_attr_text_expr(db: Session, column, key: str):
    """Extract a JSON text attribute in a dialect-safe way."""
    bind = getattr(db, "bind", None)
    dialect_name = ((bind.dialect.name if bind and bind.dialect else "") or "").lower()
    if dialect_name.startswith("postgres"):
        return column.op("->>")(key)
    return func.json_extract(column, f"$.{key}")


def _extract_total_goals_line(attrs: Dict[str, Any]) -> Optional[float]:
    for key in ("total_goals_line", "goal_line", "ou_line", "over_under", "total_goals"):
        if key in attrs:
            return _to_float(attrs.get(key))
    return None


def _extract_crown_goals_line_from_other_odds(attrs: Dict[str, Any]) -> Optional[float]:
    raw_tabs = attrs.get("other_odds_tabs")
    if isinstance(raw_tabs, str):
        try:
            raw_tabs = json.loads(raw_tabs)
        except Exception:
            raw_tabs = None
    if not isinstance(raw_tabs, dict):
        return None

    goals_rows = raw_tabs.get("goals")
    if not isinstance(goals_rows, list) or not goals_rows:
        return None

    def _is_crown_company(row: Dict[str, Any]) -> bool:
        company = str(row.get("company") or "").strip()
        provider_id = str(row.get("provider_id") or row.get("providerId") or "").strip()
        if provider_id == "629":
            return True
        if not company:
            return False
        # 盈球常见显示会做脱敏（如“皇*”），因此按“皇”前缀匹配
        return ("皇冠" in company) or company.startswith("皇")

    crown_rows = [x for x in goals_rows if isinstance(x, dict) and _is_crown_company(x)]
    if not crown_rows:
        return None

    for row in crown_rows:
        for line_key in ("instant_line", "init_line", "line", "instant_handicap", "init_handicap"):
            line_value = _parse_daxiao_line(str(row.get(line_key) or "").strip())
            if line_value is not None:
                return line_value
    return None


def _infer_total_goals_line_from_draw_odds(odds_draw: Optional[float]) -> Optional[float]:
    if odds_draw is None or odds_draw <= 1:
        return None
    draw_prob = 1.0 / odds_draw
    if draw_prob >= 0.33:
        return 2.0
    if draw_prob >= 0.31:
        return 2.15
    if draw_prob >= 0.29:
        return 2.3
    if draw_prob >= 0.27:
        return 2.45
    if draw_prob >= 0.25:
        return 2.6
    if draw_prob >= 0.23:
        return 2.75
    return 2.9


def _calc_a(odds_win: Optional[float], odds_lose: Optional[float]) -> Optional[float]:
    if odds_win is None or odds_lose is None or odds_win <= 0 or odds_lose <= 0:
        return None
    return math.exp(-3.0 * abs(math.log(odds_win / odds_lose)))


def _calc_b(odds_draw: Optional[float]) -> Optional[float]:
    if odds_draw is None or odds_draw <= 0:
        return None
    return math.exp(-((odds_draw - 3.05) / 0.45) ** 2)


def _calc_c(total_goals_line: Optional[float]) -> Optional[float]:
    if total_goals_line is None:
        return None
    return _clamp(math.exp(-0.9 * (total_goals_line - 2.2)))


def _calc_d(attrs: Dict[str, Any]) -> float:
    raw = _to_float(
        attrs.get("motivation_index")
        or attrs.get("draw_motivation")
        or attrs.get("ai_draw_motivation")
    )
    if raw is None:
        return 0.0
    return _clamp(raw, -1.0, 1.0)


def _normalize_team_name(value: Any) -> str:
    return str(value or "").strip()


def _extract_power_value(attrs: Dict[str, Any], *keys: str) -> Optional[float]:
    for key in keys:
        if key in attrs and attrs.get(key) is not None:
            return _to_float(attrs.get(key))
    return None


def _calc_a_from_power(home_power: Optional[float], away_power: Optional[float]) -> Optional[float]:
    if home_power is None or away_power is None or home_power <= 0 or away_power <= 0:
        return None
    return math.exp(-3.0 * abs(math.log(home_power / away_power)))


def _load_beidan_power_map(db: Session, rows: List[Tuple[Match, Optional[League], Optional[Team], Optional[Team]]]) -> Dict[str, Dict[Any, Dict[str, Any]]]:
    dates: List[date] = []
    line_ids: List[int] = []
    for match, _, _, _ in rows:
        kickoff = _resolve_kickoff(match)
        if kickoff:
            dates.append(kickoff.date())
        attrs = _safe_attrs(match.source_attributes)
        number_raw = attrs.get("number") or attrs.get("lineId") or attrs.get("line_id")
        if number_raw is not None:
            try:
                line_id = int(str(number_raw).lstrip("0") or "0")
                if line_id > 0:
                    line_ids.append(line_id)
            except Exception:
                continue
    if not dates and not line_ids:
        return {"by_team_date": {}, "by_period_line": {}}

    date_keys = {d.isoformat() for d in dates}
    conditions = []
    if date_keys:
        conditions.append(func.date(FootballMatch.match_time).in_(date_keys))
    if line_ids:
        conditions.append(FootballMatch.line_id.in_(line_ids))
    if not conditions:
        return {"by_team_date": {}, "by_period_line": {}}

    query = (
        db.query(FootballMatch)
        .filter(FootballMatch.data_source == "100qiu")
        .filter(or_(*conditions))
    )
    records = query.all()

    by_team_date: Dict[Any, Dict[str, Any]] = {}
    by_period_line: Dict[Any, Dict[str, Any]] = {}

    for record in records:
        attrs = _safe_attrs(record.source_attributes)
        home_power = _extract_power_value(attrs, "homePower", "home_power")
        away_power = _extract_power_value(attrs, "guestPower", "guest_power", "away_power")
        if home_power is None or away_power is None:
            continue
        date_key = record.match_time.date().isoformat() if record.match_time else ""
        home_team = _normalize_team_name(record.home_team)
        away_team = _normalize_team_name(record.away_team)
        info = {
            "home_power": home_power,
            "away_power": away_power,
            "date_time": str(record.date_time) if record.date_time is not None else None,
            "line_id": str(record.line_id) if record.line_id is not None else None,
            "match_date": date_key or None,
            "home_team": home_team,
            "away_team": away_team,
        }
        if date_key and home_team and away_team:
            by_team_date[(date_key, home_team, away_team)] = info
        if info["date_time"] and info["line_id"]:
            by_period_line[(info["date_time"], info["line_id"])] = info

    return {"by_team_date": by_team_date, "by_period_line": by_period_line}


def _resolve_beidan_info(match: Match, attrs: Dict[str, Any], beidan_maps: Dict[str, Dict[Any, Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
    kickoff = _resolve_kickoff(match)
    date_key = kickoff.date().isoformat() if kickoff else ""
    home_name = _normalize_team_name(match.home_team.name if isinstance(match.home_team, Team) else match.home_team)
    away_name = _normalize_team_name(match.away_team.name if isinstance(match.away_team, Team) else match.away_team)

    by_team_date = beidan_maps.get("by_team_date", {})
    if date_key and home_name and away_name:
        info = by_team_date.get((date_key, home_name, away_name))
        if info:
            return info

    number_raw = attrs.get("number") or attrs.get("lineId") or attrs.get("line_id")
    line_id = str(number_raw).lstrip("0") if number_raw is not None else None
    if line_id:
        by_period_line = beidan_maps.get("by_period_line", {})
        candidates = []
        for (period, line), info in by_period_line.items():
            if str(line) == line_id:
                candidates.append(info)
        if candidates:
            if date_key:
                for info in candidates:
                    if info.get("match_date") == date_key:
                        return info
            candidates.sort(key=lambda x: int(x.get("date_time") or 0), reverse=True)
            return candidates[0]

    return None


_DAXIAO_CACHE: Dict[str, Dict[str, Any]] = {}


def _parse_daxiao_line(token: str) -> Optional[float]:
    text = str(token or "").strip()
    if not text:
        return None
    if "/" in text:
        parts = [p for p in text.split("/") if p]
        nums = [_to_float(p) for p in parts]
        nums = [n for n in nums if n is not None]
        if nums:
            return sum(nums) / len(nums)
        return None
    return _to_float(text)


def _extract_daxiao_map(html: str) -> Dict[str, Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.select("table")
    target_table = None
    for table in tables:
        header_text = " ".join(th.get_text(" ", strip=True) for th in table.select("th"))
        if "场次" in header_text and ("大小指数" in header_text or "大小球" in header_text):
            target_table = table
            break
    if target_table is None and tables:
        target_table = tables[-1]

    by_number: Dict[str, float] = {}
    by_team: Dict[str, float] = {}

    def _extract_line_from_cell(text: str) -> Optional[float]:
        for token in re.findall(r"\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?(?=\s*\(球\))", text or ""):
            value = _parse_daxiao_line(token)
            if value is not None:
                return value
        for token in re.findall(r"\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?", text or ""):
            value = _parse_daxiao_line(token)
            if value is not None and 1.0 <= value <= 5.0:
                return value
        return None

    rows = target_table.select("tbody tr") if target_table else []
    for idx, row in enumerate(rows):
        cells = [c.get_text(" ", strip=True) for c in row.find_all("td")]
        if len(cells) < 7:
            continue
        if not re.match(r"^\d{1,3}$", cells[0] or ""):
            continue

        number = cells[0].lstrip("0") or cells[0]
        home_team = _normalize_team_name(cells[4]) if len(cells) > 4 else ""
        away_team = _normalize_team_name(cells[6]) if len(cells) > 6 else ""

        total_goals_line = None
        if idx + 1 < len(rows):
            next_cells = [c.get_text(" ", strip=True) for c in rows[idx + 1].find_all("td")]
            if len(next_cells) >= 5:
                total_goals_line = _extract_line_from_cell(next_cells[4])
        if total_goals_line is None and len(cells) >= 12:
            total_goals_line = _extract_line_from_cell(cells[11])

        if total_goals_line is None:
            continue
        by_number[number] = total_goals_line
        if home_team and away_team:
            by_team[f"{home_team}__{away_team}"] = total_goals_line

    return {"by_number": by_number, "by_team": by_team}


def _get_daxiao_map(period: Optional[str]) -> Optional[Dict[str, Dict[str, Any]]]:
    if not period:
        return None
    cached = _DAXIAO_CACHE.get(period)
    if cached and (time.time() - cached.get("ts", 0)) < 3600:
        return cached.get("data")

    url = "https://odds.500.com/daxiao_zqdc.shtml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://odds.500.com/",
        "Origin": "https://odds.500.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-User": "?1",
    }
    session = requests.Session()
    session.trust_env = False
    session.headers.update(headers)

    proxies = {"http": None, "https": None}
    try:
        try:
            session.get("https://odds.500.com/", timeout=10, proxies=proxies)
        except Exception:
            pass
        resp = session.get(url, timeout=15, proxies=proxies)
        if resp.status_code == 403:
            resp = session.get(url, headers={"Referer": "https://odds.500.com/"}, timeout=15, proxies=proxies)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or resp.encoding or "gbk"
    except Exception:
        return None

    html = resp.text
    data = _extract_daxiao_map(html)
    _DAXIAO_CACHE[period] = {"ts": time.time(), "data": data}
    return data


def _load_500w_daxiao_map_from_db(db: Session, target_date: date) -> Dict[str, Dict[str, Any]]:
    date_key = target_date.isoformat()
    query = (
        db.query(Match)
        .options(joinedload(Match.home_team), joinedload(Match.away_team))
        .filter(Match.data_source == "500w")
        .filter(
            or_(
                Match.match_date == target_date,
                _json_attr_text_expr(db, Match.source_attributes, "source_schedule_date") == date_key,
            )
        )
    )
    matches = query.all()

    by_number: Dict[str, float] = {}
    by_team: Dict[str, float] = {}

    for match in matches:
        attrs = _safe_attrs(match.source_attributes)
        number_raw = (
            attrs.get("number")
            or match.external_id
            or attrs.get("lineId")
            or attrs.get("line_id")
            or attrs.get("line")
        )
        line_value = _to_float(
            attrs.get("daxiao_crown_line")
            or attrs.get("total_goals_line_crown")
            or attrs.get("daxiao_crown")
            or attrs.get("total_goals_line")
        )
        if line_value is None:
            continue
        if number_raw is not None:
            number_key = str(number_raw).lstrip("0") or str(number_raw)
            by_number[number_key] = line_value
        home_name = _normalize_team_name(match.home_team.name if match.home_team else getattr(match, "home_team", ""))
        away_name = _normalize_team_name(match.away_team.name if match.away_team else getattr(match, "away_team", ""))
        if home_name and away_name:
            by_team[f"{home_name}__{away_name}"] = line_value

    return {"by_number": by_number, "by_team": by_team}


def _persist_500w_daxiao_to_db(db: Session, target_date: date, daxiaosfc_map: Dict[str, Dict[str, Any]]) -> int:
    if not daxiaosfc_map:
        return 0
    by_number = daxiaosfc_map.get("by_number", {})
    by_team = daxiaosfc_map.get("by_team", {})
    if not by_number and not by_team:
        return 0

    date_key = target_date.isoformat()
    query = (
        db.query(Match)
        .options(joinedload(Match.home_team), joinedload(Match.away_team))
        .filter(Match.data_source == "500w")
        .filter(
            or_(
                Match.match_date == target_date,
                _json_attr_text_expr(db, Match.source_attributes, "source_schedule_date") == date_key,
            )
        )
    )
    matches = query.all()

    updated = 0
    for match in matches:
        attrs = _safe_attrs(match.source_attributes)
        number_raw = (
            attrs.get("number")
            or match.external_id
            or attrs.get("lineId")
            or attrs.get("line_id")
            or attrs.get("line")
        )
        line_value = None
        if number_raw is not None:
            number_key = str(number_raw).lstrip("0") or str(number_raw)
            line_value = by_number.get(number_key)
        if line_value is None:
            home_name = _normalize_team_name(match.home_team.name if match.home_team else getattr(match, "home_team", ""))
            away_name = _normalize_team_name(match.away_team.name if match.away_team else getattr(match, "away_team", ""))
            if home_name and away_name:
                line_value = by_team.get(f"{home_name}__{away_name}")
        if line_value is None:
            continue
        attrs = dict(attrs)
        attrs["daxiao_crown_line"] = line_value
        attrs["daxiao_crown_source"] = "500w_zqdc"
        match.source_attributes = attrs
        updated += 1

    if updated:
        db.commit()
    return updated


def _resolve_total_goals_line_from_daxiao(
    attrs: Dict[str, Any],
    match: Match,
    home_team: Optional[str],
    away_team: Optional[str],
    daxiaosfc_map: Optional[Dict[str, Dict[str, Any]]],
) -> Optional[float]:
    if not daxiaosfc_map:
        return None

    number_raw = attrs.get("number") or attrs.get("lineId") or attrs.get("line_id")
    if number_raw is not None:
        number_key = str(number_raw).lstrip("0") or str(number_raw)
        by_number = daxiaosfc_map.get("by_number", {})
        if number_key in by_number:
            return by_number[number_key]

    home_name = _normalize_team_name(home_team or "")
    away_name = _normalize_team_name(away_team or "")
    if home_name and away_name:
        by_team = daxiaosfc_map.get("by_team", {})
        key = f"{home_name}__{away_name}"
        if key in by_team:
            return by_team[key]

    return None


RULES_CONFIG_KEY = "ai_draw_rules"
OVERRIDE_CONFIG_KEY = "ai_draw_overrides"
DEFAULT_RULES = {
    "base": 0.248,
    "weights": {"a": 0.32, "b": 0.24, "c": 0.28, "d": 0.16},
    "thresholds": {"high": 0.36, "midHigh": 0.31, "normal": 0.26, "low": 0.22},
}


def _match_rules_key(match_id: str) -> str:
    return f"{RULES_CONFIG_KEY}:{match_id}"


def _match_override_key(match_id: str) -> str:
    return f"{OVERRIDE_CONFIG_KEY}:{match_id}"


def _normalize_rules(rules: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    data = rules or {}
    base = _to_float(data.get("base"))
    weights = data.get("weights") or {}
    thresholds = data.get("thresholds") or {}

    def _num(value: Any, fallback: float) -> float:
        num = _to_float(value)
        if num is None:
            return fallback
        return num

    normalized = {
        "base": _clamp(_num(base, DEFAULT_RULES["base"]), 0.0, 1.0),
        "weights": {
            "a": _clamp(_num(weights.get("a"), DEFAULT_RULES["weights"]["a"]), 0.0, 1.0),
            "b": _clamp(_num(weights.get("b"), DEFAULT_RULES["weights"]["b"]), 0.0, 1.0),
            "c": _clamp(_num(weights.get("c"), DEFAULT_RULES["weights"]["c"]), 0.0, 1.0),
            "d": _clamp(_num(weights.get("d"), DEFAULT_RULES["weights"]["d"]), 0.0, 1.0),
        },
        "thresholds": {
            "high": _clamp(_num(thresholds.get("high"), DEFAULT_RULES["thresholds"]["high"]), 0.0, 1.0),
            "midHigh": _clamp(_num(thresholds.get("midHigh"), DEFAULT_RULES["thresholds"]["midHigh"]), 0.0, 1.0),
            "normal": _clamp(_num(thresholds.get("normal"), DEFAULT_RULES["thresholds"]["normal"]), 0.0, 1.0),
            "low": _clamp(_num(thresholds.get("low"), DEFAULT_RULES["thresholds"]["low"]), 0.0, 1.0),
        },
    }
    return normalized


def _calc_prob_draw(a: Optional[float], b: Optional[float], c: Optional[float], d: Optional[float], rules: Dict[str, Any]) -> float:
    a_val = a if a is not None else 0.0
    b_val = b if b is not None else 0.0
    c_val = c if c is not None else 0.0
    d_val = d if d is not None else 0.0
    base = rules["base"]
    weights = rules["weights"]
    prob = base + weights["a"] * a_val + weights["b"] * b_val + weights["c"] * c_val + weights["d"] * d_val
    return _clamp(prob, 0.0, 1.0)


def _recommend_label(prob: float, rules: Dict[str, Any]) -> str:
    thresholds = rules["thresholds"]
    if prob >= thresholds["high"]:
        return "高平"
    if prob >= thresholds["midHigh"]:
        return "偏高"
    if prob >= thresholds["normal"]:
        return "正常"
    if prob >= thresholds["low"]:
        return "偏低"
    return "不推荐"


def _extract_odds(attrs: Dict[str, Any]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    odds_win = _to_float(attrs.get("odds_win") or attrs.get("odds_nspf_win") or attrs.get("odds_spf_win"))
    odds_draw = _to_float(attrs.get("odds_draw") or attrs.get("odds_nspf_draw") or attrs.get("odds_spf_draw"))
    odds_lose = _to_float(attrs.get("odds_lose") or attrs.get("odds_nspf_lose") or attrs.get("odds_spf_lose"))
    return odds_win, odds_draw, odds_lose


def _resolve_kickoff(match: Match) -> Optional[datetime]:
    kickoff = getattr(match, "scheduled_kickoff", None)
    if kickoff:
        return kickoff
    match_date = getattr(match, "match_date", None)
    match_time = getattr(match, "match_time", None)
    if match_date is not None and match_time is not None:
        return datetime.combine(match_date, match_time)
    return None


def _is_finished_match(match: Match, attrs: Dict[str, Any]) -> bool:
    status = getattr(match, "status", None)
    status_text = status.value if hasattr(status, "value") else str(status or "")
    if status_text == "finished":
        return True
    status_des = str(attrs.get("status_des") or attrs.get("status") or "")
    if any(x in status_des for x in ["完场", "已结束", "已完成", "结束"]):
        return True
    return False


def _build_payload(
    attrs: Dict[str, Any],
    odds_win: Optional[float],
    odds_draw: Optional[float],
    odds_lose: Optional[float],
    total_goals_line_override: Optional[float] = None,
    total_goals_line_source_override: Optional[str] = None,
    allow_attr_total_goals: bool = True,
    allow_infer_total_goals: bool = True,
    power_pair: Optional[Tuple[Optional[float], Optional[float]]] = None,
    power_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    total_goals_line_source = total_goals_line_source_override or ("500w_crown" if total_goals_line_override is not None else None)
    total_goals_line = (
        total_goals_line_override
        if total_goals_line_override is not None
        else (_extract_total_goals_line(attrs) if allow_attr_total_goals else None)
    )
    if total_goals_line is not None and total_goals_line_source is None:
        total_goals_line_source = "source_attributes"
    inferred_total_goals = None
    if total_goals_line is None and allow_infer_total_goals:
        inferred_total_goals = _infer_total_goals_line_from_draw_odds(odds_draw)
        total_goals_line = inferred_total_goals
        if inferred_total_goals is not None:
            total_goals_line_source = "inferred_from_draw_odds"

    a_index = None
    a_index_source = None
    a_inputs = None
    if power_pair:
        a_index = _calc_a_from_power(power_pair[0], power_pair[1])
        if power_pair[0] is not None and power_pair[1] is not None:
            a_index_source = "100qiu_power"
            a_inputs = {
                "home_power": power_pair[0],
                "away_power": power_pair[1],
            }
            if power_info:
                if power_info.get("date_time") is not None:
                    a_inputs["date_time"] = power_info.get("date_time")
                if power_info.get("line_id") is not None:
                    a_inputs["line_id"] = power_info.get("line_id")
                if power_info.get("home_team"):
                    a_inputs["home_team"] = power_info.get("home_team")
                if power_info.get("away_team"):
                    a_inputs["away_team"] = power_info.get("away_team")

    b_index = _calc_b(odds_draw)
    c_index = _calc_c(total_goals_line)
    d_index = _calc_d(attrs)

    flags: List[str] = []
    if odds_win is None or odds_lose is None:
        flags.append("odds_win_or_lose_missing")
    if odds_draw is None:
        flags.append("odds_draw_missing")
    if total_goals_line is None:
        flags.append("total_goals_line_missing")
    if inferred_total_goals is not None:
        flags.append("total_goals_line_inferred_from_draw_odds")
    if power_pair and power_pair[0] is not None and power_pair[1] is not None:
        flags.append("a_index_from_beidan_power")

    return {
        "odds": {"win": odds_win, "draw": odds_draw, "lose": odds_lose},
        "total_goals_line": total_goals_line,
        "total_goals_line_source": total_goals_line_source,
        "inferred_total_goals_line": inferred_total_goals,
        "a_index_source": a_index_source,
        "a_inputs": a_inputs,
        "indices": {
            "a": a_index,
            "b": b_index,
            "c": c_index,
            "d": d_index,
        },
        "flags": flags,
        "source_attributes": attrs,
    }


def _build_result_row(
    match: Match,
    league: Optional[League],
    home_team: Optional[Team],
    away_team: Optional[Team],
    rules: Dict[str, Any],
    overrides: Optional[Dict[str, Any]] = None,
    beidan_info: Optional[Dict[str, Any]] = None,
    daxiaosfc_map: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    attrs = _safe_attrs(match.source_attributes)
    odds_win, odds_draw, odds_lose = _extract_odds(attrs)
    home_name = home_team.name if home_team else (match.home_team.name if getattr(match, "home_team", None) else None)
    away_name = away_team.name if away_team else (match.away_team.name if getattr(match, "away_team", None) else None)
    total_goals_line_override = None
    total_goals_line_source_override = None
    allow_attr_total_goals = True
    allow_infer_total_goals = True

    if getattr(match, "data_source", "") == "yingqiu_bd":
        # C 指数仅使用：北单详情 -> 进球数 -> 皇冠公司盘口
        total_goals_line_override = _extract_crown_goals_line_from_other_odds(attrs)
        total_goals_line_source_override = "yingqiu_goals_crown" if total_goals_line_override is not None else None
        allow_attr_total_goals = False
        allow_infer_total_goals = False
    else:
        total_goals_line_override = _resolve_total_goals_line_from_daxiao(
            attrs,
            match,
            home_name,
            away_name,
            daxiaosfc_map,
        )
        if total_goals_line_override is not None:
            total_goals_line_source_override = "500w_crown"

    power_pair = None
    if beidan_info:
        power_pair = (beidan_info.get("home_power"), beidan_info.get("away_power"))
    payload = _build_payload(
        attrs,
        odds_win,
        odds_draw,
        odds_lose,
        total_goals_line_override=total_goals_line_override,
        total_goals_line_source_override=total_goals_line_source_override,
        allow_attr_total_goals=allow_attr_total_goals,
        allow_infer_total_goals=allow_infer_total_goals,
        power_pair=power_pair,
        power_info=beidan_info,
    )

    a_index = payload["indices"]["a"]
    b_index = payload["indices"]["b"]
    c_index = payload["indices"]["c"]
    d_index = payload["indices"]["d"]

    if overrides:
        a_index = _to_float(overrides.get("a")) if overrides.get("a") is not None else a_index
        b_index = _to_float(overrides.get("b")) if overrides.get("b") is not None else b_index
        c_index = _to_float(overrides.get("c")) if overrides.get("c") is not None else c_index
        d_index = _to_float(overrides.get("d")) if overrides.get("d") is not None else d_index
        payload["indices"] = {"a": a_index, "b": b_index, "c": c_index, "d": d_index}

    prob_draw = _calc_prob_draw(a_index, b_index, c_index, d_index, rules)

    a_index_display = "-" if a_index is None else a_index
    payload_indices = payload.get("indices") or {}
    payload_indices["a"] = a_index_display
    payload["indices"] = payload_indices

    number = attrs.get("number") or match.external_id or match.source_match_id
    kickoff = _resolve_kickoff(match)

    full_score = None
    if _is_finished_match(match, attrs):
        if match.home_score is not None and match.away_score is not None:
            full_score = f"{match.home_score}-{match.away_score}"
        else:
            raw_score = attrs.get("full_score") or attrs.get("score")
            if raw_score is not None:
                raw_text = str(raw_score).strip()
                full_score = raw_text or None

    return {
        "match_id": match.match_identifier,
        "match_date": match.match_date,
        "match_time": kickoff or match.match_time,
        "league": league.name if league else "-",
        "home_team": home_team.name if home_team else "-",
        "away_team": away_team.name if away_team else "-",
        "number": number,
        "score": full_score,
        "odds_win": odds_win,
        "odds_draw": odds_draw,
        "odds_lose": odds_lose,
        "total_goals_line": payload.get("total_goals_line"),
        "a_index": a_index_display,
        "b_index": b_index,
        "c_index": c_index,
        "d_index": d_index,
        "prob_draw": prob_draw,
        "p_value": prob_draw,
        "recommendation": _recommend_label(prob_draw, rules),
        "input_payload": payload,
        "override_indices": bool(overrides),
    }


def _load_rules_from_db(db: Session) -> Dict[str, Any]:
    try:
        from backend.models.system_config import SystemConfig

        cfg = db.query(SystemConfig).filter(SystemConfig.config_key == RULES_CONFIG_KEY).first()
        if not cfg:
            return DEFAULT_RULES
        try:
            parsed = json.loads(cfg.config_value or "{}")
            return _normalize_rules(parsed)
        except Exception:
            return DEFAULT_RULES
    except Exception:
        return DEFAULT_RULES


def _load_match_rules_map(db: Session, match_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    if not match_ids:
        return {}
    try:
        from backend.models.system_config import SystemConfig

        keys = [_match_rules_key(match_id) for match_id in match_ids]
        rows = db.query(SystemConfig).filter(SystemConfig.config_key.in_(keys)).all()
        out: Dict[str, Dict[str, Any]] = {}
        for cfg in rows:
            try:
                parsed = json.loads(cfg.config_value or "{}")
                normalized = _normalize_rules(parsed)
            except Exception:
                normalized = DEFAULT_RULES
            match_id = cfg.config_key.replace(f"{RULES_CONFIG_KEY}:", "", 1)
            if match_id:
                out[match_id] = normalized
        return out
    except Exception:
        return {}


def _load_match_overrides_map(db: Session, match_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    if not match_ids:
        return {}
    try:
        from backend.models.system_config import SystemConfig

        keys = [_match_override_key(match_id) for match_id in match_ids]
        rows = db.query(SystemConfig).filter(SystemConfig.config_key.in_(keys)).all()
        out: Dict[str, Dict[str, Any]] = {}
        for cfg in rows:
            try:
                parsed = json.loads(cfg.config_value or "{}")
                if not isinstance(parsed, dict):
                    continue
            except Exception:
                continue
            match_id = cfg.config_key.replace(f"{OVERRIDE_CONFIG_KEY}:", "", 1)
            if match_id:
                out[match_id] = parsed
        return out
    except Exception:
        return {}


def get_rules(db: Session) -> Dict[str, Any]:
    return _load_rules_from_db(db)


def get_match_rules(db: Session, match_id: str) -> Optional[Dict[str, Any]]:
    try:
        from backend.models.system_config import SystemConfig

        cfg = db.query(SystemConfig).filter(SystemConfig.config_key == _match_rules_key(match_id)).first()
        if not cfg:
            return None
        parsed = json.loads(cfg.config_value or "{}")
        return _normalize_rules(parsed)
    except Exception:
        return None


def get_match_overrides(db: Session, match_id: str) -> Optional[Dict[str, Any]]:
    try:
        from backend.models.system_config import SystemConfig

        cfg = db.query(SystemConfig).filter(SystemConfig.config_key == _match_override_key(match_id)).first()
        if not cfg:
            return None
        parsed = json.loads(cfg.config_value or "{}")
        if not isinstance(parsed, dict):
            return None
        return parsed
    except Exception:
        return None


def save_rules(db: Session, rules: Dict[str, Any]) -> Dict[str, Any]:
    from backend.models.system_config import SystemConfig

    normalized = _normalize_rules(rules)
    payload = json.dumps(normalized, ensure_ascii=False)
    cfg = db.query(SystemConfig).filter(SystemConfig.config_key == RULES_CONFIG_KEY).first()
    if cfg:
        cfg.config_value = payload
        cfg.config_name = "AI平局预测计算规则"
        cfg.config_type = "json"
        cfg.description = "AI平局预测计算规则（权重与阈值）"
        cfg.group = "draw_prediction"
        cfg.is_active = True
    else:
        cfg = SystemConfig(
            config_key=RULES_CONFIG_KEY,
            config_name="AI平局预测计算规则",
            config_value=payload,
            config_type="json",
            description="AI平局预测计算规则（权重与阈值）",
            group="draw_prediction",
            is_active=True,
        )
        db.add(cfg)
    db.commit()
    return normalized


def save_match_rules(db: Session, match_id: str, rules: Dict[str, Any]) -> Dict[str, Any]:
    from backend.models.system_config import SystemConfig

    normalized = _normalize_rules(rules)
    payload = json.dumps(normalized, ensure_ascii=False)
    key = _match_rules_key(match_id)
    cfg = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    if cfg:
        cfg.config_value = payload
        cfg.config_name = "AI平局预测单场优化规则"
        cfg.config_type = "json"
        cfg.description = f"AI平局预测单场优化规则: {match_id}"
        cfg.group = "draw_prediction_match"
        cfg.is_active = True
    else:
        cfg = SystemConfig(
            config_key=key,
            config_name="AI平局预测单场优化规则",
            config_value=payload,
            config_type="json",
            description=f"AI平局预测单场优化规则: {match_id}",
            group="draw_prediction_match",
            is_active=True,
        )
        db.add(cfg)
    db.commit()
    return normalized


def save_match_overrides(db: Session, match_id: str, overrides: Dict[str, Any]) -> Dict[str, Any]:
    from backend.models.system_config import SystemConfig

    cleaned = {
        "a": _to_float(overrides.get("a")) if overrides.get("a") is not None else None,
        "b": _to_float(overrides.get("b")) if overrides.get("b") is not None else None,
        "c": _to_float(overrides.get("c")) if overrides.get("c") is not None else None,
        "d": _to_float(overrides.get("d")) if overrides.get("d") is not None else None,
    }
    payload = json.dumps(cleaned, ensure_ascii=False)
    key = _match_override_key(match_id)
    cfg = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    if cfg:
        cfg.config_value = payload
        cfg.config_name = "AI平局预测单场手动修正"
        cfg.config_type = "json"
        cfg.description = f"AI平局预测单场手动修正: {match_id}"
        cfg.group = "draw_prediction_match"
        cfg.is_active = True
    else:
        cfg = SystemConfig(
            config_key=key,
            config_name="AI平局预测单场手动修正",
            config_value=payload,
            config_type="json",
            description=f"AI平局预测单场手动修正: {match_id}",
            group="draw_prediction_match",
            is_active=True,
        )
        db.add(cfg)
    db.commit()
    return cleaned


def list_for_date(
    db: Session,
    target_date: date,
    data_source: str = "yingqiu_bd",
    rules: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    date_str = target_date.isoformat()
    home_team = aliased(Team)
    away_team = aliased(Team)
    applied_rules = _normalize_rules(rules or _load_rules_from_db(db))

    query = (
        db.query(Match, League, home_team, away_team)
        .join(League, Match.league_id == League.id, isouter=True)
        .join(home_team, Match.home_team_id == home_team.id, isouter=True)
        .join(away_team, Match.away_team_id == away_team.id, isouter=True)
        .filter(Match.data_source == data_source)
    )
    if data_source == "yingqiu_bd":
        query = query.filter(_json_attr_text_expr(db, Match.source_attributes, "source_schedule_date") == date_str)
    else:
        query = query.filter(
            or_(
                Match.match_date == target_date,
                _json_attr_text_expr(db, Match.source_attributes, "source_schedule_date") == date_str,
            )
        )
    query = query.order_by(Match.scheduled_kickoff)

    rows = query.all()
    match_ids = [match.match_identifier for match, _, _, _ in rows]
    match_rules_map = _load_match_rules_map(db, match_ids)
    match_overrides_map = _load_match_overrides_map(db, match_ids)

    beidan_maps = _load_beidan_power_map(db, rows)
    daxiaosfc_map = _load_500w_daxiao_map_from_db(db, target_date)
    if not daxiaosfc_map.get("by_number") and not daxiaosfc_map.get("by_team"):
        fetched = _get_daxiao_map(target_date.isoformat())
        if fetched:
            _persist_500w_daxiao_to_db(db, target_date, fetched)
            reloaded = _load_500w_daxiao_map_from_db(db, target_date)
            if not reloaded.get("by_number") and not reloaded.get("by_team"):
                daxiaosfc_map = fetched
            else:
                daxiaosfc_map = reloaded

    items = []
    for match, league, h, a in rows:
        attrs = _safe_attrs(match.source_attributes)
        beidan_info = _resolve_beidan_info(match, attrs, beidan_maps)
        items.append(
            _build_result_row(
                match,
                league,
                h,
                a,
                match_rules_map.get(match.match_identifier, applied_rules),
                match_overrides_map.get(match.match_identifier),
                beidan_info=beidan_info,
                daxiaosfc_map=daxiaosfc_map,
            )
        )
    items.sort(key=lambda x: x.get("prob_draw") or 0.0, reverse=True)
    for idx, item in enumerate(items, 1):
        item["rank"] = idx
        item["data_source"] = data_source
    return items


def get_detail(db: Session, match_id: str, rules: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    home_team = aliased(Team)
    away_team = aliased(Team)
    match_rules = get_match_rules(db, match_id)
    match_overrides = get_match_overrides(db, match_id)
    applied_rules = _normalize_rules(match_rules or rules or _load_rules_from_db(db))
    row = (
        db.query(Match, League, home_team, away_team)
        .join(League, Match.league_id == League.id, isouter=True)
        .join(home_team, Match.home_team_id == home_team.id, isouter=True)
        .join(away_team, Match.away_team_id == away_team.id, isouter=True)
        .filter(Match.match_identifier == match_id)
        .first()
    )
    if not row:
        return None
    match, league, h, a = row
    beidan_maps = _load_beidan_power_map(db, [row])
    attrs = _safe_attrs(match.source_attributes)
    beidan_info = _resolve_beidan_info(match, attrs, beidan_maps)
    kickoff = _resolve_kickoff(match)
    target_date = kickoff.date() if kickoff else (match.match_date or datetime.now().date())
    daxiaosfc_map = _load_500w_daxiao_map_from_db(db, target_date)
    if not daxiaosfc_map.get("by_number") and not daxiaosfc_map.get("by_team"):
        fetched = _get_daxiao_map(target_date.isoformat())
        if fetched:
            _persist_500w_daxiao_to_db(db, target_date, fetched)
            reloaded = _load_500w_daxiao_map_from_db(db, target_date)
            if not reloaded.get("by_number") and not reloaded.get("by_team"):
                daxiaosfc_map = fetched
            else:
                daxiaosfc_map = reloaded
    item = _build_result_row(
        match,
        league,
        h,
        a,
        applied_rules,
        match_overrides,
        beidan_info=beidan_info,
        daxiaosfc_map=daxiaosfc_map,
    )
    item["data_source"] = match.data_source
    return item
