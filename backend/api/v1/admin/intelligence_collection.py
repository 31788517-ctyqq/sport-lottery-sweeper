from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import uuid
from datetime import datetime, timedelta
from html import unescape
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from ....database_async import AsyncSessionLocal, get_async_db
from ....models.intelligence_collection import (
    IntelligenceChannelBinding,
    IntelligenceCollectionItem,
    IntelligenceCollectionMatchSubtask,
    IntelligenceCollectionTask,
    IntelligencePushTask,
    IntelligenceUserSubscription,
)
from ....models.match import League, Match, Team
from ....models.llm_provider import LLMProvider, LLMProviderTypeEnum
from ....models.system_config import SystemConfig
from ...deps import get_current_admin
from ....core.security import decrypt_sensitive_data
from ....config import settings as app_settings
from ....services.dingtalk_integration import send_dingtalk_message
from ....tasks.intelligence_collection_queue_app import celery_app as task_queue_app


router = APIRouter(prefix="/intelligence/collection", tags=["intelligence-collection"])
logger = logging.getLogger(__name__)

PREDICTION_TYPES = {
    "win_draw_lose",
    "handicap_1x2",
    "correct_score",
    "total_goals",
    "half_full_time",
}

SOURCE_URL_MAP = {
    "sina": "https://sports.sina.com.cn/",
    "netease": "https://sports.163.com/",
    "sohu": "https://sports.sohu.com/",
    "tencent": "https://sports.qq.com/",
    "cctv": "https://sports.cctv.com/",
    "weibo": "https://weibo.com/",
    "wechat": "https://mp.weixin.qq.com/",
    "500w": "https://trade.500.com/",
    "ttyingqiu": "https://www.ttyingqiu.com/",
    "toutiao": "https://www.toutiao.com/",
}

INTELLIGENCE_TIME_WINDOW_BEFORE_KEY = "intelligence.collection.time_window.before_hours"
INTELLIGENCE_TIME_WINDOW_AFTER_KEY = "intelligence.collection.time_window.after_hours"
INTELLIGENCE_TIME_WINDOW_STRICT_MODE_KEY = "intelligence.collection.time_window.strict_mode"
INTELLIGENCE_COLLECTION_NETWORK_KEY = "intelligence.collection.network"
INTELLIGENCE_COLLECTION_SOURCE_RULES_KEY = "intelligence.collection.source_rules"
INTELLIGENCE_COLLECTION_QUALITY_THRESHOLDS_KEY = "intelligence.collection.quality_thresholds"
INTELLIGENCE_COLLECTION_ALIAS_DICTIONARY_KEY = "intelligence.collection.alias_dictionary"
INTELLIGENCE_TIME_WINDOW_GROUP = "intelligence_collection"
DEFAULT_TIME_WINDOW_BEFORE_HOURS = 240
DEFAULT_TIME_WINDOW_AFTER_HOURS = 12
DEFAULT_TIME_WINDOW_STRICT_MODE = True
TIME_WINDOW_BEFORE_HOURS_MIN = 1
TIME_WINDOW_BEFORE_HOURS_MAX = 720
TIME_WINDOW_AFTER_HOURS_MIN = 0
TIME_WINDOW_AFTER_HOURS_MAX = 72

DEFAULT_AI_ENHANCEMENT_SETTINGS = {
    "enabled": True,
    "provider": "qwen",
    "model": "qwen-turbo",
    "temperature": 0.2,
    "max_tokens": 420,
    "timeout_seconds": 10,
    "min_quality_score": 1.8,
    "max_calls_per_task": 40,
}

TASK_TERMINAL_STATUSES = {"success", "partial", "failed", "cancelled"}
TASK_QUEUE_NAME = "backend.tasks.intelligence_collection_tasks.run_intelligence_collection_task"
TASK_QUEUE_ACTIVE_STATES = {"PENDING", "RECEIVED", "STARTED", "RETRY"}
TASK_QUEUE_FAILURE_STATES = {"FAILURE"}
TASK_QUEUE_CANCELLED_STATES = {"REVOKED"}
TASK_EVENT_DEFAULT_INTERVAL_MS = 2500
TASK_EVENT_MIN_INTERVAL_MS = 800
TASK_EVENT_MAX_INTERVAL_MS = 10000
TASK_EVENT_DEFAULT_MAX_DURATION_SECONDS = 600
TASK_EVENT_MIN_DURATION_SECONDS = 15
TASK_EVENT_MAX_DURATION_SECONDS = 3600

TASK_EVENT_STAGE_PATTERNS = [
    (re.compile(r"retry triggered", re.IGNORECASE), "retrying"),
    (re.compile(r"task cancelled|queue job revoked|queue revoke failed", re.IGNORECASE), "cancelled"),
    (re.compile(r"queued task via celery|immediate task queued", re.IGNORECASE), "queued"),
    (re.compile(r"pending task dispatched|queue state synced: .* -> running", re.IGNORECASE), "dispatching"),
    (re.compile(r"match run started|decision match_id=", re.IGNORECASE), "collecting"),
    (re.compile(r"source_runtime|ai_runtime summary|top fallback reasons", re.IGNORECASE), "aggregating"),
    (re.compile(r"queue state synced: success|match run done", re.IGNORECASE), "completed"),
    (re.compile(r"failed", re.IGNORECASE), "failed"),
]


def _normalize_int(value: Any, *, default: int, min_value: int, max_value: int) -> int:
    try:
        iv = int(value)
    except Exception:
        iv = int(default)
    if iv < min_value:
        return min_value
    if iv > max_value:
        return max_value
    return iv


def _normalize_float(value: Any, *, default: float, min_value: float, max_value: float) -> float:
    try:
        fv = float(value)
    except Exception:
        fv = float(default)
    if fv < min_value:
        return min_value
    if fv > max_value:
        return max_value
    return fv


def _normalize_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return bool(default)
    txt = str(value).strip().lower()
    if txt in {"1", "true", "yes", "y", "on"}:
        return True
    if txt in {"0", "false", "no", "n", "off"}:
        return False
    return bool(default)


def _deep_merge_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in base.items():
        if isinstance(v, dict):
            out[k] = _deep_merge_dict(v, {})
        elif isinstance(v, list):
            out[k] = list(v)
        else:
            out[k] = v
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge_dict(out.get(k, {}), v)
        elif isinstance(v, list):
            out[k] = list(v)
        else:
            out[k] = v
    return out


def _default_network_settings() -> Dict[str, Any]:
    return {
        "trust_env": False,
        "source_timeout_seconds": {
            "default": 2.5,
            "500w": 2.8,
            "ttyingqiu": 3.5,
            "tencent": 2.8,
            "weibo": 2.8,
            "sina": 2.8,
        },
        "max_retry": 2,
        "retry_backoff_ms": 120,
        "circuit_breaker_threshold": 6,
        "circuit_breaker_seconds": 45,
    }


def _default_source_rules() -> Dict[str, Any]:
    return {
        "ttyingqiu": {
            "blacklist_exact_paths": ["/news/-1", "/news/75"],
            "soft_penalty_paths": {"/news/3": 1.2, "/news/6009": 1.2},
            "forbidden_path_contains": [
                "/news/home",
                "/news/tag",
                "/news/topic",
                "/news/index",
                "/news/list",
                "live/leagueindex",
            ],
            "require_numeric_news_detail": True,
        },
        "sina": {
            "deny_host_exact": ["weather.sina.com.cn"],
            "allowed_host_suffix": ["sports.sina.com.cn"],
        },
        "tencent": {
            "allowed_host_suffix": ["qq.com"],
        },
        "500w": {
            "allowed_host_suffix": ["500.com"],
        },
    }


def _default_quality_thresholds() -> Dict[str, Any]:
    return {
        "min_title_len": 6,
        "min_context_hits": 1,
        "min_excerpt_len": {
            "prediction": 80,
            "off_field": 120,
            "weibo": 40,
        },
        "min_match_score_by_source": {
            "500w": 1.6,
            "sina": 1.5,
            "tencent": 1.6,
            "weibo": 1.4,
            "ttyingqiu": 1.8,
            "default": 1.8,
        },
        "soft_page_filter": {
            "min_body_len": 120,
            "min_team_hits": 1,
        },
        "low_quality_title_hints": [
            "首页",
            "列表",
            "赛程",
            "直播",
            "赔率",
            "开奖",
            "专题",
            "标签",
            "新闻中心",
            "频道",
            "聚合",
            "快讯",
            "官方公告",
            "图片",
            "视频",
            "博彩",
            "彩票",
        ],
    }


def _default_alias_dictionary() -> Dict[str, Any]:
    return {
        "league": {},
        "team": {},
    }


def _normalize_source_timeout_map(raw: Any, fallback: Dict[str, Any]) -> Dict[str, float]:
    defaults = {str(k): float(v) for k, v in (fallback or {}).items() if isinstance(v, (int, float, str))}
    src = raw if isinstance(raw, dict) else {}
    out: Dict[str, float] = {}
    for key, value in defaults.items():
        out[key] = _normalize_float(value, default=value, min_value=0.3, max_value=30.0)
    for key, value in src.items():
        k = str(key).strip()
        if not k:
            continue
        out[k] = _normalize_float(value, default=out.get(k, 2.5), min_value=0.3, max_value=30.0)
    if "default" not in out:
        out["default"] = 2.5
    return out


async def _load_config_rows(db: AsyncSession, keys: List[str]) -> Dict[str, SystemConfig]:
    rows = (
        await db.execute(
            select(SystemConfig).where(SystemConfig.config_key.in_(keys))
        )
    ).scalars().all()
    return {str(x.config_key): x for x in rows}


async def _upsert_config_row(
    db: AsyncSession,
    *,
    key: str,
    name: str,
    value: str,
    config_type: str,
    description: str,
    group: str,
    admin_id: Optional[int],
) -> None:
    row = (
        await db.execute(
            select(SystemConfig).where(SystemConfig.config_key == key).limit(1)
        )
    ).scalar_one_or_none()
    effective_admin_id = int(admin_id or 0) or None
    if not row:
        row = SystemConfig(
            config_key=key,
            config_name=name,
            config_value=value,
            config_type=config_type,
            description=description,
            group=group,
            is_active=True,
            created_by=effective_admin_id,
            updated_by=effective_admin_id,
        )
        db.add(row)
        return
    row.config_name = name
    row.config_value = value
    row.config_type = config_type
    row.description = description
    row.group = group
    row.is_active = True
    row.updated_by = effective_admin_id


async def _load_json_config(
    db: AsyncSession,
    *,
    key: str,
    default_value: Dict[str, Any],
) -> Dict[str, Any]:
    row = (
        await db.execute(
            select(SystemConfig).where(SystemConfig.config_key == key).limit(1)
        )
    ).scalar_one_or_none()
    if not row or not row.is_active:
        return {"value": _deep_merge_dict(default_value, {}), "source": "default"}
    parsed = _json_loads(row.config_value, {})
    if not isinstance(parsed, dict):
        parsed = {}
    merged = _deep_merge_dict(default_value, parsed)
    return {"value": merged, "source": "db"}


def _build_time_window_payload(
    before_hours: int,
    after_hours: int,
    *,
    strict_mode: bool = DEFAULT_TIME_WINDOW_STRICT_MODE,
    source_before: str = "default",
    source_after: str = "default",
    source_strict: str = "default",
) -> Dict[str, Any]:
    return {
        "before_hours": int(before_hours),
        "after_hours": int(after_hours),
        "strict_mode": bool(strict_mode),
        "bounds_label": f"-{int(before_hours)}h ~ +{int(after_hours)}h",
        "source": {"before": source_before, "after": source_after, "strict": source_strict},
        "limits": {
            "before": {"min": TIME_WINDOW_BEFORE_HOURS_MIN, "max": TIME_WINDOW_BEFORE_HOURS_MAX},
            "after": {"min": TIME_WINDOW_AFTER_HOURS_MIN, "max": TIME_WINDOW_AFTER_HOURS_MAX},
        },
    }


async def _load_time_window_config(db: AsyncSession) -> Dict[str, Any]:
    before_hours = DEFAULT_TIME_WINDOW_BEFORE_HOURS
    after_hours = DEFAULT_TIME_WINDOW_AFTER_HOURS
    strict_mode = DEFAULT_TIME_WINDOW_STRICT_MODE
    source_before = "default"
    source_after = "default"
    source_strict = "default"
    try:
        row_map = await _load_config_rows(
            db,
            [
                INTELLIGENCE_TIME_WINDOW_BEFORE_KEY,
                INTELLIGENCE_TIME_WINDOW_AFTER_KEY,
                INTELLIGENCE_TIME_WINDOW_STRICT_MODE_KEY,
            ],
        )
        before_row = row_map.get(INTELLIGENCE_TIME_WINDOW_BEFORE_KEY)
        after_row = row_map.get(INTELLIGENCE_TIME_WINDOW_AFTER_KEY)
        strict_row = row_map.get(INTELLIGENCE_TIME_WINDOW_STRICT_MODE_KEY)
        if before_row and before_row.is_active:
            before_hours = _normalize_int(
                before_row.config_value,
                default=DEFAULT_TIME_WINDOW_BEFORE_HOURS,
                min_value=TIME_WINDOW_BEFORE_HOURS_MIN,
                max_value=TIME_WINDOW_BEFORE_HOURS_MAX,
            )
            source_before = "db"
        if after_row and after_row.is_active:
            after_hours = _normalize_int(
                after_row.config_value,
                default=DEFAULT_TIME_WINDOW_AFTER_HOURS,
                min_value=TIME_WINDOW_AFTER_HOURS_MIN,
                max_value=TIME_WINDOW_AFTER_HOURS_MAX,
            )
            source_after = "db"
        if strict_row and strict_row.is_active:
            strict_mode = _normalize_bool(strict_row.config_value, DEFAULT_TIME_WINDOW_STRICT_MODE)
            source_strict = "db"
    except Exception as e:
        logger.warning("[intelligence.collection.settings] load time-window config failed: %s", e)

    return _build_time_window_payload(
        before_hours,
        after_hours,
        strict_mode=strict_mode,
        source_before=source_before,
        source_after=source_after,
        source_strict=source_strict,
    )


async def _upsert_time_window_config(
    db: AsyncSession,
    *,
    before_hours: int,
    after_hours: int,
    strict_mode: bool,
    admin_id: Optional[int],
) -> Dict[str, Any]:
    before_hours = _normalize_int(
        before_hours,
        default=DEFAULT_TIME_WINDOW_BEFORE_HOURS,
        min_value=TIME_WINDOW_BEFORE_HOURS_MIN,
        max_value=TIME_WINDOW_BEFORE_HOURS_MAX,
    )
    after_hours = _normalize_int(
        after_hours,
        default=DEFAULT_TIME_WINDOW_AFTER_HOURS,
        min_value=TIME_WINDOW_AFTER_HOURS_MIN,
        max_value=TIME_WINDOW_AFTER_HOURS_MAX,
    )
    strict_mode = _normalize_bool(strict_mode, DEFAULT_TIME_WINDOW_STRICT_MODE)

    definitions = [
        (
            INTELLIGENCE_TIME_WINDOW_BEFORE_KEY,
            "情报采集时间窗-赛前小时数",
            str(before_hours),
            "integer",
            "比赛开赛前允许命中的文章发布时间窗口（小时）",
        ),
        (
            INTELLIGENCE_TIME_WINDOW_AFTER_KEY,
            "情报采集时间窗-赛后小时数",
            str(after_hours),
            "integer",
            "比赛开赛后允许命中的文章发布时间窗口（小时）",
        ),
        (
            INTELLIGENCE_TIME_WINDOW_STRICT_MODE_KEY,
            "情报采集时间窗-硬门槛开关",
            "true" if strict_mode else "false",
            "boolean",
            "开启后，发布时间超出窗口或无法解析发布时间将直接拦截",
        ),
    ]
    for key, name, value, config_type, desc in definitions:
        await _upsert_config_row(
            db,
            key=key,
            name=name,
            value=value,
            config_type=config_type,
            description=desc,
            group=INTELLIGENCE_TIME_WINDOW_GROUP,
            admin_id=admin_id,
        )
    await db.commit()
    return await _load_time_window_config(db)


def _build_network_settings_payload(config: Dict[str, Any], *, source: str) -> Dict[str, Any]:
    defaults = _default_network_settings()
    merged = _deep_merge_dict(defaults, config or {})
    timeout_map = _normalize_source_timeout_map(
        merged.get("source_timeout_seconds"),
        defaults.get("source_timeout_seconds", {}),
    )
    payload = {
        "trust_env": _normalize_bool(merged.get("trust_env"), defaults["trust_env"]),
        "source_timeout_seconds": timeout_map,
        "max_retry": _normalize_int(merged.get("max_retry"), default=defaults["max_retry"], min_value=1, max_value=5),
        "retry_backoff_ms": _normalize_int(
            merged.get("retry_backoff_ms"), default=defaults["retry_backoff_ms"], min_value=0, max_value=5000
        ),
        "circuit_breaker_threshold": _normalize_int(
            merged.get("circuit_breaker_threshold"),
            default=defaults["circuit_breaker_threshold"],
            min_value=1,
            max_value=50,
        ),
        "circuit_breaker_seconds": _normalize_int(
            merged.get("circuit_breaker_seconds"),
            default=defaults["circuit_breaker_seconds"],
            min_value=1,
            max_value=600,
        ),
    }
    payload["source"] = source
    payload["limits"] = {
        "max_retry": {"min": 1, "max": 5},
        "retry_backoff_ms": {"min": 0, "max": 5000},
        "circuit_breaker_threshold": {"min": 1, "max": 50},
        "circuit_breaker_seconds": {"min": 1, "max": 600},
        "timeout_seconds": {"min": 0.3, "max": 30.0},
    }
    return payload


async def _load_network_settings(db: AsyncSession) -> Dict[str, Any]:
    cfg = await _load_json_config(
        db,
        key=INTELLIGENCE_COLLECTION_NETWORK_KEY,
        default_value=_default_network_settings(),
    )
    return _build_network_settings_payload(cfg["value"], source=cfg["source"])


async def _upsert_network_settings(
    db: AsyncSession,
    *,
    payload: Dict[str, Any],
    admin_id: Optional[int],
) -> Dict[str, Any]:
    normalized = _build_network_settings_payload(payload or {}, source="db")
    save_obj = {k: v for k, v in normalized.items() if k not in {"source", "limits"}}
    await _upsert_config_row(
        db,
        key=INTELLIGENCE_COLLECTION_NETWORK_KEY,
        name="情报采集网络配置",
        value=_json_dumps(save_obj),
        config_type="json",
        description="采集请求网络策略（代理、超时、重试、熔断）",
        group=INTELLIGENCE_TIME_WINDOW_GROUP,
        admin_id=admin_id,
    )
    await db.commit()
    return await _load_network_settings(db)


def _build_source_rules_payload(config: Dict[str, Any], *, source: str) -> Dict[str, Any]:
    merged = _deep_merge_dict(_default_source_rules(), config or {})
    tty_rules = merged.get("ttyingqiu", {})
    tty_rules["blacklist_exact_paths"] = sorted(
        {
            (str(x).strip().lower().rstrip("/") or "/")
            for x in (tty_rules.get("blacklist_exact_paths") or [])
            if str(x).strip()
        }
    )
    soft_map = tty_rules.get("soft_penalty_paths") if isinstance(tty_rules.get("soft_penalty_paths"), dict) else {}
    tty_rules["soft_penalty_paths"] = {
        str(k).strip().lower().rstrip("/") or "/": _normalize_float(v, default=1.0, min_value=0.0, max_value=5.0)
        for k, v in soft_map.items()
        if str(k).strip()
    }
    tty_rules["forbidden_path_contains"] = [
        str(x).strip().lower()
        for x in (tty_rules.get("forbidden_path_contains") or [])
        if str(x).strip()
    ]
    tty_rules["require_numeric_news_detail"] = _normalize_bool(
        tty_rules.get("require_numeric_news_detail"), True
    )
    merged["ttyingqiu"] = tty_rules
    return {"rules": merged, "source": source}


async def _load_source_rules(db: AsyncSession) -> Dict[str, Any]:
    cfg = await _load_json_config(
        db,
        key=INTELLIGENCE_COLLECTION_SOURCE_RULES_KEY,
        default_value=_default_source_rules(),
    )
    return _build_source_rules_payload(cfg["value"], source=cfg["source"])


async def _upsert_source_rules(
    db: AsyncSession,
    *,
    payload: Dict[str, Any],
    admin_id: Optional[int],
) -> Dict[str, Any]:
    normalized = _build_source_rules_payload(payload or {}, source="db")
    await _upsert_config_row(
        db,
        key=INTELLIGENCE_COLLECTION_SOURCE_RULES_KEY,
        name="情报采集来源规则",
        value=_json_dumps(normalized["rules"]),
        config_type="json",
        description="来源规则：黑名单/降权/路径约束",
        group=INTELLIGENCE_TIME_WINDOW_GROUP,
        admin_id=admin_id,
    )
    await db.commit()
    return await _load_source_rules(db)


def _build_quality_thresholds_payload(config: Dict[str, Any], *, source: str) -> Dict[str, Any]:
    defaults = _default_quality_thresholds()
    merged = _deep_merge_dict(defaults, config or {})
    merged["min_title_len"] = _normalize_int(merged.get("min_title_len"), default=defaults["min_title_len"], min_value=2, max_value=40)
    merged["min_context_hits"] = _normalize_int(
        merged.get("min_context_hits"),
        default=defaults["min_context_hits"],
        min_value=1,
        max_value=5,
    )
    min_excerpt = merged.get("min_excerpt_len") if isinstance(merged.get("min_excerpt_len"), dict) else {}
    merged["min_excerpt_len"] = {
        "prediction": _normalize_int(
            min_excerpt.get("prediction", defaults["min_excerpt_len"]["prediction"]),
            default=defaults["min_excerpt_len"]["prediction"],
            min_value=20,
            max_value=500,
        ),
        "off_field": _normalize_int(
            min_excerpt.get("off_field", defaults["min_excerpt_len"]["off_field"]),
            default=defaults["min_excerpt_len"]["off_field"],
            min_value=40,
            max_value=800,
        ),
        "weibo": _normalize_int(
            min_excerpt.get("weibo", defaults["min_excerpt_len"]["weibo"]),
            default=defaults["min_excerpt_len"]["weibo"],
            min_value=10,
            max_value=300,
        ),
    }
    score_map = merged.get("min_match_score_by_source") if isinstance(merged.get("min_match_score_by_source"), dict) else {}
    merged["min_match_score_by_source"] = {
        str(k): _normalize_float(v, default=1.8, min_value=0.0, max_value=10.0)
        for k, v in score_map.items()
    }
    if "default" not in merged["min_match_score_by_source"]:
        merged["min_match_score_by_source"]["default"] = defaults["min_match_score_by_source"]["default"]

    soft_filter = merged.get("soft_page_filter") if isinstance(merged.get("soft_page_filter"), dict) else {}
    merged["soft_page_filter"] = {
        "min_body_len": _normalize_int(
            soft_filter.get("min_body_len", defaults["soft_page_filter"]["min_body_len"]),
            default=defaults["soft_page_filter"]["min_body_len"],
            min_value=20,
            max_value=2000,
        ),
        "min_team_hits": _normalize_int(
            soft_filter.get("min_team_hits", defaults["soft_page_filter"]["min_team_hits"]),
            default=defaults["soft_page_filter"]["min_team_hits"],
            min_value=1,
            max_value=5,
        ),
    }
    merged["low_quality_title_hints"] = [
        str(x).strip().lower()
        for x in (merged.get("low_quality_title_hints") or defaults["low_quality_title_hints"])
        if str(x).strip()
    ]
    return {"thresholds": merged, "source": source}


async def _load_quality_thresholds(db: AsyncSession) -> Dict[str, Any]:
    cfg = await _load_json_config(
        db,
        key=INTELLIGENCE_COLLECTION_QUALITY_THRESHOLDS_KEY,
        default_value=_default_quality_thresholds(),
    )
    return _build_quality_thresholds_payload(cfg["value"], source=cfg["source"])


async def _upsert_quality_thresholds(
    db: AsyncSession,
    *,
    payload: Dict[str, Any],
    admin_id: Optional[int],
) -> Dict[str, Any]:
    normalized = _build_quality_thresholds_payload(payload or {}, source="db")
    await _upsert_config_row(
        db,
        key=INTELLIGENCE_COLLECTION_QUALITY_THRESHOLDS_KEY,
        name="情报采集质量阈值",
        value=_json_dumps(normalized["thresholds"]),
        config_type="json",
        description="采集质量过滤阈值（标题、正文、命中词、来源分数）",
        group=INTELLIGENCE_TIME_WINDOW_GROUP,
        admin_id=admin_id,
    )
    await db.commit()
    return await _load_quality_thresholds(db)


def _build_alias_dictionary_payload(config: Dict[str, Any], *, source: str) -> Dict[str, Any]:
    merged = _deep_merge_dict(_default_alias_dictionary(), config or {})

    def _normalize_alias_map(raw: Any) -> Dict[str, List[str]]:
        src_map = raw if isinstance(raw, dict) else {}
        out: Dict[str, List[str]] = {}
        for canonical, aliases in src_map.items():
            key = str(canonical).strip()
            if not key:
                continue
            values = aliases if isinstance(aliases, list) else [aliases]
            cleaned = [str(x).strip() for x in values if str(x).strip()]
            if cleaned:
                out[key] = cleaned
        return out

    merged["league"] = _normalize_alias_map(merged.get("league"))
    merged["team"] = _normalize_alias_map(merged.get("team"))
    return {"dictionary": merged, "source": source}


async def _load_alias_dictionary(db: AsyncSession) -> Dict[str, Any]:
    cfg = await _load_json_config(
        db,
        key=INTELLIGENCE_COLLECTION_ALIAS_DICTIONARY_KEY,
        default_value=_default_alias_dictionary(),
    )
    return _build_alias_dictionary_payload(cfg["value"], source=cfg["source"])


async def _upsert_alias_dictionary(
    db: AsyncSession,
    *,
    payload: Dict[str, Any],
    admin_id: Optional[int],
) -> Dict[str, Any]:
    normalized = _build_alias_dictionary_payload(payload or {}, source="db")
    await _upsert_config_row(
        db,
        key=INTELLIGENCE_COLLECTION_ALIAS_DICTIONARY_KEY,
        name="情报采集别名词典",
        value=_json_dumps(normalized["dictionary"]),
        config_type="json",
        description="球队/联赛别名词典（中英、简称、繁简）",
        group=INTELLIGENCE_TIME_WINDOW_GROUP,
        admin_id=admin_id,
    )
    await db.commit()
    return await _load_alias_dictionary(db)


def _ok(data: Any = None, message: str = "ok") -> Dict[str, Any]:
    return {"success": True, "data": data, "message": message}


def _json_loads(raw: Optional[str], fallback: Any) -> Any:
    if not raw:
        return fallback
    try:
        return json.loads(raw)
    except Exception:
        return fallback


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _append_log(task: IntelligenceCollectionTask, level: str, message: str) -> None:
    logs = _json_loads(task.logs_json, [])
    logs.append(
        {
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "message": message,
        }
    )
    task.logs_json = _json_dumps(logs[-300:])


def _append_subtask_log(subtask: IntelligenceCollectionMatchSubtask, level: str, message: str) -> None:
    logs = _json_loads(subtask.logs_json, [])
    logs.append(
        {
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "message": message,
        }
    )
    subtask.logs_json = _json_dumps(logs[-200:])


def _subtask_to_dict(subtask: IntelligenceCollectionMatchSubtask) -> Dict[str, Any]:
    item_count = int(subtask.item_count or 0)
    success_count = int(subtask.success_count or 0)
    failed_count = int(subtask.failed_count or 0)
    candidate_count = int(subtask.candidate_count or item_count)
    parsed_count = int(subtask.parsed_count or item_count)
    matched_count = int(subtask.matched_count or success_count)
    accepted_count = int(subtask.accepted_count or success_count)
    blocked_count = int(subtask.blocked_count or failed_count)
    return {
        "id": subtask.id,
        "task_id": subtask.task_id,
        "match_id": subtask.match_id,
        "status": subtask.status,
        "expected_count": subtask.expected_count,
        "item_count": item_count,
        "success_count": success_count,
        "failed_count": failed_count,
        "candidate_count": candidate_count,
        "parsed_count": parsed_count,
        "matched_count": matched_count,
        "accepted_count": accepted_count,
        "blocked_count": blocked_count,
        "retry_count": subtask.retry_count,
        "last_error": subtask.last_error,
        "started_at": subtask.started_at.isoformat() if subtask.started_at else None,
        "finished_at": subtask.finished_at.isoformat() if subtask.finished_at else None,
        "created_at": subtask.created_at.isoformat() if subtask.created_at else None,
        "updated_at": subtask.updated_at.isoformat() if subtask.updated_at else None,
    }


def _task_to_dict(task: IntelligenceCollectionTask) -> Dict[str, Any]:
    total_count = int(task.total_count or 0)
    success_count = int(task.success_count or 0)
    progress_percent = round((success_count / total_count) * 100, 2) if total_count > 0 else 0.0
    stored_success_rate = task.success_rate
    if stored_success_rate is None:
        stored_success_rate = round((success_count / total_count), 4) if total_count > 0 else 0.0
    success_rate = round(_safe_float(stored_success_rate, 0.0), 4)
    return {
        "id": task.id,
        "task_uuid": task.task_uuid,
        "task_name": task.task_name,
        "mode": task.mode,
        "status": task.status,
        "match_ids": _json_loads(task.match_ids_json, []),
        "sources": _json_loads(task.sources_json, []),
        "intel_types": _json_loads(task.intel_types_json, []),
        "offset_hours": _json_loads(task.offset_hours_json, []),
        "total_count": total_count,
        "success_count": success_count,
        "failed_count": task.failed_count,
        "success_rate": success_rate,
        "retry_count": task.retry_count,
        "late_run": task.late_run,
        "progress_percent": progress_percent,
        "queue_job_id": task.queue_job_id,
        "estimated_start": task.planned_at.isoformat() if task.planned_at else None,
        "planned_at": task.planned_at.isoformat() if task.planned_at else None,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "finished_at": task.finished_at.isoformat() if task.finished_at else None,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "total_matches": 0,
        "matched_matches": 0,
        "success_matches": 0,
        "failed_matches": 0,
        "partial_matches": 0,
        "coverage_rate": 0.0,
        "expected_per_match": 0,
        "match_progress": [],
    }


def _derive_task_status(
    *,
    total_matches: int,
    success_matches: int,
    failed_matches: int,
    partial_matches: int,
) -> str:
    if total_matches <= 0:
        return "failed"
    if success_matches >= total_matches and failed_matches <= 0 and partial_matches <= 0:
        return "success"
    if failed_matches >= total_matches and success_matches <= 0 and partial_matches <= 0:
        return "failed"
    if success_matches > 0 and failed_matches <= 0 and partial_matches <= 0:
        return "success"
    if failed_matches > 0 and success_matches <= 0 and partial_matches <= 0:
        return "failed"
    return "partial"


def _parse_source_runtime_log(message: str) -> Optional[Dict[str, Any]]:
    text = str(message or "")
    m = re.search(
        r"source_runtime source=([^;]+);\s*requests=(\d+);\s*ok=(\d+);\s*timeout=(\d+);\s*errors=(\d+);\s*retries=(\d+);\s*circuit_skipped=(\d+)",
        text,
    )
    if not m:
        return None
    return {
        "source": _sanitize_meta_text(m.group(1)),
        "requests": int(m.group(2) or 0),
        "ok": int(m.group(3) or 0),
        "timeout": int(m.group(4) or 0),
        "errors": int(m.group(5) or 0),
        "retries": int(m.group(6) or 0),
        "circuit_skipped": int(m.group(7) or 0),
    }


def _extract_reason_tokens_from_log(message: str) -> List[str]:
    text = str(message or "")
    reasons: List[str] = []
    for m in re.findall(r"reason=([^;]+)", text):
        token = _sanitize_meta_text(m)
        if token and token != "-":
            reasons.append(token)
    for pattern in (r"collect failed:\s*(.+)$", r"retry failed:\s*(.+)$", r"match run failed:[^;]*; reason=([^;]+)"):
        m = re.search(pattern, text)
        if not m:
            continue
        token = _sanitize_meta_text(m.group(1))
        if token and token != "-":
            reasons.append(token)
    return reasons


def _task_status_to_stage(status: str) -> str:
    normalized = str(status or "").strip().lower()
    if normalized in {"pending"}:
        return "queued"
    if normalized in {"running"}:
        return "collecting"
    if normalized in {"success", "partial"}:
        return "completed"
    if normalized in {"failed"}:
        return "failed"
    if normalized in {"cancelled"}:
        return "cancelled"
    return "unknown"


def _infer_task_stage_from_logs(status: str, logs: List[Dict[str, Any]]) -> str:
    for entry in reversed(logs[-30:]):
        message = str(entry.get("message") or "")
        for pattern, stage in TASK_EVENT_STAGE_PATTERNS:
            if pattern.search(message):
                return stage
    return _task_status_to_stage(status)


def _extract_task_runtime_context(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    current_source = ""
    current_intel_type = ""
    current_match_id: Optional[int] = None
    last_log: Optional[Dict[str, Any]] = None

    for entry in reversed(logs[-120:]):
        message = str(entry.get("message") or "")
        if not message:
            continue
        if last_log is None:
            last_log = {
                "time": entry.get("time"),
                "level": str(entry.get("level") or "").lower(),
                "message": message[:300],
            }

        if not current_source:
            m_source = re.search(r"\bsource=([^;,\s]+)", message, re.IGNORECASE)
            if m_source:
                current_source = _sanitize_meta_text(m_source.group(1))
        if current_match_id is None:
            m_match = re.search(r"\bmatch_id=(\d+)", message, re.IGNORECASE)
            if m_match:
                try:
                    current_match_id = int(m_match.group(1))
                except Exception:
                    current_match_id = None
        if not current_intel_type:
            m_intel_type = re.search(r"\bintel_type=([^;,\s]+)", message, re.IGNORECASE)
            if m_intel_type:
                current_intel_type = _sanitize_meta_text(m_intel_type.group(1))
        if current_source and current_match_id is not None and current_intel_type:
            break

    return {
        "current_source": current_source or None,
        "current_match_id": current_match_id,
        "current_intel_type": current_intel_type or None,
        "last_log": last_log,
    }


async def _build_task_events_payload(
    db: AsyncSession,
    task: IntelligenceCollectionTask,
    *,
    include_match_progress: bool = False,
) -> Dict[str, Any]:
    task_data = _task_to_dict(task)
    progress_stats = await _collect_task_progress_stats(db, [task])
    task_data.update(progress_stats.get(task.id, {}))

    status = str(task_data.get("status") or "").strip().lower() or "pending"
    logs = _json_loads(task.logs_json, [])
    runtime_ctx = _extract_task_runtime_context(logs)
    stage = _infer_task_stage_from_logs(status, logs)

    payload: Dict[str, Any] = {
        "task_id": int(task_data.get("id") or task.id),
        "task_uuid": task_data.get("task_uuid"),
        "status": status,
        "stage": stage,
        "progress_percent": round(_safe_float(task_data.get("progress_percent"), 0.0), 2),
        "success_rate": round(_safe_float(task_data.get("success_rate"), 0.0), 4),
        "completed_count": int(task_data.get("success_count") or 0),
        "failed_count": int(task_data.get("failed_count") or 0),
        "total_count": int(task_data.get("total_count") or 0),
        "total_matches": int(task_data.get("total_matches") or 0),
        "success_matches": int(task_data.get("success_matches") or 0),
        "failed_matches": int(task_data.get("failed_matches") or 0),
        "partial_matches": int(task_data.get("partial_matches") or 0),
        "coverage_rate": round(_safe_float(task_data.get("coverage_rate"), 0.0), 4),
        "queue_job_id": task_data.get("queue_job_id"),
        "retry_count": int(task_data.get("retry_count") or 0),
        "error_message": _sanitize_meta_text(task_data.get("error_message"), ""),
        "current_source": runtime_ctx.get("current_source"),
        "current_match_id": runtime_ctx.get("current_match_id"),
        "current_intel_type": runtime_ctx.get("current_intel_type"),
        "last_log": runtime_ctx.get("last_log"),
        "terminal": status in TASK_TERMINAL_STATUSES,
        "updated_at": task_data.get("updated_at"),
        "generated_at": datetime.utcnow().isoformat(),
    }
    if include_match_progress:
        payload["match_progress"] = task_data.get("match_progress", [])
    return payload


def _build_task_events_fingerprint(payload: Dict[str, Any]) -> str:
    fingerprint_payload: Dict[str, Any] = {
        "task_id": payload.get("task_id"),
        "status": payload.get("status"),
        "stage": payload.get("stage"),
        "progress_percent": payload.get("progress_percent"),
        "success_rate": payload.get("success_rate"),
        "completed_count": payload.get("completed_count"),
        "failed_count": payload.get("failed_count"),
        "total_count": payload.get("total_count"),
        "total_matches": payload.get("total_matches"),
        "success_matches": payload.get("success_matches"),
        "failed_matches": payload.get("failed_matches"),
        "partial_matches": payload.get("partial_matches"),
        "coverage_rate": payload.get("coverage_rate"),
        "current_source": payload.get("current_source"),
        "current_match_id": payload.get("current_match_id"),
        "current_intel_type": payload.get("current_intel_type"),
        "terminal": payload.get("terminal"),
        "error_message": payload.get("error_message"),
    }
    last_log = payload.get("last_log") or {}
    fingerprint_payload["last_log"] = {
        "time": last_log.get("time"),
        "level": last_log.get("level"),
        "message": last_log.get("message"),
    }
    if "match_progress" in payload:
        fingerprint_payload["match_progress"] = payload.get("match_progress")
    return json.dumps(fingerprint_payload, ensure_ascii=False, sort_keys=True)


def _format_sse_message(event: str, payload: Dict[str, Any], *, event_id: Optional[int] = None) -> str:
    lines: List[str] = []
    if event_id is not None:
        lines.append(f"id: {int(event_id)}")
    if event:
        lines.append(f"event: {event}")
    json_text = _json_dumps(payload)
    for row in json_text.splitlines():
        lines.append(f"data: {row}")
    return "\n".join(lines) + "\n\n"


async def _build_task_completion_snapshot(
    db: AsyncSession,
    task: IntelligenceCollectionTask,
    match_ids: Optional[List[int]] = None,
) -> Dict[str, Any]:
    clean_match_ids = [int(x) for x in (match_ids or []) if str(x).isdigit()]
    stmt = select(IntelligenceCollectionMatchSubtask).where(
        IntelligenceCollectionMatchSubtask.task_id == task.id
    )
    if clean_match_ids:
        stmt = stmt.where(IntelligenceCollectionMatchSubtask.match_id.in_(clean_match_ids))
    rows = (await db.execute(stmt)).scalars().all()

    if not rows:
        fallback_match_ids = clean_match_ids or [int(x) for x in _json_loads(task.match_ids_json, []) if str(x).isdigit()]
        total_matches = len(fallback_match_ids)
        success_matches = 1 if int(task.success_count or 0) > 0 else 0
        failed_matches = total_matches if int(task.success_count or 0) <= 0 else 0
        partial_matches = max(total_matches - success_matches - failed_matches, 0)
        return {
            "total_matches": total_matches,
            "success_matches": success_matches,
            "failed_matches": failed_matches,
            "partial_matches": partial_matches,
            "expected_count": int(task.total_count or 0),
            "success_count": int(task.success_count or 0),
            "failed_count": int(task.failed_count or 0),
            "top_reason": _sanitize_meta_text(task.error_message),
            "status": _derive_task_status(
                total_matches=total_matches,
                success_matches=success_matches,
                failed_matches=failed_matches,
                partial_matches=partial_matches,
            ),
        }

    status_counter = {"success": 0, "failed": 0, "partial": 0, "pending": 0, "running": 0, "cancelled": 0}
    reason_counter: Dict[str, int] = {}
    expected_count = 0
    success_count = 0
    failed_count = 0

    for row in rows:
        status = str(row.status or "pending").strip().lower()
        if status not in status_counter:
            status = "pending"
        status_counter[status] += 1
        expected_count += int(row.expected_count or 0)
        success_count += int(row.success_count or 0)
        failed_count += int(row.failed_count or 0)
        if row.last_error:
            key = _sanitize_meta_text(row.last_error)
            if key:
                reason_counter[key] = reason_counter.get(key, 0) + 1

    total_matches = len(rows)
    success_matches = int(status_counter["success"])
    failed_matches = int(status_counter["failed"])
    partial_matches = int(status_counter["partial"])
    top_reason = ""
    if reason_counter:
        top_reason = sorted(reason_counter.items(), key=lambda kv: kv[1], reverse=True)[0][0]

    status = _derive_task_status(
        total_matches=total_matches,
        success_matches=success_matches,
        failed_matches=failed_matches,
        partial_matches=partial_matches,
    )
    return {
        "total_matches": total_matches,
        "success_matches": success_matches,
        "failed_matches": failed_matches,
        "partial_matches": partial_matches,
        "expected_count": expected_count,
        "success_count": success_count,
        "failed_count": failed_count,
        "top_reason": top_reason,
        "status": status,
    }


async def _finalize_task_after_run(
    db: AsyncSession,
    task: IntelligenceCollectionTask,
    *,
    match_ids: Optional[List[int]] = None,
    sources: Optional[List[str]] = None,
    intel_types: Optional[List[str]] = None,
    trigger: str = "run",
) -> Dict[str, Any]:
    snapshot = await _build_task_completion_snapshot(db, task, match_ids=match_ids)
    run_match_ids = [int(x) for x in (match_ids or _json_loads(task.match_ids_json, [])) if str(x).isdigit()]
    run_sources = [str(x) for x in (sources or _json_loads(task.sources_json, [])) if str(x).strip()]
    run_intel_types = [str(x) for x in (intel_types or _json_loads(task.intel_types_json, [])) if str(x).strip()]
    desired_total = len(run_match_ids) * len(run_sources) * len(run_intel_types)

    total_count = max(
        desired_total,
        int(snapshot.get("expected_count") or 0),
        int(snapshot.get("success_count") or 0) + int(snapshot.get("failed_count") or 0),
        int(task.total_count or 0),
    )
    success_count = int(snapshot.get("success_count") or 0)
    failed_count = int(snapshot.get("failed_count") or 0)
    task.total_count = int(total_count)
    task.success_count = int(success_count)
    task.failed_count = int(failed_count)
    task.status = str(snapshot.get("status") or "failed")
    task.finished_at = datetime.utcnow()
    success_rate = round((success_count / total_count), 4) if total_count > 0 else 0.0
    task.success_rate = success_rate
    top_reason = _sanitize_meta_text(snapshot.get("top_reason"), "")
    if task.status == "failed":
        task.error_message = top_reason or "all-failed"
    elif task.status == "partial":
        task.error_message = top_reason or None
    else:
        task.error_message = None

    final_log_level = "success" if task.status == "success" else ("warning" if task.status == "partial" else "error")
    _append_log(
        task,
        final_log_level,
        (
            f"{trigger} finalized: status={task.status}; "
            f"success_count={success_count}; failed_count={failed_count}; total_count={total_count}; "
            f"success_rate={success_rate}"
        ),
    )
    return {
        **snapshot,
        "success_rate": success_rate,
        "status": task.status,
    }


async def _run_collection_task_async(
    task_id: int,
    *,
    trigger: str,
    run_match_ids: Optional[List[int]] = None,
    run_sources: Optional[List[str]] = None,
    run_intel_types: Optional[List[str]] = None,
) -> None:
    async with AsyncSessionLocal() as session:
        task = await session.get(IntelligenceCollectionTask, task_id)
        if not task:
            return
        if str(task.status or "").lower() == "cancelled":
            return

        actual_match_ids = [int(x) for x in (run_match_ids or _json_loads(task.match_ids_json, [])) if str(x).isdigit()]
        actual_sources = [str(x) for x in (run_sources or _json_loads(task.sources_json, [])) if str(x).strip()]
        actual_intel_types = [str(x) for x in (run_intel_types or _json_loads(task.intel_types_json, [])) if str(x).strip()]
        if not actual_match_ids or not actual_sources or not actual_intel_types:
            task.status = "failed"
            task.finished_at = datetime.utcnow()
            task.error_message = "task scope is empty"
            task.success_rate = 0.0
            _append_log(task, "error", f"{trigger} failed: task scope is empty")
            await session.commit()
            return

        try:
            task.status = "running"
            task.started_at = task.started_at or datetime.utcnow()
            task.finished_at = None
            task.error_message = None
            task.total_count = max(int(task.total_count or 0), len(actual_match_ids) * len(actual_sources) * len(actual_intel_types))
            _append_log(
                task,
                "info",
                (
                    f"{trigger} started: "
                    f"scope(match_ids={actual_match_ids}, sources={actual_sources}, intel_types={actual_intel_types})"
                ),
            )
            await _ensure_task_match_subtasks(
                db=session,
                task=task,
                match_ids=actual_match_ids,
                sources=actual_sources,
                intel_types=actual_intel_types,
            )
            await session.commit()

            stats = await _simulate_collect_items(
                db=session,
                task=task,
                match_ids=actual_match_ids,
                sources=actual_sources,
                intel_types=actual_intel_types,
            )
            if stats.get("fail_reasons"):
                top = sorted(stats["fail_reasons"].items(), key=lambda x: x[1], reverse=True)[:5]
                _append_log(task, "warning", "top fallback reasons: " + "; ".join([f"{k}={v}" for k, v in top]))

            await _finalize_task_after_run(
                session,
                task,
                match_ids=actual_match_ids,
                sources=actual_sources,
                intel_types=actual_intel_types,
                trigger=trigger,
            )
            await session.commit()
        except asyncio.CancelledError:
            task_ref = await session.get(IntelligenceCollectionTask, task_id)
            if task_ref and str(task_ref.status or "").lower() not in TASK_TERMINAL_STATUSES:
                task_ref.status = "cancelled"
                task_ref.finished_at = datetime.utcnow()
                _append_log(task_ref, "warning", f"{trigger} cancelled")
                await session.commit()
            raise
        except Exception as exc:
            task_ref = await session.get(IntelligenceCollectionTask, task_id)
            if not task_ref:
                return
            task_ref.status = "failed"
            task_ref.finished_at = datetime.utcnow()
            task_ref.error_message = str(exc)
            task_ref.success_rate = 0.0
            _append_log(task_ref, "error", f"{trigger} failed: {exc}")
            await session.commit()


def _queue_countdown_seconds(delay_seconds: float) -> int:
    try:
        delay = float(delay_seconds or 0.0)
    except Exception:
        delay = 0.0
    if delay <= 0:
        return 0
    return max(0, int(round(delay)))


def _query_queue_state(queue_job_id: Optional[str]) -> str:
    job_id = str(queue_job_id or "").strip()
    if not job_id:
        return ""
    try:
        state = str(task_queue_app.AsyncResult(job_id).state or "PENDING").upper()
        return state
    except Exception as exc:
        logger.warning("[intelligence.collection.queue] query state failed job_id=%s err=%s", job_id, exc)
        return "UNKNOWN"


def _is_queue_job_active(queue_job_id: Optional[str]) -> bool:
    state = _query_queue_state(queue_job_id)
    return state in TASK_QUEUE_ACTIVE_STATES


def _enqueue_task_execution(
    task: IntelligenceCollectionTask,
    *,
    trigger: str,
    delay_seconds: float = 0.0,
    run_match_ids: Optional[List[int]] = None,
    run_sources: Optional[List[str]] = None,
    run_intel_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    countdown = _queue_countdown_seconds(delay_seconds)
    payload: Dict[str, Any] = {
        "task_id": int(task.id),
        "trigger": str(trigger or "collect"),
    }
    if run_match_ids is not None:
        payload["run_match_ids"] = [int(x) for x in run_match_ids if str(x).isdigit()]
    if run_sources is not None:
        payload["run_sources"] = [str(x) for x in run_sources if str(x).strip()]
    if run_intel_types is not None:
        payload["run_intel_types"] = [str(x) for x in run_intel_types if str(x).strip()]

    try:
        async_result = task_queue_app.send_task(
            TASK_QUEUE_NAME,
            kwargs=payload,
            countdown=countdown,
        )
        queue_job_id = str(async_result.id or "").strip()
        if not queue_job_id:
            raise RuntimeError("empty queue_job_id from task queue")
        task.queue_job_id = queue_job_id
        _append_log(
            task,
            "info",
            (
                f"queued task via celery: trigger={trigger}; queue_job_id={queue_job_id}; "
                f"countdown={countdown}"
            ),
        )
        return {
            "accepted": True,
            "queue_job_id": queue_job_id,
            "countdown": countdown,
            "queue_state": "PENDING",
            "error": None,
        }
    except Exception as exc:
        logger.exception("[intelligence.collection.queue] enqueue failed task_id=%s", task.id)
        _append_log(task, "error", f"queue submit failed: {exc}")
        return {
            "accepted": False,
            "queue_job_id": "",
            "countdown": countdown,
            "queue_state": "FAILED",
            "error": str(exc),
        }


async def _sync_task_status_from_queue(
    db: AsyncSession,
    task: IntelligenceCollectionTask,
) -> bool:
    if not task or not task.queue_job_id:
        return False
    task_status = str(task.status or "").strip().lower()
    if task_status in TASK_TERMINAL_STATUSES:
        return False

    queue_state = _query_queue_state(task.queue_job_id)
    if not queue_state:
        return False

    now = datetime.utcnow()
    changed = False

    if queue_state in {"RECEIVED", "STARTED", "RETRY"}:
        if task_status != "running":
            task.status = "running"
            task.started_at = task.started_at or now
            task.finished_at = None
            changed = True
            _append_log(task, "info", f"queue state synced: {queue_state.lower()} -> running")
        return changed

    if queue_state in TASK_QUEUE_FAILURE_STATES:
        task.status = "failed"
        task.finished_at = now
        if not task.error_message:
            task.error_message = "queue failure"
        task.success_rate = round(_safe_float(task.success_rate, 0.0), 4)
        changed = True
        _append_log(task, "error", "queue state synced: failure")
        return changed

    if queue_state in TASK_QUEUE_CANCELLED_STATES:
        task.status = "cancelled"
        task.finished_at = now
        changed = True
        _append_log(task, "warning", "queue state synced: revoked")
        return changed

    if queue_state == "SUCCESS" and task_status in {"pending", "running"}:
        snapshot = await _build_task_completion_snapshot(db, task)
        total_count = max(
            int(task.total_count or 0),
            int(snapshot.get("expected_count") or 0),
            int(snapshot.get("success_count") or 0) + int(snapshot.get("failed_count") or 0),
        )
        success_count = int(snapshot.get("success_count") or 0)
        failed_count = int(snapshot.get("failed_count") or 0)
        task.total_count = total_count
        task.success_count = success_count
        task.failed_count = failed_count
        task.success_rate = round((success_count / total_count), 4) if total_count > 0 else 0.0
        task.status = str(snapshot.get("status") or "success")
        task.finished_at = task.finished_at or now
        top_reason = _sanitize_meta_text(snapshot.get("top_reason"), "")
        if task.status == "failed":
            task.error_message = top_reason or task.error_message or "queue failure"
        elif task.status == "partial":
            task.error_message = top_reason or task.error_message
        else:
            task.error_message = None
        changed = True
        _append_log(task, "info", f"queue state synced: success -> {task.status}")
        return changed

    return False


async def _recover_active_tasks_from_queue(
    db: AsyncSession,
    *,
    focus_tasks: Optional[List[IntelligenceCollectionTask]] = None,
    limit: int = 80,
) -> int:
    now = datetime.utcnow()
    if focus_tasks is None:
        rows = (
            await db.execute(
                select(IntelligenceCollectionTask)
                .where(
                    IntelligenceCollectionTask.status.in_(["pending", "running"])
                )
                .order_by(IntelligenceCollectionTask.updated_at.desc(), IntelligenceCollectionTask.id.desc())
                .limit(limit)
            )
        ).scalars().all()
    else:
        rows = list(focus_tasks)

    recovered = 0
    changed = False
    for task in rows:
        if task.queue_job_id:
            if await _sync_task_status_from_queue(db, task):
                changed = True
                recovered += 1
            continue

        task_status = str(task.status or "").strip().lower()
        should_requeue = False
        if task_status == "running":
            should_requeue = True
        elif task_status == "pending":
            planned_at = task.planned_at
            should_requeue = planned_at is None or planned_at <= now

        if not should_requeue:
            continue

        if task_status == "running":
            task.status = "pending"
            task.started_at = None
            task.finished_at = None
            _append_log(task, "warning", "queue_job_id missing on running task, converted to pending for recovery")

        enqueue_result = _enqueue_task_execution(
            task,
            trigger="restart-recovery",
            delay_seconds=0.0,
        )
        if enqueue_result["accepted"]:
            recovered += 1
            changed = True
            if task.planned_at and task.planned_at < now:
                task.late_run = True
        else:
            task.error_message = enqueue_result["error"] or "queue submit failed"
            changed = True

    if changed:
        await db.commit()
    return recovered


async def _dispatch_due_pending_tasks(db: AsyncSession, limit: int = 20) -> int:
    now = datetime.utcnow()
    rows = (
        await db.execute(
            select(IntelligenceCollectionTask)
            .where(
                IntelligenceCollectionTask.status == "pending",
                IntelligenceCollectionTask.planned_at.isnot(None),
                IntelligenceCollectionTask.planned_at <= now,
                or_(
                    IntelligenceCollectionTask.queue_job_id.is_(None),
                    IntelligenceCollectionTask.queue_job_id == "",
                ),
            )
            .order_by(IntelligenceCollectionTask.planned_at.asc(), IntelligenceCollectionTask.id.asc())
            .limit(limit)
        )
    ).scalars().all()
    dispatched = 0
    changed = False
    for task in rows:
        enqueue_result = _enqueue_task_execution(task, trigger="scheduled-dispatch", delay_seconds=0.0)
        if not enqueue_result["accepted"]:
            continue
        dispatched += 1
        changed = True
        planned_at = task.planned_at
        if planned_at and planned_at < now:
            task.late_run = True
        _append_log(task, "info", "pending task dispatched by runtime scheduler")
    if changed:
        await db.commit()
    return dispatched


async def _build_task_failure_summary(db: AsyncSession, task: IntelligenceCollectionTask) -> Dict[str, Any]:
    logs = _json_loads(task.logs_json, [])
    reason_counter: Dict[str, int] = {}
    source_runtime: Dict[str, Dict[str, Any]] = {}
    source_block_counter: Dict[str, int] = {}
    sample_logs: List[Dict[str, Any]] = []

    for entry in logs:
        message = str(entry.get("message") or "")
        level = str(entry.get("level") or "").lower()
        if level in {"error", "warning"}:
            sample_logs.append(
                {
                    "time": entry.get("time"),
                    "level": level,
                    "message": message[:300],
                }
            )

        runtime_row = _parse_source_runtime_log(message)
        if runtime_row:
            src = runtime_row["source"]
            bucket = source_runtime.setdefault(
                src,
                {"source": src, "requests": 0, "ok": 0, "timeout": 0, "errors": 0, "retries": 0, "circuit_skipped": 0},
            )
            for key in ("requests", "ok", "timeout", "errors", "retries", "circuit_skipped"):
                bucket[key] = int(bucket.get(key, 0)) + int(runtime_row.get(key, 0))

        decision_match = re.search(r"decision .*source=([^;]+);.*decision=blocked;", message)
        if decision_match:
            source = _sanitize_meta_text(decision_match.group(1))
            if source:
                source_block_counter[source] = source_block_counter.get(source, 0) + 1

        reason_tokens = _extract_reason_tokens_from_log(message)
        for token in reason_tokens:
            reason_counter[token] = reason_counter.get(token, 0) + 1

    subtask_rows = (
        await db.execute(
            select(IntelligenceCollectionMatchSubtask).where(
                IntelligenceCollectionMatchSubtask.task_id == task.id
            )
        )
    ).scalars().all()
    for row in subtask_rows:
        if row.last_error:
            key = _sanitize_meta_text(row.last_error)
            if key:
                reason_counter[key] = reason_counter.get(key, 0) + 1

    top_reasons = [
        {"reason": key, "count": count}
        for key, count in sorted(reason_counter.items(), key=lambda kv: kv[1], reverse=True)[:8]
    ]

    source_failures: List[Dict[str, Any]] = []
    for source, stats in source_runtime.items():
        blocked_count = int(source_block_counter.get(source, 0))
        severity_score = int(stats.get("timeout", 0)) + int(stats.get("errors", 0)) + int(stats.get("circuit_skipped", 0))
        if severity_score <= 0 and blocked_count <= 0:
            continue
        source_failures.append(
            {
                "source": source,
                "timeout": int(stats.get("timeout", 0)),
                "errors": int(stats.get("errors", 0)),
                "retries": int(stats.get("retries", 0)),
                "circuit_skipped": int(stats.get("circuit_skipped", 0)),
                "blocked_decisions": blocked_count,
                "severity_score": severity_score + blocked_count,
            }
        )
    source_failures.sort(key=lambda x: x.get("severity_score", 0), reverse=True)
    sample_logs = sample_logs[-10:]

    return {
        "task_id": task.id,
        "task_status": task.status,
        "top_reasons": top_reasons,
        "source_failures": source_failures,
        "sample_logs": sample_logs,
        "generated_at": datetime.utcnow().isoformat(),
    }


def _sanitize_meta_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    text = text.replace(";", ",").replace("\n", " ").replace("\r", " ")
    return re.sub(r"\s+", " ", text).strip()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _get_runtime_llm_service():
    svc = None
    try:
        from .... import main as main_module
        svc = getattr(main_module, "llm_service", None)
    except Exception:
        svc = None
    if not svc:
        try:
            import __main__ as main_module
            svc = getattr(main_module, "llm_service", None)
        except Exception:
            svc = None
    return svc


def _extract_first_json_object(raw_text: str) -> Dict[str, Any]:
    text = (raw_text or "").strip()
    if not text:
        return {}
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {}
    try:
        obj = json.loads(match.group(0))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _graph_node_id(node_type: str, raw_id: Any) -> str:
    return f"{node_type}:{raw_id}"


def _upsert_graph_node(
    node_map: Dict[str, Dict[str, Any]],
    *,
    node_id: str,
    label: str,
    node_type: str,
    category: str,
    base_size: int = 22,
    value_inc: int = 1,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    row = node_map.get(node_id)
    if not row:
        row = {
            "id": node_id,
            "name": label or node_id,
            "type": node_type,
            "category": category,
            "value": 0,
            "symbol_size": base_size,
            "meta": meta or {},
        }
        node_map[node_id] = row
    row["value"] = int(row.get("value", 0)) + int(value_inc)
    # 让热点节点更醒目，但避免过大
    row["symbol_size"] = min(64, max(base_size, base_size + int((row["value"] ** 0.5) * 2)))


def _upsert_graph_edge(
    edge_map: Dict[str, Dict[str, Any]],
    *,
    source: str,
    target: str,
    relation: str,
    value_inc: int = 1,
) -> None:
    edge_id = f"{source}|{relation}|{target}"
    row = edge_map.get(edge_id)
    if not row:
        row = {
            "id": edge_id,
            "source": source,
            "target": target,
            "relation": relation,
            "count": 0,
        }
        edge_map[edge_id] = row
    row["count"] = int(row.get("count", 0)) + int(value_inc)


def _extract_quality_from_raw(raw_text: str) -> Dict[str, Any]:
    raw = raw_text or ""
    quality_score = None
    quality_pass_reason = ""
    quality_block_reason = ""
    source_parser = ""
    article_url = ""
    match_hit_terms: List[str] = []
    is_article_page = False
    ai_enhanced = False
    ai_provider = ""
    ai_model = ""
    ai_summary = ""
    ai_viewpoint = ""
    ai_risk_level = ""
    ai_confidence: Optional[float] = None
    ai_reason = ""

    if raw.startswith("[match-article]"):
        is_article_page = True
    if raw.startswith("[match-article-fallback]"):
        is_article_page = False

    m = re.search(r"quality_score=([^;]+);", raw)
    if m:
        quality_score = _safe_float(m.group(1), 0.0)
    else:
        m = re.search(r"match_score=([^;]+);", raw)
        if m:
            quality_score = _safe_float(m.group(1), 0.0)

    m = re.search(r"quality_pass_reason=([^;]+);", raw)
    if m:
        quality_pass_reason = _sanitize_meta_text(m.group(1))

    m = re.search(r"quality_block_reason=([^;]+);", raw)
    if m:
        quality_block_reason = _sanitize_meta_text(m.group(1))
    else:
        m = re.search(r"fetch_error=\((.*?)\);", raw)
        if m:
            quality_block_reason = _sanitize_meta_text(m.group(1))

    m = re.search(r"source_parser=([^;]+);", raw)
    if m:
        source_parser = _sanitize_meta_text(m.group(1))

    m = re.search(r"article_url=([^;]+);", raw)
    if m:
        article_url = _sanitize_meta_text(m.group(1))

    m = re.search(r"hit_terms=([^;]+);", raw)
    if m:
        terms_raw = _sanitize_meta_text(m.group(1))
        if terms_raw and terms_raw != "-":
            for token in re.split(r"[,\|/]", terms_raw):
                t = token.strip()
                if t and t not in match_hit_terms:
                    match_hit_terms.append(t)

    m = re.search(r"is_article_page=([^;]+);", raw)
    if m:
        is_article_page = m.group(1).strip() in {"1", "true", "True"}

    m = re.search(r"ai_enhanced=([^;]+);", raw)
    if m:
        ai_enhanced = m.group(1).strip() in {"1", "true", "True"}

    m = re.search(r"ai_provider=([^;]+);", raw)
    if m:
        ai_provider = _sanitize_meta_text(m.group(1))

    m = re.search(r"ai_model=([^;]+);", raw)
    if m:
        ai_model = _sanitize_meta_text(m.group(1))

    m = re.search(r"ai_summary=([^;]+);", raw)
    if m:
        ai_summary = _sanitize_meta_text(m.group(1))

    m = re.search(r"ai_viewpoint=([^;]+);", raw)
    if m:
        ai_viewpoint = _sanitize_meta_text(m.group(1))

    m = re.search(r"ai_risk_level=([^;]+);", raw)
    if m:
        ai_risk_level = _sanitize_meta_text(m.group(1))

    m = re.search(r"ai_confidence=([^;]+);", raw)
    if m:
        ai_confidence = round(_safe_float(m.group(1), 0.0), 3)

    m = re.search(r"ai_reason=([^;]+);", raw)
    if m:
        ai_reason = _sanitize_meta_text(m.group(1))

    if quality_score is None:
        quality_score = 0.0

    quality_status = "source_view"
    if raw.startswith("[match-article]"):
        quality_status = "accepted"
    elif raw.startswith("[match-article-fallback]"):
        quality_status = "blocked"

    return {
        "quality_score": round(quality_score, 2),
        "quality_pass_reason": quality_pass_reason,
        "quality_block_reason": quality_block_reason,
        "source_parser": source_parser,
        "article_url": article_url,
        "match_hit_terms": match_hit_terms,
        "is_article_page": bool(is_article_page),
        "quality_status": quality_status,
        "ai_enhanced": bool(ai_enhanced),
        "ai_provider": ai_provider,
        "ai_model": ai_model,
        "ai_summary": ai_summary,
        "ai_viewpoint": ai_viewpoint,
        "ai_risk_level": ai_risk_level,
        "ai_confidence": ai_confidence,
        "ai_reason": ai_reason,
    }


def _normalize_match_hit_terms(raw_terms: Any) -> List[str]:
    if isinstance(raw_terms, str):
        candidate_tokens = re.split(r"[,\|/]", raw_terms)
    elif isinstance(raw_terms, list):
        candidate_tokens = raw_terms
    else:
        return []
    out: List[str] = []
    for token in candidate_tokens:
        txt = _sanitize_meta_text(token)
        if txt and txt not in out:
            out.append(txt)
    return out


def _build_structured_quality_fields(
    source_snapshot: Dict[str, Any],
    article_pick: Dict[str, Any],
) -> Dict[str, Any]:
    matched = bool(article_pick.get("matched"))
    source_code = _sanitize_meta_text(source_snapshot.get("source_code"), "")
    source_parser = _sanitize_meta_text(article_pick.get("source_parser"), f"{source_code}-snapshot" if source_code else "")
    hit_terms = _normalize_match_hit_terms(article_pick.get("match_hit_terms"))
    raw_score = article_pick.get("quality_score", article_pick.get("match_score", 0.0))
    quality_score = round(_safe_float(raw_score, 0.0), 2)
    pass_reason = _sanitize_meta_text(article_pick.get("quality_pass_reason"), "detail-page-context-hit" if matched else "")
    block_reason = _sanitize_meta_text(article_pick.get("quality_block_reason"), "")
    if not block_reason:
        block_reason = _sanitize_meta_text(article_pick.get("error") or source_snapshot.get("error"), "")

    quality_status = "accepted" if matched else "source_view"
    if not matched and block_reason:
        quality_status = "blocked"
    if not matched and not block_reason:
        block_reason = "no-article-match"

    article_url = _sanitize_meta_text(article_pick.get("article_url"), "")
    return {
        "quality_status": quality_status,
        "quality_score": quality_score,
        "quality_pass_reason": pass_reason,
        "quality_block_reason": block_reason,
        "source_parser": source_parser,
        "article_url": article_url,
        "match_hit_terms": hit_terms,
        "is_article_page": matched,
    }


def _extract_quality_from_item(item: IntelligenceCollectionItem) -> Dict[str, Any]:
    legacy = _extract_quality_from_raw(item.content_raw or "")

    structured_terms = _normalize_match_hit_terms(_json_loads(item.match_hit_terms_json, []))
    quality_status = str(item.quality_status or "").strip().lower()
    if quality_status not in {"accepted", "blocked", "source_view"}:
        quality_status = str(legacy.get("quality_status") or "source_view")
    # Existing rows migrated from raw may carry default source_view values.
    if quality_status == "source_view" and str(legacy.get("quality_status")) in {"accepted", "blocked"}:
        no_structured_signal = not (
            _sanitize_meta_text(item.quality_pass_reason, "")
            or _sanitize_meta_text(item.quality_block_reason, "")
            or _sanitize_meta_text(item.source_parser, "")
            or _sanitize_meta_text(item.article_url, "")
            or structured_terms
        )
        if no_structured_signal:
            quality_status = str(legacy.get("quality_status"))

    quality_score = round(_safe_float(item.quality_score, _safe_float(legacy.get("quality_score"), 0.0)), 2)
    if quality_score <= 0 and _safe_float(legacy.get("quality_score"), 0.0) > 0 and quality_status in {"accepted", "blocked"}:
        quality_score = round(_safe_float(legacy.get("quality_score"), 0.0), 2)

    quality_pass_reason = _sanitize_meta_text(item.quality_pass_reason, "")
    if not quality_pass_reason and quality_status == "accepted":
        quality_pass_reason = _sanitize_meta_text(legacy.get("quality_pass_reason"), "")
    quality_block_reason = _sanitize_meta_text(item.quality_block_reason, "")
    if not quality_block_reason and quality_status != "accepted":
        quality_block_reason = _sanitize_meta_text(legacy.get("quality_block_reason"), "")
    source_parser = _sanitize_meta_text(item.source_parser, "") or _sanitize_meta_text(legacy.get("source_parser"), "")
    article_url = (
        _sanitize_meta_text(item.article_url, "")
        or _sanitize_meta_text(legacy.get("article_url"), "")
        or _sanitize_meta_text(item.source_url, "")
    )
    match_hit_terms = structured_terms or _normalize_match_hit_terms(legacy.get("match_hit_terms"))

    is_article_page = quality_status == "accepted"
    if quality_status == "source_view":
        is_article_page = bool(legacy.get("is_article_page"))

    return {
        "quality_score": quality_score,
        "quality_pass_reason": quality_pass_reason,
        "quality_block_reason": quality_block_reason,
        "source_parser": source_parser,
        "article_url": article_url,
        "match_hit_terms": match_hit_terms,
        "is_article_page": bool(is_article_page),
        "quality_status": quality_status,
        "ai_enhanced": legacy.get("ai_enhanced"),
        "ai_provider": legacy.get("ai_provider"),
        "ai_model": legacy.get("ai_model"),
        "ai_summary": legacy.get("ai_summary"),
        "ai_viewpoint": legacy.get("ai_viewpoint"),
        "ai_risk_level": legacy.get("ai_risk_level"),
        "ai_confidence": legacy.get("ai_confidence"),
        "ai_reason": legacy.get("ai_reason"),
    }


async def _collect_task_progress_stats(
    db: AsyncSession,
    tasks: List[IntelligenceCollectionTask],
) -> Dict[int, Dict[str, Any]]:
    if not tasks:
        return {}

    task_ids = [t.id for t in tasks]
    subtask_rows = (
        await db.execute(
            select(IntelligenceCollectionMatchSubtask).where(
                IntelligenceCollectionMatchSubtask.task_id.in_(task_ids)
            )
        )
    ).scalars().all()
    subtask_map: Dict[int, Dict[int, IntelligenceCollectionMatchSubtask]] = {}
    for row in subtask_rows:
        subtask_map.setdefault(int(row.task_id), {})[int(row.match_id)] = row

    grouped_rows = (
        await db.execute(
            select(
                IntelligenceCollectionItem.task_id,
                IntelligenceCollectionItem.match_id,
                func.count(IntelligenceCollectionItem.id).label("item_count"),
            )
            .where(IntelligenceCollectionItem.task_id.in_(task_ids))
            .group_by(IntelligenceCollectionItem.task_id, IntelligenceCollectionItem.match_id)
        )
    ).all()

    grouped_map: Dict[int, Dict[int, int]] = {}
    for task_id, match_id, item_count in grouped_rows:
        grouped_map.setdefault(int(task_id), {})[int(match_id)] = int(item_count or 0)

    stats_map: Dict[int, Dict[str, Any]] = {}
    for task in tasks:
        match_ids = [int(x) for x in _json_loads(task.match_ids_json, []) if str(x).isdigit()]
        sources = _json_loads(task.sources_json, [])
        intel_types = _json_loads(task.intel_types_json, [])
        expected_per_match = max(len(sources) * len(intel_types), 1)
        task_grouped = grouped_map.get(task.id, {})
        task_subtasks = subtask_map.get(task.id, {})
        task_match_ids = match_ids[:]
        for sid in task_subtasks.keys():
            if sid not in task_match_ids:
                task_match_ids.append(sid)

        match_progress: List[Dict[str, Any]] = []
        matched_matches = 0
        success_matches = 0
        failed_matches = 0

        for match_id in task_match_ids:
            subtask = task_subtasks.get(match_id)
            if subtask:
                item_count = int(subtask.item_count or 0)
                expected_count = int(subtask.expected_count or expected_per_match or 0)
                success_count = int(subtask.success_count or 0)
                failed_count = int(subtask.failed_count or 0)
                status = (subtask.status or "").strip().lower()
            else:
                item_count = int(task_grouped.get(match_id, 0))
                expected_count = expected_per_match
                success_count = 0
                failed_count = 0
                status = ""

            completion_rate = round(item_count / expected_count, 3) if expected_count else 0.0
            match_progress.append(
                {
                    "match_id": match_id,
                    "item_count": item_count,
                    "expected_count": expected_count,
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "status": status or ("success" if item_count >= expected_count and item_count > 0 else "failed" if item_count <= 0 else "partial"),
                    "completion_rate": completion_rate,
                }
            )
            if status == "success":
                matched_matches += 1
                success_matches += 1
                continue
            if status == "partial":
                matched_matches += 1
                continue
            if status == "failed":
                failed_matches += 1
                continue
            if item_count <= 0:
                failed_matches += 1
            else:
                matched_matches += 1
                if item_count >= expected_count:
                    success_matches += 1

        total_matches = len(task_match_ids)
        partial_matches = max(total_matches - success_matches - failed_matches, 0)
        coverage_rate = round(matched_matches / total_matches, 4) if total_matches else 0.0

        stats_map[task.id] = {
            "total_matches": total_matches,
            "matched_matches": matched_matches,
            "success_matches": success_matches,
            "failed_matches": failed_matches,
            "partial_matches": partial_matches,
            "coverage_rate": coverage_rate,
            "expected_per_match": expected_per_match if total_matches else 0,
            "match_progress": match_progress,
        }

    return stats_map


async def _ensure_task_match_subtasks(
    db: AsyncSession,
    task: IntelligenceCollectionTask,
    match_ids: List[int],
    sources: List[str],
    intel_types: List[str],
) -> Dict[int, IntelligenceCollectionMatchSubtask]:
    clean_ids = [int(x) for x in match_ids if str(x).isdigit()]
    if not clean_ids:
        return {}
    expected_per_match = max(len(sources) * len(intel_types), 1)
    rows = (
        await db.execute(
            select(IntelligenceCollectionMatchSubtask).where(
                IntelligenceCollectionMatchSubtask.task_id == task.id,
                IntelligenceCollectionMatchSubtask.match_id.in_(clean_ids),
            )
        )
    ).scalars().all()
    row_map: Dict[int, IntelligenceCollectionMatchSubtask] = {int(x.match_id): x for x in rows}
    for match_id in clean_ids:
        row = row_map.get(match_id)
        if row:
            if int(row.expected_count or 0) != expected_per_match:
                row.expected_count = expected_per_match
            row.candidate_count = int(row.candidate_count or 0)
            row.parsed_count = int(row.parsed_count or 0)
            row.matched_count = int(row.matched_count or 0)
            row.accepted_count = int(row.accepted_count or 0)
            row.blocked_count = int(row.blocked_count or 0)
            continue
        row = IntelligenceCollectionMatchSubtask(
            task_id=task.id,
            match_id=match_id,
            status="pending",
            expected_count=expected_per_match,
            item_count=0,
            success_count=0,
            failed_count=0,
            candidate_count=0,
            parsed_count=0,
            matched_count=0,
            accepted_count=0,
            blocked_count=0,
        )
        _append_subtask_log(row, "info", "subtask created")
        db.add(row)
        row_map[match_id] = row
    await db.flush()
    return row_map


async def _reset_task_match_subtasks(
    db: AsyncSession,
    task_id: int,
    match_ids: Optional[List[int]] = None,
) -> Dict[int, IntelligenceCollectionMatchSubtask]:
    stmt = select(IntelligenceCollectionMatchSubtask).where(
        IntelligenceCollectionMatchSubtask.task_id == task_id
    )
    clean_ids = [int(x) for x in (match_ids or []) if str(x).isdigit()]
    if clean_ids:
        stmt = stmt.where(IntelligenceCollectionMatchSubtask.match_id.in_(clean_ids))
    rows = (await db.execute(stmt)).scalars().all()
    row_map: Dict[int, IntelligenceCollectionMatchSubtask] = {}
    for row in rows:
        row.retry_count = int(row.retry_count or 0) + 1
        row.status = "pending"
        row.item_count = 0
        row.success_count = 0
        row.failed_count = 0
        row.candidate_count = 0
        row.parsed_count = 0
        row.matched_count = 0
        row.accepted_count = 0
        row.blocked_count = 0
        row.started_at = None
        row.finished_at = None
        row.last_error = None
        _append_subtask_log(row, "info", f"subtask reset for task retry #{row.retry_count}")
        row_map[int(row.match_id)] = row
    await db.flush()
    return row_map


class TaskCreateRequest(BaseModel):
    match_ids: List[int] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    intel_types: List[str] = Field(default_factory=list)
    mode: str = "immediate"  # immediate/scheduled
    offset_hours: List[int] = Field(default_factory=list)


class TaskRetryRequest(BaseModel):
    match_ids: List[int] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    intel_types: List[str] = Field(default_factory=list)


class PushPreviewRequest(BaseModel):
    user_risk_profile: str = "balanced"
    max_evidence: int = 3
    top_n: Optional[int] = Field(default=None, ge=1, le=20)
    min_score: Optional[float] = Field(default=None, ge=0, le=10)
    include_blocked: bool = False


class PushTaskCreateRequest(BaseModel):
    match_id: int
    channel: str = "dingtalk"
    target_users: List[int] = Field(default_factory=list)
    preview: Dict[str, Any] = Field(default_factory=dict)
    binding_id: Optional[int] = None


class SubscriptionUpdateRequest(BaseModel):
    leagues: List[str] = Field(default_factory=list)
    teams: List[str] = Field(default_factory=list)
    intel_types: List[str] = Field(default_factory=list)
    risk_profile: str = "balanced"
    push_frequency: str = "milestone"
    info_density: str = "standard"
    daily_limit: int = 5


class DingTalkBindingRequest(BaseModel):
    webhook: str
    secret: Optional[str] = None
    enabled: bool = True


class TtyingqiuDebugRequest(BaseModel):
    match_id: int
    intel_type: str = "win_draw_lose"


class MatchCandidatesDebugRequest(BaseModel):
    match_id: int
    source: str = "ttyingqiu"
    intel_type: str = "win_draw_lose"
    max_candidates: int = Field(default=20, ge=5, le=80)


class TimeWindowSettingsUpdateRequest(BaseModel):
    before_hours: int = Field(default=DEFAULT_TIME_WINDOW_BEFORE_HOURS, ge=TIME_WINDOW_BEFORE_HOURS_MIN, le=TIME_WINDOW_BEFORE_HOURS_MAX)
    after_hours: int = Field(default=DEFAULT_TIME_WINDOW_AFTER_HOURS, ge=TIME_WINDOW_AFTER_HOURS_MIN, le=TIME_WINDOW_AFTER_HOURS_MAX)
    strict_mode: bool = DEFAULT_TIME_WINDOW_STRICT_MODE


class NetworkSettingsUpdateRequest(BaseModel):
    trust_env: Optional[bool] = None
    source_timeout_seconds: Optional[Dict[str, float]] = None
    max_retry: Optional[int] = Field(default=None, ge=1, le=5)
    retry_backoff_ms: Optional[int] = Field(default=None, ge=0, le=5000)
    circuit_breaker_threshold: Optional[int] = Field(default=None, ge=1, le=50)
    circuit_breaker_seconds: Optional[int] = Field(default=None, ge=1, le=600)


class SourceRulesUpdateRequest(BaseModel):
    rules: Dict[str, Any] = Field(default_factory=dict)


class QualityThresholdsUpdateRequest(BaseModel):
    thresholds: Dict[str, Any] = Field(default_factory=dict)


class AliasDictionaryUpdateRequest(BaseModel):
    dictionary: Dict[str, Any] = Field(default_factory=dict)


class DebugReplayRequest(BaseModel):
    match_id: int
    source: str = "ttyingqiu"
    intel_type: str = "win_draw_lose"
    max_candidates: int = Field(default=20, ge=5, le=80)


async def _simulate_collect_items(
    db: AsyncSession,
    task: IntelligenceCollectionTask,
    match_ids: List[int],
    sources: List[str],
    intel_types: List[str],
) -> Dict[str, int]:
    ARTICLE_HINT_PATTERNS = (
        "news",
        "article",
        "match",
        "analysis",
        "preview",
        "opinion",
        "zq",
        "soccer",
        "zuqiu",
        "saishi",
        "xinwen",
        "qingbao",
        "qianzhan",
        "yuce",
        "dongtai",
    )
    OPINION_HINT_PATTERNS = (
        "analysis",
        "preview",
        "opinion",
        "qianzhan",
        "yuce",
        "tuijian",
        "jiqiao",
        "瑙傜偣",
        "瑙ｈ",
        "鍓嶇灮",
        "棰勬祴",
        "鍒嗘瀽",
        "鎺ㄨ崘",
        "鎯呮姤",
    )
    NAV_HINT_PATTERNS = (
        "news",
        "zixun",
        "saishi",
        "match",
        "jczq",
        "bjdc",
        "soccer",
        "football",
        "zuqiu",
        "xinwen",
        "璧勮",
        "璧涗簨",
        "璧涚▼",
        "瓒崇悆",
        "鎯呮姤",
        "鍒嗘瀽",
    )
    LOW_QUALITY_TITLE_HINTS = (
        "首页",
        "频道",
        "导航",
        "直播",
        "赛程",
        "数据",
        "下载",
        "登录",
        "注册",
        "专题",
        "列表",
        "滚动",
        "资讯",
        "news home",
    )
    SOURCE_TRUSTED_HOST_SUFFIX = {
        "500w": ["500.com"],
        "ttyingqiu": ["ttyingqiu.com"],
        "tencent": ["qq.com"],
        "sina": ["sina.com.cn"],
        "weibo": ["weibo.com", "sina.com.cn"],
        "wechat": ["qq.com", "weixin.qq.com"],
    }
    LEAGUE_ALIAS_MAP = {
        "澳超": ["澳大利亚甲级联赛", "a-league"],
        "英超": ["英格兰超级联赛", "epl", "premier league"],
        "西甲": ["西班牙甲级联赛", "laliga", "la liga"],
        "意甲": ["意大利甲级联赛", "serie a"],
        "德甲": ["德国甲级联赛", "bundesliga"],
        "法甲": ["法国甲级联赛", "ligue 1"],
        "欧冠": ["欧洲冠军联赛", "uefa champions league", "ucl"],
        "欧联": ["欧罗巴联赛", "uefa europa league"],
    }

    ttyingqiu_seed_cache: Dict[str, List[Dict[str, str]]] = {}
    expected_per_match = max(len(sources) * len(intel_types), 1)
    time_window_config = await _load_time_window_config(db)
    time_window_before_hours = int(time_window_config.get("before_hours", DEFAULT_TIME_WINDOW_BEFORE_HOURS))
    time_window_after_hours = int(time_window_config.get("after_hours", DEFAULT_TIME_WINDOW_AFTER_HOURS))
    network_settings = await _load_network_settings(db)
    source_rules_payload = await _load_source_rules(db)
    source_rules = source_rules_payload.get("rules", {}) if isinstance(source_rules_payload, dict) else {}
    source_timeout_seconds = _normalize_source_timeout_map(
        network_settings.get("source_timeout_seconds"),
        _default_network_settings().get("source_timeout_seconds", {}),
    )

    def _debug_timeout(code: str) -> float:
        return _normalize_float(
            source_timeout_seconds.get(code, source_timeout_seconds.get("default", 2.0)),
            default=2.0,
            min_value=0.3,
            max_value=30.0,
        )
    time_window_strict_mode = _normalize_bool(
        time_window_config.get("strict_mode"),
        DEFAULT_TIME_WINDOW_STRICT_MODE,
    )
    network_settings = await _load_network_settings(db)
    source_rules_payload = await _load_source_rules(db)
    quality_thresholds_payload = await _load_quality_thresholds(db)
    alias_dictionary_payload = await _load_alias_dictionary(db)

    source_rules = source_rules_payload.get("rules", {})
    quality_thresholds = quality_thresholds_payload.get("thresholds", {})
    alias_dictionary = alias_dictionary_payload.get("dictionary", {})
    source_timeout_seconds = _normalize_source_timeout_map(
        network_settings.get("source_timeout_seconds"),
        _default_network_settings().get("source_timeout_seconds", {}),
    )
    source_max_retry = _normalize_int(network_settings.get("max_retry"), default=2, min_value=1, max_value=5)
    source_breaker_threshold = _normalize_int(
        network_settings.get("circuit_breaker_threshold"), default=6, min_value=1, max_value=50
    )
    source_breaker_seconds = _normalize_int(
        network_settings.get("circuit_breaker_seconds"), default=45, min_value=1, max_value=600
    )
    retry_backoff_ms = _normalize_int(network_settings.get("retry_backoff_ms"), default=120, min_value=0, max_value=5000)
    retry_backoff_seconds = max(float(retry_backoff_ms) / 1000.0, 0.0)
    network_trust_env = _normalize_bool(network_settings.get("trust_env"), False)
    enable_playwright_fallback = _normalize_bool(network_settings.get("enable_playwright_fallback"), False)
    low_quality_title_hints = tuple(
        [
            str(x).strip().lower()
            for x in (quality_thresholds.get("low_quality_title_hints") or LOW_QUALITY_TITLE_HINTS)
            if str(x).strip()
        ]
    )
    min_title_len = _normalize_int(quality_thresholds.get("min_title_len"), default=6, min_value=2, max_value=40)
    min_context_hits = _normalize_int(quality_thresholds.get("min_context_hits"), default=1, min_value=1, max_value=5)
    excerpt_cfg = quality_thresholds.get("min_excerpt_len") if isinstance(quality_thresholds.get("min_excerpt_len"), dict) else {}
    min_excerpt_len_prediction = _normalize_int(excerpt_cfg.get("prediction"), default=80, min_value=20, max_value=500)
    min_excerpt_len_off_field = _normalize_int(excerpt_cfg.get("off_field"), default=120, min_value=40, max_value=800)
    min_excerpt_len_weibo = _normalize_int(excerpt_cfg.get("weibo"), default=40, min_value=10, max_value=300)
    soft_page_filter = quality_thresholds.get("soft_page_filter") if isinstance(quality_thresholds.get("soft_page_filter"), dict) else {}
    soft_page_min_body_len = _normalize_int(
        soft_page_filter.get("min_body_len"), default=120, min_value=20, max_value=2000
    )
    soft_page_min_team_hits = _normalize_int(
        soft_page_filter.get("min_team_hits"), default=1, min_value=1, max_value=5
    )
    source_min_match_score_map = (
        quality_thresholds.get("min_match_score_by_source")
        if isinstance(quality_thresholds.get("min_match_score_by_source"), dict)
        else {}
    )

    def _source_min_match_score(source_code: str, default: float) -> float:
        return _normalize_float(
            source_min_match_score_map.get(source_code, source_min_match_score_map.get("default", default)),
            default=default,
            min_value=0.0,
            max_value=10.0,
        )

    ai_enabled = _normalize_bool(
        os.getenv("INTELLIGENCE_COLLECTION_AI_ENABLED"),
        DEFAULT_AI_ENHANCEMENT_SETTINGS["enabled"],
    )
    ai_provider = str(
        os.getenv("INTELLIGENCE_COLLECTION_AI_PROVIDER", DEFAULT_AI_ENHANCEMENT_SETTINGS["provider"])
    ).strip().lower()
    ai_model = str(
        os.getenv("INTELLIGENCE_COLLECTION_AI_MODEL", DEFAULT_AI_ENHANCEMENT_SETTINGS["model"])
    ).strip() or DEFAULT_AI_ENHANCEMENT_SETTINGS["model"]
    ai_temperature = _normalize_float(
        os.getenv("INTELLIGENCE_COLLECTION_AI_TEMPERATURE"),
        default=float(DEFAULT_AI_ENHANCEMENT_SETTINGS["temperature"]),
        min_value=0.0,
        max_value=1.5,
    )
    ai_max_tokens = _normalize_int(
        os.getenv("INTELLIGENCE_COLLECTION_AI_MAX_TOKENS"),
        default=int(DEFAULT_AI_ENHANCEMENT_SETTINGS["max_tokens"]),
        min_value=64,
        max_value=1500,
    )
    ai_timeout_seconds = _normalize_float(
        os.getenv("INTELLIGENCE_COLLECTION_AI_TIMEOUT_SECONDS"),
        default=float(DEFAULT_AI_ENHANCEMENT_SETTINGS["timeout_seconds"]),
        min_value=2.0,
        max_value=40.0,
    )
    ai_min_quality_score = _normalize_float(
        os.getenv("INTELLIGENCE_COLLECTION_AI_MIN_QUALITY_SCORE"),
        default=float(DEFAULT_AI_ENHANCEMENT_SETTINGS["min_quality_score"]),
        min_value=0.0,
        max_value=10.0,
    )
    ai_max_calls_per_task = _normalize_int(
        os.getenv("INTELLIGENCE_COLLECTION_AI_MAX_CALLS_PER_TASK"),
        default=int(DEFAULT_AI_ENHANCEMENT_SETTINGS["max_calls_per_task"]),
        min_value=1,
        max_value=300,
    )

    ai_runtime: Dict[str, Any] = {
        "enabled": ai_enabled,
        "provider": ai_provider,
        "model": ai_model,
        "provider_ready": None,
        "calls": 0,
        "success": 0,
        "failed": 0,
        "cache_hit": 0,
        "skipped_unmatched": 0,
        "skipped_low_quality": 0,
        "skipped_budget": 0,
        "last_error": "",
    }
    ai_cache: Dict[tuple, Dict[str, Any]] = {}
    ai_db_runtime = {
        "checked": False,
        "api_key": "",
        "provider_name": "",
    }

    async def _load_qwen_api_key_from_db() -> tuple[str, str]:
        if ai_db_runtime["checked"]:
            return str(ai_db_runtime.get("api_key") or ""), str(ai_db_runtime.get("provider_name") or "")
        ai_db_runtime["checked"] = True
        try:
            row = (
                await db.execute(
                    select(LLMProvider)
                    .where(
                        LLMProvider.enabled.is_(True),
                        LLMProvider.provider_type == LLMProviderTypeEnum.ALIBABA,
                    )
                    .order_by(LLMProvider.priority.asc(), LLMProvider.id.asc())
                    .limit(1)
                )
            ).scalars().first()
            if not row or not row.api_key:
                return "", ""
            encrypted = str(row.api_key or "")
            if not encrypted:
                return "", ""
            try:
                secret_raw = str(getattr(app_settings, "SECRET_KEY", "") or "")
                cipher_key = secret_raw.encode()[:32].ljust(32, b"0")[:32] if secret_raw else b"0" * 32
                decrypted = decrypt_sensitive_data(encrypted, cipher_key)
            except Exception:
                decrypted = encrypted
            ai_db_runtime["api_key"] = str(decrypted or "")
            ai_db_runtime["provider_name"] = str(row.name or f"provider-{row.id}")
            return str(ai_db_runtime["api_key"]), str(ai_db_runtime["provider_name"])
        except Exception:
            return "", ""

    async def _call_qwen(prompt: str) -> tuple[str, str]:
        # First try already-initialized runtime llm_service.
        svc = _get_runtime_llm_service()
        if svc and getattr(svc, "providers", None):
            providers = set(getattr(svc, "providers", {}).keys())
            provider_name = "qwen" if "qwen" in providers else ("alibaba" if "alibaba" in providers else "")
            if provider_name:
                try:
                    txt = await asyncio.wait_for(
                        svc.generate_response(
                            prompt,
                            provider=provider_name,
                            model=ai_model,
                            temperature=ai_temperature,
                            max_tokens=ai_max_tokens,
                        ),
                        timeout=ai_timeout_seconds + 2.0,
                    )
                    ai_runtime["provider_ready"] = True
                    return str(txt or ""), provider_name
                except Exception as e:
                    ai_runtime["last_error"] = _sanitize_meta_text(e)

        # Fallback: call QWEN directly using key from llm_providers(alibaba).
        api_key, provider_name = await _load_qwen_api_key_from_db()
        if not api_key:
            ai_runtime["provider_ready"] = False
            return "", ""

        def _sync_call() -> str:
            resp = requests.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": ai_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": ai_temperature,
                    "max_tokens": ai_max_tokens,
                },
                timeout=ai_timeout_seconds,
            )
            resp.raise_for_status()
            payload = resp.json() if resp.content else {}
            return str((((payload or {}).get("choices") or [{}])[0].get("message") or {}).get("content") or "")

        try:
            txt = await asyncio.wait_for(asyncio.to_thread(_sync_call), timeout=ai_timeout_seconds + 2.0)
            ai_runtime["provider_ready"] = True
            return txt, (provider_name or "qwen-direct")
        except Exception as e:
            ai_runtime["last_error"] = _sanitize_meta_text(e)
            return "", ""

    async def _ai_enhance_article(
        *,
        match_id: int,
        source_code: str,
        intel_category: str,
        intel_type: str,
        league_name: str,
        home_team: str,
        away_team: str,
        article_pick: Dict[str, Any],
    ) -> Dict[str, Any]:
        result = {
            "enabled": ai_enabled,
            "used": False,
            "provider": "",
            "model": ai_model,
            "summary": "",
            "viewpoint": "",
            "risk_level": "",
            "confidence": None,
            "reason": "disabled",
            "key_factors": "",
        }
        if not ai_enabled:
            return result

        if not article_pick.get("matched"):
            ai_runtime["skipped_unmatched"] = int(ai_runtime.get("skipped_unmatched", 0) or 0) + 1
            result["reason"] = "skip-unmatched"
            return result

        if ai_runtime.get("provider_ready") is False:
            result["reason"] = "llm-provider-unavailable"
            return result

        quality_score = _safe_float(article_pick.get("quality_score", article_pick.get("match_score", 0.0)), 0.0)
        if quality_score < ai_min_quality_score:
            ai_runtime["skipped_low_quality"] = int(ai_runtime.get("skipped_low_quality", 0) or 0) + 1
            result["reason"] = f"skip-low-quality:{round(quality_score, 2)}"
            return result

        cache_key = (
            int(match_id),
            str(source_code),
            str(intel_category),
            str(article_pick.get("article_url") or article_pick.get("article_title") or ""),
        )
        if cache_key in ai_cache:
            ai_runtime["cache_hit"] = int(ai_runtime.get("cache_hit", 0) or 0) + 1
            cached = dict(ai_cache[cache_key])
            cached["reason"] = cached.get("reason") or "cache-hit"
            return cached

        if int(ai_runtime.get("calls", 0) or 0) >= ai_max_calls_per_task:
            ai_runtime["skipped_budget"] = int(ai_runtime.get("skipped_budget", 0) or 0) + 1
            result["reason"] = "skip-call-budget"
            return result

        article_title = _sanitize_meta_text(article_pick.get("article_title"), "")
        article_excerpt = _sanitize_meta_text(article_pick.get("article_excerpt"), "")
        article_url = _sanitize_meta_text(article_pick.get("article_url"), "")
        hit_terms = article_pick.get("match_hit_terms") if isinstance(article_pick.get("match_hit_terms"), list) else []
        hit_terms_text = ", ".join([str(x) for x in hit_terms[:8]])

        prompt = (
            "你是体育竞猜情报结构化助手。请根据给定比赛与文章来源观点，输出严格 JSON（不要 markdown，不要解释）。\n"
            "字段要求：\n"
            "summary: 50~90字，聚焦可操作信息；\n"
            "key_factors: 长度2~4的字符串数组；\n"
            "viewpoint: 1句话，给出倾向/关注点（非投注建议）；\n"
            "risk_level: 仅 low/medium/high；\n"
            "confidence: 0~1 浮点数。\n"
            f"比赛: {league_name} {home_team} vs {away_team} (match_id={match_id})\n"
            f"情报分类: {intel_category}; 情报类型: {intel_type}; 来源: {source_code}\n"
            f"文章来源: {article_title}\n"
            f"链接: {article_url}\n"
            f"命中词: {hit_terms_text}\n"
            f"正文摘要: {article_excerpt[:1200]}\n"
        )

        ai_runtime["calls"] = int(ai_runtime.get("calls", 0) or 0) + 1
        raw_text, used_provider = await _call_qwen(prompt)
        if not raw_text:
            ai_runtime["failed"] = int(ai_runtime.get("failed", 0) or 0) + 1
            result["reason"] = ai_runtime.get("last_error") or "llm-empty-response"
            return result

        parsed = _extract_first_json_object(raw_text)
        summary = _sanitize_meta_text(parsed.get("summary") if isinstance(parsed, dict) else "", "")
        key_factors = parsed.get("key_factors") if isinstance(parsed, dict) else []
        viewpoint = _sanitize_meta_text(parsed.get("viewpoint") if isinstance(parsed, dict) else "", "")
        risk_level = _sanitize_meta_text(parsed.get("risk_level") if isinstance(parsed, dict) else "", "").lower()
        confidence = _safe_float(parsed.get("confidence") if isinstance(parsed, dict) else None, -1)

        if not summary:
            summary = article_excerpt[:120]
        if not viewpoint:
            viewpoint = summary[:70]
        if risk_level not in {"low", "medium", "high"}:
            risk_level = "medium"
        if confidence < 0:
            confidence = min(0.95, max(0.45, round(quality_score / 4.0, 2)))
        confidence = round(_normalize_float(confidence, default=0.65, min_value=0.0, max_value=1.0), 3)

        if isinstance(key_factors, list):
            factors = [str(x).strip() for x in key_factors if str(x).strip()][:4]
        else:
            factors = [x.strip() for x in str(key_factors or "").split(",") if x.strip()][:4]

        result = {
            "enabled": True,
            "used": True,
            "provider": used_provider or ai_provider,
            "model": ai_model,
            "summary": summary,
            "viewpoint": viewpoint,
            "risk_level": risk_level,
            "confidence": confidence,
            "reason": "ai-structured",
            "key_factors": _sanitize_meta_text(" | ".join(factors), ""),
        }
        ai_runtime["success"] = int(ai_runtime.get("success", 0) or 0) + 1
        ai_cache[cache_key] = dict(result)
        return result

    _append_log(
        task,
        "info",
        (
            f"time-window-config loaded: before={time_window_before_hours}h after={time_window_after_hours}h "
            f"strict={time_window_strict_mode}; network(max_retry={source_max_retry}, trust_env={network_trust_env}); "
            f"quality(min_title_len={min_title_len}, min_context_hits={min_context_hits}); "
            f"ai(enabled={ai_enabled}, provider={ai_provider}, model={ai_model}, min_quality={ai_min_quality_score}, max_calls={ai_max_calls_per_task})"
        ),
    )
    source_state: Dict[str, Dict[str, Any]] = {
        src: {
            "requests": 0,
            "ok": 0,
            "timeout": 0,
            "errors": 0,
            "retries": 0,
            "circuit_skipped": 0,
            "consecutive_failures": 0,
            "circuit_open_until": None,
        }
        for src in set(list(sources) + list(SOURCE_URL_MAP.keys()))
    }

    def _infer_source_code(url: str) -> str:
        host = (urlparse(url).netloc or "").lower()
        if not host:
            return "default"
        for code, suffixes in SOURCE_TRUSTED_HOST_SUFFIX.items():
            for suffix in suffixes:
                suffix = suffix.lower()
                if host == suffix or host.endswith("." + suffix):
                    return code
        return "default"

    def _source_stat(code: str) -> Dict[str, Any]:
        if code not in source_state:
            source_state[code] = {
                "requests": 0,
                "ok": 0,
                "timeout": 0,
                "errors": 0,
                "retries": 0,
                "circuit_skipped": 0,
                "consecutive_failures": 0,
                "circuit_open_until": None,
            }
        return source_state[code]

    def _is_circuit_open(code: str) -> bool:
        stats = _source_stat(code)
        until = stats.get("circuit_open_until")
        if not until:
            return False
        return datetime.utcnow() < until

    def _record_source_success(code: str) -> None:
        stats = _source_stat(code)
        stats["ok"] = int(stats.get("ok", 0) or 0) + 1
        stats["consecutive_failures"] = 0
        stats["circuit_open_until"] = None

    def _record_source_failure(code: str, timeout_error: bool = False) -> None:
        stats = _source_stat(code)
        if timeout_error:
            stats["timeout"] = int(stats.get("timeout", 0) or 0) + 1
        else:
            stats["errors"] = int(stats.get("errors", 0) or 0) + 1
        stats["consecutive_failures"] = int(stats.get("consecutive_failures", 0) or 0) + 1
        if stats["consecutive_failures"] >= source_breaker_threshold:
            stats["circuit_open_until"] = datetime.utcnow() + timedelta(seconds=source_breaker_seconds)

    def _resolve_timeout_seconds(source_code: str, timeout: int) -> float:
        timeout_val = float(timeout or 1)
        prefer = float(source_timeout_seconds.get(source_code, source_timeout_seconds["default"]))
        return max(timeout_val, prefer)

    def _new_session() -> requests.Session:
        session = requests.Session()
        session.trust_env = network_trust_env
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
        )
        return session

    def _safe_get(session: requests.Session, url: str, timeout: int = 1) -> str:
        source_code = _infer_source_code(url)
        stats = _source_stat(source_code)
        if _is_circuit_open(source_code):
            stats["circuit_skipped"] = int(stats.get("circuit_skipped", 0) or 0) + 1
            raise RuntimeError(f"source-circuit-open:{source_code}")

        req_timeout = _resolve_timeout_seconds(source_code, timeout)
        last_error: Optional[Exception] = None
        for attempt in range(1, source_max_retry + 1):
            stats["requests"] = int(stats.get("requests", 0) or 0) + 1
            try:
                resp = session.get(url, timeout=req_timeout, allow_redirects=True)
                resp.encoding = resp.apparent_encoding or resp.encoding
                status_code = int(resp.status_code or 0)
                if status_code >= 500:
                    raise RuntimeError(f"http-status-{status_code}")
                _record_source_success(source_code)
                return resp.text or ""
            except requests.Timeout as e:
                last_error = e
                _record_source_failure(source_code, timeout_error=True)
            except Exception as e:
                last_error = e
                _record_source_failure(source_code, timeout_error=False)

            if attempt < source_max_retry:
                stats["retries"] = int(stats.get("retries", 0) or 0) + 1
                try:
                    import time as _time
                    _time.sleep(retry_backoff_seconds * attempt)
                except Exception:
                    pass
        raise last_error or RuntimeError(f"request-failed:{source_code}")

    def _safe_get_with_status(session: requests.Session, url: str, timeout: int = 1) -> tuple[str, int]:
        source_code = _infer_source_code(url)
        stats = _source_stat(source_code)
        if _is_circuit_open(source_code):
            stats["circuit_skipped"] = int(stats.get("circuit_skipped", 0) or 0) + 1
            return ("", 599)

        req_timeout = _resolve_timeout_seconds(source_code, timeout)
        last_status = 0
        for attempt in range(1, source_max_retry + 1):
            stats["requests"] = int(stats.get("requests", 0) or 0) + 1
            try:
                resp = session.get(url, timeout=req_timeout, allow_redirects=True)
                resp.encoding = resp.apparent_encoding or resp.encoding
                status_code = int(resp.status_code or 0)
                last_status = status_code
                if status_code >= 500:
                    _record_source_failure(source_code, timeout_error=False)
                else:
                    _record_source_success(source_code)
                    return (resp.text or "", status_code)
            except requests.Timeout:
                _record_source_failure(source_code, timeout_error=True)
                last_status = 598
            except Exception:
                _record_source_failure(source_code, timeout_error=False)
                last_status = 597

            if attempt < source_max_retry:
                stats["retries"] = int(stats.get("retries", 0) or 0) + 1
                try:
                    import time as _time
                    _time.sleep(retry_backoff_seconds * attempt)
                except Exception:
                    pass
        return ("", last_status or 597)

    def _normalize_text(text: str) -> str:
        low = (text or "").strip().lower()
        low = re.sub(r"[\u3000\r\n\t]+", " ", low)
        low = re.sub(r"[\.\,\:\;\|\(\)\[\]\{\}<>\"'`~!@#$%^&*_+=?/\\\-]+", " ", low)
        return re.sub(r"\s+", " ", low).strip()

    def _host_allowed(source_code: str, base_url: str, candidate_url: str) -> bool:
        try:
            c_host = (urlparse(candidate_url).netloc or "").lower()
            b_host = (urlparse(base_url).netloc or "").lower()
            if not c_host:
                return False
            if c_host == b_host or c_host.endswith("." + b_host):
                return True
            for suffix in SOURCE_TRUSTED_HOST_SUFFIX.get(source_code, []):
                if c_host == suffix or c_host.endswith("." + suffix):
                    return True
            return False
        except Exception:
            return False

    def _is_nav_link(url: str, anchor: str) -> bool:
        low = (url + " " + anchor).lower()
        return any(h in low for h in NAV_HINT_PATTERNS)

    def _is_article_link(url: str, anchor: str) -> bool:
        low = (url + " " + anchor).lower()
        return any(h in low for h in ARTICLE_HINT_PATTERNS)

    def _source_url_allowed(source_code: str, url: str) -> bool:
        low = (url or "").lower()
        host = (urlparse(url).netloc or "").lower()
        path = (urlparse(url).path or "").lower()
        rule = source_rules.get(source_code, {}) if isinstance(source_rules, dict) else {}
        allow_suffix = (
            rule.get("allowed_host_suffix")
            if isinstance(rule, dict) and isinstance(rule.get("allowed_host_suffix"), list)
            else []
        )
        deny_exact = (
            rule.get("deny_host_exact")
            if isinstance(rule, dict) and isinstance(rule.get("deny_host_exact"), list)
            else []
        )
        forbidden_contains = (
            rule.get("forbidden_path_contains")
            if isinstance(rule, dict) and isinstance(rule.get("forbidden_path_contains"), list)
            else []
        )
        if any(host == str(x).strip().lower() for x in deny_exact):
            return False
        if allow_suffix:
            if not any(
                host == str(x).strip().lower() or host.endswith("." + str(x).strip().lower())
                for x in allow_suffix
                if str(x).strip()
            ):
                return False
        if any(str(x).strip().lower() in low for x in forbidden_contains if str(x).strip()):
            return False

        if source_code == "sina":
            # Reduce false positives from non-sports channels (e.g. weather)
            if "weather.sina.com.cn" in host:
                return False
            if "sports.sina.com.cn" not in host:
                return False
            # Require sports article/list channel style paths; block generic/non-article roots.
            if path and path != "/" and not any(x in path for x in ("/football", "/china", "/global", "/g/", "/zl/")):
                return False
            if path and path not in ("/", "") and not any(x in path for x in (".shtml", "/doc-", "/article", "/news")):
                return False
        if source_code == "tencent":
            # Keep sports/news channels for Tencent source.
            if "qq.com" not in host:
                return False
            if not any(x in low for x in ("sports.qq.com", "new.qq.com", "/sports/", "/a/")):
                return False
        if source_code == "500w":
            if "500.com" not in host:
                return False
            if path and path != "/" and not any(x in low for x in ("zq", "jczq", "bd", "news", "saishi", "match")):
                return False
        if source_code == "ttyingqiu":
            if "ttyingqiu.com" not in host:
                return False
            if "live/leagueindex" in low:
                return False
            if "/news/home" in low:
                return False
            if path and path != "/" and "news" not in low:
                return False
            require_numeric_news_detail = _normalize_bool(
                (rule or {}).get("require_numeric_news_detail"), True
            )
            if require_numeric_news_detail and "/news/" in path and not re.search(r"/news/\d+", path):
                return False
        return True

    def _clean_html_text(raw: str) -> str:
        text = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
        text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = unescape(text)
        return re.sub(r"\s+", " ", text).strip()

    def _extract_title(html: str) -> str:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
        if not m:
            return ""
        return _clean_html_text(m.group(1))

    def _extract_ttyingqiu_article_body(html: str) -> str:
        if not html:
            return ""
        patterns = [
            r"<article[^>]*>(.*?)</article>",
            r"<div[^>]+class=[\"'][^\"']*(?:news|article|content|detail)[^\"']*[\"'][^>]*>(.*?)</div>",
            r"<section[^>]+class=[\"'][^\"']*(?:news|article|content|detail)[^\"']*[\"'][^>]*>(.*?)</section>",
        ]
        best = ""
        for p in patterns:
            blocks = re.findall(p, html, flags=re.I | re.S)
            for b in blocks:
                txt = _clean_html_text(b)
                if len(txt) > len(best):
                    best = txt
        if len(best) >= 60:
            return best[:2000]
        return _clean_html_text(html)[:2000]

    def _is_ttyingqiu_blacklisted(url: str) -> bool:
        low = (url or "").lower()
        rule = source_rules.get("ttyingqiu", {}) if isinstance(source_rules, dict) else {}
        blocked_exact = {
            (str(x).strip().lower().rstrip("/") or "/")
            for x in ((rule.get("blacklist_exact_paths") or []) if isinstance(rule, dict) else [])
            if str(x).strip()
        }
        path = (urlparse(url).path or "").lower().rstrip("/")
        if path in blocked_exact:
            return True
        forbidden_contains = (
            rule.get("forbidden_path_contains")
            if isinstance(rule, dict) and isinstance(rule.get("forbidden_path_contains"), list)
            else []
        )
        if any(str(x).strip().lower() in low for x in forbidden_contains if str(x).strip()):
            return True
        # Generic tag/index-like pages
        if re.search(r"/news/(tag|topic|index|list)(/|$)", low):
            return True
        return False

    def _ttyingqiu_penalty(url: str) -> float:
        rule = source_rules.get("ttyingqiu", {}) if isinstance(source_rules, dict) else {}
        soft_penalty_paths = (
            rule.get("soft_penalty_paths")
            if isinstance(rule, dict) and isinstance(rule.get("soft_penalty_paths"), dict)
            else {}
        )
        path = (urlparse(url).path or "").lower().rstrip("/")
        return _normalize_float(soft_penalty_paths.get(path), default=0.0, min_value=0.0, max_value=5.0)

    def _is_ttyingqiu_soft_page(url: str) -> bool:
        rule = source_rules.get("ttyingqiu", {}) if isinstance(source_rules, dict) else {}
        soft_penalty_paths = (
            rule.get("soft_penalty_paths")
            if isinstance(rule, dict) and isinstance(rule.get("soft_penalty_paths"), dict)
            else {}
        )
        path = (urlparse(url).path or "").lower().rstrip("/")
        return path in set(soft_penalty_paths.keys())

    def _search_web_site_links(session: requests.Session, site: str, query_text: str, max_links: int = 6) -> List[str]:
        if not query_text.strip():
            return []
        search_url = f"https://www.bing.com/search?q=site:{site}%20{query_text}"
        try:
            html = _safe_get(session, search_url, timeout=1)
        except Exception:
            return []
        links: List[str] = []
        for href in re.findall(r"<a[^>]*href=[\"'](https?://[^\"']+)[\"']", html, flags=re.I):
            low = href.lower()
            if site not in low:
                continue
            if any(x in low for x in ("bing.com", "javascript:", "translate.google")):
                continue
            links.append(href)
        return list(dict.fromkeys(links))[:max_links]

    def _extract_ttyingqiu_links_playwright(entry_url: str) -> List[Dict[str, str]]:
        try:
            from playwright.sync_api import sync_playwright
        except Exception:
            return []
        links: List[Dict[str, str]] = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(entry_url, wait_until="domcontentloaded", timeout=8000)
                page.wait_for_timeout(1200)
                hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href') || '')")
                texts = page.eval_on_selector_all("a[href]", "els => els.map(e => (e.textContent || '').trim())")
                browser.close()
        except Exception:
            return []
        for i, href in enumerate(hrefs or []):
            full = urljoin(entry_url, (href or "").strip())
            low = full.lower()
            if "ttyingqiu.com" not in low:
                continue
            if "/news/home" in low or low.rstrip("/").endswith("/news"):
                continue
            if "/news/" not in low:
                continue
            text = _clean_html_text((texts[i] if i < len(texts) else "") or "")[:140]
            if not text:
                continue
            links.append({"url": full, "anchor": text})
        dedup: Dict[str, Dict[str, str]] = {}
        for x in links:
            if x["url"] not in dedup:
                dedup[x["url"]] = x
        return list(dedup.values())[:20]

    def _fetch_source_snapshot(source_code: str, timeout: int = 8) -> Dict[str, Any]:
        url = SOURCE_URL_MAP.get(source_code, "")
        if not url:
            return {"source_code": source_code, "url": "", "title": "", "excerpt": "", "error": "source url missing"}
        try:
            session = _new_session()
            html = _safe_get(session, url, timeout=timeout)
            return {
                "source_code": source_code,
                "url": url,
                "html": html,
                "title": _extract_title(html),
                "excerpt": _clean_html_text(html)[:220],
                "fetched_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "error": None,
            }
        except Exception as e:
            return {
                "source_code": source_code,
                "url": url,
                "html": "",
                "title": "",
                "excerpt": "",
                "fetched_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
            }

    def _extract_candidate_links(
        source_code: str,
        base_url: str,
        html: str,
        require_article_hint: bool = False,
        max_links: int = 60,
    ) -> List[Dict[str, Any]]:
        candidates: List[Dict[str, Any]] = []
        if not html:
            return candidates

        anchor_pattern = re.compile(
            r"<a[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>",
            flags=re.I | re.S,
        )
        for href, inner in anchor_pattern.findall(html):
            full_url = urljoin(base_url, href.strip())
            if not full_url.startswith("http"):
                continue
            if not _host_allowed(source_code, base_url, full_url):
                continue
            if not _source_url_allowed(source_code, full_url):
                continue
            text = _clean_html_text(inner)[:120]
            if not text:
                continue
            if require_article_hint and not _is_article_link(full_url, text):
                continue
            candidates.append(
                {
                    "url": full_url,
                    "anchor": text,
                    "is_article_hint": _is_article_link(full_url, text),
                    "is_nav_hint": _is_nav_link(full_url, text),
                }
            )

        dedup: Dict[str, Dict[str, Any]] = {}
        for c in candidates:
            dedup[c["url"]] = c
        return list(dedup.values())[:max_links]

    def _expand_league_alias(league_name: str) -> List[str]:
        text = (league_name or "").strip()
        if not text or text == "-":
            return []
        values = [text]
        for k, alias in LEAGUE_ALIAS_MAP.items():
            if text == k or text in alias or k in text:
                values.extend([k, *alias])
        custom_league_map = alias_dictionary.get("league") if isinstance(alias_dictionary, dict) else {}
        if isinstance(custom_league_map, dict):
            for canonical, aliases in custom_league_map.items():
                alias_list = aliases if isinstance(aliases, list) else [aliases]
                if text == canonical or text in alias_list or canonical in text:
                    values.extend([str(canonical), *[str(x) for x in alias_list]])
        out: List[str] = []
        seen = set()
        for x in values:
            norm = _normalize_text(x)
            if len(norm) >= 2 and norm not in seen:
                seen.add(norm)
                out.append(norm)
        return out

    def _expand_team_alias(team_name: str) -> List[str]:
        text = (team_name or "").strip()
        if not text or text == "-":
            return []
        candidates = [text]
        plain = re.sub(r"[\[\]\(\)锛堬級]", " ", text)
        plain = re.sub(r"\s+", " ", plain).strip()
        candidates.append(plain)
        strip_tokens = ("足球俱乐部", "俱乐部", "足球队", "队", "fc", "sc", "cf", "club")
        low_plain = plain.lower()
        for token in strip_tokens:
            if low_plain.endswith(token):
                candidates.append(plain[: len(plain) - len(token)].strip())
            if low_plain.startswith(token + " "):
                candidates.append(plain[len(token) + 1 :].strip())
        custom_team_map = alias_dictionary.get("team") if isinstance(alias_dictionary, dict) else {}
        if isinstance(custom_team_map, dict):
            for canonical, aliases in custom_team_map.items():
                alias_list = aliases if isinstance(aliases, list) else [aliases]
                if text == canonical or text in alias_list or canonical in text:
                    candidates.extend([str(canonical), *[str(x) for x in alias_list]])
        out: List[str] = []
        seen = set()
        for x in candidates:
            norm = _normalize_text(x)
            if len(norm) >= 2 and norm not in seen:
                seen.add(norm)
                out.append(norm)
        return out

    def _expand_team_alias_variants(team_name: str) -> List[str]:
        base_aliases = _expand_team_alias(team_name)
        if not base_aliases:
            return []

        # Lightweight CJK variant mapping (simplified/traditional subset for football names).
        cjk_map = {
            "联": "聯", "隊": "队", "队": "隊", "國": "国", "国": "國", "兰": "蘭", "马": "馬",
            "罗": "羅", "亚": "亞", "萨": "薩", "维": "維", "门": "門", "纳": "納", "尔": "爾",
            "图": "圖", "莱": "萊", "贝": "貝", "汉": "漢", "诺": "諾", "伦": "倫", "德": "德",
            "齐": "齊", "费": "費", "克": "克", "奥": "奧", "乌": "烏", "顿": "頓", "热": "熱",
            "刺": "刺", "皇": "皇", "城": "城", "联队": "聯隊", "联": "聯",
        }

        def _cjk_variants(s: str) -> List[str]:
            outs = {s}
            t = s
            for k, v in cjk_map.items():
                t = t.replace(k, v)
            outs.add(t)
            s2 = s
            for k, v in cjk_map.items():
                s2 = s2.replace(v, k)
            outs.add(s2)
            return [x for x in outs if x]

        variants: List[str] = []
        for alias in base_aliases:
            variants.extend(_cjk_variants(alias))
            # English abbreviation expansion (for Latin names).
            latin = re.sub(r"[^a-zA-Z\s]", " ", alias).strip()
            if latin:
                parts = [p for p in latin.lower().split() if p and p not in {"fc", "cf", "sc", "club"}]
                if parts:
                    variants.append(" ".join(parts))
                if len(parts) >= 2:
                    initials = "".join(p[0] for p in parts if p)
                    if len(initials) >= 2:
                        variants.append(initials)
                # Common football short forms.
                joined = " ".join(parts)
                variants.append(joined.replace("united", "utd"))
                variants.append(joined.replace("saint", "st"))
                variants.append(joined.replace("athletic", "ath"))

        out: List[str] = []
        seen = set()
        for x in variants:
            norm = _normalize_text(x)
            if len(norm) >= 2 and norm not in seen:
                seen.add(norm)
                out.append(norm)
        return out

    def _build_keyword_weights(league_name: str, home_team: str, away_team: str) -> Dict[str, float]:
        weights: Dict[str, float] = {}

        def _add(values: List[str], base_weight: float) -> None:
            for v in values:
                weights[v] = max(weights.get(v, 0.0), base_weight)
                for token in re.split(r"[\s\-_/]+", v):
                    token = token.strip()
                    if len(token) >= 2:
                        weights[token] = max(weights.get(token, 0.0), base_weight - 0.3)

        _add(_expand_league_alias(league_name), 1.3)
        _add(_expand_team_alias_variants(home_team), 2.4)
        _add(_expand_team_alias_variants(away_team), 2.4)
        return weights

    def _build_strong_keywords(home_team: str, away_team: str) -> List[str]:
        strong: List[str] = []
        for x in _expand_team_alias(home_team) + _expand_team_alias(away_team):
            if x and len(x) >= 2:
                strong.append(x)
        # Team tokens are high precision; keep set size bounded.
        return list(dict.fromkeys(strong))[:12]

    def _build_context_keywords(kw_weights: Dict[str, float], strong_keywords: List[str]) -> List[str]:
        keys: List[str] = []
        keys.extend(strong_keywords)
        for k, w in kw_weights.items():
            if w >= 1.3 and len(k) >= 2:
                keys.append(k)
        return list(dict.fromkeys(keys))[:20]

    def _context_hit_count(text: str, context_keywords: List[str]) -> int:
        low = _normalize_text(text)
        return len([k for k in context_keywords if k and k in low])

    def _effective_len(text: str) -> int:
        plain = re.sub(r"\s+", "", text or "")
        plain = re.sub(r"[，。！？、；：,.!?;:\-_/|()\[\]{}<>\"'`~@#$%^&*+=]", "", plain)
        return len(plain)

    def _parse_datetime_candidates(text: str, kickoff_time: Optional[datetime]) -> List[datetime]:
        raw = unescape(text or "")
        if not raw:
            return []
        norm = (
            raw.replace("年", "-")
            .replace("月", "-")
            .replace("日", " ")
            .replace("时", ":")
            .replace("分", " ")
            .replace("T", " ")
            .replace("/", "-")
            .replace(".", "-")
        )
        results: List[datetime] = []
        seen = set()

        def _add_dt(year: int, month: int, day: int, hour: int = 0, minute: int = 0):
            try:
                dt = datetime(year, month, day, hour, minute)
            except Exception:
                return
            key = dt.strftime("%Y-%m-%d %H:%M")
            if key in seen:
                return
            seen.add(key)
            results.append(dt)

        # YYYY-MM-DD HH:MM / YYYY-MM-DD
        for m in re.finditer(
            r"(?<!\d)(20\d{2})-(\d{1,2})-(\d{1,2})(?:\s+(\d{1,2})[:：](\d{1,2}))?(?!\d)",
            norm,
        ):
            y = int(m.group(1))
            mo = int(m.group(2))
            d = int(m.group(3))
            hh = int(m.group(4) or 0)
            mm = int(m.group(5) or 0)
            _add_dt(y, mo, d, hh, mm)

        # YYYYMMDD[HHMM]
        for m in re.finditer(r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?:([01]\d|2[0-3])([0-5]\d))?(?!\d)", norm):
            y = int(m.group(1))
            mo = int(m.group(2))
            d = int(m.group(3))
            hh = int(m.group(4) or 0)
            mm = int(m.group(5) or 0)
            _add_dt(y, mo, d, hh, mm)

        # MM-DD HH:MM / MM-DD (infer year by kickoff)
        base_year = kickoff_time.year if kickoff_time else datetime.utcnow().year
        for m in re.finditer(
            r"(?<!\d)(\d{1,2})-(\d{1,2})(?:\s+(\d{1,2})[:：](\d{1,2}))?(?!\d)",
            norm,
        ):
            mo = int(m.group(1))
            d = int(m.group(2))
            hh = int(m.group(3) or 0)
            mm = int(m.group(4) or 0)
            try:
                probe = datetime(base_year, mo, d, hh, mm)
            except Exception:
                continue
            if kickoff_time:
                # Keep inferred date close to kickoff year to avoid cross-year mismatch.
                candidates = [probe, probe.replace(year=base_year - 1), probe.replace(year=base_year + 1)]
                probe = min(candidates, key=lambda x: abs((x - kickoff_time).total_seconds()))
            _add_dt(probe.year, probe.month, probe.day, probe.hour, probe.minute)

        return results

    def _pick_best_publish_time(
        article_url: str,
        article_title: str,
        article_excerpt: str,
        kickoff_time: Optional[datetime],
    ) -> Optional[datetime]:
        bags = [article_url or "", article_title or "", article_excerpt or ""]
        all_dt: List[datetime] = []
        for bag in bags:
            all_dt.extend(_parse_datetime_candidates(bag, kickoff_time))
        if not all_dt:
            return None
        if kickoff_time:
            return min(all_dt, key=lambda x: abs((x - kickoff_time).total_seconds()))
        return sorted(all_dt)[0]

    def _time_window_bounds(kickoff_time: datetime) -> tuple[datetime, datetime]:
        # Hard gate: article publish time must be in a finite pre/post window around kickoff.
        lower = kickoff_time - timedelta(hours=time_window_before_hours)
        upper = kickoff_time + timedelta(hours=time_window_after_hours)
        return lower, upper

    def _apply_match_time_window_gate(
        source_code: str,
        article_pick: Dict[str, Any],
        kickoff_time: Optional[datetime],
    ) -> Dict[str, Any]:
        if not article_pick.get("matched"):
            return article_pick
        parser_name = _sanitize_meta_text(article_pick.get("source_parser"), f"{source_code}-parser")
        if not kickoff_time:
            if time_window_strict_mode:
                return _build_unmatched_result(source_code, "time-window-gate:no-match-kickoff", f"{parser_name}-time-gate")
            pass_reason = _sanitize_meta_text(article_pick.get("quality_pass_reason"), "article-page-hit")
            article_pick["quality_pass_reason"] = f"{pass_reason},time-window-soft(no-kickoff)"
            return article_pick
        publish_time = _pick_best_publish_time(
            article_url=str(article_pick.get("article_url") or ""),
            article_title=str(article_pick.get("article_title") or ""),
            article_excerpt=str(article_pick.get("article_excerpt") or ""),
            kickoff_time=kickoff_time,
        )
        if not publish_time:
            if time_window_strict_mode:
                return _build_unmatched_result(source_code, "time-window-gate:no-publish-time", f"{parser_name}-time-gate")
            pass_reason = _sanitize_meta_text(article_pick.get("quality_pass_reason"), "article-page-hit")
            article_pick["quality_pass_reason"] = f"{pass_reason},time-window-soft(no-publish-time)"
            return article_pick
        lower, upper = _time_window_bounds(kickoff_time)
        if not (lower <= publish_time <= upper):
            reason = (
                "time-window-gate:out-of-window "
                f"publish={publish_time.strftime('%Y-%m-%d %H:%M')} "
                f"kickoff={kickoff_time.strftime('%Y-%m-%d %H:%M')} "
                f"window={lower.strftime('%Y-%m-%d %H:%M')}~{upper.strftime('%Y-%m-%d %H:%M')}"
            )
            if time_window_strict_mode:
                return _build_unmatched_result(
                    source_code,
                    reason,
                    f"{parser_name}-time-gate",
                )
            pass_reason = _sanitize_meta_text(article_pick.get("quality_pass_reason"), "article-page-hit")
            article_pick["quality_pass_reason"] = f"{pass_reason},time-window-soft(out-of-window)"
            return article_pick
        article_pick["published_at_inferred"] = publish_time.strftime("%Y-%m-%d %H:%M:%S")
        pass_reason = _sanitize_meta_text(article_pick.get("quality_pass_reason"), "article-page-hit")
        article_pick["quality_pass_reason"] = f"{pass_reason},time-window-hit"
        return article_pick

    def _is_low_quality_candidate(
        source_code: str,
        url: str,
        title: str,
        excerpt: str,
        context_keywords: List[str],
        intel_type: str,
    ) -> bool:
        low_url = (url or "").lower()
        low_title = _normalize_text(title)
        path = (urlparse(url).path or "").lower().rstrip("/")

        # Generic non-detail patterns.
        if any(x in low_url for x in ("/news/home", "/index", "/list", "/tag", "/topic", "/match-center")):
            return True

        # Source-specific detail constraints.
        if source_code == "ttyingqiu":
            if path in {"", "/", "/news", "/news/home"}:
                return True
            if "/news/" in path and not re.search(r"/news/\d+", path):
                return True
        elif source_code == "500w":
            if "500.com" in low_url and not any(x in low_url for x in ("news.500.com", "/zq/", "/jczq/", "/bd/")):
                return True
        elif source_code == "sina":
            if "sports.sina.com.cn" not in low_url:
                return True
            if not any(x in low_url for x in (".shtml", "/doc-", "/article", "/news", "/g/")):
                return True
        elif source_code == "tencent":
            if "qq.com" in low_url and not any(x in low_url for x in ("/a/", "/omn/", "/article/", "/sports/")):
                return True

        # Basic title/content quality.
        if _effective_len(title) < min_title_len:
            return True
        if any(x in low_title for x in low_quality_title_hints) and _context_hit_count(title, context_keywords) < min_context_hits:
            return True

        if source_code == "weibo":
            min_excerpt_len = min_excerpt_len_weibo
        else:
            min_excerpt_len = min_excerpt_len_prediction if intel_type in PREDICTION_TYPES else min_excerpt_len_off_field
        if _effective_len(excerpt) < min_excerpt_len:
            return True

        # Require at least one context keyword in title+excerpt.
        if _context_hit_count(f"{title} {excerpt}", context_keywords) < min_context_hits:
            return True
        return False

    def _has_context_match(text: str, context_keywords: List[str]) -> bool:
        if not context_keywords:
            return False
        low = _normalize_text(text)
        hit = 0
        for k in context_keywords:
            if k in low:
                hit += 1
                if hit >= 1:
                    return True
        return False

    def _score_candidate_text(text: str, kw_weights: Dict[str, float], intel_type: str) -> float:
        low = _normalize_text(text)
        score = 0.0
        for kw, weight in kw_weights.items():
            if kw in low:
                score += weight
        # Reduce common false positives from lottery pages.
        if any(x in low for x in ("双色球", "福彩", "体彩", "开奖", "彩票", "3d", "排列三")):
            score -= 3.2
        if intel_type in PREDICTION_TYPES:
            if any(x in low for x in OPINION_HINT_PATTERNS):
                score += 1.6
        else:
            if any(x in low for x in ("injury", "weather", "referee", "lineup", "浼ょ梾", "澶╂皵", "瑁佸垽", "闃靛", "涓诲竻", "鎴樻湳", "鎴樻剰", "浜ら攱")):
                score += 1.2
        return score

    def _build_article_candidate(
        source_code: str,
        url: str,
        title: str,
        excerpt: str,
        score: float,
        *,
        source_parser: str = "",
        hit_terms: Optional[List[str]] = None,
        pass_reason: str = "",
    ) -> Dict[str, Any]:
        return {
            "matched": True,
            "source_code": source_code,
            "article_url": url,
            "article_title": (title or f"{source_code} article")[:240],
            "article_excerpt": (excerpt or "")[:260],
            "match_score": round(score, 2),
            "quality_score": round(score, 2),
            "quality_pass_reason": _sanitize_meta_text(pass_reason, "article-page-hit"),
            "quality_block_reason": "",
            "match_hit_terms": hit_terms or [],
            "source_parser": source_parser or f"{source_code}-parser",
            "is_article_page": True,
        }

    def _build_unmatched_result(source_code: str, error: str, source_parser: str = "") -> Dict[str, Any]:
        block_reason = _sanitize_meta_text(error, "no-match")
        return {
            "matched": False,
            "error": block_reason,
            "quality_score": 0.0,
            "quality_pass_reason": "",
            "quality_block_reason": block_reason,
            "match_hit_terms": [],
            "source_parser": source_parser or f"{source_code}-parser",
            "is_article_page": False,
        }

    def _fetch_500w_article(
        session: requests.Session,
        kw_weights: Dict[str, float],
        context_keywords: List[str],
        intel_type: str,
    ) -> Optional[Dict[str, Any]]:
        entry_urls = [
            "https://news.500.com/zq/",
            "https://www.500.com/jczq/",
        ]
        best: Optional[Dict[str, Any]] = None
        for entry in entry_urls:
            try:
                entry_html = _safe_get(session, entry, timeout=1)
            except Exception:
                continue
            links = _extract_candidate_links("500w", entry, entry_html, require_article_hint=False, max_links=12)
            for link in links[:4]:
                url = link.get("url", "")
                low_url = url.lower()
                if not any(x in low_url for x in ("news.500.com", "/zq/", "/jczq/", "saishi")):
                    continue
                title = link.get("anchor", "")
                seed = _score_candidate_text(f"{title} {url}", kw_weights, intel_type)
                if seed <= 1.0:
                    continue
                try:
                    html = _safe_get(session, url, timeout=1)
                except Exception:
                    continue
                page_title = _extract_title(html) or title
                excerpt = _clean_html_text(html)[:420]
                score = _score_candidate_text(f"{page_title} {excerpt} {url}", kw_weights, intel_type) + min(seed, 1.8)
                cand = _build_article_candidate(
                    "500w",
                    url,
                    page_title,
                    excerpt,
                    score,
                    source_parser="500w-dedicated",
                    pass_reason="500w dedicated detail page matched by teams/league keywords",
                )
                if _is_low_quality_candidate("500w", url, page_title, excerpt, context_keywords, intel_type):
                    continue
                if not best or cand["match_score"] > best["match_score"]:
                    best = cand
        if not best:
            q = " ".join(context_keywords[:2]) if context_keywords else ""
            for url in _search_web_site_links(session, "500.com", q, max_links=4):
                try:
                    html = _safe_get(session, url, timeout=1)
                except Exception:
                    continue
                title = _extract_title(html) or "500w瑙傜偣"
                excerpt = _clean_html_text(html)[:380]
                score = _score_candidate_text(f"{title} {excerpt} {url}", kw_weights, intel_type) + 1.0
                cand = _build_article_candidate(
                    "500w",
                    url,
                    title,
                    excerpt,
                    score,
                    source_parser="500w-search-fallback",
                    pass_reason="500w site-search detail page fallback",
                )
                if _is_low_quality_candidate("500w", url, title, excerpt, context_keywords, intel_type):
                    continue
                if not best or cand["match_score"] > best["match_score"]:
                    best = cand
        return best

    def _fetch_tencent_article(
        session: requests.Session,
        kw_weights: Dict[str, float],
        context_keywords: List[str],
        intel_type: str,
    ) -> Optional[Dict[str, Any]]:
        entry_urls = [
            "https://sports.qq.com/",
            "https://new.qq.com/ch/sports/",
        ]
        best: Optional[Dict[str, Any]] = None
        for entry in entry_urls:
            try:
                entry_html = _safe_get(session, entry, timeout=1)
            except Exception:
                continue
            links = _extract_candidate_links("tencent", entry, entry_html, require_article_hint=False, max_links=14)
            for link in links[:5]:
                url = link.get("url", "")
                if not any(x in url.lower() for x in ("/a/", "/sports/", "new.qq.com")):
                    continue
                seed = _score_candidate_text(f"{link.get('anchor','')} {url}", kw_weights, intel_type)
                if seed <= 1.0:
                    continue
                try:
                    html = _safe_get(session, url, timeout=1)
                except Exception:
                    continue
                title = _extract_title(html) or link.get("anchor", "")
                excerpt = _clean_html_text(html)[:420]
                score = _score_candidate_text(f"{title} {excerpt} {url}", kw_weights, intel_type) + min(seed, 2.0)
                cand = _build_article_candidate(
                    "tencent",
                    url,
                    title,
                    excerpt,
                    score,
                    source_parser="tencent-dedicated",
                    pass_reason="tencent dedicated sports article parser matched context",
                )
                if _is_low_quality_candidate("tencent", url, title, excerpt, context_keywords, intel_type):
                    continue
                if not best or cand["match_score"] > best["match_score"]:
                    best = cand
        # Dedicated Tencent search page fallback (still source-specific)
        if not best:
            q = " ".join(context_keywords[:2]) if context_keywords else ""
            if q:
                try:
                    html = _safe_get(session, f"https://new.qq.com/search?query={q}", timeout=1)
                except Exception:
                    html = ""
                for href, inner in re.findall(r"<a[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, flags=re.I | re.S):
                    full = urljoin("https://new.qq.com", href.strip())
                    if "qq.com" not in full or "/rain/" in full:
                        continue
                    title = _clean_html_text(inner)[:120]
                    if not title:
                        continue
                    score = _score_candidate_text(f"{title} {full}", kw_weights, intel_type) + 1.2
                    cand = _build_article_candidate(
                        "tencent",
                        full,
                        title,
                        title,
                        score,
                        source_parser="tencent-search-page",
                        pass_reason="tencent search-page fallback candidate",
                    )
                    if _is_low_quality_candidate("tencent", full, title, title, context_keywords, intel_type):
                        continue
                    if not best or cand["match_score"] > best["match_score"]:
                        best = cand
        if not best:
            q = " ".join(context_keywords[:2]) if context_keywords else ""
            for url in _search_web_site_links(session, "qq.com", q, max_links=4):
                try:
                    html = _safe_get(session, url, timeout=1)
                except Exception:
                    continue
                title = _extract_title(html) or "鑵捐瑙傜偣"
                excerpt = _clean_html_text(html)[:380]
                score = _score_candidate_text(f"{title} {excerpt} {url}", kw_weights, intel_type) + 1.0
                cand = _build_article_candidate(
                    "tencent",
                    url,
                    title,
                    excerpt,
                    score,
                    source_parser="tencent-site-search",
                    pass_reason="tencent site-search fallback candidate",
                )
                if _is_low_quality_candidate("tencent", url, title, excerpt, context_keywords, intel_type):
                    continue
                if not best or cand["match_score"] > best["match_score"]:
                    best = cand
        return best

    def _fetch_sina_article(
        session: requests.Session,
        kw_weights: Dict[str, float],
        context_keywords: List[str],
        intel_type: str,
    ) -> Optional[Dict[str, Any]]:
        entry_urls = [
            "https://sports.sina.com.cn/",
            "https://sports.sina.com.cn/global/",
            "https://sports.sina.com.cn/china/",
        ]
        best: Optional[Dict[str, Any]] = None
        for entry in entry_urls:
            try:
                entry_html = _safe_get(session, entry, timeout=1)
            except Exception:
                continue
            links = _extract_candidate_links("sina", entry, entry_html, require_article_hint=False, max_links=18)
            for link in links[:6]:
                url = link.get("url", "")
                low_url = url.lower()
                if "sports.sina.com.cn" not in low_url:
                    continue
                if not any(x in low_url for x in (".shtml", "/doc-", "/article", "/news", "/g/")):
                    continue
                seed = _score_candidate_text(f"{link.get('anchor', '')} {url}", kw_weights, intel_type)
                if seed <= 0.8:
                    continue
                try:
                    html = _safe_get(session, url, timeout=1)
                except Exception:
                    continue
                title = _extract_title(html) or link.get("anchor", "")
                excerpt = _clean_html_text(html)[:420]
                score = _score_candidate_text(f"{title} {excerpt} {url}", kw_weights, intel_type) + min(seed, 1.7)
                cand = _build_article_candidate(
                    "sina",
                    url,
                    title,
                    excerpt,
                    score,
                    source_parser="sina-dedicated",
                    pass_reason="sina sports article parser matched teams/league context",
                )
                if _is_low_quality_candidate("sina", url, title, excerpt, context_keywords, intel_type):
                    continue
                if not best or cand["match_score"] > best["match_score"]:
                    best = cand

        if not best:
            q = " ".join(context_keywords[:2]) if context_keywords else ""
            for url in _search_web_site_links(session, "sports.sina.com.cn", q, max_links=5):
                try:
                    html = _safe_get(session, url, timeout=1)
                except Exception:
                    continue
                title = _extract_title(html) or "新浪体育观点"
                excerpt = _clean_html_text(html)[:380]
                score = _score_candidate_text(f"{title} {excerpt} {url}", kw_weights, intel_type) + 1.0
                cand = _build_article_candidate(
                    "sina",
                    url,
                    title,
                    excerpt,
                    score,
                    source_parser="sina-site-search",
                    pass_reason="sina sports site-search fallback candidate",
                )
                if _is_low_quality_candidate("sina", url, title, excerpt, context_keywords, intel_type):
                    continue
                if not best or cand["match_score"] > best["match_score"]:
                    best = cand
        return best

    def _fetch_weibo_article(
        session: requests.Session,
        kw_weights: Dict[str, float],
        context_keywords: List[str],
        intel_type: str,
    ) -> Optional[Dict[str, Any]]:
        query_terms = list(kw_weights.keys())[:6]
        if not query_terms:
            return None
        # Use mobile public API endpoint as a dedicated parser for Weibo viewpoints.
        q = " ".join(query_terms[:2])
        api_url = "https://m.weibo.cn/api/container/getIndex"
        try:
            resp = session.get(
                api_url,
                params={"containerid": f"100103type=1&t=10&q={q}"},
                timeout=1,
            )
            data = resp.json() if resp.status_code == 200 else {}
        except Exception:
            data = {}
        cards = data.get("data", {}).get("cards", []) if isinstance(data, dict) else []
        best: Optional[Dict[str, Any]] = None
        for card in cards[:15]:
            mblog = card.get("mblog") if isinstance(card, dict) else None
            if not mblog:
                continue
            text = _clean_html_text(mblog.get("text", ""))[:420]
            if not text:
                continue
            blog_id = mblog.get("id") or ""
            url = f"https://m.weibo.cn/detail/{blog_id}" if blog_id else "https://m.weibo.cn/"
            user_name = (mblog.get("user") or {}).get("screen_name", "")
            title = f"寰崥瑙傜偣 - {user_name}" if user_name else "寰崥瑙傜偣"
            score = _score_candidate_text(f"{title} {text} {url}", kw_weights, intel_type) + 1.4
            cand = _build_article_candidate(
                "weibo",
                url,
                title,
                text,
                score,
                source_parser="weibo-mobile-api",
                pass_reason="weibo mobile api mblog detail matched context",
            )
            if _is_low_quality_candidate("weibo", url, title, text, context_keywords, intel_type):
                continue
            if not best or cand["match_score"] > best["match_score"]:
                best = cand
        if best:
            return best
        # Fallback: parse Weibo public search page for article/opinion links
        try:
            html = _safe_get(session, f"https://s.weibo.com/weibo?q={q}", timeout=1)
        except Exception:
            return None
        for href, inner in re.findall(r"<a[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, flags=re.I | re.S):
            full = urljoin("https://s.weibo.com", href.strip())
            if not any(x in full for x in ("/detail/", "/status/", "m.weibo.cn")):
                continue
            title = _clean_html_text(inner)[:120] or "寰崥瑙傜偣"
            excerpt = _clean_html_text(html)[:380]
            score = _score_candidate_text(f"{title} {excerpt} {full}", kw_weights, intel_type) + 1.2
            cand = _build_article_candidate(
                "weibo",
                full,
                title,
                excerpt,
                score,
                source_parser="weibo-search-page",
                pass_reason="weibo public search detail fallback",
            )
            if _is_low_quality_candidate("weibo", full, title, excerpt, context_keywords, intel_type):
                continue
            if not best or cand["match_score"] > best["match_score"]:
                best = cand
        if not best:
            q = " ".join(context_keywords[:2]) if context_keywords else ""
            for url in _search_web_site_links(session, "weibo.com", q, max_links=4):
                try:
                    html = _safe_get(session, url, timeout=1)
                except Exception:
                    continue
                title = _extract_title(html) or "寰崥瑙傜偣"
                excerpt = _clean_html_text(html)[:380]
                score = _score_candidate_text(f"{title} {excerpt} {url}", kw_weights, intel_type) + 1.0
                cand = _build_article_candidate(
                    "weibo",
                    url,
                    title,
                    excerpt,
                    score,
                    source_parser="weibo-site-search",
                    pass_reason="weibo site-search fallback",
                )
                if _is_low_quality_candidate("weibo", url, title, excerpt, context_keywords, intel_type):
                    continue
                if not best or cand["match_score"] > best["match_score"]:
                    best = cand
        return best

    def _fetch_ttyingqiu_article(
        session: requests.Session,
        kw_weights: Dict[str, float],
        context_keywords: List[str],
        intel_type: str,
    ) -> Optional[Dict[str, Any]]:
        import time

        parser_started_at = time.monotonic()
        parser_budget_seconds = 12.0
        primary_candidate_limit = 8
        search_fallback_limit = 3
        entry_urls = [
            "https://www.ttyingqiu.com/news/home",
            "https://www.ttyingqiu.com/news",
        ]
        best: Optional[Dict[str, Any]] = None
        detail_candidates: List[Dict[str, str]] = ttyingqiu_seed_cache.get("detail_links", [])
        if not detail_candidates:
            for entry in entry_urls:
                try:
                    entry_html = _safe_get(session, entry, timeout=1)
                except Exception:
                    continue
                for href, inner in re.findall(
                    r"<a[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>",
                    entry_html,
                    flags=re.I | re.S,
                ):
                    full = urljoin(entry, href.strip())
                    low = full.lower()
                    if "ttyingqiu.com" not in low:
                        continue
                    if "/news/home" in low:
                        continue
                    if "news" not in low:
                        continue
                    if _is_ttyingqiu_blacklisted(full):
                        continue
                    title = _clean_html_text(inner)[:140]
                    if not title:
                        continue
                    detail_candidates.append({"url": full, "anchor": title})

            if len(detail_candidates) < 3 and enable_playwright_fallback:
                detail_candidates.extend(_extract_ttyingqiu_links_playwright(entry_urls[0]))

        dedup: Dict[str, Dict[str, str]] = {}
        for x in detail_candidates:
            if x["url"] not in dedup:
                dedup[x["url"]] = x
        candidates = list(dedup.values())[:primary_candidate_limit]
        ttyingqiu_seed_cache["detail_links"] = candidates[:20]

        debug_pack: Dict[str, Any] = {
            "candidate_count": len(candidates),
            "evaluated_count": 0,
            "status_codes": {},
            "title_hit_keywords": {},
            "top_candidates": [],
            "soft_filtered": 0,
        }
        team_keywords = [k for k, w in kw_weights.items() if w >= 2.0 and len(k) >= 2]

        for cand in candidates:
            if (time.monotonic() - parser_started_at) > parser_budget_seconds:
                break
            url = cand["url"]
            if _is_ttyingqiu_blacklisted(url):
                continue
            anchor = cand.get("anchor", "")
            seed = _score_candidate_text(f"{anchor} {url}", kw_weights, intel_type)
            try:
                html, status_code = _safe_get_with_status(session, url, timeout=1)
            except Exception:
                debug_pack["status_codes"]["request_error"] = debug_pack["status_codes"].get("request_error", 0) + 1
                continue
            debug_pack["evaluated_count"] += 1
            debug_pack["status_codes"][str(status_code)] = debug_pack["status_codes"].get(str(status_code), 0) + 1
            title = _extract_title(html) or anchor
            body = _extract_ttyingqiu_article_body(html)
            excerpt = body[:460]
            if _is_ttyingqiu_soft_page(url):
                body_len = len(re.sub(r"\s+", "", body))
                body_hits = len([k for k in set(team_keywords) if k in _normalize_text(body)])
                if body_len < soft_page_min_body_len or body_hits < soft_page_min_team_hits:
                    debug_pack["soft_filtered"] += 1
                    continue
            if not _has_context_match(f"{title} {body}", context_keywords):
                continue
            norm_title = _normalize_text(title)
            norm_body = _normalize_text(body)
            hit_keys = [k for k in context_keywords if k in norm_title or k in norm_body]
            for hk in hit_keys[:4]:
                debug_pack["title_hit_keywords"][hk] = debug_pack["title_hit_keywords"].get(hk, 0) + 1
            score = _score_candidate_text(f"{title} {body} {url}", kw_weights, intel_type) + min(seed, 1.8) + 0.6
            score -= _ttyingqiu_penalty(url)
            if _is_low_quality_candidate("ttyingqiu", url, title, excerpt, context_keywords, intel_type):
                continue
            debug_pack["top_candidates"].append(
                {
                    "url": url,
                    "status": status_code,
                    "seed": round(seed, 2),
                    "score": round(score, 2),
                    "title_hits": hit_keys[:4],
                }
            )
            picked = _build_article_candidate(
                "ttyingqiu",
                url,
                title,
                excerpt,
                score,
                source_parser="ttyingqiu-news-detail",
                hit_terms=hit_keys[:6],
                pass_reason="ttyingqiu news detail page matched body/title context",
            )
            if not best or picked["match_score"] > best["match_score"]:
                best = picked

        if not best:
            q = " ".join(context_keywords[:2]) if context_keywords else ""
            for url in _search_web_site_links(session, "ttyingqiu.com", q, max_links=search_fallback_limit):
                if (time.monotonic() - parser_started_at) > parser_budget_seconds:
                    break
                low = url.lower()
                if "/news/home" in low or "news" not in low:
                    continue
                if _is_ttyingqiu_blacklisted(url):
                    continue
                try:
                    html, status_code = _safe_get_with_status(session, url, timeout=1)
                except Exception:
                    debug_pack["status_codes"]["request_error"] = debug_pack["status_codes"].get("request_error", 0) + 1
                    continue
                debug_pack["evaluated_count"] += 1
                debug_pack["status_codes"][str(status_code)] = debug_pack["status_codes"].get(str(status_code), 0) + 1
                title = _extract_title(html) or "ttyingqiu news"
                body = _extract_ttyingqiu_article_body(html)
                excerpt = body[:420]
                if _is_ttyingqiu_soft_page(url):
                    body_len = len(re.sub(r"\s+", "", body))
                    body_hits = len([k for k in set(team_keywords) if k in _normalize_text(body)])
                    if body_len < soft_page_min_body_len or body_hits < soft_page_min_team_hits:
                        debug_pack["soft_filtered"] += 1
                        continue
                if not _has_context_match(f"{title} {body}", context_keywords):
                    continue
                norm_title = _normalize_text(title)
                norm_body = _normalize_text(body)
                hit_keys = [k for k in context_keywords if k in norm_title or k in norm_body]
                for hk in hit_keys[:4]:
                    debug_pack["title_hit_keywords"][hk] = debug_pack["title_hit_keywords"].get(hk, 0) + 1
                score = _score_candidate_text(f"{title} {body} {url}", kw_weights, intel_type) + 1.0
                score -= _ttyingqiu_penalty(url)
                if _is_low_quality_candidate("ttyingqiu", url, title, excerpt, context_keywords, intel_type):
                    continue
                debug_pack["top_candidates"].append(
                    {
                        "url": url,
                        "status": status_code,
                        "seed": 0.0,
                        "score": round(score, 2),
                        "title_hits": hit_keys[:4],
                    }
                )
                picked = _build_article_candidate(
                    "ttyingqiu",
                    url,
                    title,
                    excerpt,
                    score,
                    source_parser="ttyingqiu-site-search",
                    hit_terms=hit_keys[:6],
                    pass_reason="ttyingqiu site-search detail fallback matched context",
                )
                if not best or picked["match_score"] > best["match_score"]:
                    best = picked

        debug_pack["top_candidates"] = sorted(
            debug_pack["top_candidates"], key=lambda x: x.get("score", 0), reverse=True
        )[:8]
        debug_pack["title_hit_keywords"] = dict(
            sorted(debug_pack["title_hit_keywords"].items(), key=lambda x: x[1], reverse=True)[:8]
        )
        ttyingqiu_seed_cache["last_debug"] = debug_pack
        return best

    def _fetch_match_article_inner(
        source_code: str,
        source_snapshot: Dict[str, Any],
        league_name: str,
        home_team: str,
        away_team: str,
        intel_type: str,
        kickoff_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        err = source_snapshot.get("error")
        if err:
            return _build_unmatched_result(source_code, str(err), f"{source_code}-source-snapshot")

        source_url = source_snapshot.get("url", SOURCE_URL_MAP.get(source_code, ""))
        html = source_snapshot.get("html", "")
        kw_weights = _build_keyword_weights(league_name, home_team, away_team)
        strong_keywords = _build_strong_keywords(home_team, away_team)
        context_keywords = _build_context_keywords(kw_weights, strong_keywords)
        if not kw_weights:
            return _build_unmatched_result(source_code, "match keywords empty", f"{source_code}-keyword-builder")

        session = _new_session()
        if source_code == "500w":
            picked = _fetch_500w_article(session, kw_weights, context_keywords, intel_type)
            if picked and float(picked.get("match_score", 0)) >= _source_min_match_score("500w", 1.6):
                return _apply_match_time_window_gate(source_code, picked, kickoff_time)
            return _build_unmatched_result(source_code, "500w dedicated parser no match", "500w-dedicated")
        elif source_code == "sina":
            picked = _fetch_sina_article(session, kw_weights, context_keywords, intel_type)
            if picked and float(picked.get("match_score", 0)) >= _source_min_match_score("sina", 1.5):
                return _apply_match_time_window_gate(source_code, picked, kickoff_time)
            return _build_unmatched_result(source_code, "sina dedicated parser no match", "sina-dedicated")
        elif source_code == "tencent":
            picked = _fetch_tencent_article(session, kw_weights, context_keywords, intel_type)
            if picked and float(picked.get("match_score", 0)) >= _source_min_match_score("tencent", 1.6):
                return _apply_match_time_window_gate(source_code, picked, kickoff_time)
            return _build_unmatched_result(source_code, "tencent dedicated parser no match", "tencent-dedicated")
        elif source_code == "weibo":
            picked = _fetch_weibo_article(session, kw_weights, context_keywords, intel_type)
            if picked and float(picked.get("match_score", 0)) >= _source_min_match_score("weibo", 1.4):
                return _apply_match_time_window_gate(source_code, picked, kickoff_time)
            return _build_unmatched_result(source_code, "weibo dedicated parser no match", "weibo-dedicated")
        elif source_code == "ttyingqiu":
            picked = _fetch_ttyingqiu_article(session, kw_weights, context_keywords, intel_type)
            if picked and float(picked.get("match_score", 0)) >= _source_min_match_score("ttyingqiu", 1.8):
                picked["_debug"] = ttyingqiu_seed_cache.get("last_debug", {})
                return _apply_match_time_window_gate(source_code, picked, kickoff_time)
            unmatched = _build_unmatched_result(source_code, "ttyingqiu dedicated parser no match", "ttyingqiu-dedicated")
            unmatched["_debug"] = ttyingqiu_seed_cache.get("last_debug", {})
            return unmatched

        links = _extract_candidate_links(source_code, source_url, html, require_article_hint=False, max_links=18)
        if not links:
            return _build_unmatched_result(source_code, "no candidate article links", f"{source_code}-generic-twohop")

        page_cache: Dict[str, str] = {}
        pool: List[Dict[str, Any]] = []
        for link in links[:6]:
            seed_text = f"{link.get('anchor', '')} {link.get('url', '')}"
            seed_score = _score_candidate_text(seed_text, kw_weights, intel_type)
            if link.get("is_article_hint") or seed_score > 0:
                pool.append({"url": link["url"], "anchor": link.get("anchor", ""), "depth": 0, "seed_score": seed_score})

        nav_seeds = [x for x in links if x.get("is_nav_hint")]
        for nav in nav_seeds[:1]:
            nav_url = nav["url"]
            try:
                nav_html = _safe_get(session, nav_url, timeout=1)
                page_cache[nav_url] = nav_html
            except Exception:
                continue
            child_links = _extract_candidate_links(source_code, nav_url, nav_html, require_article_hint=False, max_links=10)
            for child in child_links[:3]:
                child_seed = _score_candidate_text(
                    f"{child.get('anchor', '')} {child.get('url', '')}",
                    kw_weights,
                    intel_type,
                )
                if child.get("is_article_hint") or child_seed > 0:
                    pool.append(
                        {
                            "url": child["url"],
                            "anchor": child.get("anchor", ""),
                            "depth": 1,
                            "seed_score": child_seed + 0.5,
                        }
                    )

        dedup_pool: Dict[str, Dict[str, Any]] = {}
        for x in pool:
            u = x["url"]
            if u not in dedup_pool or x.get("seed_score", 0) > dedup_pool[u].get("seed_score", 0):
                dedup_pool[u] = x
        candidates = list(dedup_pool.values())[:4]
        if not candidates:
            return _build_unmatched_result(source_code, "no score-positive candidates after two-hop", f"{source_code}-generic-twohop")

        best: Optional[Dict[str, Any]] = None
        for cand in candidates:
            url = cand["url"]
            anchor = cand.get("anchor", "")
            seed_score = float(cand.get("seed_score", 0))
            depth = int(cand.get("depth", 0))
            try:
                article_html = page_cache.get(url) or _safe_get(session, url, timeout=1)
            except Exception:
                continue

            title = _extract_title(article_html)
            excerpt = _clean_html_text(article_html)[:480]
            if _is_low_quality_candidate(source_code, url, title or anchor, excerpt, context_keywords, intel_type):
                continue
            bag = f"{title} {anchor} {excerpt} {url}"
            final_score = _score_candidate_text(bag, kw_weights, intel_type) + min(seed_score, 2.2) + (0.2 if depth == 1 else 0.0)

            hit_terms = [k for k in context_keywords if k in _normalize_text(f"{title} {excerpt}")][:6]
            candidate = _build_article_candidate(
                source_code,
                url,
                title or anchor or f"{source_code} article",
                excerpt[:260],
                final_score,
                source_parser=f"{source_code}-generic-twohop",
                hit_terms=hit_terms,
                pass_reason="generic two-hop detail page matched context",
            )
            if not best or candidate["match_score"] > best["match_score"]:
                best = candidate

        if not best:
            return _build_unmatched_result(source_code, "no scored article page in candidates", f"{source_code}-generic-twohop")
        if float(best.get("match_score", 0)) < _source_min_match_score(source_code, 1.8):
            return _build_unmatched_result(
                source_code,
                f"best score too low: {best.get('match_score', 0)}",
                f"{source_code}-generic-twohop",
            )
        return _apply_match_time_window_gate(source_code, best, kickoff_time)

    def _fetch_match_article(
        source_code: str,
        source_snapshot: Dict[str, Any],
        league_name: str,
        home_team: str,
        away_team: str,
        intel_type: str,
        kickoff_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        try:
            return _fetch_match_article_inner(
                source_code=source_code,
                source_snapshot=source_snapshot,
                league_name=league_name,
                home_team=home_team,
                away_team=away_team,
                intel_type=intel_type,
                kickoff_time=kickoff_time,
            )
        except Exception as e:
            return _build_unmatched_result(source_code, f"parser exception: {e}", f"{source_code}-parser-wrapper")


    async def _load_match_meta() -> Dict[int, Dict[str, Any]]:
        if not match_ids:
            return {}
        home = aliased(Team)
        away = aliased(Team)
        rows = (
            await db.execute(
                select(Match.id, League.name, home.name, away.name, Match.scheduled_kickoff, Match.match_date)
                .join(League, Match.league_id == League.id, isouter=True)
                .join(home, Match.home_team_id == home.id, isouter=True)
                .join(away, Match.away_team_id == away.id, isouter=True)
                .where(Match.id.in_(match_ids))
            )
        ).all()
        meta: Dict[int, Dict[str, Any]] = {}
        for mid, league_name, home_name, away_name, scheduled_kickoff, match_date in rows:
            kickoff_time = scheduled_kickoff
            if not kickoff_time and match_date:
                kickoff_time = datetime(match_date.year, match_date.month, match_date.day, 12, 0, 0)
            meta[mid] = {
                "league_name": league_name or "-",
                "home_team": home_name or "-",
                "away_team": away_name or "-",
                "kickoff_time": kickoff_time,
            }
        return meta

    def _build_ai_meta_segment(ai_result: Optional[Dict[str, Any]]) -> str:
        if not ai_result:
            return "ai_enhanced=0; ai_reason=not-requested; "
        enhanced = bool(ai_result.get("used"))
        provider = _sanitize_meta_text(ai_result.get("provider"), "")
        model_name = _sanitize_meta_text(ai_result.get("model"), "")
        ai_summary = _sanitize_meta_text(ai_result.get("summary"), "")
        ai_viewpoint = _sanitize_meta_text(ai_result.get("viewpoint"), "")
        ai_risk_level = _sanitize_meta_text(ai_result.get("risk_level"), "")
        ai_reason = _sanitize_meta_text(ai_result.get("reason"), "")
        ai_key_factors = _sanitize_meta_text(ai_result.get("key_factors"), "")
        ai_conf = ai_result.get("confidence")
        ai_conf_text = ""
        if ai_conf is not None:
            try:
                ai_conf_text = str(round(float(ai_conf), 3))
            except Exception:
                ai_conf_text = ""
        return (
            f"ai_enhanced={(1 if enhanced else 0)}; "
            f"ai_provider={provider}; ai_model={model_name}; ai_confidence={ai_conf_text}; "
            f"ai_risk_level={ai_risk_level}; ai_viewpoint={ai_viewpoint}; ai_key_factors={ai_key_factors}; "
            f"ai_reason={ai_reason}; ai_summary={ai_summary}; "
        )

    def _build_content_raw(
        source_snapshot: Dict[str, Any],
        article_pick: Dict[str, Any],
        ai_result: Optional[Dict[str, Any]],
        match_id: int,
        intel_type: str,
        league_name: str,
        home_team: str,
        away_team: str,
        kickoff_time: Optional[datetime] = None,
    ) -> str:
        source_code = source_snapshot.get("source_code", "")
        err = article_pick.get("error") or source_snapshot.get("error")
        title = source_snapshot.get("title", "")
        excerpt = source_snapshot.get("excerpt", "")
        fetched_at = source_snapshot.get("fetched_at", "")
        match_text = f"{league_name} {home_team} vs {away_team} (match_id={match_id})"
        parser_name = _sanitize_meta_text(article_pick.get("source_parser"), f"{source_code}-snapshot")
        hit_terms = article_pick.get("match_hit_terms") or []
        if not isinstance(hit_terms, list):
            hit_terms = []
        hit_terms_text = _sanitize_meta_text("|".join([str(x) for x in hit_terms[:8]]), "-")
        quality_score = round(_safe_float(article_pick.get("quality_score", article_pick.get("match_score", 0)), 0.0), 2)
        pass_reason = _sanitize_meta_text(article_pick.get("quality_pass_reason"), "")
        block_reason = _sanitize_meta_text(article_pick.get("quality_block_reason"), _sanitize_meta_text(err))
        ai_meta_segment = _build_ai_meta_segment(ai_result)
        if err:
            return (
                f"[match-article-fallback] source={source_code}; source_parser={parser_name}; fetched_at={fetched_at}; "
                f"match={match_text}; intel_type={intel_type}; quality_score=0; quality_block_reason={block_reason}; "
                f"hit_terms={hit_terms_text}; fetch_error=({block_reason}); homepage_hint={_sanitize_meta_text(title or excerpt)}; "
                f"{ai_meta_segment}"
                "is_article_page=0;"
            )
        if article_pick.get("matched"):
            article_url = article_pick.get("article_url", "")
            article_title = _sanitize_meta_text(article_pick.get("article_title", ""))
            article_excerpt = _sanitize_meta_text(article_pick.get("article_excerpt", ""))
            inferred_publish_time = _sanitize_meta_text(article_pick.get("published_at_inferred"), "")
            kickoff_text = kickoff_time.strftime("%Y-%m-%d %H:%M:%S") if kickoff_time else ""
            score = article_pick.get("match_score", 0)
            return (
                f"[match-article] source={source_code}; fetched_at={fetched_at}; match={match_text}; "
                f"intel_type={intel_type}; article_url={article_url}; article_title={article_title}; "
                f"match_score={score}; quality_score={quality_score}; source_parser={parser_name}; "
                f"quality_pass_reason={pass_reason or 'detail-page-context-hit'}; quality_block_reason=; "
                f"hit_terms={hit_terms_text}; article_published_at={inferred_publish_time}; match_kickoff={kickoff_text}; "
                f"{ai_meta_segment}"
                f"summary={article_excerpt}; is_article_page=1;"
            )
        core = _sanitize_meta_text(title or excerpt or f"{source_code} homepage reachable but title not extracted")
        return (
            f"[source-view] source={source_code}; source_parser={parser_name}; fetched_at={fetched_at}; "
            f"match={match_text}; intel_type={intel_type}; quality_score=0; quality_block_reason={block_reason or 'no-article-match'}; "
            f"hit_terms={hit_terms_text}; {ai_meta_segment}"
            f"summary={core}; is_article_page=0;"
        )

    created = 0
    updated = 0
    failed = 0
    fail_reasons: Dict[str, int] = {}
    tty_debug_rows: List[Dict[str, Any]] = []
    now = datetime.utcnow()
    snapshots = {src: _fetch_source_snapshot(src) for src in sources}
    match_meta = await _load_match_meta()
    article_pick_cache: Dict[tuple, Dict[str, Any]] = {}
    subtask_rows = (
        await db.execute(
            select(IntelligenceCollectionMatchSubtask).where(
                IntelligenceCollectionMatchSubtask.task_id == task.id,
                IntelligenceCollectionMatchSubtask.match_id.in_(match_ids or [0]),
            )
        )
    ).scalars().all()
    subtask_map: Dict[int, IntelligenceCollectionMatchSubtask] = {int(x.match_id): x for x in subtask_rows}

    existing_rows = (
        await db.execute(
            select(IntelligenceCollectionItem).where(
                IntelligenceCollectionItem.match_id.in_(match_ids),
                IntelligenceCollectionItem.source_code.in_(sources),
                IntelligenceCollectionItem.intel_type.in_(intel_types),
            )
        )
    ).scalars().all()
    existing_map = {(x.match_id, x.source_code, x.intel_type): x for x in existing_rows}

    for match_id in match_ids:
        meta = match_meta.get(match_id, {"league_name": "-", "home_team": "-", "away_team": "-", "kickoff_time": None})
        match_success = 0
        match_failed = 0
        match_fail_reasons: Dict[str, int] = {}
        subtask = subtask_map.get(int(match_id))
        if subtask:
            subtask.status = "running"
            subtask.expected_count = expected_per_match
            subtask.started_at = subtask.started_at or datetime.utcnow()
            subtask.finished_at = None
            subtask.last_error = None
            _append_subtask_log(subtask, "info", f"match run started: match_id={match_id}")

        for source in sources:
            snapshot = snapshots.get(source, {"source_code": source, "error": "snapshot missing"})
            for intel_type in intel_types:
                cat = "prediction" if intel_type in PREDICTION_TYPES else "off_field"
                confidence = round(0.58 + ((match_id + len(source) + len(intel_type)) % 35) / 100, 2)
                cache_key = (match_id, source, cat)
                if cache_key in article_pick_cache:
                    article_pick = article_pick_cache[cache_key]
                else:
                    anchor_intel_type = "win_draw_lose" if cat == "prediction" else "injury"
                    article_pick = _fetch_match_article(
                        source_code=source,
                        source_snapshot=snapshot,
                        league_name=meta["league_name"],
                        home_team=meta["home_team"],
                        away_team=meta["away_team"],
                        intel_type=anchor_intel_type,
                        kickoff_time=meta.get("kickoff_time"),
                    )
                    article_pick_cache[cache_key] = article_pick
                    if source == "ttyingqiu":
                        dbg = article_pick.get("_debug", {}) if isinstance(article_pick, dict) else {}
                        tty_debug_rows.append(
                            {
                                "match_id": match_id,
                                "category": cat,
                                "candidate_count": int(dbg.get("candidate_count", 0) or 0),
                                "evaluated_count": int(dbg.get("evaluated_count", 0) or 0),
                                "soft_filtered": int(dbg.get("soft_filtered", 0) or 0),
                                "status_codes": dbg.get("status_codes", {}) or {},
                                "title_hit_keywords": dbg.get("title_hit_keywords", {}) or {},
                                "top_candidates": (dbg.get("top_candidates", []) or [])[:2],
                                "error": article_pick.get("error"),
                            }
                        )

                ai_result = await _ai_enhance_article(
                    match_id=match_id,
                    source_code=source,
                    intel_category=cat,
                    intel_type=intel_type,
                    league_name=meta["league_name"],
                    home_team=meta["home_team"],
                    away_team=meta["away_team"],
                    article_pick=article_pick,
                )

                if article_pick.get("matched"):
                    confidence = min(0.94, round(confidence + min(article_pick.get("match_score", 0) / 30.0, 0.18), 2))
                    ai_confidence = ai_result.get("confidence")
                    if ai_result.get("used") and ai_confidence is not None:
                        confidence = round(
                            min(0.97, max(0.35, confidence * 0.72 + _safe_float(ai_confidence, confidence) * 0.28)),
                            2,
                        )
                    match_success += 1
                else:
                    confidence = max(0.42, round(confidence - 0.14, 2))
                    failed += 1
                    match_failed += 1
                    reason = (article_pick.get("error") or "unknown").strip()[:120]
                    fail_reasons[reason] = fail_reasons.get(reason, 0) + 1
                    match_fail_reasons[reason] = match_fail_reasons.get(reason, 0) + 1

                content_raw = _build_content_raw(
                    snapshot,
                    article_pick,
                    ai_result,
                    match_id,
                    intel_type,
                    meta["league_name"],
                    meta["home_team"],
                    meta["away_team"],
                    meta.get("kickoff_time"),
                )
                decision = "accepted" if article_pick.get("matched") else "blocked"
                decision_reason = _sanitize_meta_text(
                    article_pick.get("quality_pass_reason") if article_pick.get("matched") else (article_pick.get("quality_block_reason") or article_pick.get("error")),
                    "n/a",
                )
                _append_log(
                    task,
                    "debug",
                    (
                        f"decision match_id={match_id}; source={source}; intel_type={intel_type}; decision={decision}; "
                        f"score={round(_safe_float(article_pick.get('quality_score', article_pick.get('match_score', 0)), 0.0), 2)}; "
                        f"reason={decision_reason}; ai_enhanced={(1 if ai_result.get('used') else 0)}; "
                        f"ai_provider={_sanitize_meta_text(ai_result.get('provider'), '-')}; "
                        f"ai_confidence={ai_result.get('confidence') if ai_result.get('confidence') is not None else '-'}"
                    ),
                )
                title = article_pick.get("article_title") if article_pick.get("matched") else f"{intel_type} - {source}"
                source_url = article_pick.get("article_url") if article_pick.get("matched") else SOURCE_URL_MAP.get(source, "")
                quality_fields = _build_structured_quality_fields(snapshot, article_pick)
                key = (match_id, source, intel_type)
                existed = existing_map.get(key)
                if existed:
                    existed.task_id = task.id
                    existed.intel_category = cat
                    existed.title = title
                    existed.content_raw = content_raw
                    existed.quality_status = quality_fields["quality_status"]
                    existed.quality_score = quality_fields["quality_score"]
                    existed.quality_pass_reason = quality_fields["quality_pass_reason"]
                    existed.quality_block_reason = quality_fields["quality_block_reason"]
                    existed.source_parser = quality_fields["source_parser"]
                    existed.article_url = quality_fields["article_url"] or source_url
                    existed.match_hit_terms_json = _json_dumps(quality_fields["match_hit_terms"])
                    existed.source_url = source_url
                    existed.published_at = now
                    existed.crawled_at = now
                    existed.confidence = confidence
                    updated += 1
                else:
                    item = IntelligenceCollectionItem(
                        task_id=task.id,
                        match_id=match_id,
                        source_code=source,
                        intel_category=cat,
                        intel_type=intel_type,
                        title=title,
                        content_raw=content_raw,
                        quality_status=quality_fields["quality_status"],
                        quality_score=quality_fields["quality_score"],
                        quality_pass_reason=quality_fields["quality_pass_reason"],
                        quality_block_reason=quality_fields["quality_block_reason"],
                        source_parser=quality_fields["source_parser"],
                        article_url=quality_fields["article_url"] or source_url,
                        match_hit_terms_json=_json_dumps(quality_fields["match_hit_terms"]),
                        source_url=source_url,
                        published_at=now,
                        crawled_at=now,
                        confidence=confidence,
                    )
                    db.add(item)
                    existing_map[key] = item
                    created += 1

        if subtask:
            subtask.item_count = match_success + match_failed
            subtask.success_count = match_success
            subtask.failed_count = match_failed
            subtask.candidate_count = expected_per_match
            subtask.parsed_count = expected_per_match
            subtask.matched_count = match_success
            subtask.accepted_count = match_success
            subtask.blocked_count = match_failed
            subtask.finished_at = datetime.utcnow()
            if match_failed <= 0:
                subtask.status = "success"
                _append_subtask_log(
                    subtask,
                    "success",
                    f"match run done: success={match_success}/{expected_per_match}",
                )
            elif match_success <= 0:
                subtask.status = "failed"
                top_reason = sorted(match_fail_reasons.items(), key=lambda x: x[1], reverse=True)[0][0] if match_fail_reasons else "all-failed"
                subtask.last_error = top_reason
                _append_subtask_log(
                    subtask,
                    "error",
                    f"match run failed: failed={match_failed}/{expected_per_match}; reason={top_reason}",
                )
            else:
                subtask.status = "partial"
                top_reason = sorted(match_fail_reasons.items(), key=lambda x: x[1], reverse=True)[0][0] if match_fail_reasons else ""
                subtask.last_error = top_reason or None
                _append_subtask_log(
                    subtask,
                    "warning",
                    f"match run partial: success={match_success}, failed={match_failed}, expected={expected_per_match}; reason={top_reason or '-'}",
                )

        # Persist per-match progress to avoid long in-memory transactions and reduce API polling timeout risk.
        await db.flush()
        await db.commit()
        await asyncio.sleep(0)

    if tty_debug_rows:
        status_counter: Dict[str, int] = {}
        hit_counter: Dict[str, int] = {}
        total_candidates = 0
        total_evaluated = 0
        for r in tty_debug_rows:
            total_candidates += int(r.get("candidate_count", 0) or 0)
            total_evaluated += int(r.get("evaluated_count", 0) or 0)
            for k, v in (r.get("status_codes") or {}).items():
                status_counter[str(k)] = status_counter.get(str(k), 0) + int(v or 0)
            for k, v in (r.get("title_hit_keywords") or {}).items():
                hit_counter[str(k)] = hit_counter.get(str(k), 0) + int(v or 0)
        avg_candidates = round(total_candidates / max(len(tty_debug_rows), 1), 2)
        avg_evaluated = round(total_evaluated / max(len(tty_debug_rows), 1), 2)
        top_status = dict(sorted(status_counter.items(), key=lambda x: x[1], reverse=True)[:5])
        top_hits = dict(sorted(hit_counter.items(), key=lambda x: x[1], reverse=True)[:5])
        total_soft_filtered = sum(int(r.get("soft_filtered", 0) or 0) for r in tty_debug_rows)
        _append_log(
            task,
            "debug",
            f"ttyingqiu debug summary: samples={len(tty_debug_rows)}, avg_candidates={avg_candidates}, avg_evaluated={avg_evaluated}, soft_filtered={total_soft_filtered}, status_codes={top_status}, title_hits={top_hits}",
        )
        for row in tty_debug_rows[:3]:
            _append_log(
                task,
                "debug",
                f"ttyingqiu debug sample: match={row['match_id']}, cat={row['category']}, candidates={row['candidate_count']}, evaluated={row['evaluated_count']}, error={row.get('error')}, top={row.get('top_candidates')}",
            )

    source_runtime: Dict[str, Any] = {}
    for src in sorted(set(sources)):
        stats = _source_stat(src)
        source_runtime[src] = {
            "requests": int(stats.get("requests", 0) or 0),
            "ok": int(stats.get("ok", 0) or 0),
            "timeout": int(stats.get("timeout", 0) or 0),
            "errors": int(stats.get("errors", 0) or 0),
            "retries": int(stats.get("retries", 0) or 0),
            "circuit_skipped": int(stats.get("circuit_skipped", 0) or 0),
            "consecutive_failures": int(stats.get("consecutive_failures", 0) or 0),
            "circuit_open_until": (
                stats.get("circuit_open_until").strftime("%Y-%m-%d %H:%M:%S")
                if stats.get("circuit_open_until")
                else None
            ),
        }
        _append_log(
            task,
            "debug",
            f"source_runtime source={src}; requests={source_runtime[src]['requests']}; ok={source_runtime[src]['ok']}; timeout={source_runtime[src]['timeout']}; errors={source_runtime[src]['errors']}; retries={source_runtime[src]['retries']}; circuit_skipped={source_runtime[src]['circuit_skipped']}",
        )

    if ai_runtime.get("enabled"):
        _append_log(
            task,
            "debug",
            (
                "ai_runtime summary: "
                f"provider={ai_runtime.get('provider')}; model={ai_runtime.get('model')}; "
                f"calls={ai_runtime.get('calls')}; success={ai_runtime.get('success')}; failed={ai_runtime.get('failed')}; "
                f"cache_hit={ai_runtime.get('cache_hit')}; skipped_unmatched={ai_runtime.get('skipped_unmatched')}; "
                f"skipped_low_quality={ai_runtime.get('skipped_low_quality')}; skipped_budget={ai_runtime.get('skipped_budget')}; "
                f"last_error={_sanitize_meta_text(ai_runtime.get('last_error'), '-')}"
            ),
        )

    return {
        "created": created,
        "updated": updated,
        "failed": failed,
        "fail_reasons": fail_reasons,
        "source_runtime": source_runtime,
        "ai_runtime": ai_runtime,
    }


@router.get("/sources")
async def get_sources(
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    source_codes = list(SOURCE_URL_MAP.keys())
    dedicated_parsers = {"500w", "ttyingqiu", "weibo", "tencent", "sina"}
    rows = (
        await db.execute(
            select(
                IntelligenceCollectionItem.source_code,
                func.count(IntelligenceCollectionItem.id),
            ).group_by(IntelligenceCollectionItem.source_code)
        )
    ).all()
    counter = {r[0]: int(r[1]) for r in rows}
    items = [
        {
            "code": code,
            "name": code,
            "url": SOURCE_URL_MAP.get(code, ""),
            "item_count": counter.get(code, 0),
            "parser_status": "dedicated" if code in dedicated_parsers else "generic_twohop",
        }
        for code in source_codes
    ]
    return _ok(items)


@router.get("/sources/health")
async def get_sources_health(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        await db.execute(
            select(IntelligenceCollectionItem).where(IntelligenceCollectionItem.crawled_at >= since)
        )
    ).scalars().all()
    if not rows:
        return _ok({"days": days, "items": []})

    agg: Dict[str, Dict[str, Any]] = {}
    for item in rows:
        src = str(item.source_code or "unknown")
        row = agg.setdefault(
            src,
            {
                "source": src,
                "total_items": 0,
                "accepted_count": 0,
                "blocked_count": 0,
                "source_view_count": 0,
                "quality_score_sum": 0.0,
                "confidence_sum": 0.0,
                "latest_crawled_at": None,
            },
        )
        row["total_items"] += 1
        row["confidence_sum"] += float(item.confidence or 0)
        q = _extract_quality_from_item(item)
        status = str(q.get("quality_status") or "source_view")
        if status == "accepted":
            row["accepted_count"] += 1
        elif status == "blocked":
            row["blocked_count"] += 1
        else:
            row["source_view_count"] += 1
        row["quality_score_sum"] += float(q.get("quality_score") or 0.0)
        crawled_at = item.crawled_at
        if crawled_at and (
            row["latest_crawled_at"] is None
            or crawled_at > row["latest_crawled_at"]
        ):
            row["latest_crawled_at"] = crawled_at

    items = []
    for src, row in agg.items():
        total = max(int(row["total_items"]), 1)
        items.append(
            {
                "source": src,
                "total_items": int(row["total_items"]),
                "accepted_count": int(row["accepted_count"]),
                "blocked_count": int(row["blocked_count"]),
                "source_view_count": int(row["source_view_count"]),
                "accepted_rate": round(float(row["accepted_count"]) / total, 4),
                "blocked_rate": round(float(row["blocked_count"]) / total, 4),
                "avg_quality_score": round(float(row["quality_score_sum"]) / total, 3),
                "avg_confidence": round(float(row["confidence_sum"]) / total, 3),
                "latest_crawled_at": row["latest_crawled_at"].isoformat() if row["latest_crawled_at"] else None,
            }
        )
    items.sort(key=lambda x: x["total_items"], reverse=True)
    return _ok({"days": days, "items": items})


@router.get("/settings/time-window")
async def get_time_window_settings(
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    try:
        settings = await _load_time_window_config(db)
        return _ok(settings)
    except Exception:
        logger.exception("[intelligence.collection.settings] get time-window settings failed, fallback to defaults")
        return _ok(
            _build_time_window_payload(
                DEFAULT_TIME_WINDOW_BEFORE_HOURS,
                DEFAULT_TIME_WINDOW_AFTER_HOURS,
                strict_mode=DEFAULT_TIME_WINDOW_STRICT_MODE,
                source_before="default-fallback",
                source_after="default-fallback",
                source_strict="default-fallback",
            ),
            "时间窗配置读取失败，已回退默认值",
        )


@router.put("/settings/time-window")
async def update_time_window_settings(
    payload: TimeWindowSettingsUpdateRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    settings = await _upsert_time_window_config(
        db,
        before_hours=payload.before_hours,
        after_hours=payload.after_hours,
        strict_mode=payload.strict_mode,
        admin_id=int(current_admin.get("id") or 0),
    )
    return _ok(settings, "时间窗配置已保存")


@router.get("/settings/network")
async def get_network_settings(
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    settings = await _load_network_settings(db)
    return _ok(settings)


@router.put("/settings/network")
async def update_network_settings(
    payload: NetworkSettingsUpdateRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    current = await _load_network_settings(db)
    merged = {
        "trust_env": current.get("trust_env"),
        "source_timeout_seconds": current.get("source_timeout_seconds"),
        "max_retry": current.get("max_retry"),
        "retry_backoff_ms": current.get("retry_backoff_ms"),
        "circuit_breaker_threshold": current.get("circuit_breaker_threshold"),
        "circuit_breaker_seconds": current.get("circuit_breaker_seconds"),
    }
    updates = payload.model_dump(exclude_none=True) if hasattr(payload, "model_dump") else payload.dict(exclude_none=True)
    merged.update(updates)
    settings = await _upsert_network_settings(
        db,
        payload=merged,
        admin_id=int(current_admin.get("id") or 0),
    )
    return _ok(settings, "网络配置已保存")


@router.get("/settings/source-rules")
async def get_source_rules(
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    settings = await _load_source_rules(db)
    return _ok(settings)


@router.put("/settings/source-rules")
async def update_source_rules(
    payload: SourceRulesUpdateRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    settings = await _upsert_source_rules(
        db,
        payload=payload.rules,
        admin_id=int(current_admin.get("id") or 0),
    )
    return _ok(settings, "来源规则已保存")


@router.get("/settings/quality-thresholds")
async def get_quality_thresholds(
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    settings = await _load_quality_thresholds(db)
    return _ok(settings)


@router.put("/settings/quality-thresholds")
async def update_quality_thresholds(
    payload: QualityThresholdsUpdateRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    settings = await _upsert_quality_thresholds(
        db,
        payload=payload.thresholds,
        admin_id=int(current_admin.get("id") or 0),
    )
    return _ok(settings, "质量阈值已保存")


@router.get("/settings/alias-dictionary")
async def get_alias_dictionary(
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    settings = await _load_alias_dictionary(db)
    return _ok(settings)


@router.put("/settings/alias-dictionary")
async def update_alias_dictionary(
    payload: AliasDictionaryUpdateRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    settings = await _upsert_alias_dictionary(
        db,
        payload=payload.dictionary,
        admin_id=int(current_admin.get("id") or 0),
    )
    return _ok(settings, "别名词典已保存")


@router.get("/matches")
async def get_jczq_matches(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    keyword: str = Query("", alias="search"),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    conditions = [
        or_(
            Match.data_source == "500w",
            Match.external_source == "500w",
        )
    ]
    home = aliased(Team)
    away = aliased(Team)

    if keyword:
        kw = f"%{keyword.strip()}%"
        conditions.append(
            or_(
                League.name.ilike(kw),
                home.name.ilike(kw),
                away.name.ilike(kw),
            )
        )

    stmt = (
        select(Match, League, home, away)
        .join(League, Match.league_id == League.id, isouter=True)
        .join(home, Match.home_team_id == home.id, isouter=True)
        .join(away, Match.away_team_id == away.id, isouter=True)
        .where(and_(*conditions))
        .order_by(Match.scheduled_kickoff.asc(), Match.id.asc())
    )
    rows = (await db.execute(stmt)).all()

    date_from_obj = None
    date_to_obj = None
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="date_from 格式错误，必须为 YYYY-MM-DD")
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="date_to 格式错误，必须为 YYYY-MM-DD")

    def _get_source_attrs(match_obj: Match) -> Dict[str, Any]:
        raw_attrs = match_obj.source_attributes
        if isinstance(raw_attrs, dict):
            return raw_attrs
        if isinstance(raw_attrs, str):
            try:
                parsed = json.loads(raw_attrs)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
        return {}

    def _resolve_schedule_date(match_obj: Match):
        attrs = _get_source_attrs(match_obj)
        src_date = attrs.get("source_schedule_date")
        if isinstance(src_date, str):
            try:
                return datetime.strptime(src_date, "%Y-%m-%d").date()
            except ValueError:
                pass
        return match_obj.match_date or (match_obj.scheduled_kickoff.date() if match_obj.scheduled_kickoff else None)

    filtered_rows = []
    for row in rows:
        m, _, _, _ = row
        schedule_day = _resolve_schedule_date(m)
        if not schedule_day:
            continue
        if date_from_obj and schedule_day < date_from_obj:
            continue
        if date_to_obj and schedule_day > date_to_obj:
            continue
        filtered_rows.append(row)

    total = len(filtered_rows)
    start = (page - 1) * size
    end = start + size
    paged_rows = filtered_rows[start:end]

    items: List[Dict[str, Any]] = []
    for m, l, h, a in paged_rows:
        attrs = _get_source_attrs(m)
        items.append(
            {
                "id": m.id,
                "league_name": l.name if l else "-",
                "home_team": h.name if h else "-",
                "away_team": a.name if a else "-",
                "kickoff_time": m.scheduled_kickoff.isoformat() if m.scheduled_kickoff else None,
                "status": (m.status.value if hasattr(m.status, "value") else str(m.status or "")),
                "schedule_date": attrs.get("source_schedule_date") or (m.match_date.isoformat() if m.match_date else None),
            }
        )
    logger.warning(
        "[intelligence.collection.matches] params search=%r date_from=%r date_to=%r page=%s size=%s matched_total=%s returned_ids=%s returned_schedule_dates=%s",
        keyword,
        date_from,
        date_to,
        page,
        size,
        total,
        [x["id"] for x in items],
        [x.get("schedule_date") for x in items],
    )
    return _ok({"items": items, "total": total, "page": page, "size": size})


@router.get("/graph/overview")
async def get_collection_graph_overview(
    days: int = Query(7, ge=1, le=90, description="统计最近N天采集数据"),
    limit: int = Query(800, ge=50, le=5000, description="最多参与建图的采集条数"),
    include_prediction: bool = Query(True, description="是否包含结果预测类情报"),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    since = datetime.utcnow() - timedelta(days=days)
    conditions = [IntelligenceCollectionItem.crawled_at >= since]
    if not include_prediction:
        conditions.append(IntelligenceCollectionItem.intel_category == "off_field")

    raw_items = (
        await db.execute(
            select(
                IntelligenceCollectionItem.match_id,
                IntelligenceCollectionItem.source_code,
                IntelligenceCollectionItem.intel_type,
                IntelligenceCollectionItem.intel_category,
            )
            .where(and_(*conditions))
            .order_by(IntelligenceCollectionItem.crawled_at.desc(), IntelligenceCollectionItem.id.desc())
            .limit(limit)
        )
    ).all()

    if not raw_items:
        return _ok(
            {
                "stats": {
                    "days": days,
                    "total_items": 0,
                    "total_nodes": 0,
                    "total_edges": 0,
                    "total_matches": 0,
                    "total_sources": 0,
                    "total_types": 0,
                },
                "categories": [
                    {"key": "match", "name": "比赛"},
                    {"key": "team", "name": "球队"},
                    {"key": "league", "name": "联赛"},
                    {"key": "source", "name": "来源"},
                    {"key": "intel_type", "name": "情报类型"},
                ],
                "nodes": [],
                "edges": [],
                "top_nodes": [],
                "network_metrics": {
                    "avg_degree": 0,
                    "density": 0,
                    "node_count": 0,
                    "edge_count": 0,
                },
                "source_stats": [],
                "type_stats": [],
            }
        )

    match_ids = sorted({int(x.match_id) for x in raw_items if x.match_id is not None})
    home = aliased(Team)
    away = aliased(Team)
    match_rows = (
        await db.execute(
            select(
                Match.id,
                Match.scheduled_kickoff,
                Match.status,
                League.id.label("league_id"),
                League.name.label("league_name"),
                home.id.label("home_team_id"),
                home.name.label("home_team_name"),
                away.id.label("away_team_id"),
                away.name.label("away_team_name"),
            )
            .join(League, Match.league_id == League.id, isouter=True)
            .join(home, Match.home_team_id == home.id, isouter=True)
            .join(away, Match.away_team_id == away.id, isouter=True)
            .where(Match.id.in_(match_ids))
        )
    ).all()

    match_map: Dict[int, Dict[str, Any]] = {}
    for row in match_rows:
        match_map[int(row.id)] = {
            "id": int(row.id),
            "kickoff": row.scheduled_kickoff.isoformat() if row.scheduled_kickoff else None,
            "status": row.status.value if hasattr(row.status, "value") else str(row.status or ""),
            "league_id": int(row.league_id) if row.league_id else None,
            "league_name": str(row.league_name or "未知联赛"),
            "home_team_id": int(row.home_team_id) if row.home_team_id else None,
            "home_team_name": str(row.home_team_name or "未知主队"),
            "away_team_id": int(row.away_team_id) if row.away_team_id else None,
            "away_team_name": str(row.away_team_name or "未知客队"),
        }

    node_map: Dict[str, Dict[str, Any]] = {}
    edge_map: Dict[str, Dict[str, Any]] = {}
    source_counter: Dict[str, int] = {}
    type_counter: Dict[str, int] = {}

    for x in raw_items:
        match_id = int(x.match_id)
        source_code = str(x.source_code or "unknown")
        intel_type = str(x.intel_type or "unknown")
        source_counter[source_code] = source_counter.get(source_code, 0) + 1
        type_counter[intel_type] = type_counter.get(intel_type, 0) + 1

        match_info = match_map.get(match_id, {})
        home_name = match_info.get("home_team_name", "未知主队")
        away_name = match_info.get("away_team_name", "未知客队")
        match_label = f"{home_name} vs {away_name}"

        match_node_id = _graph_node_id("match", match_id)
        source_node_id = _graph_node_id("source", source_code)
        type_node_id = _graph_node_id("intel_type", intel_type)

        _upsert_graph_node(
            node_map,
            node_id=match_node_id,
            label=match_label,
            node_type="match",
            category="比赛",
            base_size=26,
            value_inc=1,
            meta={
                "match_id": match_id,
                "kickoff": match_info.get("kickoff"),
                "status": match_info.get("status"),
                "league": match_info.get("league_name"),
            },
        )
        _upsert_graph_node(
            node_map,
            node_id=source_node_id,
            label=source_code,
            node_type="source",
            category="来源",
            base_size=20,
            value_inc=1,
            meta={"source_code": source_code},
        )
        _upsert_graph_node(
            node_map,
            node_id=type_node_id,
            label=intel_type,
            node_type="intel_type",
            category="情报类型",
            base_size=20,
            value_inc=1,
            meta={"intel_type": intel_type, "category": str(x.intel_category or "")},
        )

        _upsert_graph_edge(
            edge_map,
            source=source_node_id,
            target=match_node_id,
            relation="source_evidence",
            value_inc=1,
        )
        _upsert_graph_edge(
            edge_map,
            source=type_node_id,
            target=match_node_id,
            relation="type_evidence",
            value_inc=1,
        )

    # 构造稳定关系（联赛、主客队），每场仅一次
    for mid, m in match_map.items():
        match_node_id = _graph_node_id("match", mid)
        if m.get("league_id"):
            league_node_id = _graph_node_id("league", m["league_id"])
            _upsert_graph_node(
                node_map,
                node_id=league_node_id,
                label=m.get("league_name") or "未知联赛",
                node_type="league",
                category="联赛",
                base_size=18,
                value_inc=1,
                meta={"league_id": m.get("league_id")},
            )
            _upsert_graph_edge(
                edge_map,
                source=league_node_id,
                target=match_node_id,
                relation="league_of_match",
                value_inc=1,
            )

        if m.get("home_team_id"):
            home_node_id = _graph_node_id("team", m["home_team_id"])
            _upsert_graph_node(
                node_map,
                node_id=home_node_id,
                label=m.get("home_team_name") or "未知主队",
                node_type="team",
                category="球队",
                base_size=18,
                value_inc=1,
                meta={"team_id": m.get("home_team_id"), "role": "home"},
            )
            _upsert_graph_edge(
                edge_map,
                source=match_node_id,
                target=home_node_id,
                relation="home_team",
                value_inc=1,
            )

        if m.get("away_team_id"):
            away_node_id = _graph_node_id("team", m["away_team_id"])
            _upsert_graph_node(
                node_map,
                node_id=away_node_id,
                label=m.get("away_team_name") or "未知客队",
                node_type="team",
                category="球队",
                base_size=18,
                value_inc=1,
                meta={"team_id": m.get("away_team_id"), "role": "away"},
            )
            _upsert_graph_edge(
                edge_map,
                source=match_node_id,
                target=away_node_id,
                relation="away_team",
                value_inc=1,
            )

    nodes = list(node_map.values())
    edges = list(edge_map.values())

    degree_map: Dict[str, int] = {}
    for e in edges:
        src = str(e["source"])
        tgt = str(e["target"])
        w = int(e.get("count", 1))
        degree_map[src] = degree_map.get(src, 0) + w
        degree_map[tgt] = degree_map.get(tgt, 0) + w

    node_lookup = {x["id"]: x for x in nodes}
    top_nodes = []
    for node_id, deg in sorted(degree_map.items(), key=lambda kv: kv[1], reverse=True)[:15]:
        n = node_lookup.get(node_id)
        if not n:
            continue
        top_nodes.append(
            {
                "id": node_id,
                "name": n.get("name"),
                "type": n.get("type"),
                "degree": deg,
                "value": n.get("value", 0),
            }
        )

    node_count = len(nodes)
    edge_count = len(edges)
    avg_degree = round((sum(degree_map.values()) / node_count), 2) if node_count else 0
    density = (
        round((2 * edge_count) / (node_count * (node_count - 1)), 4)
        if node_count > 1
        else 0
    )

    source_stats = [
        {"source": k, "count": v}
        for k, v in sorted(source_counter.items(), key=lambda kv: kv[1], reverse=True)
    ]
    type_stats = [
        {"intel_type": k, "count": v}
        for k, v in sorted(type_counter.items(), key=lambda kv: kv[1], reverse=True)
    ]

    return _ok(
        {
            "stats": {
                "days": days,
                "total_items": len(raw_items),
                "total_nodes": node_count,
                "total_edges": edge_count,
                "total_matches": len(match_ids),
                "total_sources": len(source_counter),
                "total_types": len(type_counter),
            },
            "categories": [
                {"key": "match", "name": "比赛"},
                {"key": "team", "name": "球队"},
                {"key": "league", "name": "联赛"},
                {"key": "source", "name": "来源"},
                {"key": "intel_type", "name": "情报类型"},
            ],
            "nodes": nodes,
            "edges": edges,
            "top_nodes": top_nodes,
            "network_metrics": {
                "avg_degree": avg_degree,
                "density": density,
                "node_count": node_count,
                "edge_count": edge_count,
            },
            "source_stats": source_stats,
            "type_stats": type_stats,
        }
    )


@router.post("/tasks")
async def create_collection_task(
    payload: TaskCreateRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    if not payload.match_ids:
        raise HTTPException(status_code=400, detail="match_ids is required")
    if not payload.sources:
        raise HTTPException(status_code=400, detail="sources is required")
    if not payload.intel_types:
        raise HTTPException(status_code=400, detail="intel_types is required")
    logger.warning(
        "[intelligence.collection.tasks.create] request mode=%s match_ids_count=%s match_ids=%s sources=%s intel_types=%s offset_hours=%s by_admin=%s",
        payload.mode,
        len(payload.match_ids or []),
        payload.match_ids,
        payload.sources,
        payload.intel_types,
        payload.offset_hours,
        current_admin.get("id"),
    )

    mode = payload.mode if payload.mode in {"immediate", "scheduled"} else "immediate"
    request_payload = {
        "mode": mode,
        "match_ids": payload.match_ids,
        "sources": payload.sources,
        "intel_types": payload.intel_types,
        "offset_hours": payload.offset_hours or [],
    }
    config_snapshot = {
        "time_window": await _load_time_window_config(db),
        "network": await _load_network_settings(db),
        "quality_thresholds": await _load_quality_thresholds(db),
    }
    task = IntelligenceCollectionTask(
        task_uuid=uuid.uuid4().hex,
        task_name=f"intelligence-collect-{datetime.utcnow().strftime('%m%d-%H%M%S')}",
        mode=mode,
        status="pending",
        match_ids_json=_json_dumps(payload.match_ids),
        sources_json=_json_dumps(payload.sources),
        intel_types_json=_json_dumps(payload.intel_types),
        offset_hours_json=_json_dumps(payload.offset_hours or []),
        request_payload_json=_json_dumps(request_payload),
        config_snapshot_json=_json_dumps(config_snapshot),
        success_rate=0.0,
        queue_job_id=None,
        created_by=int(current_admin.get("id") or 0),
        started_at=None,
        planned_at=datetime.utcnow() if mode == "immediate" else datetime.utcnow() + timedelta(minutes=5),
    )
    _append_log(task, "info", "task created")
    _append_log(task, "debug", f"request_payload={_sanitize_meta_text(_json_dumps(request_payload))}")
    _append_log(task, "debug", f"config_snapshot={_sanitize_meta_text(_json_dumps(config_snapshot))}")
    db.add(task)
    await db.flush()
    desired_total = len(payload.match_ids) * len(payload.sources) * len(payload.intel_types)
    task.total_count = desired_total
    await _ensure_task_match_subtasks(
        db=db,
        task=task,
        match_ids=payload.match_ids,
        sources=payload.sources,
        intel_types=payload.intel_types,
    )
    await db.commit()
    await db.refresh(task)
    planned_at = task.planned_at or datetime.utcnow()
    delay_seconds = max((planned_at - datetime.utcnow()).total_seconds(), 0.0)
    enqueue_result = _enqueue_task_execution(
        task,
        trigger="collect",
        delay_seconds=delay_seconds,
    )
    accepted = bool(enqueue_result["accepted"])
    if mode == "scheduled":
        if accepted:
            _append_log(
                task,
                "info",
                f"scheduled task queued; estimated_start={planned_at.strftime('%Y-%m-%d %H:%M:%S')}",
            )
    else:
        if accepted:
            _append_log(task, "info", "immediate task queued")
    if not accepted:
        task.status = "failed"
        task.finished_at = datetime.utcnow()
        task.error_message = enqueue_result["error"] or "queue submit failed"
        _append_log(task, "error", f"task enqueue failed: {task.error_message}")
    await db.commit()
    await db.refresh(task)
    logger.warning(
        "[intelligence.collection.tasks.create] created task_id=%s status=%s total_count=%s accepted=%s",
        task.id,
        task.status,
        task.total_count,
        accepted,
    )
    task_data = _task_to_dict(task)
    task_data.update(
        {
            "accepted": bool(accepted),
            "queue_job_id": task.queue_job_id,
            "estimated_start": planned_at.isoformat() if planned_at else None,
        }
    )
    return _ok(task_data, "task accepted" if accepted else "task enqueue failed")


@router.post("/schedules")
async def create_collection_schedule(
    payload: TaskCreateRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    payload.mode = "scheduled"
    return await create_collection_task(payload=payload, db=db, current_admin=current_admin)


@router.get("/tasks")
async def list_collection_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    status: Optional[str] = Query(None),
    mode: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    await _dispatch_due_pending_tasks(db)
    await _recover_active_tasks_from_queue(db)
    conditions = []
    if status:
        conditions.append(IntelligenceCollectionTask.status == status)
    if mode:
        conditions.append(IntelligenceCollectionTask.mode == mode)

    stmt = select(IntelligenceCollectionTask).where(*conditions).order_by(IntelligenceCollectionTask.created_at.desc())
    total_stmt = select(func.count(IntelligenceCollectionTask.id)).where(*conditions)
    total = int((await db.execute(total_stmt)).scalar() or 0)
    rows = (await db.execute(stmt.offset((page - 1) * size).limit(size))).scalars().all()
    progress_stats = await _collect_task_progress_stats(db, rows)
    logger.warning(
        "[intelligence.collection.tasks.list] params status=%r mode=%r page=%s size=%s total=%s returned_ids=%s",
        status,
        mode,
        page,
        size,
        total,
        [x.id for x in rows],
    )
    items = []
    for task in rows:
        task_data = _task_to_dict(task)
        task_data.update(progress_stats.get(task.id, {}))
        items.append(task_data)
    return _ok({"items": items, "total": total, "page": page, "size": size})


@router.get("/tasks/{task_id}")
async def get_collection_task(
    task_id: int,
    lightweight: bool = Query(False),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    await _dispatch_due_pending_tasks(db)
    task = await db.get(IntelligenceCollectionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    await _recover_active_tasks_from_queue(db, focus_tasks=[task])
    await db.refresh(task)
    data = _task_to_dict(task)
    if lightweight:
        data["polling_mode"] = "lightweight"
        return _ok(data)

    progress_stats = await _collect_task_progress_stats(db, [task])
    data.update(progress_stats.get(task.id, {}))
    return _ok(data)


@router.get("/tasks/{task_id}/subtasks")
async def get_collection_task_subtasks(
    task_id: int,
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    task = await db.get(IntelligenceCollectionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    stmt = select(IntelligenceCollectionMatchSubtask).where(
        IntelligenceCollectionMatchSubtask.task_id == task_id
    )
    if status:
        stmt = stmt.where(IntelligenceCollectionMatchSubtask.status == status)
    rows = (await db.execute(stmt.order_by(IntelligenceCollectionMatchSubtask.match_id.asc()))).scalars().all()
    return _ok({"task_id": task_id, "items": [_subtask_to_dict(x) for x in rows], "total": len(rows)})


@router.get("/tasks/{task_id}/logs")
async def get_collection_task_logs(
    task_id: int,
    match_id: Optional[int] = Query(None),
    source: Optional[str] = Query(None),
    decision: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    task = await db.get(IntelligenceCollectionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    logs = _json_loads(task.logs_json, [])
    if match_id is not None:
        logs = [x for x in logs if f"match_id={match_id}" in str(x.get("message", ""))]
    if source:
        source_token = f"source={source}".lower()
        logs = [x for x in logs if source_token in str(x.get("message", "")).lower()]
    if decision:
        decision_token = f"decision={decision}".lower()
        logs = [x for x in logs if decision_token in str(x.get("message", "")).lower()]
    if level:
        logs = [x for x in logs if str(x.get("level", "")).lower() == str(level).lower()]
    if stage:
        stage_token = f"stage={stage}".lower()
        logs = [x for x in logs if stage_token in str(x.get("message", "")).lower()]
    return _ok({"task_id": task_id, "logs": logs, "total": len(logs)})


@router.get("/tasks/{task_id}/failure-summary")
async def get_collection_task_failure_summary(
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    task = await db.get(IntelligenceCollectionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    await _recover_active_tasks_from_queue(db, focus_tasks=[task])
    await db.refresh(task)
    summary = await _build_task_failure_summary(db, task)
    return _ok(summary)


@router.get("/tasks/{task_id}/events")
async def get_collection_task_events(
    task_id: int,
    request: Request,
    interval_ms: int = Query(
        TASK_EVENT_DEFAULT_INTERVAL_MS,
        ge=TASK_EVENT_MIN_INTERVAL_MS,
        le=TASK_EVENT_MAX_INTERVAL_MS,
    ),
    max_duration_seconds: int = Query(
        TASK_EVENT_DEFAULT_MAX_DURATION_SECONDS,
        ge=TASK_EVENT_MIN_DURATION_SECONDS,
        le=TASK_EVENT_MAX_DURATION_SECONDS,
    ),
    include_match_progress: bool = Query(False),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    task = await db.get(IntelligenceCollectionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    async def _event_stream():
        interval_seconds = max(float(interval_ms) / 1000.0, TASK_EVENT_MIN_INTERVAL_MS / 1000.0)
        keepalive_seconds = max(interval_seconds * 3, 8.0)
        stream_start = datetime.utcnow()
        last_emit_at = stream_start
        last_fingerprint = ""
        event_id = 1

        while True:
            if await request.is_disconnected():
                break

            if (datetime.utcnow() - stream_start).total_seconds() >= float(max_duration_seconds):
                timeout_payload = {
                    "task_id": task_id,
                    "event": "timeout",
                    "message": "task events stream max duration reached",
                    "generated_at": datetime.utcnow().isoformat(),
                }
                yield _format_sse_message("timeout", timeout_payload, event_id=event_id)
                break

            try:
                await _recover_active_tasks_from_queue(db, focus_tasks=[task])
                await db.refresh(task)
                payload = await _build_task_events_payload(
                    db,
                    task,
                    include_match_progress=include_match_progress,
                )
            except Exception as exc:
                logger.exception("[intelligence.collection.task.events] stream failed task_id=%s", task_id)
                error_payload = {
                    "task_id": task_id,
                    "event": "error",
                    "message": _sanitize_meta_text(exc, "stream failure"),
                    "generated_at": datetime.utcnow().isoformat(),
                }
                yield _format_sse_message("error", error_payload, event_id=event_id)
                break

            fingerprint = _build_task_events_fingerprint(payload)
            now = datetime.utcnow()
            if fingerprint != last_fingerprint:
                last_fingerprint = fingerprint
                last_emit_at = now
                yield _format_sse_message("progress", payload, event_id=event_id)
                event_id += 1
            elif (now - last_emit_at).total_seconds() >= keepalive_seconds:
                last_emit_at = now
                yield ": keep-alive\n\n"

            if payload.get("terminal"):
                break

            await asyncio.sleep(interval_seconds)

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/tasks/{task_id}/retry")
async def retry_collection_task(
    task_id: int,
    payload: Optional[TaskRetryRequest] = Body(default=None),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    task = await db.get(IntelligenceCollectionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    await _recover_active_tasks_from_queue(db, focus_tasks=[task])
    await db.refresh(task)
    if str(task.status or "").strip().lower() == "running":
        raise HTTPException(status_code=409, detail="task is already running")
    if task.queue_job_id and _is_queue_job_active(task.queue_job_id):
        raise HTTPException(status_code=409, detail="task queue job is still active")

    saved_match_ids = [int(x) for x in _json_loads(task.match_ids_json, []) if str(x).isdigit()]
    saved_sources = [str(x) for x in _json_loads(task.sources_json, []) if str(x).strip()]
    saved_intel_types = [str(x) for x in _json_loads(task.intel_types_json, []) if str(x).strip()]
    retry_match_ids = [int(x) for x in (payload.match_ids if payload else []) if str(x).isdigit()] or saved_match_ids
    retry_sources = [str(x) for x in (payload.sources if payload else []) if str(x).strip()] or saved_sources
    retry_intel_types = [str(x) for x in (payload.intel_types if payload else []) if str(x).strip()] or saved_intel_types
    if not retry_match_ids or not retry_sources or not retry_intel_types:
        raise HTTPException(status_code=400, detail="retry scope is empty")

    task.retry_count += 1
    task.status = "pending"
    task.started_at = None
    task.finished_at = None
    task.error_message = None
    task.success_rate = 0.0
    task.queue_job_id = None
    task.request_payload_json = _json_dumps(
        {
            "mode": task.mode,
            "match_ids": retry_match_ids,
            "sources": retry_sources,
            "intel_types": retry_intel_types,
            "offset_hours": _json_loads(task.offset_hours_json, []),
            "action": "retry",
            "retry_count": task.retry_count,
        }
    )
    _append_log(
        task,
        "info",
        (
            f"retry triggered: #{task.retry_count}; "
            f"scope(match_ids={retry_match_ids}, sources={retry_sources}, intel_types={retry_intel_types})"
        ),
    )
    await _reset_task_match_subtasks(db, task.id, match_ids=retry_match_ids)
    await db.commit()
    await db.refresh(task)
    enqueue_result = _enqueue_task_execution(
        task,
        trigger="retry",
        delay_seconds=0.0,
        run_match_ids=retry_match_ids,
        run_sources=retry_sources,
        run_intel_types=retry_intel_types,
    )
    accepted = bool(enqueue_result["accepted"])
    if not accepted:
        task.status = "failed"
        task.finished_at = datetime.utcnow()
        task.error_message = enqueue_result["error"] or "retry queue submit failed"
        _append_log(task, "error", f"retry queue submit failed: {task.error_message}")
    await db.commit()
    await db.refresh(task)
    task_data = _task_to_dict(task)
    task_data["retry_scope"] = {
        "match_ids": retry_match_ids,
        "sources": retry_sources,
        "intel_types": retry_intel_types,
    }
    task_data["accepted"] = bool(accepted)
    task_data["queue_job_id"] = task.queue_job_id
    task_data["estimated_start"] = datetime.utcnow().isoformat()
    return _ok(task_data, "retry accepted" if accepted else "retry enqueue failed")


@router.post("/tasks/{task_id}/cancel")
async def cancel_collection_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    task = await db.get(IntelligenceCollectionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    if task.status in TASK_TERMINAL_STATUSES:
        return _ok(_task_to_dict(task), "task already finished")
    if task.queue_job_id:
        try:
            task_queue_app.control.revoke(task.queue_job_id, terminate=False)
            _append_log(task, "warning", f"queue job revoked: {task.queue_job_id}")
        except Exception as exc:
            logger.warning("[intelligence.collection.tasks.cancel] revoke failed task_id=%s err=%s", task_id, exc)
            _append_log(task, "warning", f"queue revoke failed: {exc}")
    task.status = "cancelled"
    task.finished_at = datetime.utcnow()
    _append_log(task, "warning", "task cancelled")
    subtask_rows = (
        await db.execute(
            select(IntelligenceCollectionMatchSubtask).where(
                IntelligenceCollectionMatchSubtask.task_id == task_id
            )
        )
    ).scalars().all()
    for row in subtask_rows:
        if row.status not in {"success", "failed", "partial"}:
            row.status = "cancelled"
        row.finished_at = row.finished_at or datetime.utcnow()
        _append_subtask_log(row, "warning", "cancelled by task cancel action")
    await db.commit()
    await db.refresh(task)
    return _ok(_task_to_dict(task), "task cancelled")


@router.get("/matches/{match_id}/items")
async def get_match_items(
    match_id: int,
    category: Optional[str] = Query(None),
    quality_status: Optional[str] = Query(None),
    dedupe: bool = Query(False),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    stmt = select(IntelligenceCollectionItem).where(IntelligenceCollectionItem.match_id == match_id)
    if category in {"off_field", "prediction"}:
        stmt = stmt.where(IntelligenceCollectionItem.intel_category == category)
    rows = (
        await db.execute(stmt.order_by(IntelligenceCollectionItem.crawled_at.desc()).limit(limit))
    ).scalars().all()

    normalized_quality_status = str(quality_status or "").strip().lower()
    dedupe_seen: set = set()
    items = []
    for x in rows:
        quality_meta = _extract_quality_from_item(x)
        if normalized_quality_status and quality_meta["quality_status"] != normalized_quality_status:
            continue
        article_url = _sanitize_meta_text(quality_meta.get("article_url"), "")
        dedupe_key = f"{x.source_code}|{article_url or x.source_url or ''}|{x.title or ''}"
        if dedupe and dedupe_key in dedupe_seen:
            continue
        dedupe_seen.add(dedupe_key)
        published_parse_status = "missing"
        if x.published_at:
            published_parse_status = "ok"
        elif article_url:
            published_parse_status = "parsed-from-article-url-missing"
        items.append(
            {
                "id": x.id,
                "task_id": x.task_id,
                "match_id": x.match_id,
                "source_code": x.source_code,
                "intel_category": x.intel_category,
                "intel_type": x.intel_type,
                "title": x.title,
                "content_raw": x.content_raw,
                "source_url": x.source_url,
                "published_at": x.published_at.isoformat() if x.published_at else None,
                "crawled_at": x.crawled_at.isoformat() if x.crawled_at else None,
                "confidence": x.confidence,
                "quality_score": quality_meta["quality_score"],
                "quality_pass_reason": quality_meta["quality_pass_reason"],
                "quality_block_reason": quality_meta["quality_block_reason"],
                "source_parser": quality_meta["source_parser"],
                "match_hit_terms": quality_meta["match_hit_terms"],
                "is_article_page": quality_meta["is_article_page"],
                "quality_status": quality_meta["quality_status"],
                "ai_enhanced": quality_meta.get("ai_enhanced"),
                "ai_provider": quality_meta.get("ai_provider"),
                "ai_model": quality_meta.get("ai_model"),
                "ai_summary": quality_meta.get("ai_summary"),
                "ai_viewpoint": quality_meta.get("ai_viewpoint"),
                "ai_risk_level": quality_meta.get("ai_risk_level"),
                "ai_confidence": quality_meta.get("ai_confidence"),
                "ai_reason": quality_meta.get("ai_reason"),
                "article_url": article_url or x.source_url,
                "published_at_parse_status": published_parse_status,
            }
        )
    logger.warning(
        "[intelligence.collection.match.items] params match_id=%s category=%r quality_status=%r dedupe=%s limit=%s returned_total=%s returned_item_ids=%s",
        match_id,
        category,
        quality_status,
        dedupe,
        limit,
        len(items),
        [x.get("id") for x in items[:20]],
    )
    return _ok({"match_id": match_id, "items": items, "total": len(items)})


async def _debug_generic_source_capture(
    payload: MatchCandidatesDebugRequest,
    db: AsyncSession,
) -> Dict[str, Any]:
    source = (payload.source or "").strip().lower()
    if source not in SOURCE_URL_MAP:
        raise HTTPException(status_code=400, detail=f"unsupported source: {source}")

    home = aliased(Team)
    away = aliased(Team)
    row = (
        await db.execute(
            select(Match.id, League.name, home.name, away.name, Match.scheduled_kickoff, Match.match_date)
            .join(League, Match.league_id == League.id, isouter=True)
            .join(home, Match.home_team_id == home.id, isouter=True)
            .join(away, Match.away_team_id == away.id, isouter=True)
            .where(Match.id == payload.match_id)
        )
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="match not found")

    _, league_name, home_name, away_name, scheduled_kickoff, match_date = row
    kickoff_time = scheduled_kickoff
    if not kickoff_time and match_date:
        kickoff_time = datetime(match_date.year, match_date.month, match_date.day, 12, 0, 0)
    time_window_config = await _load_time_window_config(db)
    time_window_before_hours = int(time_window_config.get("before_hours", DEFAULT_TIME_WINDOW_BEFORE_HOURS))
    time_window_after_hours = int(time_window_config.get("after_hours", DEFAULT_TIME_WINDOW_AFTER_HOURS))

    def _norm(s: str) -> str:
        return re.sub(r"\s+", " ", (s or "").strip().lower())

    def _clean(s: str) -> str:
        txt = re.sub(r"<script[^>]*>.*?</script>", " ", s or "", flags=re.I | re.S)
        txt = re.sub(r"<style[^>]*>.*?</style>", " ", txt, flags=re.I | re.S)
        txt = re.sub(r"<[^>]+>", " ", txt)
        return re.sub(r"\s+", " ", unescape(txt)).strip()

    def _title(html: str) -> str:
        m = re.search(r"<title[^>]*>(.*?)</title>", html or "", flags=re.I | re.S)
        return _clean(m.group(1)) if m else ""

    def _team_variants(raw: str) -> List[str]:
        base = (raw or "").strip()
        if not base:
            return []
        outs = {base}
        pairs = [
            ("联", "聯"), ("国", "國"), ("兰", "蘭"), ("马", "馬"), ("罗", "羅"), ("亚", "亞"),
            ("萨", "薩"), ("维", "維"), ("纳", "納"), ("尔", "爾"), ("顿", "頓"), ("乌", "烏"),
        ]
        t = base
        for a, b in pairs:
            t = t.replace(a, b)
        outs.add(t)
        s = base
        for a, b in pairs:
            s = s.replace(b, a)
        outs.add(s)
        latin = re.sub(r"[^a-zA-Z\\s]", " ", base).strip().lower()
        if latin:
            parts = [p for p in latin.split() if p and p not in {"fc", "cf", "sc", "club"}]
            if parts:
                outs.add(" ".join(parts))
            if len(parts) >= 2:
                outs.add("".join(p[0] for p in parts))
            outs.add(" ".join(parts).replace("united", "utd"))
            outs.add(" ".join(parts).replace("saint", "st"))
        return [x for x in outs if x]

    def _parse_datetime_candidates(text: str) -> List[datetime]:
        raw = unescape(text or "")
        if not raw:
            return []
        norm = (
            raw.replace("年", "-")
            .replace("月", "-")
            .replace("日", " ")
            .replace("时", ":")
            .replace("分", " ")
            .replace("T", " ")
            .replace("/", "-")
            .replace(".", "-")
        )
        results: List[datetime] = []
        seen = set()

        def _add_dt(year: int, month: int, day: int, hour: int = 0, minute: int = 0):
            try:
                dt = datetime(year, month, day, hour, minute)
            except Exception:
                return
            key = dt.strftime("%Y-%m-%d %H:%M")
            if key in seen:
                return
            seen.add(key)
            results.append(dt)

        for m in re.finditer(
            r"(?<!\d)(20\d{2})-(\d{1,2})-(\d{1,2})(?:\s+(\d{1,2})[:：](\d{1,2}))?(?!\d)",
            norm,
        ):
            _add_dt(
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
                int(m.group(4) or 0),
                int(m.group(5) or 0),
            )
        for m in re.finditer(r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?:([01]\d|2[0-3])([0-5]\d))?(?!\d)", norm):
            _add_dt(
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
                int(m.group(4) or 0),
                int(m.group(5) or 0),
            )
        if kickoff_time:
            base_year = kickoff_time.year
            for m in re.finditer(r"(?<!\d)(\d{1,2})-(\d{1,2})(?:\s+(\d{1,2})[:：](\d{1,2}))?(?!\d)", norm):
                mo = int(m.group(1))
                d = int(m.group(2))
                hh = int(m.group(3) or 0)
                mm = int(m.group(4) or 0)
                candidates = []
                for y in [base_year - 1, base_year, base_year + 1]:
                    try:
                        candidates.append(datetime(y, mo, d, hh, mm))
                    except Exception:
                        continue
                if candidates:
                    best = min(candidates, key=lambda x: abs((x - kickoff_time).total_seconds()))
                    _add_dt(best.year, best.month, best.day, best.hour, best.minute)
        return results

    def _best_publish_time(url: str, title: str, excerpt: str) -> Optional[datetime]:
        all_dt: List[datetime] = []
        for text in [url, title, excerpt]:
            all_dt.extend(_parse_datetime_candidates(text))
        if not all_dt:
            return None
        if kickoff_time:
            return min(all_dt, key=lambda x: abs((x - kickoff_time).total_seconds()))
        return sorted(all_dt)[0]

    def _time_window_check(publish_time: Optional[datetime]) -> tuple[bool, str]:
        if not kickoff_time:
            return False, "no-kickoff-time"
        if not publish_time:
            return False, "no-publish-time"
        lower = kickoff_time - timedelta(hours=time_window_before_hours)
        upper = kickoff_time + timedelta(hours=time_window_after_hours)
        if lower <= publish_time <= upper:
            return True, "time-window-pass"
        return (
            False,
            (
                "time-window-out "
                f"publish={publish_time.strftime('%Y-%m-%d %H:%M')} "
                f"window={lower.strftime('%Y-%m-%d %H:%M')}~{upper.strftime('%Y-%m-%d %H:%M')}"
            ),
        )

    source_url = SOURCE_URL_MAP[source]
    session = requests.Session()
    session.trust_env = _normalize_bool(network_settings.get("trust_env"), False)
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
    )

    keyword_bag = []
    for x in [league_name, home_name, away_name]:
        keyword_bag.extend([_norm(v) for v in _team_variants(x or "") if _norm(v)])
    keyword_bag = list(dict.fromkeys([x for x in keyword_bag if len(x) >= 2]))[:40]
    base_host = (urlparse(source_url).netloc or "").lower()
    source_host_rules = {
        "500w": ["500.com"],
        "sina": ["sports.sina.com.cn"],
        "tencent": ["qq.com"],
        "weibo": ["weibo.com", "sina.com.cn"],
        "netease": ["163.com"],
        "sohu": ["sohu.com"],
        "cctv": ["cctv.com"],
        "wechat": ["weixin.qq.com", "qq.com"],
        "toutiao": ["toutiao.com"],
        "ttyingqiu": ["ttyingqiu.com"],
    }
    custom_allow_suffix = (
        (source_rules.get(source, {}) or {}).get("allowed_host_suffix")
        if isinstance(source_rules, dict)
        else []
    )
    if isinstance(custom_allow_suffix, list) and custom_allow_suffix:
        source_host_rules[source] = list(
            {
                *source_host_rules.get(source, []),
                *[str(x).strip().lower() for x in custom_allow_suffix if str(x).strip()],
            }
        )

    def _host_allowed(candidate_url: str) -> bool:
        host = (urlparse(candidate_url).netloc or "").lower()
        if not host:
            return False
        if host == base_host or host.endswith("." + base_host):
            return True
        for suffix in source_host_rules.get(source, []):
            if host == suffix or host.endswith("." + suffix):
                return True
        return False

    try:
        seed_resp = session.get(source_url, timeout=_debug_timeout(source), allow_redirects=True)
        seed_html = seed_resp.text or ""
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"seed fetch failed: {e}")

    links: List[Dict[str, Any]] = []
    for href, inner in re.findall(r"<a[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", seed_html, flags=re.I | re.S):
        full = urljoin(source_url, href.strip())
        if not full.startswith("http"):
            continue
        if not _host_allowed(full):
            continue
        anchor = _clean(inner)[:140]
        if not anchor:
            continue
        links.append({"url": full, "anchor": anchor})

    dedup: Dict[str, Dict[str, Any]] = {}
    for x in links:
        dedup.setdefault(x["url"], x)
    candidates = list(dedup.values())[:120]

    status_codes: Dict[str, int] = {}
    evaluated: List[Dict[str, Any]] = []
    eval_limit = min(max(payload.max_candidates * 2, 20), 120)
    for cand in candidates[:eval_limit]:
        url = cand["url"]
        try:
            resp = session.get(url, timeout=_debug_timeout(source), allow_redirects=True)
            html = resp.text or ""
            code = int(resp.status_code or 0)
        except Exception:
            html = ""
            code = -1
        status_codes[str(code)] = status_codes.get(str(code), 0) + 1
        title = _title(html) or cand.get("anchor", "")
        excerpt = _clean(html)[:320]
        text_bag = _norm(f"{title} {excerpt} {url}")
        hits = [k for k in keyword_bag if k in text_bag]
        detail_hint = 0.4 if any(x in url.lower() for x in ("/news/", "/article", "/a/", "/doc-", ".shtml", "/detail/")) else 0.0
        score = round(0.58 * len(hits) + detail_hint + (0.15 if code == 200 else -0.2), 2)
        publish_time = _best_publish_time(url, title, excerpt)
        time_pass, time_reason = _time_window_check(publish_time)
        if not time_pass:
            score = round(score - 1.4, 2)
        evaluated.append(
            {
                "url": url,
                "status_code": code,
                "title": title[:140],
                "score": score,
                "hit_terms": hits[:8],
                "publish_time": publish_time.strftime("%Y-%m-%d %H:%M:%S") if publish_time else None,
                "time_window_pass": time_pass,
                "time_window_reason": time_reason,
                "filter_reason": "" if (time_pass and len(hits) >= 1) else ("keyword-miss" if len(hits) < 1 else "time-window-block"),
            }
        )
    evaluated.sort(key=lambda x: ((1 if x.get("time_window_pass") else 0), x.get("score", 0)), reverse=True)

    return _ok(
        {
            "match_id": payload.match_id,
            "source": source,
            "intel_type": payload.intel_type,
            "match": {
                "league_name": league_name or "-",
                "home_team": home_name or "-",
                "away_team": away_name or "-",
                "kickoff_time": kickoff_time.isoformat() if kickoff_time else None,
            },
            "seed_url": source_url,
            "time_window": {
                "before_hours": time_window_before_hours,
                "after_hours": time_window_after_hours,
                "bounds_label": f"-{time_window_before_hours}h ~ +{time_window_after_hours}h",
            },
            "candidate_count": len(candidates),
            "evaluated_count": len(evaluated),
            "status_codes": status_codes,
            "top_candidates": evaluated[: payload.max_candidates],
        }
    )


@router.post("/debug/match-candidates")
async def debug_match_candidates(
    payload: MatchCandidatesDebugRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    source = (payload.source or "").strip().lower()
    if source == "ttyingqiu":
        tty_payload = TtyingqiuDebugRequest(match_id=payload.match_id, intel_type=payload.intel_type)
        return await debug_ttyingqiu_capture(tty_payload, db, current_admin)
    return await _debug_generic_source_capture(payload, db)


@router.post("/debug/replay")
async def debug_replay(
    payload: DebugReplayRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    req = MatchCandidatesDebugRequest(
        match_id=payload.match_id,
        source=payload.source,
        intel_type=payload.intel_type,
        max_candidates=payload.max_candidates,
    )
    result = await debug_match_candidates(req, db, current_admin)
    return _ok(
        {
            "mode": "replay",
            "request": {
                "match_id": payload.match_id,
                "source": payload.source,
                "intel_type": payload.intel_type,
                "max_candidates": payload.max_candidates,
            },
            "result": result.get("data") if isinstance(result, dict) else result,
        }
    )


@router.post("/debug/ttyingqiu")
async def debug_ttyingqiu_capture(
    payload: TtyingqiuDebugRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    home = aliased(Team)
    away = aliased(Team)
    row = (
        await db.execute(
            select(Match.id, League.name, home.name, away.name)
            .join(League, Match.league_id == League.id, isouter=True)
            .join(home, Match.home_team_id == home.id, isouter=True)
            .join(away, Match.away_team_id == away.id, isouter=True)
            .where(Match.id == payload.match_id)
        )
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="match not found")

    _, league_name, home_name, away_name = row
    query_terms = [x for x in [league_name, home_name, away_name] if x and x != "-"]
    q = " ".join(query_terms[:2]).strip()
    network_settings = await _load_network_settings(db)
    source_rules_payload = await _load_source_rules(db)
    source_rules = source_rules_payload.get("rules", {}) if isinstance(source_rules_payload, dict) else {}
    tty_rules = source_rules.get("ttyingqiu", {}) if isinstance(source_rules, dict) else {}
    timeout_map = _normalize_source_timeout_map(
        network_settings.get("source_timeout_seconds"),
        _default_network_settings().get("source_timeout_seconds", {}),
    )
    debug_timeout = _normalize_float(
        timeout_map.get("ttyingqiu", timeout_map.get("default", 2.0)),
        default=2.0,
        min_value=0.3,
        max_value=30.0,
    )
    blocked_exact = {
        str(x).strip().lower()
        for x in (tty_rules.get("blacklist_exact_paths") or [])
        if str(x).strip()
    }
    soft_penalty_map = (
        tty_rules.get("soft_penalty_paths")
        if isinstance(tty_rules, dict) and isinstance(tty_rules.get("soft_penalty_paths"), dict)
        else {}
    )

    session = requests.Session()
    session.trust_env = _normalize_bool(network_settings.get("trust_env"), False)
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
    )

    def _norm(s: str) -> str:
        return re.sub(r"\s+", " ", (s or "").strip().lower())

    def _clean(s: str) -> str:
        txt = re.sub(r"<script[^>]*>.*?</script>", " ", s or "", flags=re.I | re.S)
        txt = re.sub(r"<style[^>]*>.*?</style>", " ", txt, flags=re.I | re.S)
        txt = re.sub(r"<[^>]+>", " ", txt)
        return re.sub(r"\s+", " ", unescape(txt)).strip()

    def _title(html: str) -> str:
        m = re.search(r"<title[^>]*>(.*?)</title>", html or "", flags=re.I | re.S)
        return _clean(m.group(1)) if m else ""

    links: List[Dict[str, Any]] = []
    for entry in ["https://www.ttyingqiu.com/news/home", "https://www.ttyingqiu.com/news"]:
        try:
            r = session.get(entry, timeout=debug_timeout, allow_redirects=True)
            html = r.text or ""
        except Exception:
            continue
        for href, inner in re.findall(r"<a[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", html, flags=re.I | re.S):
            full = urljoin(entry, href.strip())
            low = full.lower()
            if "ttyingqiu.com" not in low or "/news/home" in low or "news" not in low:
                continue
            path = (urlparse(full).path or "").lower().rstrip("/")
            if path in blocked_exact or "/news/-1" in low or "/news/75" in low:
                continue
            anchor = _clean(inner)[:120]
            if not anchor:
                continue
            links.append({"url": full, "anchor": anchor, "from": "html"})

    if len(links) < 3:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("https://www.ttyingqiu.com/news/home", wait_until="domcontentloaded", timeout=10000)
                page.wait_for_timeout(1200)
                hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href') || '')")
                texts = page.eval_on_selector_all("a[href]", "els => els.map(e => (e.textContent || '').trim())")
                browser.close()
            for i, href in enumerate(hrefs or []):
                full = urljoin("https://www.ttyingqiu.com/news/home", (href or "").strip())
                low = full.lower()
                if "ttyingqiu.com" not in low or "/news/home" in low or "news" not in low:
                    continue
                path = (urlparse(full).path or "").lower().rstrip("/")
                if path in blocked_exact or "/news/-1" in low or "/news/75" in low:
                    continue
                anchor = _clean(texts[i] if i < len(texts) else "")[:120]
                if not anchor:
                    continue
                links.append({"url": full, "anchor": anchor, "from": "playwright"})
        except Exception:
            pass

    dedup: Dict[str, Dict[str, Any]] = {}
    for x in links:
        dedup.setdefault(x["url"], x)
    candidates = list(dedup.values())[:30]

    def _team_variants(raw: str) -> List[str]:
        base = (raw or "").strip()
        if not base:
            return []
        outs = {base}
        # small cjk variant expansion
        pairs = [("联", "聯"), ("国", "國"), ("兰", "蘭"), ("马", "馬"), ("罗", "羅"), ("亚", "亞"), ("萨", "薩"), ("维", "維"), ("纳", "納"), ("尔", "爾"), ("顿", "頓"), ("乌", "烏")]
        t = base
        for a, b in pairs:
            t = t.replace(a, b)
        outs.add(t)
        s = base
        for a, b in pairs:
            s = s.replace(b, a)
        outs.add(s)
        latin = re.sub(r"[^a-zA-Z\\s]", " ", base).strip().lower()
        if latin:
            parts = [p for p in latin.split() if p and p not in {"fc", "cf", "sc", "club"}]
            if parts:
                outs.add(" ".join(parts))
            if len(parts) >= 2:
                outs.add("".join(p[0] for p in parts))
            outs.add(" ".join(parts).replace("united", "utd"))
        return [x for x in outs if x]

    keyword_bag = []
    for x in query_terms:
        keyword_bag.extend([_norm(v) for v in _team_variants(x) if _norm(v)])
    keyword_bag = list(dict.fromkeys(keyword_bag))
    evaluated: List[Dict[str, Any]] = []
    status_codes: Dict[str, int] = {}
    for c in candidates:
        url = c["url"]
        try:
            r = session.get(url, timeout=debug_timeout, allow_redirects=True)
            html = r.text or ""
            code = int(r.status_code or 0)
        except Exception:
            html = ""
            code = -1
        status_codes[str(code)] = status_codes.get(str(code), 0) + 1
        title = _title(html) or c.get("anchor", "")
        excerpt = _clean(html)[:260]
        low = _norm(f"{title} {excerpt} {url}")
        hits = [k for k in keyword_bag if k in low]
        path = (urlparse(url).path or "").lower().rstrip("/")
        soft_penalty = _normalize_float(soft_penalty_map.get(path), default=0.0, min_value=0.0, max_value=5.0)
        score = round(0.6 * len(hits) + (0.4 if "news" in url.lower() else 0.0) - soft_penalty, 2)
        evaluated.append(
            {
                "url": url,
                "from": c.get("from"),
                "status_code": code,
                "title": title[:120],
                "title_hit_keywords": [k for k in keyword_bag if k in _norm(title)],
                "score": score,
            }
        )
    evaluated.sort(key=lambda x: x.get("score", 0), reverse=True)

    return _ok(
        {
            "match_id": payload.match_id,
            "match": {
                "league_name": league_name or "-",
                "home_team": home_name or "-",
                "away_team": away_name or "-",
            },
            "query": q,
            "candidate_count": len(candidates),
            "status_codes": status_codes,
            "top_candidates": evaluated[:20],
        }
    )


@router.post("/matches/{match_id}/push-preview")
async def build_push_preview(
    match_id: int,
    payload: PushPreviewRequest = Body(default=PushPreviewRequest()),
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    rows = (
        await db.execute(
            select(IntelligenceCollectionItem)
            .where(IntelligenceCollectionItem.match_id == match_id)
            .order_by(IntelligenceCollectionItem.crawled_at.desc())
            .limit(200)
        )
    ).scalars().all()

    if not rows:
        return _ok(
            {
                "match_id": match_id,
                "status": "insufficient",
                "headline": "No intelligence available",
                "confidence": 0.0,
                "confidence_score": 0.0,
                "evidence": [],
                "risk_level": "high",
            }
        )

    filtered_rows = []
    for row in rows:
        quality_meta = _extract_quality_from_item(row)
        if not payload.include_blocked and quality_meta.get("quality_status") == "blocked":
            continue
        if payload.min_score is not None and float(quality_meta.get("quality_score") or 0.0) < float(payload.min_score):
            continue
        filtered_rows.append((row, quality_meta))
    if not filtered_rows:
        return _ok(
            {
                "match_id": match_id,
                "status": "insufficient",
                "headline": "No intelligence available",
                "confidence": 0.0,
                "confidence_score": 0.0,
                "evidence": [],
                "risk_level": "high",
            }
        )

    top_n = payload.top_n if payload.top_n is not None else payload.max_evidence
    top_n = max(1, min(int(top_n), 20))
    filtered_rows.sort(
        key=lambda pair: (
            float(pair[1].get("quality_score") or 0.0),
            float(pair[1].get("ai_confidence") or 0.0),
            float(pair[0].confidence or 0.0),
            pair[0].crawled_at or datetime.min,
        ),
        reverse=True,
    )

    confidence_pool: List[float] = []
    for row, q in filtered_rows:
        ai_conf = q.get("ai_confidence")
        if ai_conf is not None:
            confidence_pool.append(_normalize_float(ai_conf, default=float(row.confidence or 0.0), min_value=0.0, max_value=1.0))
        else:
            confidence_pool.append(_normalize_float(row.confidence, default=0.0, min_value=0.0, max_value=1.0))
    confidence = round(sum(confidence_pool) / len(confidence_pool), 2) if confidence_pool else 0.0
    evidence = [
        {
            "source": x.source_code,
            "intel_type": x.intel_type,
            "content": q.get("ai_summary") or q.get("ai_viewpoint") or x.content_raw,
            "time": x.crawled_at.strftime("%Y-%m-%d %H:%M:%S") if x.crawled_at else None,
            "quality_score": q.get("quality_score"),
            "quality_status": q.get("quality_status"),
            "ai_enhanced": q.get("ai_enhanced"),
            "ai_confidence": q.get("ai_confidence"),
            "ai_risk_level": q.get("ai_risk_level"),
            "ai_viewpoint": q.get("ai_viewpoint"),
        }
        for x, q in filtered_rows[:top_n]
    ]
    risk_level = "low" if confidence >= 0.75 else ("medium" if confidence >= 0.62 else "high")
    headline = f"Match {match_id} intelligence summary: confidence={confidence}"
    return _ok(
        {
            "match_id": match_id,
            "status": "ready" if confidence >= 0.6 else "observe",
            "headline": headline,
            "confidence": confidence,
            "confidence_score": confidence,
            "risk_level": risk_level,
            "evidence": evidence,
            "user_risk_profile": payload.user_risk_profile,
        }
    )


@router.get("/subscriptions/me")
async def get_my_subscription(
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    user_id = int(current_admin.get("id") or 0)
    row = (
        await db.execute(
            select(IntelligenceUserSubscription).where(IntelligenceUserSubscription.user_id == user_id)
        )
    ).scalar_one_or_none()
    if not row:
        row = IntelligenceUserSubscription(user_id=user_id)
        db.add(row)
        await db.commit()
        await db.refresh(row)

    data = {
        "user_id": row.user_id,
        "leagues": _json_loads(row.leagues_json, []),
        "teams": _json_loads(row.teams_json, []),
        "intel_types": _json_loads(row.intel_types_json, []),
        "risk_profile": row.risk_profile,
        "push_frequency": row.push_frequency,
        "info_density": row.info_density,
        "daily_limit": row.daily_limit,
    }
    return _ok(data)


@router.put("/subscriptions/me")
async def update_my_subscription(
    payload: SubscriptionUpdateRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    user_id = int(current_admin.get("id") or 0)
    row = (
        await db.execute(
            select(IntelligenceUserSubscription).where(IntelligenceUserSubscription.user_id == user_id)
        )
    ).scalar_one_or_none()
    if not row:
        row = IntelligenceUserSubscription(user_id=user_id)
        db.add(row)

    row.leagues_json = _json_dumps(payload.leagues)
    row.teams_json = _json_dumps(payload.teams)
    row.intel_types_json = _json_dumps(payload.intel_types)
    row.risk_profile = payload.risk_profile
    row.push_frequency = payload.push_frequency
    row.info_density = payload.info_density
    row.daily_limit = payload.daily_limit
    await db.commit()
    await db.refresh(row)
    return _ok({"user_id": user_id}, "订阅配置已保存")


@router.get("/channels/dingtalk/bindings")
async def get_dingtalk_bindings(
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    user_id = int(current_admin.get("id") or 0)
    rows = (
        await db.execute(
            select(IntelligenceChannelBinding).where(
                and_(
                    IntelligenceChannelBinding.user_id == user_id,
                    IntelligenceChannelBinding.channel == "dingtalk",
                )
            )
        )
    ).scalars().all()
    items = [
        {
            "id": x.id,
            "webhook": x.webhook,
            "secret": x.secret,
            "enabled": x.enabled,
            "last_test_at": x.last_test_at.isoformat() if x.last_test_at else None,
        }
        for x in rows
    ]
    return _ok(items)


@router.post("/channels/dingtalk/bindings")
async def create_dingtalk_binding(
    payload: DingTalkBindingRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    row = IntelligenceChannelBinding(
        user_id=int(current_admin.get("id") or 0),
        channel="dingtalk",
        webhook=payload.webhook,
        secret=payload.secret,
        enabled=payload.enabled,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return _ok({"id": row.id}, "钉钉绑定已创建")


@router.put("/channels/dingtalk/bindings/{binding_id}")
async def update_dingtalk_binding(
    binding_id: int,
    payload: DingTalkBindingRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    row = await db.get(IntelligenceChannelBinding, binding_id)
    if not row or row.user_id != int(current_admin.get("id") or 0):
        raise HTTPException(status_code=404, detail="绑定不存在")
    row.webhook = payload.webhook
    row.secret = payload.secret
    row.enabled = payload.enabled
    await db.commit()
    return _ok({"id": binding_id}, "钉钉绑定已更新")


@router.delete("/channels/dingtalk/bindings/{binding_id}")
async def delete_dingtalk_binding(
    binding_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    row = await db.get(IntelligenceChannelBinding, binding_id)
    if not row or row.user_id != int(current_admin.get("id") or 0):
        raise HTTPException(status_code=404, detail="绑定不存在")
    await db.delete(row)
    await db.commit()
    return _ok({"id": binding_id}, "钉钉绑定已删除")


@router.post("/channels/dingtalk/bindings/{binding_id}/test")
async def test_dingtalk_binding(
    binding_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    row = await db.get(IntelligenceChannelBinding, binding_id)
    if not row or row.user_id != int(current_admin.get("id") or 0):
        raise HTTPException(status_code=404, detail="绑定不存在")
    if not row.enabled:
        raise HTTPException(status_code=400, detail="璇ョ粦瀹氬凡绂佺敤")

    message = f"情报系统测试消息（{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}）"
    sent = send_dingtalk_message(row.webhook, message)
    row.last_test_at = datetime.utcnow()
    await db.commit()
    if not sent:
        raise HTTPException(status_code=502, detail="钉钉测试发送失败")
    return _ok({"id": binding_id}, "钉钉测试发送成功")


@router.post("/push/tasks")
async def create_push_task(
    payload: PushTaskCreateRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    push_task = IntelligencePushTask(
        match_id=payload.match_id,
        preview_json=_json_dumps(payload.preview),
        channel=payload.channel,
        target_users_json=_json_dumps(payload.target_users),
        status="pending",
        created_by=int(current_admin.get("id") or 0),
    )
    db.add(push_task)
    await db.flush()

    if payload.channel == "dingtalk" and payload.binding_id:
        binding = await db.get(IntelligenceChannelBinding, payload.binding_id)
        if binding and binding.enabled:
            sent = send_dingtalk_message(binding.webhook, payload.preview.get("headline", "情报推送"))
            push_task.status = "success" if sent else "failed"
            push_task.error_message = None if sent else "钉钉发送失败"
            push_task.pushed_at = datetime.utcnow() if sent else None
        else:
            push_task.status = "failed"
            push_task.error_message = "绑定不存在或已禁用"
    else:
        push_task.status = "success"
        push_task.pushed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(push_task)
    return _ok({"id": push_task.id, "status": push_task.status}, "鎺ㄩ€佷换鍔″凡鍒涘缓")

