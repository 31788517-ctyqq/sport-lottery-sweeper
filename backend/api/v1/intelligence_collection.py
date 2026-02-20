from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from ....database_async import get_async_db
from ....models.intelligence_collection import (
    IntelligenceChannelBinding,
    IntelligenceCollectionItem,
    IntelligenceCollectionTask,
    IntelligencePushTask,
    IntelligenceUserSubscription,
)
from ....models.match import League, Match, Team
from ...deps import get_current_admin
from ....services.dingtalk_integration import send_dingtalk_message


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


def _task_to_dict(task: IntelligenceCollectionTask) -> Dict[str, Any]:
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
        "total_count": task.total_count,
        "success_count": task.success_count,
        "failed_count": task.failed_count,
        "retry_count": task.retry_count,
        "late_run": task.late_run,
        "planned_at": task.planned_at.isoformat() if task.planned_at else None,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "finished_at": task.finished_at.isoformat() if task.finished_at else None,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


class TaskCreateRequest(BaseModel):
    match_ids: List[int] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    intel_types: List[str] = Field(default_factory=list)
    mode: str = "immediate"  # immediate/scheduled
    offset_hours: List[int] = Field(default_factory=list)


class PushPreviewRequest(BaseModel):
    user_risk_profile: str = "balanced"
    max_evidence: int = 3


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


async def _simulate_collect_items(
    db: AsyncSession,
    task: IntelligenceCollectionTask,
    match_ids: List[int],
    sources: List[str],
    intel_types: List[str],
) -> int:
    created = 0
    now = datetime.utcnow()
    for match_id in match_ids:
        for source in sources:
            for intel_type in intel_types:
                cat = "prediction" if intel_type in PREDICTION_TYPES else "off_field"
                item = IntelligenceCollectionItem(
                    task_id=task.id,
                    match_id=match_id,
                    source_code=source,
                    intel_category=cat,
                    intel_type=intel_type,
                    title=f"{intel_type} - {source}",
                    content_raw=f"来源观点：{source} 对比赛 {match_id} 的 {intel_type} 情报更新。",
                    source_url=SOURCE_URL_MAP.get(source, ""),
                    published_at=now,
                    crawled_at=now,
                    confidence=round(0.58 + ((match_id + len(source) + len(intel_type)) % 35) / 100, 2),
                )
                db.add(item)
                created += 1
    return created


@router.get("/sources")
async def get_sources(
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    source_codes = list(SOURCE_URL_MAP.keys())
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
        }
        for code in source_codes
    ]
    return _ok(items)


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


@router.post("/tasks")
async def create_collection_task(
    payload: TaskCreateRequest = Body(...),
    db: AsyncSession = Depends(get_async_db),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    if not payload.match_ids:
        raise HTTPException(status_code=400, detail="match_ids 不能为空")
    if not payload.sources:
        raise HTTPException(status_code=400, detail="sources 不能为空")
    if not payload.intel_types:
        raise HTTPException(status_code=400, detail="intel_types 不能为空")

    mode = payload.mode if payload.mode in {"immediate", "scheduled"} else "immediate"
    task = IntelligenceCollectionTask(
        task_uuid=uuid.uuid4().hex,
        task_name=f"情报采集-{datetime.utcnow().strftime('%m%d-%H%M%S')}",
        mode=mode,
        status="running" if mode == "immediate" else "pending",
        match_ids_json=_json_dumps(payload.match_ids),
        sources_json=_json_dumps(payload.sources),
        intel_types_json=_json_dumps(payload.intel_types),
        offset_hours_json=_json_dumps(payload.offset_hours or []),
        created_by=int(current_admin.get("id") or 0),
        started_at=datetime.utcnow() if mode == "immediate" else None,
        planned_at=datetime.utcnow() if mode == "immediate" else datetime.utcnow() + timedelta(minutes=5),
    )
    _append_log(task, "info", "任务已创建")
    db.add(task)
    await db.flush()

    if mode == "immediate":
        created_count = await _simulate_collect_items(
            db=db,
            task=task,
            match_ids=payload.match_ids,
            sources=payload.sources,
            intel_types=payload.intel_types,
        )
        task.total_count = created_count
        task.success_count = created_count
        task.failed_count = 0
        task.status = "success"
        task.finished_at = datetime.utcnow()
        _append_log(task, "success", f"采集完成，新增 {created_count} 条情报")
    else:
        task.total_count = len(payload.match_ids) * len(payload.sources) * len(payload.intel_types)
        _append_log(task, "info", "计划任务已入队，等待调度执行")

    await db.commit()
    await db.refresh(task)
    return _ok(_task_to_dict(task), "任务创建成功")


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
    conditions = []
    if status:
        conditions.append(IntelligenceCollectionTask.status == status)
    if mode:
        conditions.append(IntelligenceCollectionTask.mode == mode)

    stmt = select(IntelligenceCollectionTask).where(*conditions).order_by(IntelligenceCollectionTask.created_at.desc())
    total_stmt = select(func.count(IntelligenceCollectionTask.id)).where(*conditions)
    total = int((await db.execute(total_stmt)).scalar() or 0)
    rows = (await db.execute(stmt.offset((page - 1) * size).limit(size))).scalars().all()
    return _ok({"items": [_task_to_dict(x) for x in rows], "total": total, "page": page, "size": size})


@router.get("/tasks/{task_id}")
async def get_collection_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    task = await db.get(IntelligenceCollectionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return _ok(_task_to_dict(task))


@router.get("/tasks/{task_id}/logs")
async def get_collection_task_logs(
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    task = await db.get(IntelligenceCollectionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return _ok({"task_id": task_id, "logs": _json_loads(task.logs_json, [])})


@router.post("/tasks/{task_id}/retry")
async def retry_collection_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    task = await db.get(IntelligenceCollectionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.retry_count += 1
    task.status = "running"
    task.started_at = datetime.utcnow()
    _append_log(task, "info", f"触发重试，第 {task.retry_count} 次")

    match_ids = _json_loads(task.match_ids_json, [])
    sources = _json_loads(task.sources_json, [])
    intel_types = _json_loads(task.intel_types_json, [])
    created = await _simulate_collect_items(db, task, match_ids, sources, intel_types)
    task.total_count += created
    task.success_count += created
    task.status = "success"
    task.finished_at = datetime.utcnow()
    _append_log(task, "success", f"重试完成，新增 {created} 条")
    await db.commit()
    await db.refresh(task)
    return _ok(_task_to_dict(task), "重试已执行")


@router.post("/tasks/{task_id}/cancel")
async def cancel_collection_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
    _: Dict[str, Any] = Depends(get_current_admin),
):
    task = await db.get(IntelligenceCollectionTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.status in {"success", "failed", "cancelled"}:
        return _ok(_task_to_dict(task), "任务已结束，无需取消")
    task.status = "cancelled"
    task.finished_at = datetime.utcnow()
    _append_log(task, "warning", "任务已取消")
    await db.commit()
    await db.refresh(task)
    return _ok(_task_to_dict(task), "任务已取消")


@router.get("/matches/{match_id}/items")
async def get_match_items(
    match_id: int,
    category: Optional[str] = Query(None),
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

    items = [
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
        }
        for x in rows
    ]
    return _ok({"match_id": match_id, "items": items, "total": len(items)})


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
                "headline": "暂无可推送情报",
                "confidence": 0.0,
                "evidence": [],
                "risk_level": "high",
            }
        )

    confidence = round(sum(x.confidence for x in rows) / len(rows), 2)
    evidence = [
        {
            "source": x.source_code,
            "intel_type": x.intel_type,
            "content": x.content_raw,
            "time": x.crawled_at.strftime("%Y-%m-%d %H:%M:%S") if x.crawled_at else None,
        }
        for x in rows[: max(1, payload.max_evidence)]
    ]
    risk_level = "low" if confidence >= 0.75 else ("medium" if confidence >= 0.62 else "high")
    headline = f"比赛 {match_id} 情报汇总：置信度 {confidence}"
    return _ok(
        {
            "match_id": match_id,
            "status": "ready" if confidence >= 0.6 else "observe",
            "headline": headline,
            "confidence": confidence,
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
        raise HTTPException(status_code=400, detail="该绑定已禁用")

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
    return _ok({"id": push_task.id, "status": push_task.status}, "推送任务已创建")
