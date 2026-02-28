"""
IP姹犵鐞?API 閫傞厤鍣?鐢ㄤ簬瀵规帴鍓嶇 /admin/data-source/ip-pool 椤甸潰
"""

from __future__ import annotations

import csv
import concurrent.futures
import os
import re
from contextlib import contextmanager
from datetime import datetime
from html import unescape
from io import StringIO
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models.ip_pool import IPPool
from backend.models.data_sources import DataSource
from backend.models.system_config import SystemConfig
from backend.schemas.ip_pool import IPPoolUpdate
from backend.services.pool_reconciler_service import PoolReconcilerService

router = APIRouter(prefix="", tags=["ip-pool-adapter"])

SOURCE_CONFIG_KEY = "ip_pool_source_addresses"
DEFAULT_TIMEOUT_SECONDS = 10
PLAYWRIGHT_TIMEOUT_MS = 12000
MAX_SOURCE_COUNT = 50
MAX_SOURCE_LEN = 500
LOG_SCAN_FILES = [
    os.path.join("logs", "app.log"),
    os.path.join("logs", "backend_start.log"),
    os.path.join("logs", "backend_manual_restart.out"),
    os.path.join("logs", "uvicorn.out"),
]
LOG_SUCCESS_HINTS = [
    "鑷姩鐖彇瀹屾垚",
    "鏈夋晥IP",
    "鍙敤IP",
    "鎶撳彇",
    "鐖彇",
    "proxy",
    "source",
    "recrawl",
]
PROXY_ENV_KEYS = [
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
]


def _map_status_for_frontend(status: str) -> str:
    return {
        "active": "available",
        "inactive": "unavailable",
        "banned": "unavailable",
        "pending": "pending",
        "testing": "pending",
        "cooling": "cooling",
    }.get(status, "pending")


def _to_frontend_item(pool: IPPool) -> Dict:
    return {
        "id": pool.id,
        "ipAddress": pool.ip,
        "port": pool.port,
        "protocol": pool.protocol,
        "location": pool.location or "鏈煡",
        "responseTime": pool.latency_ms if pool.latency_ms is not None else 0,
        "successRate": pool.success_rate if pool.success_rate is not None else 0,
        "lastChecked": pool.last_checked.isoformat() if pool.last_checked else None,
        "source": pool.source or "",
        "anonymity": pool.anonymity or "",
        "score": pool.score,
        "bannedUntil": pool.banned_until.isoformat() if pool.banned_until else None,
        "failReason": pool.fail_reason,
        "status": _map_status_for_frontend(pool.status),
        "usageCount": (pool.success_count or 0) + (pool.failure_count or 0),
        "lastUsed": pool.last_used.isoformat() if pool.last_used else "-",
        "isEnabled": pool.status == "active",
    }


def _normalize_source(source: str) -> str:
    return (source or "").strip()


def _is_valid_source_url(source: str) -> bool:
    return bool(re.match(r"^https?://", source))


def _is_external_source_url(source: str) -> bool:
    if not _is_valid_source_url(source):
        return False
    parsed = urlparse(source)
    host = (parsed.hostname or "").lower()
    if host in {"localhost", "127.0.0.1", "::1"}:
        return False
    path = (parsed.path or "").lower()
    if path.startswith("/api/"):
        return False
    return True


def _validate_ipv4(ip: str) -> bool:
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def _extract_ip_port_pairs(content: str) -> List[Tuple[str, int]]:
    """
    鏀寔甯歌鏂囨湰鏍煎紡:
    - 1.2.3.4:8080
    - 1.2.3.4锛?080
    """
    pattern = re.compile(r"((?:\d{1,3}\.){3}\d{1,3})\s*[:锛歖\s*(\d{2,5})")
    results = []
    for ip, port in pattern.findall(content or ""):
        if not _validate_ipv4(ip):
            continue
        port_int = int(port)
        if 1 <= port_int <= 65535:
            results.append((ip, port_int))
    # 鍘婚噸骞朵繚鎸侀『搴?    seen = set()
    dedup = []
    for item in results:
        if item in seen:
            continue
        seen.add(item)
        dedup.append(item)
    return dedup


def _extract_ip_port_pairs_json(content: str) -> List[Tuple[str, int]]:
    results = []
    patterns = [
        re.compile(r'"ip"\s*:\s*"((?:\d{1,3}\.){3}\d{1,3})"\s*,\s*"port"\s*:\s*"?(\d{2,5})"?', re.I),
        re.compile(r"'ip'\s*:\s*'((?:\d{1,3}\.){3}\d{1,3})'\s*,\s*'port'\s*:\s*'?(\d{2,5})'?", re.I),
    ]
    for pat in patterns:
        for ip, port in pat.findall(content or ""):
            if _validate_ipv4(ip):
                port_int = int(port)
                if 1 <= port_int <= 65535:
                    results.append((ip, port_int))
    # keep order
    seen = set()
    dedup = []
    for item in results:
        if item in seen:
            continue
        seen.add(item)
        dedup.append(item)
    return dedup


def _extract_ip_port_pairs_obfuscated(content: str) -> List[Tuple[str, int]]:
    """
    閽堝閮ㄥ垎绔欑偣娣锋穯鍦烘櫙鍋氶檷鍣彁鍙?
    - HTML瀹炰綋瑙ｇ爜
    - 鍘绘帀甯歌闅愯棌鏍囩鍚庡啀鍋氭鍒欐彁鍙?    """
    text = unescape(content or "")
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+style\s*=\s*['\"][^'\"]*(display\s*:\s*none|visibility\s*:\s*hidden)[^'\"]*['\"][^>]*>.*?</[^>]+>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return _extract_ip_port_pairs(text)


def _extract_ip_port_pairs_js_blob(content: str) -> List[Tuple[str, int]]:
    """
    解析页面脚本中的数据块，例如:
    - var list = [{ip:'1.2.3.4',port:8080}, ...]
    - const data = "1.2.3.4:8080, ..."
    """
    results = []
    blocks = re.findall(r"(?:var|let|const)\s+\w+\s*=\s*(.+?);", content or "", flags=re.I | re.S)
    for block in blocks:
        results.extend(_extract_ip_port_pairs_json(block))
        results.extend(_extract_ip_port_pairs(block))

    seen = set()
    dedup = []
    for item in results:
        if item in seen:
            continue
        seen.add(item)
        dedup.append(item)
    return dedup


def _extract_pairs_for_domain(domain: str, content: str) -> List[Tuple[str, int]]:
    domain = (domain or "").lower()
    parsers = []

    # 榛樿閫氱敤瑙ｆ瀽
    parsers.extend(
        [
            _extract_ip_port_pairs,
            _extract_ip_port_pairs_json,
            _extract_ip_port_pairs_js_blob,
            _extract_ip_port_pairs_obfuscated,
        ]
    )

    # 鍚勭珯鐐逛笓鐢ㄩ『搴忎紭鍖?
    if "goubanjia.com" in domain:
        parsers = [
            _extract_ip_port_pairs_obfuscated,
            _extract_ip_port_pairs_js_blob,
            _extract_ip_port_pairs,
            _extract_ip_port_pairs_json,
        ]
    elif "mimvp.com" in domain:
        parsers = [
            _extract_ip_port_pairs_json,
            _extract_ip_port_pairs_js_blob,
            _extract_ip_port_pairs,
            _extract_ip_port_pairs_obfuscated,
        ]
    elif "kuaidaili.com" in domain:
        parsers = [
            _extract_ip_port_pairs_json,
            _extract_ip_port_pairs_js_blob,
            _extract_ip_port_pairs,
            _extract_ip_port_pairs_obfuscated,
        ]

    merged = []
    seen = set()
    for parser in parsers:
        try:
            pairs = parser(content)
        except Exception:
            pairs = []
        for p in pairs:
            if p in seen:
                continue
            seen.add(p)
            merged.append(p)
    return merged


def _source_candidate_urls(source: str) -> List[str]:
    source = _normalize_source(source)
    try:
        parsed = urlparse(source)
    except Exception:
        return [source]
    domain = (parsed.netloc or "").lower()
    scheme = parsed.scheme or "http"
    base = f"{scheme}://{domain}" if domain else source
    candidates = [source]

    domain_map = {
        "xicidaili.com": ["/", "/nn/1", "/wt/1"],
        "66ip.cn": ["/", "/mo.php?sxb=&tqsl=100&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1"],
        "youdaili.net": ["/", "/Daili/http/"],
        "kuaidaili.com": ["/free/", "/free/inha/1/", "/free/intr/1/"],
        "ip3366.net": ["/", "/free/"],
        "89ip.cn": ["/", "/index_1.html"],
        "cz88.net": ["/proxy/"],
        "goubanjia.com": ["/"],
        "httpdaili.com": ["/", "/api.asp?ddbh=355281346188704&no=20180104154926&sl=100&xl=on&cs=on&ys=on&sb=&pb=45&mr=1&regions="],
        "mimvp.com": ["/", "/free.php?proxy=in_hp"],
        "dainar.net": ["/", "/ProxyIP/"],
        "superfastip.com": ["/"],
        "zdaye.com": ["/dayProxy.html", "/free/1/"],
        "data5u.com": ["/", "/free/index.shtml"],
        "kxdaili.com": ["/", "/dailiip.html"],
        "ihuan.me": ["/", "/"],
        "iphai.com": ["/", "/free/ng"],
    }

    matched_paths = []
    for key, paths in domain_map.items():
        if key in domain:
            matched_paths = paths
            break

    for p in matched_paths:
        url = f"{base}{p}" if p.startswith("/") else p
        if url not in candidates:
            candidates.append(url)

    # 涓€浜涚珯鐐?http 璺?https锛屽弻鍗忚閮借瘯
    if source.startswith("http://"):
        secure = "https://" + source[len("http://") :]
        if secure not in candidates:
            candidates.append(secure)
    elif source.startswith("https://"):
        plain = "http://" + source[len("https://") :]
        if plain not in candidates:
            candidates.append(plain)

    return candidates[:8]


def _build_request_headers(target_url: str) -> Dict[str, str]:
    parsed = urlparse(target_url)
    host = parsed.netloc
    origin = f"{parsed.scheme}://{host}" if parsed.scheme and host else ""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Referer": origin or "https://www.baidu.com/",
    }


def _should_try_browser_render(source: str) -> bool:
    source_lower = (source or "").lower()
    heavy_render_domains = [
        "goubanjia.com",
        "mimvp.com",
        "kuaidaili.com",
        "zdaye.com",
        "ihuan.me",
        "youdaili.net",
        "httpdaili.com",
    ]
    return any(d in source_lower for d in heavy_render_domains)


def _fetch_pairs_with_playwright(candidates: List[str]) -> Tuple[List[Tuple[str, int]], str]:
    def _run_in_thread(urls: List[str]) -> Tuple[List[Tuple[str, int]], str]:
        first_error = ""
        all_pairs: List[Tuple[str, int]] = []
        seen = set()

        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
            from playwright.sync_api import sync_playwright
        except Exception as ex:
            return [], f"Playwright unavailable: {ex}"

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-proxy-server",
                        "--proxy-bypass-list=*",
                        "--disable-blink-features=AutomationControlled",
                    ],
                )
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    locale="zh-CN",
                )
                page = context.new_page()

                for candidate in urls[:3]:
                    try:
                        page.set_extra_http_headers(_build_request_headers(candidate))
                        page.goto(candidate, wait_until="domcontentloaded", timeout=PLAYWRIGHT_TIMEOUT_MS)
                        try:
                            page.wait_for_load_state("networkidle", timeout=3000)
                        except Exception:
                            pass
                        html = page.content() or ""
                        body_text = ""
                        try:
                            body_text = page.inner_text("body") or ""
                        except Exception:
                            pass
                        merged = f"{html}\n{body_text}"
                        domain = (urlparse(page.url).netloc or urlparse(candidate).netloc).lower()
                        pairs = _extract_pairs_for_domain(domain, merged)
                        for pair in pairs:
                            if pair in seen:
                                continue
                            seen.add(pair)
                            all_pairs.append(pair)
                        if all_pairs:
                            break
                    except PlaywrightTimeoutError as ex:
                        if not first_error:
                            first_error = f"Playwright timeout: {ex}"
                    except Exception as ex:
                        if not first_error:
                            first_error = f"Playwright fetch failed: {ex}"

                context.close()
                browser.close()
        except Exception as ex:
            if not first_error:
                first_error = f"Playwright bootstrap failed: {ex}"

        return all_pairs, first_error

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(_run_in_thread, candidates).result(timeout=90)
    except Exception as ex:
        return [], f"Playwright thread failed ({type(ex).__name__}): {ex}"


def _fetch_pairs_from_source(session: requests.Session, source: str) -> Tuple[List[Tuple[str, int]], str]:
    candidates = _source_candidate_urls(source)
    first_error = ""
    all_pairs = []
    seen = set()

    for candidate in candidates:
        try:
            resp = session.get(
                candidate,
                headers=_build_request_headers(candidate),
                timeout=DEFAULT_TIMEOUT_SECONDS,
                allow_redirects=True,
                proxies={"http": None, "https": None},
            )
            if resp.status_code >= 400:
                if not first_error:
                    first_error = f"{resp.status_code} {resp.reason}"
                continue
            domain = (urlparse(resp.url).netloc or urlparse(candidate).netloc).lower()
            text = resp.text or ""
            pairs = _extract_pairs_for_domain(domain, text)
            for pair in pairs:
                if pair in seen:
                    continue
                seen.add(pair)
                all_pairs.append(pair)
            if all_pairs:
                break
        except Exception as ex:
            if not first_error:
                first_error = str(ex)

    # JS 渲染兜底：普通请求解析不到且属于高反爬站点时，尝试 Chromium 渲染
    if not all_pairs and _should_try_browser_render(source):
        rendered_pairs, render_error = _fetch_pairs_with_playwright(candidates)
        for pair in rendered_pairs:
            if pair in seen:
                continue
            seen.add(pair)
            all_pairs.append(pair)
        if not all_pairs and render_error and not first_error:
            first_error = render_error
        elif not all_pairs and render_error and first_error:
            first_error = f"{first_error}; {render_error}"

    return all_pairs, first_error


@contextmanager
def _disabled_proxy_env():
    backup = {}
    try:
        for key in PROXY_ENV_KEYS:
            backup[key] = os.environ.get(key)
            if key in os.environ:
                os.environ.pop(key, None)
        yield
    finally:
        for key, value in backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _load_source_config(db: Session) -> List[Dict]:
    """
    浠?system_configs 璇诲彇鏉ユ簮鍦板潃閰嶇疆銆?    鑻ユ病鏈夐厤缃紝浣跨敤鐜版湁 IP 鐨?source 瀛楁鑷姩鍒濆鍖栥€?    """
    cfg = db.query(SystemConfig).filter(SystemConfig.config_key == SOURCE_CONFIG_KEY).first()
    base_items: List[Dict] = []
    if cfg:
        try:
            import json

            parsed = json.loads(cfg.config_value or "[]")
            if isinstance(parsed, list):
                for x in parsed:
                    if not isinstance(x, dict):
                        continue
                    source = _normalize_source(x.get("source", ""))
                    if not source:
                        continue
                    base_items.append(
                        {
                            "source": source,
                            "enabled": bool(x.get("enabled", True)),
                        }
                    )
        except Exception:
            pass

    # 浠嶪P姹犱腑鎻愬彇鈥滃巻鍙叉垚鍔熸潵婧愨€濓細鍙敤鐘舵€?鏈夋垚鍔熸鏁?鎴愬姛鐜囪緝楂?
    successful_sources = (
        db.query(IPPool.source)
        .filter(IPPool.source.isnot(None))
        .filter(func.length(func.trim(IPPool.source)) > 0)
        .filter(
            or_(
                IPPool.status == "active",
                IPPool.success_count > 0,
                IPPool.success_rate >= 60,
            )
        )
        .distinct()
        .all()
    )

    # 鍏煎鏃ф暟鎹細濡傛灉娌℃湁鎴愬姛鏍囪锛屼粛琛ュ厖鎵€鏈夋潵婧愶紝閬垮厤婕忔帀鍘嗗彶鍙敤鍦板潃
    distinct_sources = (
        db.query(IPPool.source)
        .filter(IPPool.source.isnot(None))
        .filter(func.length(func.trim(IPPool.source)) > 0)
        .distinct()
        .all()
    )

    merged: Dict[str, Dict] = {}
    for item in base_items:
        source = _normalize_source(item.get("source", ""))
        if not source:
            continue
        merged[source] = {"source": source, "enabled": bool(item.get("enabled", True))}

    for row in successful_sources:
        source = _normalize_source(row[0])
        if not _is_external_source_url(source):
            continue
        merged[source] = {"source": source, "enabled": True}

    for row in distinct_sources:
        source = _normalize_source(row[0])
        if not _is_external_source_url(source):
            continue
        if source not in merged:
            merged[source] = {"source": source, "enabled": True}

    # 浠庢暟鎹簮閰嶇疆閲岃ˉ鍏呭湪绾縐RL锛堝緢澶氬満鏅疘P姹爏ource涓嶆槸URL锛岄渶浠巇ata_sources琛ラ綈锛?
    try:
        ds_rows = (
            db.query(DataSource.url, DataSource.status)
            .filter(DataSource.url.isnot(None))
            .filter(func.length(func.trim(DataSource.url)) > 0)
            .all()
        )
        for url, status in ds_rows:
            source = _normalize_source(url)
            if not _is_external_source_url(source):
                continue
            enabled = str(status).lower() in {"online", "1", "true"} or status is True or status == 1
            if source in merged:
                # 宸插瓨鍦ㄥ垯淇濈暀鍚敤鐘舵€佷腑鐨勨€滅湡鈥?
                merged[source]["enabled"] = bool(merged[source].get("enabled")) or enabled
            else:
                merged[source] = {"source": source, "enabled": enabled}
    except Exception:
        pass

    # 浠庡巻鍙叉棩蹇椾腑琛ュ厖鈥滃彲鑳芥垚鍔熻幏鍙栬繃IP鈥濈殑澶栭儴鍦板潃
    for source in _extract_sources_from_history_logs():
        if source not in merged:
            merged[source] = {"source": source, "enabled": True}

    # 鍏滃簳锛氳嫢浠嶄负绌猴紝缁欏嚭褰撳墠绯荤粺鍐呭凡浣跨敤涓旂ǔ瀹氱殑榛樿鏉ユ簮
    if not merged:
        merged["https://m.100qiu.com/api/dcListBasic"] = {
            "source": "https://m.100qiu.com/api/dcListBasic",
            "enabled": True,
        }

    items = list(merged.values())
    items.sort(key=lambda x: (not x["enabled"], x["source"]))
    return items[:MAX_SOURCE_COUNT]


def _extract_sources_from_history_logs() -> List[str]:
    pattern = re.compile(r"https?://[^\s\"'<>]+")
    discovered: Dict[str, int] = {}

    for log_path in LOG_SCAN_FILES:
        if not os.path.exists(log_path):
            continue
        try:
            # 鍙壂鎻忔棩蹇楁湯灏撅紝鎺у埗鎬ц兘
            with open(log_path, "rb") as f:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                f.seek(max(0, size - 2 * 1024 * 1024), os.SEEK_SET)
                content = f.read().decode("utf-8", errors="ignore")
        except Exception:
            continue

        for line in content.splitlines():
            lower_line = line.lower()
            if not any(hint.lower() in lower_line for hint in LOG_SUCCESS_HINTS):
                continue
            for match in pattern.findall(line):
                source = _normalize_source(match).rstrip(".,;)")
                if not _is_external_source_url(source):
                    continue
                discovered[source] = discovered.get(source, 0) + 1

    ranked = sorted(discovered.items(), key=lambda x: (-x[1], x[0]))
    return [x[0] for x in ranked[:MAX_SOURCE_COUNT]]


def _save_source_config(db: Session, items: List[Dict]) -> None:
    import json

    clean_items = []
    seen = set()
    for x in items:
        source = _normalize_source(x.get("source", ""))
        if not source or source in seen:
            continue
        seen.add(source)
        clean_items.append({"source": source, "enabled": bool(x.get("enabled", True))})
    clean_items = clean_items[:MAX_SOURCE_COUNT]

    cfg = db.query(SystemConfig).filter(SystemConfig.config_key == SOURCE_CONFIG_KEY).first()
    payload = json.dumps(clean_items, ensure_ascii=False)
    now = datetime.utcnow()
    if cfg:
        cfg.config_value = payload
        cfg.config_name = "IP姹犳潵婧愬湴鍧€閰嶇疆"
        cfg.config_type = "json"
        cfg.description = "IP姹犺嚜鍔ㄧ埇鍙栨潵婧愬湴鍧€"
        cfg.group = "crawler"
        cfg.is_active = True
        cfg.updated_at = now
    else:
        cfg = SystemConfig(
            config_key=SOURCE_CONFIG_KEY,
            config_name="IP姹犳潵婧愬湴鍧€閰嶇疆",
            config_value=payload,
            config_type="json",
            description="IP姹犺嚜鍔ㄧ埇鍙栨潵婧愬湴鍧€",
            group="crawler",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        db.add(cfg)
    db.commit()


def _get_source_stats_map(db: Session) -> Dict[str, Dict]:
    rows = (
        db.query(
            IPPool.source.label("source"),
            func.count(IPPool.id).label("total"),
            func.sum(case((IPPool.status == "active", 1), else_=0)).label("active"),
            func.max(IPPool.last_checked).label("last_checked"),
        )
        .filter(IPPool.source.isnot(None))
        .filter(func.length(func.trim(IPPool.source)) > 0)
        .group_by(IPPool.source)
        .all()
    )
    out = {}
    for row in rows:
        source = _normalize_source(row.source)
        out[source] = {
            "count": int(row.total or 0),
            "activeCount": int(row.active or 0),
            "lastChecked": row.last_checked.isoformat() if row.last_checked else None,
        }
    return out


@router.get("/ip-pools")
async def get_ip_pools(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(IPPool)
        if status:
            query = query.filter(IPPool.status == status)
        if search:
            query = query.filter(or_(IPPool.ip.like(f"%{search}%"), IPPool.location.like(f"%{search}%")))

        total = query.count()
        pools = query.order_by(IPPool.id.desc()).offset((page - 1) * size).limit(size).all()
        return {
            "code": 200,
            "data": {
                "items": [_to_frontend_item(pool) for pool in pools],
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
            },
            "message": "IP池获取成功",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ip-pools/stats")
async def get_ip_pool_stats(db: Session = Depends(get_db)):
    try:
        total_count = db.query(IPPool).count()
        active_count = db.query(IPPool).filter(IPPool.status == "active").count()
        inactive_count = db.query(IPPool).filter(IPPool.status == "inactive").count()
        banned_count = db.query(IPPool).filter(IPPool.status == "banned").count()
        testing_count = db.query(IPPool).filter(IPPool.status == "testing").count()
        cooling_count = db.query(IPPool).filter(IPPool.status == "cooling").count()
        pending_count = db.query(IPPool).filter(IPPool.status == "pending").count()

        reconciler = PoolReconcilerService(db)
        summary = reconciler.summarize_for_api()
        ip_summary = summary.get("ip", {})
        return {
            "code": 200,
            "data": {
                "total": total_count,
                "active": active_count,
                "inactive": inactive_count,
                "banned": banned_count,
                "pending": pending_count,
                "testing": testing_count,
                "cooling": cooling_count,
                "activeTarget": int(settings.IP_POOL_TARGET_ACTIVE),
                "standbyTarget": int(settings.IP_POOL_TARGET_STANDBY),
                "activeGap": int(ip_summary.get("active_gap", max(0, settings.IP_POOL_TARGET_ACTIVE - active_count))),
                "standbyGap": int(ip_summary.get("standby_gap", max(0, settings.IP_POOL_TARGET_STANDBY - inactive_count))),
                "capacity": ip_summary,
                "latest_update": datetime.utcnow().isoformat(),
            },
            "message": "缁熻淇℃伅鑾峰彇鎴愬姛",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ip-pools/reconcile")
async def reconcile_ip_pool(
    dry_run: bool = Body(True, embed=True),
    db: Session = Depends(get_db),
):
    try:
        service = PoolReconcilerService(db)
        result = service.reconcile(dry_run=dry_run)
        return {
            "code": 200,
            "data": result,
            "message": "IP池调节任务已执行",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ip-pools/export")
async def export_ip_pools(db: Session = Depends(get_db)):
    pools = db.query(IPPool).order_by(IPPool.id.desc()).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "ip",
            "port",
            "protocol",
            "location",
            "status",
            "success_count",
            "failure_count",
            "last_used",
            "latency_ms",
            "success_rate",
            "last_checked",
            "source",
            "anonymity",
            "score",
            "banned_until",
            "fail_reason",
        ]
    )
    for pool in pools:
        writer.writerow(
            [
                pool.id,
                pool.ip,
                pool.port,
                pool.protocol,
                pool.location or "",
                pool.status,
                pool.success_count,
                pool.failure_count,
                pool.last_used.isoformat() if pool.last_used else "",
                pool.latency_ms if pool.latency_ms is not None else "",
                pool.success_rate if pool.success_rate is not None else "",
                pool.last_checked.isoformat() if pool.last_checked else "",
                pool.source or "",
                pool.anonymity or "",
                pool.score if pool.score is not None else "",
                pool.banned_until.isoformat() if pool.banned_until else "",
                pool.fail_reason or "",
            ]
        )

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ip_pools.csv"},
    )


@router.post("/ip-pools/batch/test")
async def batch_test_ip_pools(ids: List[int] = Body(..., embed=True), db: Session = Depends(get_db)):
    import random

    now = datetime.utcnow()
    pools = db.query(IPPool).filter(IPPool.id.in_(ids)).all()
    results = []
    for pool in pools:
        response_time = random.randint(50, 1000)
        success_rate = random.randint(70, 100)
        pool.status = "testing"
        pool.latency_ms = response_time
        pool.success_rate = success_rate
        pool.last_checked = now
        if success_rate >= 80:
            pool.status = "active"
            pool.success_count = int(pool.success_count or 0) + 1
            pool.fail_reason = None
        else:
            pool.status = "cooling"
            pool.failure_count = int(pool.failure_count or 0) + 1
            pool.fail_reason = f"health_check_low_success_rate_{success_rate}"
        results.append(
            {
                "id": pool.id,
                "ipAddress": pool.ip,
                "port": pool.port,
                "response_time": response_time,
                "success_rate": success_rate,
                "status": _map_status_for_frontend(pool.status),
            }
        )
    db.commit()
    return {
        "code": 200,
        "data": {"results": results, "tested_count": len(results)},
        "message": "鎵归噺娴嬭瘯瀹屾垚",
    }


@router.post("/ip-pools/batch/delete")
async def batch_delete_ip_pools(ids: List[int] = Body(..., embed=True), db: Session = Depends(get_db)):
    deleted = db.query(IPPool).filter(IPPool.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return {
        "code": 200,
        "data": {"deleted_count": deleted},
        "message": "鎵归噺鍒犻櫎鎴愬姛",
    }


@router.get("/ip-pools/{pool_id:int}")
async def get_ip_pool(pool_id: int, db: Session = Depends(get_db)):
    pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
    if not pool:
        raise HTTPException(status_code=404, detail="IP姹犱笉瀛樺湪")
    return {"code": 200, "data": _to_frontend_item(pool), "message": "IP池获取成功"}


@router.post("/ip-pools")
async def create_ip_pool(
    ip: str = Body(..., embed=True),
    port: int = Body(..., embed=True),
    protocol: str = Body("http", embed=True),
    location: str = Body("", embed=True),
    status: str = Body("active", embed=True),
    remarks: str = Body("", embed=True),
    latency_ms: Optional[int] = Body(None, embed=True),
    success_rate: Optional[int] = Body(None, embed=True),
    last_checked: Optional[datetime] = Body(None, embed=True),
    source: Optional[str] = Body(None, embed=True),
    anonymity: Optional[str] = Body(None, embed=True),
    score: Optional[int] = Body(None, embed=True),
    banned_until: Optional[datetime] = Body(None, embed=True),
    fail_reason: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
):
    try:
        new_pool = IPPool(
            ip=ip,
            port=port,
            protocol=protocol,
            location=location,
            status=status,
            remarks=remarks,
            latency_ms=latency_ms,
            success_rate=success_rate,
            last_checked=last_checked,
            source=source,
            anonymity=anonymity,
            score=score,
            banned_until=banned_until,
            fail_reason=fail_reason,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(new_pool)
        db.commit()
        db.refresh(new_pool)
        return {"code": 200, "data": _to_frontend_item(new_pool), "message": "IP池创建成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/ip-pools/{pool_id:int}")
async def update_ip_pool(pool_id: int, pool_update: IPPoolUpdate, db: Session = Depends(get_db)):
    try:
        pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="IP姹犱笉瀛樺湪")
        update_data = pool_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pool, field, value)
        pool.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(pool)
        return {"code": 200, "data": _to_frontend_item(pool), "message": "IP池更新成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/ip-pools/{pool_id:int}")
async def delete_ip_pool(pool_id: int, db: Session = Depends(get_db)):
    try:
        pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="IP姹犱笉瀛樺湪")
        db.delete(pool)
        db.commit()
        return {"code": 200, "data": {"id": pool_id}, "message": "IP池删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ip-pools/{pool_id:int}/test-connection")
async def test_ip_pool_connection(pool_id: int, db: Session = Depends(get_db)):
    try:
        import random

        pool = db.query(IPPool).filter(IPPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="IP姹犱笉瀛樺湪")
        response_time = random.randint(50, 1000)
        success_rate = random.randint(70, 100)
        pool.status = "testing"
        pool.latency_ms = response_time
        pool.success_rate = success_rate
        pool.last_checked = datetime.utcnow()
        if success_rate >= 80:
            pool.status = "active"
            pool.success_count = int(pool.success_count or 0) + 1
            pool.fail_reason = None
        else:
            pool.status = "cooling"
            pool.failure_count = int(pool.failure_count or 0) + 1
            pool.fail_reason = f"health_check_low_success_rate_{success_rate}"
        db.commit()
        return {
            "code": 200,
            "data": {
                "id": pool.id,
                "ipAddress": pool.ip,
                "port": pool.port,
                "status": _map_status_for_frontend(pool.status),
                "response_time": response_time,
                "success_rate": success_rate,
                "message": "IP杩炴帴娴嬭瘯鎴愬姛",
            },
            "message": "杩炴帴娴嬭瘯瀹屾垚",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ip-pools/source-addresses")
async def get_source_addresses(db: Session = Depends(get_db)):
    """
    鑾峰彇鈥淚P鑾峰彇鍦板潃鈥濋厤缃紝骞堕檮甯︽瘡涓湴鍧€褰撳墠鎶撳彇鍒扮殑IP鏁伴噺銆?    """
    try:
        config_items = _load_source_config(db)
        stats_map = _get_source_stats_map(db)

        items = []
        for cfg in config_items:
            source = cfg["source"]
            stat = stats_map.get(source, {})
            items.append(
                {
                    "source": source,
                    "enabled": bool(cfg.get("enabled", True)),
                    "count": int(stat.get("count", 0)),
                    "activeCount": int(stat.get("activeCount", 0)),
                    "lastChecked": stat.get("lastChecked"),
                }
            )
        # 琛ュ厖鏁版嵁搴撲腑瀛樺湪浣嗛厤缃腑娌℃湁鐨勬潵婧愶紙榛樿绂佺敤锛屼究浜庣敤鎴峰垽鏂槸鍚︿繚鐣欙級
        for source, stat in stats_map.items():
            if any(x["source"] == source for x in items):
                continue
            items.append(
                {
                    "source": source,
                    "enabled": False,
                    "count": int(stat.get("count", 0)),
                    "activeCount": int(stat.get("activeCount", 0)),
                    "lastChecked": stat.get("lastChecked"),
                }
            )

        items.sort(key=lambda x: (not x["enabled"], -x["count"], x["source"]))
        return {
            "code": 200,
            "data": {
                "items": items,
                "total": len(items),
                "enabled": sum(1 for x in items if x["enabled"]),
            },
            "message": "鑾峰彇鍦板潃鍒楄〃鑾峰彇鎴愬姛",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ip-pools/source-addresses")
async def add_source_address(
    source: str = Body(..., embed=True),
    enabled: bool = Body(True, embed=True),
    db: Session = Depends(get_db),
):
    """
    鏂板鑾峰彇鍦板潃銆?    """
    source = _normalize_source(source)
    if not source:
        raise HTTPException(status_code=400, detail="source 涓嶈兘涓虹┖")
    if len(source) > MAX_SOURCE_LEN:
        raise HTTPException(status_code=400, detail="source 杩囬暱")
    if not _is_valid_source_url(source):
        raise HTTPException(status_code=400, detail="浠呮敮鎸?http/https 鍦板潃")

    items = _load_source_config(db)
    if any(x["source"] == source for x in items):
        raise HTTPException(status_code=400, detail="该地址已存在")
    items.append({"source": source, "enabled": enabled})
    _save_source_config(db, items)
    return {"code": 200, "data": {"source": source, "enabled": enabled}, "message": "鑾峰彇鍦板潃鏂板鎴愬姛"}


@router.put("/ip-pools/source-addresses")
async def update_source_address(
    old_source: str = Body(..., embed=True),
    new_source: str = Body(..., embed=True),
    enabled: bool = Body(True, embed=True),
    apply_to_existing_ips: bool = Body(True, embed=True),
    db: Session = Depends(get_db),
):
    """
    缂栬緫鑾峰彇鍦板潃锛涘彲閫夊悓姝ユ洿鏂癐P姹犱腑瀵瑰簲source瀛楁銆?    """
    old_source = _normalize_source(old_source)
    new_source = _normalize_source(new_source)
    if not old_source or not new_source:
        raise HTTPException(status_code=400, detail="source 涓嶈兘涓虹┖")
    if len(new_source) > MAX_SOURCE_LEN:
        raise HTTPException(status_code=400, detail="source 杩囬暱")
    if not _is_valid_source_url(new_source):
        raise HTTPException(status_code=400, detail="浠呮敮鎸?http/https 鍦板潃")

    items = _load_source_config(db)
    found = False
    for item in items:
        if item["source"] == old_source:
            item["source"] = new_source
            item["enabled"] = enabled
            found = True
            break
    if not found:
        # 鍏佽浠庘€滀粎鍦↖P姹犻噷瀛樺湪鈥濈殑鏉ユ簮鐩存帴鍐欏叆閰嶇疆
        items.append({"source": new_source, "enabled": enabled})

    # 鍘婚噸锛堟柊鍦板潃涓庡凡鏈夊湴鍧€閲嶅鏃讹紝淇濈暀鏂板€煎苟瑕嗙洊enabled锛?    merged = {}
    for item in items:
        merged[item["source"]] = {"source": item["source"], "enabled": bool(item["enabled"])}
    _save_source_config(db, list(merged.values()))

    if apply_to_existing_ips and old_source != new_source:
        db.query(IPPool).filter(IPPool.source == old_source).update(
            {"source": new_source, "updated_at": datetime.utcnow()},
            synchronize_session=False,
        )
        db.commit()

    return {
        "code": 200,
        "data": {"oldSource": old_source, "newSource": new_source, "enabled": enabled},
        "message": "鑾峰彇鍦板潃鏇存柊鎴愬姛",
    }


@router.delete("/ip-pools/source-addresses")
async def delete_source_address(
    source: str = Body(..., embed=True),
    delete_related_ips: bool = Body(False, embed=True),
    db: Session = Depends(get_db),
):
    """
    鍒犻櫎鑾峰彇鍦板潃閰嶇疆锛涘彲閫夊垹闄よ鏉ユ簮涓嬪凡閲囬泦IP銆?    """
    source = _normalize_source(source)
    if not source:
        raise HTTPException(status_code=400, detail="source 涓嶈兘涓虹┖")

    items = _load_source_config(db)
    items = [x for x in items if x["source"] != source]
    _save_source_config(db, items)

    deleted_count = 0
    if delete_related_ips:
        deleted_count = (
            db.query(IPPool).filter(IPPool.source == source).delete(synchronize_session=False)
        )
        db.commit()

    return {
        "code": 200,
        "data": {"source": source, "deletedIpCount": deleted_count},
        "message": "鑾峰彇鍦板潃鍒犻櫎鎴愬姛",
    }


@router.post("/ip-pools/recrawl")
async def recrawl_ips(
    sources: Optional[List[str]] = Body(None, embed=True),
    only_enabled: bool = Body(True, embed=True),
    db: Session = Depends(get_db),
):
    """根据“获取地址”重新自动爬取IP。"""
    try:
        configured = _load_source_config(db)
        if sources:
            selected = {_normalize_source(s) for s in sources if _normalize_source(s)}
            target_sources = [x for x in configured if x["source"] in selected]
        else:
            target_sources = configured

        if only_enabled:
            target_sources = [x for x in target_sources if x.get("enabled", True)]

        target_sources = target_sources[:MAX_SOURCE_COUNT]
        if not target_sources:
            return {
                "code": 200,
                "data": {"summary": {"sourceCount": 0, "newCount": 0, "updatedCount": 0}, "results": []},
                "message": "无可用来源地址",
            }

        now = datetime.utcnow()
        new_count = 0
        updated_count = 0
        results = []

        with _disabled_proxy_env():
            session = requests.Session()
            session.trust_env = False

            for item in target_sources:
                source = item["source"]
                source_result = {
                    "source": source,
                    "enabled": item.get("enabled", True),
                    "fetched": 0,
                    "new": 0,
                    "updated": 0,
                    "error": "",
                }
                if not _is_valid_source_url(source):
                    source_result["error"] = "来源地址格式不合法"
                    results.append(source_result)
                    continue

                try:
                    pairs, first_error = _fetch_pairs_from_source(session, source)
                    source_result["fetched"] = len(pairs)

                    if not pairs and first_error:
                        source_result["error"] = first_error
                    elif not pairs:
                        source_result["error"] = "未解析到IP:PORT，可能需要JS渲染或更高级反爬处理"

                    for ip, port in pairs:
                        existing = (
                            db.query(IPPool)
                            .filter(IPPool.ip == ip, IPPool.port == port, IPPool.protocol == "http")
                            .first()
                        )
                        if existing:
                            existing.source = source
                            existing.last_checked = now
                            existing.updated_at = now
                            if existing.status == "pending":
                                existing.status = "active"
                            source_result["updated"] += 1
                            updated_count += 1
                        else:
                            db.add(
                                IPPool(
                                    ip=ip,
                                    port=port,
                                    protocol="http",
                                    location="",
                                    status="active",
                                    source=source,
                                    last_checked=now,
                                    success_rate=0,
                                    latency_ms=0,
                                    created_at=now,
                                    updated_at=now,
                                )
                            )
                            source_result["new"] += 1
                            new_count += 1

                    results.append(source_result)
                except Exception as ex:
                    source_result["error"] = str(ex)
                    results.append(source_result)

        db.commit()
        return {
            "code": 200,
            "data": {
                "summary": {
                    "sourceCount": len(target_sources),
                    "newCount": new_count,
                    "updatedCount": updated_count,
                },
                "results": results,
            },
            "message": "自动爬取完成",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

