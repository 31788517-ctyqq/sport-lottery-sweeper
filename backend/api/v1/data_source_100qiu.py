"""
100qiu数据源API - 专门处理100qiu数据源的获取和管理
"""
import json
import re
from datetime import datetime as dt, datetime
import os
import requests
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.exceptions import HTTPException
from pydantic import ValidationError, BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.exc import SQLAlchemyError

# 导入数据库依赖
from ...database import get_db

# 导入数据模型
from ...models.data_sources import DataSource
from ...models.data_source_headers import DataSourceHeader
from ...models.headers import RequestHeader
from ...models.ip_pool import IPPool
from ...config import settings

# 添加日志服务导入
from ...services.log_service import LogService
from ...models.log_entry import LogEntry
from ...schemas.log_entry import LogEntryCreate

router = APIRouter()
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
_NO_PROXY_SESSION = requests.Session()
_NO_PROXY_SESSION.trust_env = False
_EXPECT_OPTIONS_CACHE: List[str] = []
_EXPECT_OPTIONS_CACHE_TS: Optional[dt] = None
_EXPECT_OPTIONS_CACHE_TTL_SECONDS = 300


def _parse_json_payload(response: requests.Response) -> Any:
    """
    Parse upstream response payload with lightweight compatibility fallbacks:
    - UTF-8 BOM
    - JSONP wrapper: callback({...})
    """
    try:
        return response.json()
    except Exception:
        text = (response.text or "").strip()
        text = text.lstrip("\ufeff").strip()
        if not text:
            raise ValueError("empty response body")

        # JSONP fallback
        jsonp_match = re.match(r"^[A-Za-z_$][\w$]*\s*\((.*)\)\s*;?\s*$", text, re.S)
        if jsonp_match:
            inner = jsonp_match.group(1).strip()
            return json.loads(inner)

        return json.loads(text)


def _looks_like_json_payload(response: requests.Response) -> bool:
    try:
        text = (response.text or "").lstrip("\ufeff \t\r\n")
    except Exception:
        return False
    if not text:
        return False
    if text[0] in ("{", "["):
        return True
    # JSONP style callback(...)
    if re.match(r"^[A-Za-z_$][\w$]*\s*\(", text):
        return True
    return False


def _fetch_500w_expect_options(limit: int = 6) -> List[str]:
    """
    Read latest Beidan issue numbers from 500w.
    Returned values are ordered as they appear on page (latest first).
    """
    global _EXPECT_OPTIONS_CACHE_TS
    now = dt.utcnow()
    if (
        _EXPECT_OPTIONS_CACHE
        and _EXPECT_OPTIONS_CACHE_TS is not None
        and (now - _EXPECT_OPTIONS_CACHE_TS).total_seconds() < _EXPECT_OPTIONS_CACHE_TTL_SECONDS
    ):
        return _EXPECT_OPTIONS_CACHE[: max(1, int(limit))]

    try:
        response = _NO_PROXY_SESSION.get(
            "https://trade.500.com/bjdc/",
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
                ),
                "Referer": "https://trade.500.com/bjdc/",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
            timeout=15,
        )
        if response.status_code != 200:
            return []

        values = re.findall(r'<option[^>]+value=["\'](\d{5,6})["\']', response.text or "", flags=re.I)
        result: List[str] = []
        seen = set()
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            result.append(value)
            if len(result) >= max(1, int(limit)):
                break
        if result:
            _EXPECT_OPTIONS_CACHE.clear()
            _EXPECT_OPTIONS_CACHE.extend(result)
            _EXPECT_OPTIONS_CACHE_TS = now
        return result
    except Exception:
        return []


def _resolve_date_time_candidates(raw_date_time: Optional[Any], max_candidates: int = 3) -> List[str]:
    """
    Resolve candidate dateTime values for 100qiu requests.
    - explicit date_time -> use it directly
    - latest/empty -> use latest issues from 500w, fallback to 26011
    """
    value = str(raw_date_time or "").strip().lower()
    explicit = str(raw_date_time).strip() if raw_date_time is not None else ""
    # Explicit date_time should not trigger extra remote lookups.
    if value and value != "latest" and explicit:
        return [explicit]

    options = _fetch_500w_expect_options(limit=max(3, max_candidates))
    if options:
        return options[: max(1, int(max_candidates))]
    return ["26011"]


def _build_100qiu_api_url(base_url: str, date_time: str) -> str:
    if "dateTime=" in base_url:
        return re.sub(r"dateTime=\w+", f"dateTime={date_time}", base_url)
    joiner = "&" if "?" in base_url else "?"
    return f"{base_url}{joiner}dateTime={date_time}"


def _resolve_domain(raw_url: Optional[str]) -> str:
    try:
        return (urlparse(raw_url or "").hostname or "__global__").lower()
    except Exception:
        return "__global__"


def _build_header_context(db: Session, data_source_id: int, url: str) -> Dict[str, Any]:
    domain = _resolve_domain(url)
    bindings = (
        db.query(DataSourceHeader, RequestHeader)
        .join(RequestHeader, DataSourceHeader.header_id == RequestHeader.id)
        .filter(DataSourceHeader.data_source_id == int(data_source_id))
        .filter(DataSourceHeader.enabled.is_(True))
        .filter(RequestHeader.status == "enabled")
        .all()
    )
    selected: Dict[str, Dict[str, Any]] = {}
    selected_ids: List[int] = []
    for binding, header in bindings:
        if header.domain not in {domain, "__global__"}:
            continue
        priority = binding.priority_override if binding.priority_override is not None else int(header.priority or 0)
        existing = selected.get(header.name)
        if not existing or priority >= existing["priority"]:
            selected[header.name] = {"value": header.value, "priority": priority, "id": int(header.id)}
    for row in selected.values():
        selected_ids.append(int(row["id"]))
    headers = {name: row["value"] for name, row in selected.items()}
    return {"headers": headers, "header_ids": selected_ids, "domain": domain}


def _choose_proxy(db: Session) -> Optional[IPPool]:
    if not settings.REQUEST_USE_PROXY_BY_DEFAULT:
        return None
    return (
        db.query(IPPool)
        .filter(IPPool.status.in_(["active", "testing"]))
        .order_by(IPPool.last_used.asc(), IPPool.id.asc())
        .first()
    )


def _record_proxy_result(db: Session, proxy: Optional[IPPool], success: bool, reason: Optional[str] = None) -> None:
    if not proxy:
        return
    proxy.last_used = datetime.utcnow()
    if success:
        proxy.success_count = int(proxy.success_count or 0) + 1
        proxy.status = "active"
        proxy.fail_reason = None
    else:
        proxy.failure_count = int(proxy.failure_count or 0) + 1
        threshold = max(1, int(settings.IP_POOL_FAILURES_BEFORE_COOLING))
        proxy.status = "cooling" if int(proxy.failure_count or 0) >= threshold else "testing"
        proxy.fail_reason = reason or "request_failed"
    db.commit()


def _record_header_usage(db: Session, header_ids: List[int], success: bool) -> None:
    if not header_ids:
        return
    now = datetime.utcnow()
    rows = db.query(RequestHeader).filter(RequestHeader.id.in_(header_ids)).all()
    for row in rows:
        row.usage_count = int(row.usage_count or 0) + 1
        if success:
            row.success_count = int(row.success_count or 0) + 1
        row.last_used = now
    db.commit()


def _request_with_pool_context(db: Session, source_id: int, url: str, timeout: int = 30) -> Dict[str, Any]:
    header_ctx = _build_header_context(db, source_id, url)
    headers = header_ctx["headers"] or {}
    if "User-Agent" not in headers:
        headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        )

    proxy = _choose_proxy(db)
    trace = {
        "proxy_used": None,
        "proxy_id": int(proxy.id) if proxy else None,
        "header_ids": list(header_ctx["header_ids"]),
        "fallback_reason": None,
        "used_direct": proxy is None,
    }
    request_kwargs: Dict[str, Any] = {"headers": headers, "timeout": timeout}
    if proxy:
        proxy_url = f"{proxy.protocol}://{proxy.ip}:{proxy.port}"
        request_kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
        trace["proxy_used"] = proxy_url

    try:
        response = _NO_PROXY_SESSION.get(url, **request_kwargs)
    except requests.RequestException:
        if request_kwargs.get("proxies") and settings.REQUEST_ALLOW_DIRECT_FALLBACK:
            trace["fallback_reason"] = "proxy_request_failed_direct_fallback"
            trace["used_direct"] = True
            trace["proxy_used"] = None
            request_kwargs.pop("proxies", None)
            response = _NO_PROXY_SESSION.get(url, **request_kwargs)
        else:
            _record_proxy_result(db, proxy, False, reason="request_exception")
            _record_header_usage(db, header_ctx["header_ids"], False)
            raise

    # Proxy may return HTTP 200 with non-JSON/html content; fallback to direct once.
    if (
        request_kwargs.get("proxies")
        and settings.REQUEST_ALLOW_DIRECT_FALLBACK
        and response.status_code == 200
        and not _looks_like_json_payload(response)
    ):
        trace["fallback_reason"] = "proxy_non_json_direct_fallback"
        trace["used_direct"] = True
        trace["proxy_used"] = None
        request_kwargs.pop("proxies", None)
        response = _NO_PROXY_SESSION.get(url, **request_kwargs)

    success = response.status_code == 200
    _record_proxy_result(db, proxy, success, reason=f"status_{response.status_code}")
    _record_header_usage(db, header_ctx["header_ids"], success)
    if proxy is None and settings.REQUEST_USE_PROXY_BY_DEFAULT:
        trace["fallback_reason"] = "proxy_pool_empty_direct"
    return {
        "response": response,
        "trace": trace,
        "headers": headers,
        "timeout": timeout,
        "url": url,
    }


def validation_exception_handler(request: Request, exc: ValidationError):
    """
    自定义验证异常处理器，返回前端期望的格式
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error['loc']),
            "message": error['msg'],
            "type": error['type']
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "data": {
                "errors": errors
            }
        }
    )


class DataSource100qiuCreate(BaseModel):
    name: str
    url: str
    date_time: Optional[str] = "latest"  # 默认获取最新数据
    update_frequency: Optional[int] = 60  # 更新频率，默认60分钟
    field_mapping: Optional[Dict[str, str]] = {}
    status: Optional[str] = "online"  # 添加status字段，默认为online


class DataSource100qiuUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    date_time: Optional[str] = None
    update_frequency: Optional[int] = None
    field_mapping: Optional[Dict[str, str]] = None
    status: Optional[str] = None


class DataSource100qiuResponse(BaseModel):
    id: int
    source_id: str
    name: str
    type: str
    url: str
    status: str
    config: Dict[str, Any]
    last_update: Optional[str] = None
    error_rate: float = 0.0
    created_at: str
    updated_at: str
    created_by: Optional[int] = None
    last_error: Optional[str] = None
    last_error_time: Optional[str] = None


class DataSource100qiuListResponse(BaseModel):
    items: List[DataSource100qiuResponse]
    total: int


class TestConnectionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    sample_data: Optional[List[Dict[str, Any]]] = None


class FetchDataResponse(BaseModel):
    success: bool
    message: str
    total_fetched: int
    sample_data: Optional[List[Dict[str, Any]]] = None
    request_trace: Optional[Dict[str, Any]] = None


router = APIRouter(prefix="/data-source-100qiu", tags=["data-source-100qiu"])

@router.get("/date-time-options")
async def get_date_time_options(db: Session = Depends(get_db)):
    """Return available date_time options from successful 100qiu sources."""
    try:
        sources = (
            db.query(DataSource)
            .filter(DataSource.last_error.is_(None))
            .filter(DataSource.last_update.isnot(None))
            .all()
        )

        values = set()
        for source in sources:
            config = source.config_dict or {}
            status_val = source.status
            is_online = status_val == 1 or status_val == "online"
            is_100qiu = source.type == "100qiu" or config.get("source_type") == "100qiu"
            if not is_online:
                continue
            if not is_100qiu:
                continue
            date_time = config.get("date_time")
            if date_time and str(date_time).lower() != "latest":
                values.add(str(date_time))

        options = sorted(values, reverse=True)

        return {
            "success": True,
            "data": {"options": options, "total": len(options)},
            "message": "date_time options loaded"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load date_time options: {str(e)}",
            "data": {"options": [], "total": 0}
        }


@router.get("/latest-matches")
async def get_latest_100qiu_matches(
    include_raw: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Return matches from the latest date_time (latest period) stored from 100qiu data source."""
    try:
        sources = db.query(DataSource).all()
        source_count = 0
        for source in sources:
            config = source.config_dict or {}
            if source.type == "100qiu" or config.get("source_type") == "100qiu":
                source_count += 1
        if source_count == 0:
            return {
                "success": False,
                "message": "No 100qiu data source configured",
                "data": {"matches": [], "total": 0}
            }

        from ...models.matches import FootballMatch

        # 获取所有100qiu比赛
        all_matches = db.query(FootballMatch).all()
        
        if not all_matches:
            return {
                "success": True,
                "data": {
                    "matches": [],
                    "total": 0
                },
                "message": "No matches found"
            }
        
        # 提取所有非空的date_time并找到最新的date_time
        date_times = [match.date_time for match in all_matches if match.date_time]
        if not date_times:
            return {
                "success": True,
                "data": {
                    "matches": [],
                    "total": 0
                },
                "message": "No matches with date_time found"
            }
        
        # 按字符串比较找到最新的date_time（格式如：2026-02-13 20:00:00）
        latest_date_time = max(date_times)
        
        # 过滤出最新date_time对应的所有比赛
        latest_matches = [match for match in all_matches if match.date_time == latest_date_time]

        payload = []
        for match in latest_matches:
            item = {
                "match_id": match.match_id,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "league": match.league,
                "match_time": match.match_time.isoformat() if match.match_time else None,
                "date_time": match.date_time,  # 添加date_time字段供前端参考
                "power_home": None,
                "power_away": None,
                "win_pan_home": None,
                "win_pan_away": None,
                "p_level": None,
                "delta_wp": None,
                "rq": None
            }
            if include_raw:
                item["data_source"] = getattr(match, "data_source", None)
                item["source_attributes"] = getattr(match, "source_attributes", None)
            payload.append(item)

        return {
            "success": True,
            "data": {
                "matches": payload,
                "total": len(payload),
                "latest_date_time": latest_date_time  # 返回最新date_time信息
            },
            "message": f"Loaded {len(payload)} matches from latest period ({latest_date_time})"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load latest matches: {str(e)}",
            "data": {"matches": [], "total": 0}
        }


@router.get("/match/{match_id}")
async def get_100qiu_match_raw(
    match_id: str,
    db: Session = Depends(get_db)
):
    """Return stored 100qiu raw payload for a match_id."""
    try:
        from ...models.matches import FootballMatch

        match = db.query(FootballMatch).filter(FootballMatch.match_id == match_id).first()
        if not match:
            return {
                "success": False,
                "message": "Match not found",
                "data": None
            }

        raw = getattr(match, "source_attributes", None)
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                pass

        return {
            "success": True,
            "message": "Match raw loaded",
            "data": {
                "match_id": match.match_id,
                "source_attributes": raw
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load match raw: {str(e)}",
            "data": None
        }


@router.post("/")
async def create_100qiu_data_source(
    data: DataSource100qiuCreate,
    db: Session = Depends(get_db)
):
    """创建100qiu数据源配置"""
    try:
        # 构建配置
        config = {
            "date_time": data.date_time,
            "update_frequency": data.update_frequency
        }
        
        # 创建数据源记录，开发环境中暂时设置created_by为固定值
        db_data_source = DataSource(
            name=data.name,
            type="100qiu",  # 设置为100qiu类型
            url=data.url,
            config=json.dumps(config, ensure_ascii=False),
            field_mapping=data.field_mapping,
            update_frequency=data.update_frequency,
            status=1 if data.status != "offline" else 0,
            created_by=1  # 开发环境临时设置为固定值，后续应通过认证获取
        )
        
        db.add(db_data_source)
        db.commit()
        db.refresh(db_data_source)
        
        # 转换为响应格式
        response_data = DataSource100qiuResponse(
            id=db_data_source.id,
            source_id=db_data_source.source_id or f"DS{db_data_source.id:03d}",
            name=db_data_source.name,
            type=db_data_source.type,
            url=db_data_source.url,
            status="online" if db_data_source.status == 1 else "offline",
            config=db_data_source.config_dict,
            last_update=db_data_source.last_update.isoformat() if db_data_source.last_update else None,
            error_rate=db_data_source.error_rate,
            created_at=db_data_source.created_at.isoformat(),
            updated_at=db_data_source.updated_at.isoformat(),
            created_by=db_data_source.created_by,
            last_error=db_data_source.last_error,
            last_error_time=db_data_source.last_error_time.isoformat() if db_data_source.last_error_time else None
        )
        
        return {"success": True, "data": response_data, "message": "数据源创建成功"}
    except Exception as e:
        return {"success": False, "message": f"创建数据源失败: {str(e)}", "data": None}


@router.get("/{source_id}")
async def get_100qiu_data_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """获取指定ID的100qiu数据源"""
    try:
        db_data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
        
        if not db_data_source:
            raise HTTPException(status_code=404, detail="数据源不存在")
        
        response_data = DataSource100qiuResponse(
            id=db_data_source.id,
            source_id=db_data_source.source_id or f"DS{db_data_source.id:03d}",
            name=db_data_source.name,
            type=db_data_source.type,
            url=db_data_source.url,
            status="online" if db_data_source.status == 1 else "offline",
            config=db_data_source.config_dict,
            last_update=db_data_source.last_update.isoformat() if db_data_source.last_update else None,
            error_rate=db_data_source.error_rate,
            created_at=db_data_source.created_at.isoformat(),
            updated_at=db_data_source.updated_at.isoformat(),
            created_by=db_data_source.created_by,
            last_error=db_data_source.last_error,
            last_error_time=db_data_source.last_error_time.isoformat() if db_data_source.last_error_time else None
        )
        
        return {"success": True, "data": response_data, "message": "获取数据源成功"}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": f"获取数据源失败: {str(e)}", "data": None}


@router.put("/{source_id}")
async def update_100qiu_data_source(
    source_id: int,
    data: DataSource100qiuUpdate,
    db: Session = Depends(get_db)
):
    """更新100qiu数据源配置"""
    try:
        db_data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
        
        if not db_data_source:
            raise HTTPException(status_code=404, detail="数据源不存在")
        
        # 更新字段
        if data.name is not None:
            db_data_source.name = data.name
        if data.url is not None:
            db_data_source.url = data.url
        if data.status is not None:
            db_data_source.status = 1 if data.status == "online" else 0
        if data.update_frequency is not None:
            db_data_source.update_frequency = data.update_frequency
        
        # 确保type保持为100qiu
        db_data_source.type = "100qiu"
        
        # 更新配置
        config = db_data_source.config_dict
        if data.date_time is not None:
            config["date_time"] = data.date_time
        if data.field_mapping is not None:
            db_data_source.field_mapping = data.field_mapping
        
        # 重新序列化配置到数据库
        db_data_source.config = json.dumps(config, ensure_ascii=False)
        from datetime import datetime as dt
        db_data_source.updated_at = dt.utcnow()
        
        db.commit()
        db.refresh(db_data_source)
        
        response_data = DataSource100qiuResponse(
            id=db_data_source.id,
            source_id=db_data_source.source_id or f"DS{db_data_source.id:03d}",
            name=db_data_source.name,
            type=db_data_source.type,
            url=db_data_source.url,
            status="online" if db_data_source.status == 1 else "offline",
            config=db_data_source.config_dict,
            last_update=db_data_source.last_update.isoformat() if db_data_source.last_update else None,
            error_rate=db_data_source.error_rate,
            created_at=db_data_source.created_at.isoformat(),
            updated_at=db_data_source.updated_at.isoformat(),
            created_by=db_data_source.created_by,
            last_error=db_data_source.last_error,
            last_error_time=db_data_source.last_error_time.isoformat() if db_data_source.last_error_time else None
        )
        
        return {"success": True, "data": response_data, "message": "更新数据源成功"}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": f"更新数据源失败: {str(e)}", "data": None}


@router.delete("/{source_id}")
async def delete_100qiu_data_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """删除100qiu数据源"""
    try:
        db_data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
        
        if not db_data_source:
            raise HTTPException(status_code=404, detail="数据源不存在")
        
        db.delete(db_data_source)
        db.commit()
        
        return {"success": True, "message": "数据源删除成功", "data": {"id": source_id}}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "message": f"删除数据源失败: {str(e)}", "data": None}


@router.get("/")
async def list_100qiu_data_sources(
    name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取100qiu数据源列表"""
    try:
        query = db.query(DataSource).filter(DataSource.type == "100qiu")
        
        # 应用筛选条件
        if name:
            query = query.filter(DataSource.name.contains(name))
        if status:
            query = query.filter(DataSource.status == (1 if status == "online" else 0))
        
        # 计算总数
        total = query.count()
        
        # 应用分页
        data_sources = query.offset(skip).limit(limit).all()
        
        # 转换为响应格式
        items = []
        for ds in data_sources:
            items.append(DataSource100qiuResponse(
                id=ds.id,
                source_id=ds.source_id or f"DS{ds.id:03d}",
                name=ds.name,
                type=ds.type,
                url=ds.url,
                status="online" if ds.status == 1 else "offline",
                config=ds.config_dict,
                last_update=ds.last_update.isoformat() if ds.last_update else None,
                error_rate=ds.error_rate,
                created_at=ds.created_at.isoformat(),
                updated_at=ds.updated_at.isoformat(),
                created_by=ds.created_by,
                last_error=ds.last_error,
                last_error_time=ds.last_error_time.isoformat() if ds.last_error_time else None
            ))
        
        response_data = DataSource100qiuListResponse(items=items, total=total)
        
        return {"success": True, "data": response_data, "message": "获取数据源列表成功"}
    except Exception as e:
        return {"success": False, "message": f"获取数据源列表失败: {str(e)}", "data": None}


@router.post("/{source_id}/test")
async def test_100qiu_data_source_connection(
    source_id: int,
    db: Session = Depends(get_db)
):
    """测试100qiu数据源连接"""
    try:
        db_data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
        
        if not db_data_source:
            raise HTTPException(status_code=404, detail="数据源不存在")
        
        # 获取配置并解析期号候选（latest 会自动解析为 500w 最新期号）
        config = db_data_source.config_dict
        date_time_candidates = _resolve_date_time_candidates(config.get("date_time", "latest"), max_candidates=3)

        data: Any = None
        response: Optional[requests.Response] = None
        request_trace: Dict[str, Any] = {}
        api_url = ""
        last_error_message = ""
        used_date_time = ""

        for candidate in date_time_candidates:
            used_date_time = candidate
            api_url = _build_100qiu_api_url(db_data_source.url, candidate)
            request_ctx = _request_with_pool_context(db, source_id, api_url, timeout=30)
            response = request_ctx["response"]
            request_trace = request_ctx["trace"]
            request_trace["date_time"] = candidate

            if response.status_code != 200:
                last_error_message = f"API请求失败，状态码: {response.status_code}"
                continue

            try:
                data = _parse_json_payload(response)
                break
            except Exception as e:
                last_error_message = f"响应不是有效JSON格式: {str(e)}"
                continue

        if response is None or data is None:
            return TestConnectionResponse(
                success=False,
                message=last_error_message or "测试失败：上游返回无效响应",
                data={
                    "request_trace": request_trace,
                    "tried_date_times": date_time_candidates,
                    "api_url": api_url,
                }
            )
        
        # 检查数据结构
        if not isinstance(data, (list, dict)):
            return TestConnectionResponse(
                success=False,
                message="API返回的数据格式不符合预期，应为数组或对象",
                data={"request_trace": request_trace}
            )
        
        # 获取样本数据
        sample_data = []
        if isinstance(data, list):
            sample_data = data[:3]  # 前3条数据作为样本
        elif isinstance(data, dict) and "data" in data:
            sample_data = data["data"][:3] if isinstance(data["data"], list) else [data["data"]]
        else:
            sample_data = [data]
        
        response_obj = TestConnectionResponse(
            success=True,
            message="连接测试成功",
            data={
                "status_code": response.status_code,
                "content_length": len(response.content),
                "has_data": len(sample_data) > 0,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "request_trace": request_trace,
                "date_time": used_date_time,
                "tried_date_times": date_time_candidates,
            },
            sample_data=sample_data
        )
        
        return {
            "success": True,
            "message": "连接测试成功",
            "data": response_obj
        }
    
    except Exception as e:
        response_obj = TestConnectionResponse(
            success=False,
            message=f"连接测试失败: {str(e)}",
            data=None
        )
        return {
            "success": False,
            "message": f"连接测试失败: {str(e)}",
            "data": response_obj.dict()
        }


@router.post("/{source_id}/fetch")
async def fetch_100qiu_data(
    source_id: int,
    compare_update: bool = Query(True, description="当记录已存在时，是否对比更新"),
    db: Session = Depends(get_db)
):
    """从100qiu API获取数据并存储到数据库"""
    # 初始化日志服务
    log_service = LogService(db)
    
    request_trace: Dict[str, Any] = {
        "proxy_used": None,
        "proxy_id": None,
        "header_ids": [],
        "fallback_reason": None,
        "used_direct": True,
    }
    try:
        db_data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
        
        if not db_data_source:
            raise HTTPException(status_code=404, detail="数据源不存在")
        
        # 记录开始日志
        start_time = dt.utcnow()
        log_service.create_log_entry(LogEntryCreate(
            timestamp=start_time,
            level="INFO",
            message=f"开始获取100qiu数据源 {source_id} 的数据",
            module="data_source_100qiu",
            user_id=None,
            extra_data=json.dumps({
                "source_id": source_id,
                "source_name": db_data_source.name,
                "url": db_data_source.url,
                "action": "fetch_start"
            }, ensure_ascii=False)
        ))
        
        # 获取配置并解析期号候选（latest 会自动解析为 500w 最新期号）
        config = db_data_source.config_dict
        date_time_candidates = _resolve_date_time_candidates(config.get("date_time", "latest"), max_candidates=3)

        response: Optional[requests.Response] = None
        data: Any = None
        api_url = ""
        used_date_time = ""
        last_error_msg = ""

        for candidate in date_time_candidates:
            used_date_time = candidate
            api_url = _build_100qiu_api_url(db_data_source.url, candidate)
            request_ctx = _request_with_pool_context(db, source_id, api_url, timeout=30)
            response = request_ctx["response"]
            request_trace = request_ctx["trace"]
            request_trace["date_time"] = candidate

            if response.status_code != 200:
                last_error_msg = f"API请求失败，状态码: {response.status_code}"
                continue

            try:
                data = _parse_json_payload(response)
                break
            except Exception as e:
                last_error_msg = f"响应不是有效JSON格式: {str(e)}"
                continue

        if response is None or data is None:
            error_msg = last_error_msg or "API返回无效响应"
            print(f"[ERROR] {error_msg}")
            # 更新数据源错误信息
            db_data_source.last_error = error_msg
            db_data_source.last_error_time = datetime.utcnow()
            db.commit()

            # 记录错误日志
            log_service.create_log_entry(LogEntryCreate(
                timestamp=dt.utcnow(),
                level="ERROR",
                message=f"100qiu数据源 {source_id} 获取失败: {error_msg}",
                module="data_source_100qiu",
                user_id=None,
                extra_data=json.dumps({
                    "source_id": source_id,
                    "url": api_url,
                    "action": "fetch_failed",
                    "error_type": "upstream_invalid_response",
                    "tried_date_times": date_time_candidates,
                    "request_trace": request_trace,
                }, ensure_ascii=False)
            ))

            return FetchDataResponse(
                success=False,
                message=error_msg,
                total_fetched=0,
                request_trace=request_trace,
            )

        date_time = used_date_time
        
        # 解析数据并存储到数据库
        from ...models.matches import FootballMatch
        from ...database import engine
        from sqlalchemy.orm import Session as SqlSession
        
        # 添加调试信息
        print(f"[DEBUG] API响应数据类型: {type(data)}")
        print(f"[DEBUG] API响应数据内容预览: {str(data)[:1000]}...")  # 增加预览长度
        
        # 确保数据格式正确
        matches_data = []
        if isinstance(data, list):
            matches_data = data
            print(f"[INFO] 数据是列表格式，包含 {len(matches_data)} 个项目")
        elif isinstance(data, dict):
            if "data" in data:
                matches_data = data["data"] if isinstance(data["data"], list) else []
                print(f"[INFO] 数据是字典格式，包含 'data' 键，解析出 {len(matches_data)} 个项目")
            elif "rows" in data:
                matches_data = data["rows"] if isinstance(data["rows"], list) else []
                print(f"[INFO] 数据是字典格式，包含 'rows' 键，解析出 {len(matches_data)} 个项目")
            elif "results" in data:
                matches_data = data["results"] if isinstance(data["results"], list) else []
                print(f"[INFO] 数据是字典格式，包含 'results' 键，解析出 {len(matches_data)} 个项目")
            elif "items" in data:
                matches_data = data["items"] if isinstance(data["items"], list) else []
                print(f"[INFO] 数据是字典格式，包含 'items' 键，解析出 {len(matches_data)} 个项目")
            elif "matches" in data:
                matches_data = data["matches"] if isinstance(data["matches"], list) else []
                print(f"[INFO] 数据是字典格式，包含 'matches' 键，解析出 {len(matches_data)} 个项目")
            else:
                # 检查字典中是否包含比赛相关字段，如果是，则作为单个项目处理
                match_keys = ['homeTeam', 'awayTeam', 'home_team', 'away_team', 'league', 'matchTime', 'startTime', 'status']
                if any(key in data for key in match_keys):
                    matches_data = [data]
                    print(f"[INFO] 数据是字典格式，包含比赛相关字段，作为单个项目处理")
                else:
                    matches_data = []
                    print(f"[WARNING] 数据是字典格式，但不包含已知数据键或比赛字段，无法解析")
                    # 记录详细错误信息
                    available_keys = list(data.keys()) if hasattr(data, 'keys') else []
                    warning_msg = f"数据格式不符合预期，可用键: {available_keys[:10]}"
                    print(f"[DEBUG] {warning_msg}")
        else:
            matches_data = []
            error_msg = f"数据格式未知，无法解析: {type(data)}"
            print(f"[ERROR] {error_msg}")
            # 更新数据源错误信息
            db_data_source.last_error = error_msg
            db_data_source.last_error_time = datetime.utcnow()
            db.commit()
            
            # 记录错误日志
            log_service.create_log_entry(LogEntryCreate(
                level="ERROR",
                message=f"100qiu数据源 {source_id} 数据格式解析失败: {error_msg}",
                module="data_source_100qiu",
                user_id=None,
                extra_data=json.dumps({
                    "source_id": source_id,
                    "data_type": str(type(data)),
                    "action": "fetch_failed",
                    "error_type": "data_format_error"
                }, ensure_ascii=False)
            ))
            
            return FetchDataResponse(
                success=False,
                message=error_msg,
                total_fetched=0,
                request_trace=request_trace,
            )
        
        print(f"[INFO] 最终解析的比赛数据数量: {len(matches_data)}")
        
        # 如果没有解析到任何比赛数据，返回成功但数量为0
        if len(matches_data) == 0:
            success_msg = f"获取成功，获取数量：0；数据库未新增数据条数。API返回了 {len(matches_data)} 条原始数据，但未能解析出有效的比赛数据。"
            print(f"[INFO] {success_msg}")
            # 清除之前的错误信息（因为这不是错误）
            db_data_source.last_error = None
            db_data_source.last_error_time = None
            db.commit()
            
            end_time = dt.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # 记录详细日志
            log_service.create_log_entry(LogEntryCreate(
                timestamp=end_time,
                level="INFO",
                message=f"100qiu数据源 {source_id} 获取完成: {success_msg}",
                module="data_source_100qiu",
                user_id=None,
                extra_data=json.dumps({
                    "source_id": source_id,
                    "total_fetched": 0,
                    "raw_data_count": len(matches_data),
                    "action": "fetch_success_zero",
                    "available_keys": list(data.keys()) if isinstance(data, dict) else [],
                    "duration_seconds": duration,
                    "request_trace": request_trace,
                }, ensure_ascii=False)
            ))
            
            response_obj = FetchDataResponse(
                success=True,
                message=success_msg,
                total_fetched=0,
                sample_data=[],
                request_trace=request_trace,
            )
            return response_obj
        
        # 存储到数据库
        session = SqlSession(bind=engine)
        count = 0
        updated_count = 0
        unchanged_count = 0
        processed_count = 0
        failed_parsing_count = 0
        try:
            for i, item in enumerate(matches_data):
                print(f"[DEBUG] 正在处理第 {i+1}/{len(matches_data)} 个项目: {str(item)[:500]}...")
                processed_count += 1
                
                # 调试：打印date_time值
                print(f"[DEBUG] 传递给parse_match_from_100qiu的date_time参数: {date_time} (类型: {type(date_time)})")
                
                # 解析比赛数据
                match_data = parse_match_from_100qiu(item, date_time)
                # 调试：打印match_data完整内容（限制长度）
                if match_data:
                    print(f"[DEBUG] parse_match_from_100qiu返回的完整match_data: {match_data}")
                    print(f"[INFO] 成功解析比赛数据: {match_data.get('match_id', 'N/A')}")
                    # 检查是否已存在
                    existing_match = session.query(FootballMatch).filter(
                        FootballMatch.match_id == match_data["match_id"]
                    ).first()
                    
                    if not existing_match:
                        # 创建新的比赛记录 - 使用FootballMatch模型的字段
                        new_match = FootballMatch(**match_data)
                        session.add(new_match)
                        count += 1
                        print(f"[INFO] 新增比赛记录: {match_data.get('match_id', 'N/A')}")
                    else:
                        if compare_update:
                            updated_fields = []
                            for field in [
                                "date_time",
                                "line_id",
                                "home_team",
                                "away_team",
                                "match_time",
                                "league",
                                "status",
                                "home_score",
                                "away_score",
                                "data_source",
                                "source_attributes"
                            ]:
                                new_val = match_data.get(field)
                                if new_val is None:
                                    continue
                                old_val = getattr(existing_match, field, None)
                                if old_val != new_val:
                                    setattr(existing_match, field, new_val)
                                    updated_fields.append(field)
                            if updated_fields:
                                updated_count += 1
                                print(f"[INFO] 更新比赛记录: {match_data.get('match_id', 'N/A')} fields={updated_fields}")
                            else:
                                unchanged_count += 1
                                print(f"[INFO] 比赛记录未变化，跳过更新: {match_data.get('match_id', 'N/A')}")
                        else:
                            unchanged_count += 1
                            print(f"[INFO] 比赛记录已存在，跳过: {match_data.get('match_id', 'N/A')}")
                else:
                    failed_parsing_count += 1
                    print(f"[WARNING] 解析比赛数据失败，跳过第 {i+1} 个项目")
            
            session.commit()
            
            end_time = dt.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            if count == 0:
                success_msg = (
                    f"获取成功，获取数量：0；数据库未新增数据条数。共处理 {processed_count} 条原始数据，"
                    f"更新 {updated_count} 条，未变化 {unchanged_count} 条，解析失败 {failed_parsing_count} 条。"
                )
                print(f"[INFO] {success_msg}")
                # 清除之前的错误信息
                db_data_source.last_error = None
                db_data_source.last_error_time = None
                db.commit()
                
                # 记录详细日志
                log_service.create_log_entry(LogEntryCreate(
                    timestamp=dt.utcnow(),
                    level="INFO",
                    message=f"100qiu数据源 {source_id} 获取完成: {success_msg}",
                    module="data_source_100qiu",
                    user_id=None,
                    extra_data=json.dumps({
                        "source_id": source_id,
                        "total_fetched": 0,
                        "processed_count": processed_count,
                        "updated_count": updated_count,
                        "unchanged_count": unchanged_count,
                        "failed_parsing_count": failed_parsing_count,
                        "duration_seconds": duration,
                        "action": "fetch_success_zero_detailed",
                        "request_trace": request_trace,
                    }, ensure_ascii=False)
                ))
                
                response_obj = FetchDataResponse(
                    success=True,
                    message=success_msg,
                    total_fetched=count,
                    sample_data=matches_data[:3] if matches_data else [],
                    request_trace=request_trace,
                )
            else:
                success_msg = (
                    f"成功获取并存储了 {count} 条比赛数据 (共处理 {processed_count} 条原始数据，"
                    f"更新 {updated_count} 条，未变化 {unchanged_count} 条，解析失败 {failed_parsing_count} 条)"
                )
                print(f"[INFO] {success_msg}")
                # 清除之前的错误信息
                db_data_source.last_error = None
                db_data_source.last_error_time = None
                db.commit()
                
                # 记录成功日志
                log_service.create_log_entry(LogEntryCreate(
                    timestamp=dt.utcnow(),
                    level="INFO",
                    message=f"100qiu数据源 {source_id} 获取成功: {success_msg}",
                    module="data_source_100qiu",
                    user_id=None,
                    extra_data=json.dumps({
                        "source_id": source_id,
                        "total_fetched": count,
                        "processed_count": processed_count,
                        "updated_count": updated_count,
                        "unchanged_count": unchanged_count,
                        "failed_parsing_count": failed_parsing_count,
                        "duration_seconds": duration,
                        "action": "fetch_success",
                        "request_trace": request_trace,
                    }, ensure_ascii=False)
                ))
                
                response_obj = FetchDataResponse(
                    success=True,
                    message=success_msg,
                    total_fetched=count,
                    sample_data=matches_data[:3] if matches_data else [],
                    request_trace=request_trace,
                )
            
            return response_obj
        except Exception as e:
            session.rollback()
            error_msg = f"数据存储失败: {str(e)}"
            print(f"[ERROR] {error_msg}")
            # 更新数据源错误信息
            db_data_source.last_error = error_msg
            db_data_source.last_error_time = datetime.utcnow()
            db.commit()
            
            # 记录错误日志
            log_service.create_log_entry(LogEntryCreate(
                timestamp=dt.utcnow(),
                level="ERROR",
                message=f"100qiu数据源 {source_id} 数据存储失败: {error_msg}",
                module="data_source_100qiu",
                user_id=None,
                extra_data=json.dumps({
                    "source_id": source_id,
                    "action": "fetch_failed",
                    "error_type": "database_error",
                    "processed_count": processed_count,
                    "request_trace": request_trace,
                }, ensure_ascii=False)
            ))
            
            return {
                "success": False,
                "message": error_msg,
                "data": FetchDataResponse(
                    success=False,
                    message=error_msg,
                    total_fetched=0,
                    request_trace=request_trace,
                ).dict()
            }
        finally:
            session.close()
    
    except Exception as e:
        error_msg = f"获取数据失败: {str(e)}"
        print(f"[ERROR] {error_msg}")
        try:
            db.rollback()
        except Exception:
            pass
        # 更新数据源错误信息
        if 'db_data_source' in locals():
            try:
                db_data_source.last_error = error_msg
                db_data_source.last_error_time = datetime.utcnow()
                db.commit()
            except Exception:
                db.rollback()
        
        # 记录错误日志
        log_service.create_log_entry(LogEntryCreate(
            timestamp=dt.utcnow(),
            level="ERROR",
            message=f"100qiu数据源 {source_id} 获取异常: {error_msg}",
            module="data_source_100qiu",
            user_id=None,
            extra_data=json.dumps({
                "source_id": source_id,
                "action": "fetch_exception",
                "error_type": "unexpected_error",
                "request_trace": request_trace,
            }, ensure_ascii=False)
        ))
        
        return {
            "success": False,
            "message": error_msg,
            "data": FetchDataResponse(
                success=False,
                message=error_msg,
                total_fetched=0,
                request_trace=request_trace,
            ).dict()
        }


def parse_match_from_100qiu(item: Dict[str, Any], date_time: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    从100qiu API响应中解析比赛数据
    这里根据实际API响应结构进行解析
    """
    try:
        # 提取基本字段
        line_id = str(item.get('lineId', ''))
        home_team = item.get('homeTeam', '未知主队')
        away_team = item.get('guestTeam', '未知客队')  # 注意：100qiu使用guestTeam而不是awayTeam
        league = item.get('gameShortName', '未知联赛')
        
        # 处理比赛时间
        match_time_str = item.get('matchTimeStr', None)
        match_time = None
        if match_time_str:
            if isinstance(match_time_str, str):
                try:
                    # 100qiu返回的是"YYYY-MM-DD"格式
                    from datetime import datetime
                    match_time = datetime.strptime(match_time_str, "%Y-%m-%d")
                except ValueError:
                    # 如果解析失败，使用当前时间
                    match_time = datetime.now()
        else:
            match_time = datetime.now()
        
        # 获取比分信息
        home_score = None
        away_score = None
        
        # 状态默认为pending（未开始）
        status = 'pending'
        
        # 提取基本字段
        line_id_str = str(item.get('lineId', '')).strip()
        
        # 转换期号和序号为整数
        try:
            date_time_int = int(date_time) if date_time else 0
            line_id_int = int(line_id_str) if line_id_str else 0
        except ValueError:
            date_time_int = 0
            line_id_int = 0
        
        # 生成新的match_id格式：date_time_line_id（如：26024_001）
        if date_time_int > 0 and line_id_int > 0:
            match_id = f"{date_time_int}_{line_id_int:03d}"
        elif line_id_str:
            # 兼容旧格式
            match_id = f"100qiu_{line_id_str}"
        else:
            # 如果没有有效数据，使用时间戳生成临时ID
            import time
            match_id = f"{int(time.time() * 1000)}"
        
        # 确保date_time不为None（数据库约束可能为NOT NULL）
        final_date_time = date_time_int if date_time_int != 0 else 26022  # 默认期号
        # 确保line_id不为0
        final_line_id = line_id_int if line_id_int != 0 else 1
        
        # 调试：打印关键值
        print(f"[DEBUG] parse_match_from_100qiu内部: date_time参数={date_time}, date_time_int={date_time_int}, final_date_time={final_date_time}, line_id_int={line_id_int}, final_line_id={final_line_id}")
        
        # 将date_time和line_id添加到source_attributes中
        source_attributes = item.copy()
        source_attributes['date_time'] = final_date_time
        source_attributes['line_id'] = final_line_id
        
        # 返回符合FootballMatch模型的字段
        match_data = {
            "match_id": match_id,
            "date_time": final_date_time,
            "line_id": final_line_id,
            "home_team": home_team,
            "away_team": away_team,
            "match_time": match_time,
            "league": league,
            "status": status,
            "home_score": home_score,
            "away_score": away_score,
            "data_source": "100qiu",
            "source_attributes": source_attributes
        }
        
        # 调试：打印返回的match_data中的date_time值
        print(f"[DEBUG] parse_match_from_100qiu返回的match_data['date_time']: {match_data['date_time']} (类型: {type(match_data['date_time'])})")
        print(f"[DEBUG] parse_match_from_100qiu返回的match_data['line_id']: {match_data['line_id']} (类型: {type(match_data['line_id'])})")
        
        return match_data
    except Exception as e:
        print(f"解析比赛数据失败: {e}")
        return None
