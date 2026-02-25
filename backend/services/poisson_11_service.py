from __future__ import annotations

from datetime import date, datetime
from typing import List, Dict, Any, Optional
import math
import json
import re
import time
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup, Comment

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import delete, func, or_

from backend.models.match import Match
from backend.models.poisson_11_result import Poisson11Result


DEFAULT_TOTAL_GOALS_LINE = 2.5
DEFAULT_HANDICAP = 0.0
MIN_MU = 0.05
BJDC_ASIAN_CACHE_TTL_SECONDS = 1800

ODDSPORTAL_BASE_URL = "https://www.oddsportal.com"
UNDERSTAT_BASE_URL = "https://understat.com"
FBREF_BASE_URL = "https://fbref.com"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

UNDERSTAT_LEAGUE_MAP = {
    "英超": "EPL",
    "西甲": "La_liga",
    "德甲": "Bundesliga",
    "意甲": "Serie_A",
    "法甲": "Ligue_1",
}

TEAM_NAME_ALIASES = {
    # 英超
    "曼城": ["Manchester City", "Man City"],
    "曼联": ["Manchester United", "Man United"],
    "利物浦": ["Liverpool"],
    "阿森纳": ["Arsenal"],
    "切尔西": ["Chelsea"],
    "热刺": ["Tottenham", "Tottenham Hotspur"],
    "纽卡斯尔": ["Newcastle", "Newcastle United"],
    "阿斯顿维拉": ["Aston Villa"],
    "西汉姆": ["West Ham", "West Ham United"],
    "布莱顿": ["Brighton", "Brighton & Hove Albion"],
    "狼队": ["Wolves", "Wolverhampton", "Wolverhampton Wanderers"],
    "富勒姆": ["Fulham"],
    "水晶宫": ["Crystal Palace"],
    "伯恩茅斯": ["Bournemouth", "AFC Bournemouth"],
    "布伦特福德": ["Brentford"],
    "诺丁汉森林": ["Nottingham Forest", "Nottm Forest"],
    "谢菲联": ["Sheffield United", "Sheff Utd"],
    "埃弗顿": ["Everton"],
    "伯恩利": ["Burnley"],
    "卢顿": ["Luton", "Luton Town"],

    # 西甲
    "皇马": ["Real Madrid"],
    "巴萨": ["Barcelona", "FC Barcelona"],
    "马竞": ["Atletico Madrid", "Atl Madrid"],
    "塞维利亚": ["Sevilla", "Sevilla FC"],
    "皇家社会": ["Real Sociedad"],
    "毕尔巴鄂": ["Athletic Bilbao", "Athletic Club"],
    "比利亚雷亚尔": ["Villarreal"],
    "贝蒂斯": ["Real Betis", "Betis"],
    "瓦伦西亚": ["Valencia"],
    "赫罗纳": ["Girona"],
    "塞尔塔": ["Celta Vigo", "Celta"],
    "奥萨苏纳": ["Osasuna"],
    "阿拉维斯": ["Alaves", "Deportivo Alaves"],
    "赫塔菲": ["Getafe"],
    "马略卡": ["Mallorca"],
    "拉斯帕尔马斯": ["Las Palmas"],
    "巴列卡诺": ["Rayo Vallecano", "Rayo"],
    "格拉纳达": ["Granada"],
    "加的斯": ["Cadiz"],
    "阿尔梅里亚": ["Almeria"],

    # 德甲
    "拜仁": ["Bayern Munich", "Bayern"],
    "多特": ["Borussia Dortmund", "Dortmund"],
    "莱比锡": ["RB Leipzig", "RasenBallsport Leipzig"],
    "勒沃库森": ["Bayer Leverkusen", "Leverkusen"],
    "法兰克福": ["Eintracht Frankfurt", "Frankfurt"],
    "门兴": ["Borussia Monchengladbach", "M'gladbach", "Gladbach"],
    "弗赖堡": ["Freiburg", "SC Freiburg"],
    "霍芬海姆": ["Hoffenheim", "TSG Hoffenheim"],
    "沃尔夫斯堡": ["Wolfsburg", "VfL Wolfsburg"],
    "不莱梅": ["Werder Bremen", "Bremen"],
    "美因茨": ["Mainz", "Mainz 05"],
    "奥格斯堡": ["Augsburg"],
    "科隆": ["Koln", "FC Koln", "Cologne"],
    "斯图加特": ["Stuttgart", "VfB Stuttgart"],
    "波鸿": ["Bochum"],
    "海登海姆": ["Heidenheim"],
    "柏林联合": ["Union Berlin", "1. FC Union Berlin"],
    "柏林赫塔": ["Hertha Berlin", "Hertha BSC"],
    "达姆施塔特": ["Darmstadt", "SV Darmstadt 98"],

    # 意甲
    "国米": ["Inter", "Inter Milan"],
    "尤文": ["Juventus"],
    "AC米兰": ["AC Milan"],
    "那不勒斯": ["Napoli"],
    "罗马": ["Roma", "AS Roma"],
    "拉齐奥": ["Lazio"],
    "亚特兰大": ["Atalanta"],
    "佛罗伦萨": ["Fiorentina"],
    "都灵": ["Torino"],
    "博洛尼亚": ["Bologna"],
    "萨索洛": ["Sassuolo"],
    "乌迪内斯": ["Udinese"],
    "蒙扎": ["Monza"],
    "热那亚": ["Genoa"],
    "莱切": ["Lecce"],
    "恩波利": ["Empoli"],
    "维罗纳": ["Verona", "Hellas Verona"],
    "卡利亚里": ["Cagliari"],
    "萨勒尼塔纳": ["Salernitana"],
    "弗罗西诺内": ["Frosinone"],

    # 法甲
    "巴黎": ["PSG", "Paris SG", "Paris Saint-Germain"],
    "马赛": ["Marseille", "Olympique Marseille"],
    "里昂": ["Lyon", "Olympique Lyon"],
    "摩纳哥": ["Monaco", "AS Monaco"],
    "里尔": ["Lille", "LOSC Lille"],
    "雷恩": ["Rennes"],
    "朗斯": ["Lens"],
    "尼斯": ["Nice"],
    "南特": ["Nantes"],
    "布雷斯特": ["Brest"],
    "兰斯": ["Reims", "Stade Reims"],
    "蒙彼利埃": ["Montpellier"],
    "斯特拉斯堡": ["Strasbourg"],
    "洛里昂": ["Lorient"],
    "梅斯": ["Metz"],
    "图卢兹": ["Toulouse"],
    "克莱蒙": ["Clermont", "Clermont Foot"],
    "勒阿弗尔": ["Le Havre"],
}

_BJDC_ASIAN_CACHE: Dict[str, Dict[str, Any]] = {}

def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        text = str(value).strip().replace(",", ".")
        return float(text)
    except (TypeError, ValueError):
        return None


def _normalize_attrs(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}
    return {}


def _normalize_number_key(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    m = re.search(r"\d+", text)
    if m:
        try:
            return str(int(m.group(0)))
        except Exception:
            return m.group(0).lstrip("0") or m.group(0)
    return text


def _normalize_other_odds_tabs(raw_tabs: Any, fallback_eu: Any = None) -> Dict[str, List[Dict[str, Any]]]:
    if isinstance(raw_tabs, str) and raw_tabs:
        try:
            raw_tabs = json.loads(raw_tabs)
        except Exception:
            raw_tabs = None

    tabs: Dict[str, List[Dict[str, Any]]] = {"eu": [], "asia": [], "goals": []}
    if isinstance(raw_tabs, dict):
        for key in tabs.keys():
            rows = raw_tabs.get(key)
            if isinstance(rows, list):
                tabs[key] = [row for row in rows if isinstance(row, dict)]

    if not tabs["eu"] and isinstance(fallback_eu, list):
        tabs["eu"] = [row for row in fallback_eu if isinstance(row, dict)]
    return tabs


def _is_crown_company(row: Dict[str, Any]) -> bool:
    company = str(row.get("company") or "").strip()
    provider_id = str(row.get("provider_id") or row.get("providerId") or "").strip()
    if provider_id == "629":
        return True
    if not company:
        return False
    # 盈球常见脱敏公司名如“皇*”
    return ("皇冠" in company) or company.startswith("皇")


def _parse_line_value(value: Any) -> Optional[float]:
    text = str(value or "").strip().replace(" ", "")
    if not text or text == "-":
        return None

    # 盘口常见格式：2/2.5、-0.5/1.0
    slash = re.search(r"([+-]?\d+(?:\.\d+)?)\s*/\s*([+-]?\d+(?:\.\d+)?)", text)
    if slash:
        left = _to_float(slash.group(1))
        right = _to_float(slash.group(2))
        if left is not None and right is not None:
            return (left + right) / 2.0

    direct = _to_float(text)
    if direct is not None:
        return direct

    # 仅保留首个数字片段作为兜底
    m = re.search(r"[+-]?\d+(?:\.\d+)?", text)
    if m:
        return _to_float(m.group(0))

    # 中文盘口兜底（极少数场景）
    cn_map = {
        "平手/半球": 0.25,
        "半球/一球": 0.75,
        "一球/球半": 1.25,
        "球半/两球": 1.75,
        "平手": 0.0,
        "半球": 0.5,
        "一球": 1.0,
        "球半": 1.5,
        "两球": 2.0,
    }
    for token, num in cn_map.items():
        if token in text:
            sign = -1.0 if "受" in text else 1.0
            return sign * num
    return None


def _fetch_500_bjdc_asian_map(schedule_date: str) -> Dict[str, Dict[str, Any]]:
    date_key = str(schedule_date or "").strip()
    if not date_key:
        return {}

    cached = _BJDC_ASIAN_CACHE.get(date_key)
    if cached:
        cached_items = cached.get("items") or {}
        ttl = 120 if not cached_items else BJDC_ASIAN_CACHE_TTL_SECONDS
        if (time.time() - float(cached.get("ts") or 0)) < ttl:
            return cached_items

    url = "https://trade.500.com/bjdc/index.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://trade.500.com/bjdc/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    items: Dict[str, Dict[str, Any]] = {}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            _BJDC_ASIAN_CACHE[date_key] = {"ts": time.time(), "items": {}}
            return {}

        encoding = (resp.encoding or "").lower()
        if not encoding or encoding == "iso-8859-1":
            encoding = (resp.apparent_encoding or "gb2312").lower()
        html = resp.content.decode(encoding, errors="ignore")

        soup = BeautifulSoup(html, "html.parser")
        for tbody in soup.select("table#vs_table > tbody"):
            tbody_id = str(tbody.get("id") or "").strip()
            if not tbody_id.startswith(f"{date_key}_"):
                continue

            for row in tbody.select("tr.vs_lines"):
                number_el = row.select_one("span.chnum")
                asian_el = row.select_one("span.asianhand")
                if not number_el or not asian_el:
                    continue
                number_key = _normalize_number_key(number_el.get_text(" ", strip=True))
                if not number_key:
                    continue
                asian_text = asian_el.get_text(" ", strip=True)
                line_value = _parse_line_value(asian_text)
                if line_value is None:
                    continue
                items[number_key] = {
                    "line": line_value,
                    "text": asian_text,
                    "source": "500_bjdc_index.asianhand",
                }
    except Exception:
        _BJDC_ASIAN_CACHE[date_key] = {"ts": time.time(), "items": {}}
        return {}

    _BJDC_ASIAN_CACHE[date_key] = {"ts": time.time(), "items": items}
    return items


def _extract_line_from_rows(
    rows: List[Dict[str, Any]],
    keys: List[str],
    *,
    prefer_crown: bool = True,
) -> tuple[Optional[float], Optional[str]]:
    if not rows:
        return None, None

    row_groups: List[List[Dict[str, Any]]] = []
    if prefer_crown:
        crown_rows = [row for row in rows if _is_crown_company(row)]
        if crown_rows:
            row_groups.append(crown_rows)
    row_groups.append(rows)

    for group in row_groups:
        for row in group:
            for key in keys:
                line = _parse_line_value(row.get(key))
                if line is not None:
                    return line, key
    return None, None


def _extract_draw_odds_from_rows(rows: List[Dict[str, Any]]) -> Optional[float]:
    if not rows:
        return None

    # 优先“平均欧指”行
    for row in rows:
        company = str(row.get("company") or "").strip()
        if "平均" not in company:
            continue
        for key in ("instant_draw", "init_draw", "draw"):
            value = _to_float(row.get(key))
            if value is not None and value > 1:
                return value

    # 再优先皇冠
    for row in [r for r in rows if _is_crown_company(r)]:
        for key in ("instant_draw", "init_draw", "draw"):
            value = _to_float(row.get(key))
            if value is not None and value > 1:
                return value

    # 最后任意可用
    for row in rows:
        for key in ("instant_draw", "init_draw", "draw"):
            value = _to_float(row.get(key))
            if value is not None and value > 1:
                return value
    return None


def _normalize_team_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    return re.sub(r"[^a-z0-9]+", "", text)


def _expand_team_aliases(name: str) -> List[str]:
    aliases = {name}
    for alias in TEAM_NAME_ALIASES.get(name, []):
        aliases.add(alias)
    reverse = [k for k, v in TEAM_NAME_ALIASES.items() if name in v]
    for item in reverse:
        aliases.add(item)
    return [a for a in aliases if a]


def _is_team_match(target: str, candidate: str) -> bool:
    if not target or not candidate:
        return False
    target_variants = _expand_team_aliases(target)
    for tv in target_variants:
        t_key = _normalize_team_key(tv)
        c_key = _normalize_team_key(candidate)
        if t_key and c_key and (t_key in c_key or c_key in t_key):
            return True
    return False


def _parse_understat_json(html: str, var_name: str) -> Optional[Any]:
    if not html:
        return None
    pattern = rf"var\s+{re.escape(var_name)}\s*=\s*JSON\.parse\('([^']+)'\)"
    match = re.search(pattern, html)
    if not match:
        return None
    raw = match.group(1)
    try:
        decoded = raw.encode("utf-8").decode("unicode_escape")
        return json.loads(decoded)
    except Exception:
        return None


def _find_fbref_table(html: str, table_id: str) -> Optional[BeautifulSoup]:
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id=table_id)
    if table:
        return table
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if table_id not in comment:
            continue
        comment_soup = BeautifulSoup(comment, "html.parser")
        table = comment_soup.find("table", id=table_id)
        if table:
            return table
    return None


class ExternalDataFetcher:
    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.oddsportal_cache: Dict[str, Dict[str, Any]] = {}
        self.understat_cache: Dict[str, Dict[str, Any]] = {}
        self.fbref_team_cache: Dict[str, Optional[str]] = {}
        self.fbref_team_stats_cache: Dict[str, Dict[str, Any]] = {}

    def _get(self, url: str, timeout: int = 20) -> Optional[str]:
        for _ in range(2):
            try:
                resp = self.session.get(url, timeout=timeout)
                if resp.status_code == 200:
                    return resp.text
            except requests.RequestException:
                time.sleep(1)
        return None

    def fetch_oddsportal(self, home_team: str, away_team: str, match_date: date) -> Dict[str, Any]:
        cache_key = f"{home_team}|{away_team}|{match_date.isoformat()}"
        if cache_key in self.oddsportal_cache:
            return self.oddsportal_cache[cache_key]

        query = quote_plus(f"{home_team} {away_team}")
        search_url = f"{ODDSPORTAL_BASE_URL}/search/?query={query}"
        html = self._get(search_url)
        if not html:
            self.oddsportal_cache[cache_key] = {}
            return {}

        soup = BeautifulSoup(html, "html.parser")
        home_aliases = _expand_team_aliases(home_team)
        away_aliases = _expand_team_aliases(away_team)
        scored_candidates: List[Dict[str, Any]] = []

        for link in soup.select("a[href*='/football/']"):
            href = link.get("href")
            if not href:
                continue
            text = link.get_text(" ", strip=True)
            parent_text = link.parent.get_text(" ", strip=True) if link.parent else ""
            candidate_text = f"{text} {parent_text}"

            home_hit = any(_is_team_match(alias, candidate_text) for alias in home_aliases)
            away_hit = any(_is_team_match(alias, candidate_text) for alias in away_aliases)
            if not (home_hit and away_hit):
                continue

            score = 0
            score += 2 if home_hit else 0
            score += 2 if away_hit else 0
            if match_date.isoformat() in candidate_text:
                score += 2
            scored_candidates.append({"href": href, "score": score, "text": candidate_text})

        if not scored_candidates:
            self.oddsportal_cache[cache_key] = {}
            return {}

        scored_candidates.sort(key=lambda item: item["score"], reverse=True)
        match_url = f"{ODDSPORTAL_BASE_URL}{scored_candidates[0]['href']}"
        match_html = self._get(match_url)
        if not match_html:
            self.oddsportal_cache[cache_key] = {}
            return {}

        text = BeautifulSoup(match_html, "html.parser").get_text(" ", strip=True)
        total_goals_line = None
        handicap = None

        ou_patterns = [
            r"Over/Under\s*(\d+(?:[\.,]\d+)?)",
            r"O/U\s*(\d+(?:[\.,]\d+)?)",
            r"Total\s*Goals\s*(\d+(?:[\.,]\d+)?)",
            r"Goals\s*Over\s*(\d+(?:[\.,]\d+)?)",
        ]
        ah_patterns = [
            r"Asian\s*Handicap\s*([+-]?\d+(?:[\.,]\d+)?)",
            r"Handicap\s*([+-]?\d+(?:[\.,]\d+)?)",
            r"AH\s*([+-]?\d+(?:[\.,]\d+)?)",
        ]

        for pattern in ou_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                total_goals_line = _to_float(m.group(1))
                if total_goals_line is not None:
                    break

        for pattern in ah_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                handicap = _to_float(m.group(1))
                if handicap is not None:
                    break

        payload = {
            "source": "oddsportal",
            "match_url": match_url,
            "total_goals_line": total_goals_line,
            "handicap": handicap,
            "fetched_at": datetime.utcnow().isoformat(),
        }
        self.oddsportal_cache[cache_key] = payload
        return payload

    def fetch_understat(self, league_name: str, home_team: str, away_team: str, match_date: date) -> Dict[str, Any]:
        league_slug = UNDERSTAT_LEAGUE_MAP.get(league_name)
        if not league_slug:
            return {}
        season_year = match_date.year if match_date.month >= 7 else match_date.year - 1
        cache_key = f"{league_slug}-{season_year}"
        if cache_key not in self.understat_cache:
            league_url = f"{UNDERSTAT_BASE_URL}/league/{league_slug}/{season_year}"
            html = self._get(league_url)
            matches_data = _parse_understat_json(html or "", "matchesData") or []
            if isinstance(matches_data, dict):
                matches_data = list(matches_data.values())
            self.understat_cache[cache_key] = {
                "url": league_url,
                "matches": matches_data,
            }

        cache_entry = self.understat_cache.get(cache_key) or {}
        for match in cache_entry.get("matches", []):
            h = match.get("h", {})
            a = match.get("a", {})
            if not (_is_team_match(home_team, h.get("title")) and _is_team_match(away_team, a.get("title"))):
                continue
            match_time = str(match.get("datetime") or "")[:10]
            if match_time and match_time != match_date.isoformat():
                continue
            xg_home = _to_float(h.get("xG"))
            xg_away = _to_float(a.get("xG"))
            return {
                "source": "understat",
                "league_url": cache_entry.get("url"),
                "match_id": match.get("id"),
                "match_url": f"{UNDERSTAT_BASE_URL}/match/{match.get('id')}" if match.get("id") else None,
                "xg_home": xg_home,
                "xg_away": xg_away,
                "fetched_at": datetime.utcnow().isoformat(),
            }
        return {}

    def _fetch_fbref_team_url(self, team_name: str) -> Optional[str]:
        if team_name in self.fbref_team_cache:
            return self.fbref_team_cache[team_name]
        for alias in _expand_team_aliases(team_name):
            search_url = f"{FBREF_BASE_URL}/en/search/search.fcgi?search={quote_plus(alias)}"
            html = self._get(search_url)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            link = soup.select_one("a[href*='/en/squads/']")
            if not link:
                continue
            href = link.get("href")
            team_url = f"{FBREF_BASE_URL}{href}" if href else None
            if team_url:
                self.fbref_team_cache[team_name] = team_url
                return team_url
        self.fbref_team_cache[team_name] = None
        return None

    def _fetch_fbref_team_stats(self, team_name: str) -> Dict[str, Any]:
        if team_name in self.fbref_team_stats_cache:
            return self.fbref_team_stats_cache[team_name]
        team_url = self._fetch_fbref_team_url(team_name)
        if not team_url:
            self.fbref_team_stats_cache[team_name] = {}
            return {}
        html = self._get(team_url)
        if not html:
            self.fbref_team_stats_cache[team_name] = {}
            return {}
        table = _find_fbref_table(html, "stats_standard_squad")
        if not table:
            self.fbref_team_stats_cache[team_name] = {}
            return {}
        row = table.find("tfoot")
        row = row.find("tr") if row else table.find("tr")
        if not row:
            self.fbref_team_stats_cache[team_name] = {}
            return {}
        gf_cell = row.find("td", {"data-stat": "goals_per90"})
        ga_cell = row.find("td", {"data-stat": "goals_against_per90"})
        xg_cell = row.find("td", {"data-stat": "xg_per90"})
        xga_cell = row.find("td", {"data-stat": "xg_against_per90"})
        gf = _to_float(gf_cell.get_text(strip=True) if gf_cell else None)
        ga = _to_float(ga_cell.get_text(strip=True) if ga_cell else None)
        xg = _to_float(xg_cell.get_text(strip=True) if xg_cell else None)
        xga = _to_float(xga_cell.get_text(strip=True) if xga_cell else None)
        payload = {
            "team_url": team_url,
            "goals_for_per90": gf,
            "goals_against_per90": ga,
            "xg_per90": xg,
            "xga_per90": xga,
        }
        self.fbref_team_stats_cache[team_name] = payload
        return payload

    def fetch_fbref(self, home_team: str, away_team: str) -> Dict[str, Any]:
        home_stats = self._fetch_fbref_team_stats(home_team)
        away_stats = self._fetch_fbref_team_stats(away_team)
        if not home_stats and not away_stats:
            return {}
        return {
            "source": "fbref",
            "home_team_stats": home_stats,
            "away_team_stats": away_stats,
            "fetched_at": datetime.utcnow().isoformat(),
        }


def _extract_total_goals_line(attrs: Dict[str, Any]) -> Optional[float]:
    for key in ("total_goals_line", "goal_line", "ou_line", "over_under", "total_goals"):
        if key in attrs:
            return _to_float(attrs.get(key))
    return None


def _extract_draw_odds(attrs: Dict[str, Any]) -> Optional[float]:
    odds_draw = _to_float(attrs.get("odds_draw") or attrs.get("odds_nspf_draw") or attrs.get("odds_spf_draw"))
    if odds_draw is not None and odds_draw > 1:
        return odds_draw

    tabs = _normalize_other_odds_tabs(attrs.get("other_odds_tabs"), attrs.get("other_odds"))
    return _extract_draw_odds_from_rows(tabs.get("eu") or [])


def _infer_total_goals_line_from_draw_odds(attrs: Dict[str, Any]) -> Optional[float]:
    odds_draw = _extract_draw_odds(attrs)
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


def _extract_handicap(attrs: Dict[str, Any]) -> Optional[float]:
    for key in ("handicap", "handicap_0", "handicap0"):
        if key in attrs:
            value = _parse_line_value(attrs.get(key))
            if value is not None:
                return value
    return None


def _extract_total_goals_line_from_bd_detail(attrs: Dict[str, Any]) -> tuple[Optional[float], Optional[str]]:
    tabs = _normalize_other_odds_tabs(attrs.get("other_odds_tabs"), attrs.get("other_odds"))
    goals_rows = tabs.get("goals") or []
    line, used_key = _extract_line_from_rows(
        goals_rows,
        ["instant_line", "init_line", "line", "instant_handicap", "init_handicap"],
        prefer_crown=True,
    )
    if line is not None:
        return line, f"bd_other_odds_tabs.goals.{used_key}"
    return None, None


def _extract_handicap_from_bd_detail(attrs: Dict[str, Any]) -> tuple[Optional[float], Optional[str]]:
    tabs = _normalize_other_odds_tabs(attrs.get("other_odds_tabs"), attrs.get("other_odds"))
    asia_rows = tabs.get("asia") or []
    line, used_key = _extract_line_from_rows(
        asia_rows,
        ["instant_handicap", "init_handicap", "handicap", "line"],
        prefer_crown=True,
    )
    if line is not None:
        return line, f"bd_other_odds_tabs.asia.{used_key}"
    return None, None


def _extract_handicap_from_500_bjdc(
    attrs: Dict[str, Any],
    *,
    bjdc_asian_map: Dict[str, Dict[str, Any]],
) -> tuple[Optional[float], Optional[str]]:
    if not bjdc_asian_map:
        return None, None
    # 优先用北单场次号做匹配（同一日期内唯一）
    number_key = _normalize_number_key(attrs.get("number"))
    if not number_key:
        number_key = _normalize_number_key(attrs.get("lineId") or attrs.get("line_id"))
    if not number_key:
        return None, None

    payload = bjdc_asian_map.get(number_key)
    if not isinstance(payload, dict):
        return None, None
    line = _to_float(payload.get("line"))
    if line is None:
        return None, None
    return line, str(payload.get("source") or "500_bjdc_index.asianhand")


def _poisson_prob(mu: float, k: int) -> float:
    return math.exp(-mu) * (mu ** k) / math.factorial(k)


def _compute_poisson_11(mu_total: float, mu_diff: float) -> Dict[str, float]:
    mu_total = max(mu_total, MIN_MU * 2)
    mu_diff = max(min(mu_diff, mu_total - MIN_MU), -mu_total + MIN_MU)
    mu_home = max((mu_total + mu_diff) / 2.0, MIN_MU)
    mu_away = max((mu_total - mu_diff) / 2.0, MIN_MU)
    prob_11 = _poisson_prob(mu_home, 1) * _poisson_prob(mu_away, 1)
    return {
        "mu_total": mu_total,
        "mu_diff": mu_diff,
        "mu_home": mu_home,
        "mu_away": mu_away,
        "prob_11": prob_11,
    }


def _build_input_payload(
    match: Match,
    attrs: Dict[str, Any],
    mu_values: Dict[str, float],
    total_goals_line: float,
    handicap: float,
    flags: List[str],
    *,
    total_goals_line_source: Optional[str] = None,
    handicap_source: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "match_id": match.match_identifier,
        "number": attrs.get("number"),
        "source_match_id": match.source_match_id,
        "total_goals_line": total_goals_line,
        "total_goals_line_source": total_goals_line_source,
        "handicap": handicap,
        "handicap_source": handicap_source,
        "odds": {
            "win": attrs.get("odds_win") or attrs.get("odds_nspf_win"),
            "draw": _extract_draw_odds(attrs),
            "lose": attrs.get("odds_lose") or attrs.get("odds_nspf_lose"),
        },
        "mu": {
            "total": mu_values["mu_total"],
            "diff": mu_values["mu_diff"],
            "home": mu_values["mu_home"],
            "away": mu_values["mu_away"],
        },
        "quality_flags": flags,
        "source_attributes": attrs,
    }


def scan_for_date(db: Session, target_date: date, data_source: str = "yingqiu_bd", overwrite: bool = True) -> List[Poisson11Result]:
    schedule_source = "yingqiu_bd" if data_source == "yingqiu_bd" else "500w"
    date_key = target_date.isoformat()
    query = db.query(Match).options(joinedload(Match.league), joinedload(Match.home_team), joinedload(Match.away_team)).filter(Match.data_source == schedule_source)
    if schedule_source == "yingqiu_bd":
        query = query.filter(func.json_extract(Match.source_attributes, "$.source_schedule_date") == date_key)
    else:
        query = query.filter(
            or_(
                Match.match_date == target_date,
                func.json_extract(Match.source_attributes, "$.source_schedule_date") == date_key,
            )
        )
    matches = query.all()

    if overwrite:
        db.execute(
            delete(Poisson11Result).where(
                Poisson11Result.match_date == target_date,
                Poisson11Result.data_source == data_source,
            )
        )
        db.commit()

    results: List[Poisson11Result] = []
    computed_items: List[Dict[str, Any]] = []
    fetcher = ExternalDataFetcher() if data_source in {"oddsportal", "understat", "fbref"} else None
    bjdc_asian_map: Dict[str, Dict[str, Any]] = {}
    if schedule_source == "yingqiu_bd":
        bjdc_asian_map = _fetch_500_bjdc_asian_map(date_key)

    for match in matches:
        attrs = _normalize_attrs(match.source_attributes)
        flags: List[str] = []

        if fetcher:
            league_name = match.league.name if match.league else ""
            home_name = match.home_team.name if match.home_team else ""
            away_name = match.away_team.name if match.away_team else ""
            external_payload: Dict[str, Any] = {}

            if data_source == "oddsportal":
                external_payload = fetcher.fetch_oddsportal(home_name, away_name, target_date)
            elif data_source == "understat":
                external_payload = fetcher.fetch_understat(league_name, home_name, away_name, target_date)
            elif data_source == "fbref":
                external_payload = fetcher.fetch_fbref(home_name, away_name)

            if external_payload:
                external_sources = attrs.get("external_sources") or {}
                external_sources[data_source] = external_payload
                attrs["external_sources"] = external_sources

                if external_payload.get("total_goals_line") is not None:
                    attrs["total_goals_line"] = external_payload.get("total_goals_line")
                if external_payload.get("handicap") is not None:
                    attrs["handicap"] = external_payload.get("handicap")

                if data_source == "understat":
                    xg_home = external_payload.get("xg_home")
                    xg_away = external_payload.get("xg_away")
                    if xg_home is not None and xg_away is not None:
                        attrs["xg_home"] = xg_home
                        attrs["xg_away"] = xg_away
                        if attrs.get("total_goals_line") is None:
                            attrs["total_goals_line"] = xg_home + xg_away
                        if attrs.get("handicap") is None:
                            attrs["handicap"] = xg_home - xg_away

                if data_source == "fbref":
                    home_stats = external_payload.get("home_team_stats") or {}
                    away_stats = external_payload.get("away_team_stats") or {}
                    home_attack = home_stats.get("xg_per90") or home_stats.get("goals_for_per90")
                    away_attack = away_stats.get("xg_per90") or away_stats.get("goals_for_per90")
                    if home_attack is not None and away_attack is not None:
                        if attrs.get("total_goals_line") is None:
                            attrs["total_goals_line"] = home_attack + away_attack
                        if attrs.get("handicap") is None:
                            attrs["handicap"] = home_attack - away_attack

                match.source_attributes = attrs

        total_goals_line = None
        total_goals_line_source: Optional[str] = None
        handicap = None
        handicap_source: Optional[str] = None

        if schedule_source == "yingqiu_bd":
            handicap, handicap_source = _extract_handicap_from_500_bjdc(
                attrs,
                bjdc_asian_map=bjdc_asian_map,
            )
            if handicap is not None:
                flags.append("handicap_from_500_bjdc_index")

            total_goals_line, total_goals_line_source = _extract_total_goals_line_from_bd_detail(attrs)
            if handicap is None:
                handicap, handicap_source = _extract_handicap_from_bd_detail(attrs)

        if total_goals_line is None:
            total_goals_line = _extract_total_goals_line(attrs)
            if total_goals_line is not None:
                total_goals_line_source = "source_attributes"
        if handicap is None:
            handicap = _extract_handicap(attrs)
            if handicap is not None:
                handicap_source = "source_attributes"

        if total_goals_line is None:
            inferred_total_goals = _infer_total_goals_line_from_draw_odds(attrs)
            if inferred_total_goals is not None:
                total_goals_line = inferred_total_goals
                flags.append("total_goals_line_inferred_from_draw_odds")
                total_goals_line_source = "inferred_from_draw_odds"
            else:
                total_goals_line = DEFAULT_TOTAL_GOALS_LINE
                flags.append("total_goals_line_default")
                total_goals_line_source = "default"
        if handicap is None:
            handicap = DEFAULT_HANDICAP
            flags.append("handicap_default")
            handicap_source = "default"

        mu_values = _compute_poisson_11(total_goals_line, handicap)
        input_payload = _build_input_payload(
            match,
            attrs,
            mu_values,
            total_goals_line,
            handicap,
            flags,
            total_goals_line_source=total_goals_line_source,
            handicap_source=handicap_source,
        )

        computed_items.append({
            "match": match,
            "attrs": attrs,
            "mu_values": mu_values,
            "input_payload": input_payload,
        })

    computed_items.sort(key=lambda item: item["mu_values"]["prob_11"], reverse=True)

    for idx, item in enumerate(computed_items, start=1):
        match = item["match"]
        mu_values = item["mu_values"]
        input_payload = item["input_payload"]

        result = Poisson11Result(
            match_id=match.match_identifier,
            match_date=target_date,
            match_time=match.scheduled_kickoff,
            league=match.league.name if match.league else None,
            home_team=match.home_team.name if match.home_team else "",
            away_team=match.away_team.name if match.away_team else "",
            data_source=data_source,
            mu_total=mu_values["mu_total"],
            mu_diff=mu_values["mu_diff"],
            mu_home=mu_values["mu_home"],
            mu_away=mu_values["mu_away"],
            prob_11=mu_values["prob_11"],
            rank=idx,
            input_payload=input_payload,
        )
        results.append(result)
        db.add(result)

    db.commit()
    return results


def list_results(db: Session, target_date: date, data_source: str = "yingqiu_bd") -> List[Poisson11Result]:
    return (
        db.query(Poisson11Result)
        .filter(Poisson11Result.match_date == target_date)
        .filter(Poisson11Result.data_source == data_source)
        .order_by(Poisson11Result.rank.asc())
        .all()
    )


def get_detail(db: Session, match_id: str, data_source: Optional[str] = None) -> Optional[Poisson11Result]:
    query = db.query(Poisson11Result).filter(Poisson11Result.match_id == match_id)
    if data_source:
        query = query.filter(Poisson11Result.data_source == data_source)
    return query.order_by(Poisson11Result.updated_at.desc(), Poisson11Result.id.desc()).first()
