"""
Entity mapping and official-info management APIs.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Tuple

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from backend.database import SessionLocal
from backend.config.entity_mappings import LEAGUE_MAPPINGS, TEAM_MAPPINGS
from backend.models.entity_mapping_record import EntityMappingRecord, EntityMappingSyncRun
from backend.services.data_processor import MatchDataProcessor
from backend.services.entity_mapping_sync_service import entity_mapping_sync_service
from backend.services.official_info_service import official_info_service
from backend.utils.logger import get_logger

router = APIRouter(prefix="/entity-mapping", tags=["entity-mapping"])
logger = get_logger(__name__)

VALID_ENTITY_TYPES = {"team", "league"}
VALID_REVIEW_STATUS = {
    entity_mapping_sync_service.REVIEW_AUTO_ACCEPTED,
    entity_mapping_sync_service.REVIEW_PENDING,
    entity_mapping_sync_service.REVIEW_REVIEWED,
}


def _ensure_mapping_schema_ready() -> None:
    try:
        entity_mapping_sync_service.ensure_schema()
    except Exception as exc:  # pragma: no cover - defensive path
        logger.warning("Ensure entity mapping schema failed: %s", exc)


def _get_entity_mapping(entity_type: str) -> Tuple[Dict[str, Dict[str, Any]] | None, str | None]:
    if entity_type == "team":
        return TEAM_MAPPINGS, None
    if entity_type == "league":
        return LEAGUE_MAPPINGS, None
    return None, "Invalid entity type. Must be 'team' or 'league'."


def _normalize_text_list(value: Any) -> List[str]:
    if isinstance(value, list):
        candidates = value
    elif isinstance(value, str):
        candidates = [item.strip() for item in value.split(",")]
    else:
        candidates = []

    result: List[str] = []
    seen = set()
    for item in candidates:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _normalize_source_aliases(value: Any) -> Dict[str, List[str]]:
    if not isinstance(value, dict):
        return {}
    normalized: Dict[str, List[str]] = {}
    for source, aliases in value.items():
        source_key = str(source or "").strip()
        if not source_key:
            continue
        normalized[source_key] = _normalize_text_list(aliases)
    return normalized


def _to_mapping_payload(row: EntityMappingRecord) -> Dict[str, Any]:
    official_info = row.official_info or {}
    return {
        "zh": row.zh_names or [],
        "en": row.en_names or [],
        "jp": row.jp_names or [],
        "source_aliases": row.source_aliases or {},
        "official_info": official_info,
        "canonical_key": row.canonical_key,
        "display_name": row.display_name,
        "confidence_score": row.confidence_score,
        "quality_score": row.quality_score,
        "alias_count": row.alias_count,
        "conflict_count": row.conflict_count,
        "review_status": row.review_status,
        "official_enrich_status": row.official_enrich_status,
        "official_enrich_error": row.official_enrich_error,
        "official_last_attempt_at": row.official_last_attempt_at.isoformat() if row.official_last_attempt_at else None,
        "official_last_success_at": row.official_last_success_at.isoformat() if row.official_last_success_at else None,
        "official_source_tag": official_info.get("source_tag"),
        "official_last_enriched_at": official_info.get("last_enriched_at"),
        "auto_generated": bool(row.auto_generated),
        "last_seen_at": row.last_seen_at.isoformat() if row.last_seen_at else None,
    }


def _to_mapping_item(row: EntityMappingRecord) -> Dict[str, Any]:
    payload = _to_mapping_payload(row)
    payload["id"] = str(row.entity_ref_id)
    payload["entity_ref_id"] = str(row.entity_ref_id)
    return payload


def _load_db_mappings(entity_type: str) -> Dict[str, Dict[str, Any]]:
    _ensure_mapping_schema_ready()
    db = SessionLocal()
    try:
        rows: Iterable[EntityMappingRecord] = (
            db.query(EntityMappingRecord)
            .filter(EntityMappingRecord.entity_type == entity_type)
            .order_by(EntityMappingRecord.display_name.asc(), EntityMappingRecord.id.asc())
            .all()
        )
        result: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            result[str(row.entity_ref_id)] = _to_mapping_payload(row)
        return result
    finally:
        db.close()


def _load_db_mapping_items(entity_type: str) -> List[Dict[str, Any]]:
    _ensure_mapping_schema_ready()
    db = SessionLocal()
    try:
        rows: Iterable[EntityMappingRecord] = (
            db.query(EntityMappingRecord)
            .filter(EntityMappingRecord.entity_type == entity_type)
            .order_by(EntityMappingRecord.display_name.asc(), EntityMappingRecord.id.asc())
            .all()
        )
        return [_to_mapping_item(row) for row in rows]
    finally:
        db.close()


def _load_entity_official_info(entity_type: str, entity_id: str) -> Dict[str, Any] | None:
    _ensure_mapping_schema_ready()
    db = SessionLocal()
    try:
        row = (
            db.query(EntityMappingRecord)
            .filter(
                EntityMappingRecord.entity_type == entity_type,
                EntityMappingRecord.entity_ref_id == str(entity_id),
            )
            .first()
        )
        if row:
            return dict(row.official_info or {})
    finally:
        db.close()

    mappings, _ = _get_entity_mapping(entity_type)
    if not mappings:
        return None
    entity = mappings.get(str(entity_id))
    if not entity:
        return None
    return dict(entity.get("official_info") or {})


def _static_to_mapping_items(mappings: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for entity_id, payload in (mappings or {}).items():
        official_info = payload.get("official_info") or {}
        item = {
            "id": str(entity_id),
            "entity_ref_id": str(entity_id),
            "zh": payload.get("zh") or [],
            "en": payload.get("en") or [],
            "jp": payload.get("jp") or [],
            "source_aliases": payload.get("source_aliases") or {},
            "official_info": official_info,
            "canonical_key": payload.get("canonical_key"),
            "display_name": payload.get("display_name"),
            "confidence_score": payload.get("confidence_score"),
            "quality_score": payload.get("quality_score", 1.0),
            "alias_count": payload.get("alias_count", 0),
            "conflict_count": payload.get("conflict_count", 0),
            "review_status": payload.get("review_status", entity_mapping_sync_service.REVIEW_AUTO_ACCEPTED),
            "official_enrich_status": payload.get("official_enrich_status", "pending"),
            "official_enrich_error": payload.get("official_enrich_error"),
            "official_last_attempt_at": payload.get("official_last_attempt_at"),
            "official_last_success_at": payload.get("official_last_success_at"),
            "official_source_tag": official_info.get("source_tag"),
            "official_last_enriched_at": official_info.get("last_enriched_at"),
            "auto_generated": payload.get("auto_generated", False),
            "last_seen_at": payload.get("last_seen_at"),
        }
        items.append(item)
    return items


def _iter_alias_values(source_aliases: Any) -> Iterable[str]:
    if not isinstance(source_aliases, dict):
        return []
    values: List[str] = []
    for aliases in source_aliases.values():
        if isinstance(aliases, list):
            values.extend(str(alias or "") for alias in aliases)
        elif aliases is not None:
            values.append(str(aliases))
    return values


def _normalize_search_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _item_matches_filters(
    item: Dict[str, Any],
    *,
    search: str | None,
    review_status: str | None,
    only_conflicts: bool,
    only_missing_official: bool,
) -> bool:
    if only_conflicts and int(item.get("conflict_count") or 0) <= 0:
        return False

    if only_missing_official and not _is_missing_official_links(item.get("official_info")):
        return False

    if review_status and str(item.get("review_status") or "") != review_status:
        return False

    if search:
        keyword = _normalize_search_text(search)
        fields: List[str] = [
            item.get("id"),
            item.get("entity_ref_id"),
            item.get("display_name"),
            item.get("canonical_key"),
        ]
        fields.extend(item.get("zh") or [])
        fields.extend(item.get("en") or [])
        fields.extend(item.get("jp") or [])
        fields.extend(_iter_alias_values(item.get("source_aliases") or {}))

        normalized_fields = [_normalize_search_text(field) for field in fields if str(field or "").strip()]
        if not any(keyword in field for field in normalized_fields):
            return False

    return True


def _is_missing_official_links(official_info: Any) -> bool:
    if not isinstance(official_info, dict):
        return True
    for key in ("website", "twitter", "facebook", "instagram", "weibo"):
        if str(official_info.get(key) or "").strip():
            return False
    return True


def _paginate_items(items: List[Dict[str, Any]], page: int, size: int) -> Dict[str, Any]:
    total = len(items)
    start = (page - 1) * size
    end = start + size
    paged = items[start:end]
    return {
        "items": paged,
        "total": total,
        "page": page,
        "size": size,
        "has_more": end < total,
    }


def _build_ops_overview_payload(db) -> Dict[str, Any]:
    now = datetime.utcnow()
    window_start = now - timedelta(days=7)

    recent_runs: List[EntityMappingSyncRun] = (
        db.query(EntityMappingSyncRun)
        .filter(EntityMappingSyncRun.started_at >= window_start)
        .order_by(EntityMappingSyncRun.started_at.desc())
        .all()
    )
    completed_runs = [run for run in recent_runs if str(run.status or "").lower() in {"success", "failed"}]
    success_runs = [run for run in completed_runs if str(run.status or "").lower() == "success"]

    sync_success_rate_7d = 0.0
    if completed_runs:
        sync_success_rate_7d = round((len(success_runs) / len(completed_runs)) * 100, 2)

    latest_failed_run = (
        db.query(EntityMappingSyncRun)
        .filter(EntityMappingSyncRun.status == "failed")
        .order_by(EntityMappingSyncRun.started_at.desc())
        .first()
    )

    latest_finished_run = (
        db.query(EntityMappingSyncRun)
        .filter(EntityMappingSyncRun.finished_at.isnot(None))
        .order_by(EntityMappingSyncRun.finished_at.desc())
        .first()
    )

    pending_conflicts = (
        db.query(EntityMappingRecord)
        .filter(
            EntityMappingRecord.conflict_count > 0,
            EntityMappingRecord.review_status == entity_mapping_sync_service.REVIEW_PENDING,
        )
        .count()
    )
    total_conflicts = db.query(EntityMappingRecord).filter(EntityMappingRecord.conflict_count > 0).count()

    enrich_status = official_info_service.get_enrich_status_snapshot("all")
    enrich_summary = enrich_status.get("summary") or {}

    last_failed_at = None
    last_failed_message = None
    if latest_failed_run:
        last_failed_message = latest_failed_run.error_message
        fail_time = latest_failed_run.finished_at or latest_failed_run.started_at
        last_failed_at = fail_time.isoformat() if fail_time else None

    return {
        "sync_success_rate_7d": sync_success_rate_7d,
        "last_failed_at": last_failed_at,
        "last_failed_message": last_failed_message,
        "pending_conflicts": int(pending_conflicts or 0),
        "total_conflicts": int(total_conflicts or 0),
        "official_enrich_running": bool(enrich_status.get("is_running")),
        "official_enrich_pending": int(enrich_summary.get("pending") or 0),
        "official_enrich_failed": int(enrich_summary.get("failed") or 0),
        "last_sync_finished_at": (
            latest_finished_run.finished_at.isoformat()
            if latest_finished_run and latest_finished_run.finished_at
            else None
        ),
    }


@router.post("/matches/standardize")
async def standardize_match_data(raw_data: Dict[str, Any], source_id: str = Query(...)):
    """
    Standardize raw match payload by mapping team and league names.
    """
    processor = MatchDataProcessor({"source_id": source_id})
    required_fields = ["home_team", "away_team", "match_time"]
    missing = [field for field in required_fields if field not in raw_data]
    if missing:
        return JSONResponse(status_code=422, content={"error": "Missing required fields", "missing": missing})

    try:
        standardized = processor.process_match_data(raw_data)
        if not standardized.get("home_team_id") or not standardized.get("away_team_id"):
            return JSONResponse(
                status_code=400,
                content={"error": "Unable to resolve team names", "data": raw_data},
            )
        return {"standardized_data": standardized}
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to standardize match payload: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Internal server error", "message": str(exc)})


def _calculate_summary_from_mapping_data() -> Dict[str, Any]:
    _ensure_mapping_schema_ready()
    db = SessionLocal()
    try:
        rows = (
            db.query(EntityMappingRecord)
            .filter(EntityMappingRecord.entity_type.in_(["team", "league"]))
            .all()
        )
    finally:
        db.close()

    if not rows:
        return _calculate_summary_from_static_data()

    now = datetime.utcnow()
    total = len(rows)
    valid = 0
    invalid = 0
    needs_update = 0
    for row in rows:
        info = dict(row.official_info or {})
        if bool(info.get("verified", False)):
            valid += 1
        else:
            invalid += 1

        last_success = row.official_last_success_at
        if not last_success:
            last_verified = info.get("last_verified")
            if last_verified:
                try:
                    last_success = datetime.fromisoformat(
                        str(last_verified).replace("Z", "+00:00").replace("+00:00", "")
                    )
                except ValueError:
                    last_success = None
        if not last_success or now - last_success > timedelta(days=30):
            needs_update += 1

    return {
        "total": total,
        "valid": valid,
        "invalid": invalid,
        "needs_update": needs_update,
        "last_verified": now.isoformat(),
        "valid_rate": round(valid / total, 4) if total else 0.0,
        "stale_rate": round(needs_update / total, 4) if total else 0.0,
    }


def _calculate_summary_from_static_data() -> Dict[str, Any]:
    total = 0
    valid = 0
    invalid = 0
    needs_update = 0
    now = datetime.utcnow()

    all_mappings = [TEAM_MAPPINGS, LEAGUE_MAPPINGS]
    for mappings in all_mappings:
        for entity in mappings.values():
            total += 1
            official_info = entity.get("official_info", {})
            is_verified = bool(official_info.get("verified", False))
            if is_verified:
                valid += 1
            else:
                invalid += 1

            last_verified = official_info.get("last_verified")
            if not last_verified:
                needs_update += 1
                continue

            try:
                parsed = datetime.fromisoformat(str(last_verified).replace("Z", "+00:00").replace("+00:00", ""))
                if now - parsed > timedelta(days=30):
                    needs_update += 1
            except ValueError:
                needs_update += 1

    return {
        "total": total,
        "valid": valid,
        "invalid": invalid,
        "needs_update": needs_update,
        "last_verified": now.isoformat(),
        "valid_rate": round(valid / total, 4) if total else 0.0,
        "stale_rate": round(needs_update / total, 4) if total else 0.0,
    }


@router.get("/official-info/summary")
async def get_official_info_summary(force_verify: bool = Query(False)) -> JSONResponse:
    """Return verification summary for all entities."""
    try:
        if force_verify:
            result = await official_info_service.verify_all_official_links("all")
            summary = result["summary"]
        else:
            summary = _calculate_summary_from_mapping_data()
        enrich_status = official_info_service.get_enrich_status_snapshot("all")
        summary["last_batch_job_at"] = enrich_status.get("last_finished_at")
        return JSONResponse(
            content={
                "status": "success",
                "data": {
                    "summary": summary,
                    "enrich_status": enrich_status,
                },
            }
        )
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to get official-info summary: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})


@router.post("/official-info/verify/{entity_type}/{entity_id}")
async def verify_official_info(entity_type: str, entity_id: str) -> JSONResponse:
    """Verify official links for a single entity."""
    if entity_type not in VALID_ENTITY_TYPES:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid entity type"})

    official_info = _load_entity_official_info(entity_type, entity_id)
    if not official_info:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Entity not found"})

    try:
        result = await official_info_service.verify_entity_official_info(entity_type, entity_id, official_info)
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Verify official-info failed for %s/%s: %s", entity_type, entity_id, exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})


@router.post("/official-info/verify-all")
async def verify_official_info_all(entity_type: str = Query("all")) -> JSONResponse:
    """Verify official links in batch."""
    if entity_type not in {"all", "teams", "leagues"}:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid entity type"})

    try:
        result = await official_info_service.verify_all_official_links(entity_type)
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Batch verify official-info failed: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})


@router.post("/official-info/discover/{entity_type}/{entity_id}")
async def discover_official_info(entity_type: str, entity_id: str) -> JSONResponse:
    """Discover official links for a single entity."""
    if entity_type not in VALID_ENTITY_TYPES:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid entity type"})

    try:
        result = await official_info_service.discover_official_links(entity_type, entity_id)
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Discover official-info failed for %s/%s: %s", entity_type, entity_id, exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})


@router.post("/official-info/discover-all")
async def discover_official_info_all(entity_type: str = Query("all")) -> JSONResponse:
    """Discover official links in batch."""
    if entity_type not in {"all", "teams", "leagues"}:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid entity type"})

    _ensure_mapping_schema_ready()
    db = SessionLocal()
    try:
        query = db.query(EntityMappingRecord).filter(EntityMappingRecord.entity_type.in_(["team", "league"]))
        if entity_type == "teams":
            query = query.filter(EntityMappingRecord.entity_type == "team")
        elif entity_type == "leagues":
            query = query.filter(EntityMappingRecord.entity_type == "league")
        rows = query.order_by(EntityMappingRecord.id.asc()).all()
    finally:
        db.close()

    targets: list[tuple[str, str]] = [(row.entity_type, str(row.entity_ref_id)) for row in rows]
    if not targets:
        if entity_type == "teams":
            targets = [("team", entity_id) for entity_id in TEAM_MAPPINGS.keys()]
        elif entity_type == "leagues":
            targets = [("league", entity_id) for entity_id in LEAGUE_MAPPINGS.keys()]
        else:
            targets = [("team", entity_id) for entity_id in TEAM_MAPPINGS.keys()]
            targets.extend(("league", entity_id) for entity_id in LEAGUE_MAPPINGS.keys())

    results: Dict[str, Dict[str, Any]] = {"teams": {}, "leagues": {}}
    errors = 0

    for target_type, target_id in targets:
        try:
            discovered = await official_info_service.discover_official_links(target_type, target_id)
            bucket = "teams" if target_type == "team" else "leagues"
            results[bucket][target_id] = discovered
        except Exception as exc:  # pragma: no cover - defensive path
            logger.warning("Discover failed for %s/%s: %s", target_type, target_id, exc)
            errors += 1

    results["summary"] = {
        "total": len(targets),
        "success": len(targets) - errors,
        "failed": errors,
    }
    return JSONResponse(content={"status": "success", "data": results})


@router.put("/official-info/{entity_type}/{entity_id}")
async def update_official_info(entity_type: str, entity_id: str, updates: Dict[str, Any]) -> JSONResponse:
    """Update official-info fields for an entity."""
    if entity_type not in VALID_ENTITY_TYPES:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid entity type"})

    try:
        updated = await official_info_service.update_official_info(entity_type, entity_id, updates)
        if not updated:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Entity not found"})
        return JSONResponse(content={"status": "success", "message": "Official info updated"})
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Update official-info failed for %s/%s: %s", entity_type, entity_id, exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})


@router.post("/official-info/enrich/trigger")
async def trigger_official_info_enrich(
    entity_type: str = Query("all"),
    limit: int = Query(100, ge=1, le=2000),
    only_missing: bool = Query(True),
    min_confidence: float = Query(0.6, ge=0.0, le=1.0),
) -> JSONResponse:
    """Trigger automatic official-info enrichment task."""
    if entity_type not in {"all", "teams", "leagues", "team", "league"}:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid entity type"})
    try:
        payload = official_info_service.trigger_batch_auto_enrich(
            entity_type=entity_type,
            limit=limit,
            only_missing=only_missing,
            min_confidence=min_confidence,
        )
        return JSONResponse(content={"status": "success", "data": payload})
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to trigger official-info enrich: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})


@router.get("/official-info/enrich/status")
async def get_official_info_enrich_status(entity_type: str = Query("all")) -> JSONResponse:
    """Return automatic official-info enrichment task status."""
    if entity_type not in {"all", "teams", "leagues", "team", "league"}:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid entity type"})
    try:
        payload = official_info_service.get_enrich_status_snapshot(entity_type)
        return JSONResponse(content={"status": "success", "data": payload})
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to get official-info enrich status: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})


@router.get("/mappings/{entity_type}")
async def get_entity_mappings(
    entity_type: str,
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    search: str | None = Query(None),
    review_status: str | None = Query(None),
    only_conflicts: bool = Query(False),
    only_missing_official: bool = Query(False),
    paged: bool = Query(False),
) -> JSONResponse:
    """Return entity mapping config (DB first, static fallback)."""
    if entity_type not in VALID_ENTITY_TYPES:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid entity type. Must be 'team' or 'league'."},
        )

    if review_status and review_status not in VALID_REVIEW_STATUS:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "message": "Invalid review_status.",
                "allowed": sorted(VALID_REVIEW_STATUS),
            },
        )

    query_params = set(request.query_params.keys())
    use_paged_mode = paged or bool(
        {"page", "size", "search", "review_status", "only_conflicts", "only_missing_official", "paged"} & query_params
    )

    if not use_paged_mode:
        try:
            db_mappings = _load_db_mappings(entity_type)
        except Exception as exc:  # pragma: no cover - defensive path
            logger.error("Failed to load DB mappings for %s: %s", entity_type, exc, exc_info=True)
            db_mappings = {}

        if db_mappings:
            return JSONResponse(content={"status": "success", "data": db_mappings, "source": "db"})

        mappings, error = _get_entity_mapping(entity_type)
        if error:
            return JSONResponse(status_code=400, content={"status": "error", "message": error})
        return JSONResponse(content={"status": "success", "data": mappings, "source": "static"})

    try:
        items = _load_db_mapping_items(entity_type)
        source = "db"
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to load DB mappings for %s: %s", entity_type, exc, exc_info=True)
        items = []
        source = "db"

    if not items:
        mappings, error = _get_entity_mapping(entity_type)
        if error:
            return JSONResponse(status_code=400, content={"status": "error", "message": error})
        items = _static_to_mapping_items(mappings or {})
        source = "static"

    filtered = [
        item
        for item in items
        if _item_matches_filters(
            item,
            search=search,
            review_status=review_status,
            only_conflicts=only_conflicts,
            only_missing_official=only_missing_official,
        )
    ]
    payload = _paginate_items(filtered, page=page, size=size)
    return JSONResponse(content={"status": "success", "data": payload, "source": source})


@router.get("/conflicts/{entity_type}")
async def get_entity_mapping_conflicts(
    entity_type: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    search: str | None = Query(None),
    review_status: str | None = Query(None),
) -> JSONResponse:
    """Return conflict mappings for review workflow."""
    if entity_type not in VALID_ENTITY_TYPES:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid entity type. Must be 'team' or 'league'."},
        )

    if review_status and review_status not in VALID_REVIEW_STATUS:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "message": "Invalid review_status.",
                "allowed": sorted(VALID_REVIEW_STATUS),
            },
        )

    try:
        items = _load_db_mapping_items(entity_type)
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to load conflict mappings for %s: %s", entity_type, exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})

    filtered = [
        item
        for item in items
        if _item_matches_filters(
            item,
            search=search,
            review_status=review_status,
            only_conflicts=True,
            only_missing_official=False,
        )
    ]
    payload = _paginate_items(filtered, page=page, size=size)
    pending_total = sum(
        1
        for item in filtered
        if str(item.get("review_status") or "") == entity_mapping_sync_service.REVIEW_PENDING
    )
    payload["pending_total"] = pending_total
    payload["summary"] = {
        "total_conflicts": len(filtered),
        "pending_conflicts": pending_total,
    }
    return JSONResponse(content={"status": "success", "data": payload, "source": "db"})


@router.put("/mappings/{entity_type}/{entity_id}")
async def update_entity_mapping(entity_type: str, entity_id: str, updates: Dict[str, Any]) -> JSONResponse:
    """Update mapping fields for an entity."""
    if entity_type not in VALID_ENTITY_TYPES:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid entity type. Must be 'team' or 'league'."},
        )

    # Try DB update first.
    _ensure_mapping_schema_ready()
    db = SessionLocal()
    try:
        row = (
            db.query(EntityMappingRecord)
            .filter(
                EntityMappingRecord.entity_type == entity_type,
                EntityMappingRecord.entity_ref_id == str(entity_id),
            )
            .first()
        )
        if row:
            edited_name_fields = False
            if "zh" in updates:
                row.zh_names = _normalize_text_list(updates.get("zh"))
                edited_name_fields = True
            if "en" in updates:
                row.en_names = _normalize_text_list(updates.get("en"))
                edited_name_fields = True
            if "jp" in updates:
                row.jp_names = _normalize_text_list(updates.get("jp"))
                edited_name_fields = True
            if "source_aliases" in updates:
                row.source_aliases = _normalize_source_aliases(updates.get("source_aliases"))
                edited_name_fields = True
            if "official_info" in updates and isinstance(updates.get("official_info"), dict):
                merged = dict(row.official_info or {})
                merged.update(updates.get("official_info") or {})
                row.official_info = merged
            if "display_name" in updates:
                row.display_name = str(updates.get("display_name") or row.display_name or "")
                edited_name_fields = True
            if "canonical_key" in updates:
                row.canonical_key = str(updates.get("canonical_key") or row.canonical_key or "")
                edited_name_fields = True
            if "confidence_score" in updates:
                try:
                    row.confidence_score = float(updates.get("confidence_score"))
                except (TypeError, ValueError):
                    pass
            if "quality_score" in updates:
                try:
                    row.quality_score = float(updates.get("quality_score"))
                except (TypeError, ValueError):
                    pass
            if "alias_count" in updates:
                try:
                    row.alias_count = max(0, int(updates.get("alias_count")))
                except (TypeError, ValueError):
                    pass
            if "conflict_count" in updates:
                try:
                    row.conflict_count = max(0, int(updates.get("conflict_count")))
                except (TypeError, ValueError):
                    pass
            if "review_status" in updates:
                target_status = str(updates.get("review_status") or "").strip()
                if target_status in VALID_REVIEW_STATUS:
                    row.review_status = target_status
            elif edited_name_fields:
                row.review_status = entity_mapping_sync_service.REVIEW_REVIEWED
            row.updated_at = datetime.utcnow()
            db.commit()
            return JSONResponse(content={"status": "success", "message": "Mapping updated", "source": "db"})
    except Exception as exc:  # pragma: no cover - defensive path
        db.rollback()
        logger.error("Failed to update DB mapping %s/%s: %s", entity_type, entity_id, exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})
    finally:
        db.close()

    # Fallback to static map update for compatibility.
    mappings, error = _get_entity_mapping(entity_type)
    if error:
        return JSONResponse(status_code=400, content={"status": "error", "message": error})
    if entity_id not in (mappings or {}):
        return JSONResponse(status_code=404, content={"status": "error", "message": "Entity not found"})

    current_mapping = mappings[entity_id]
    for key, value in updates.items():
        current_mapping[key] = value
    return JSONResponse(content={"status": "success", "message": "Mapping updated", "source": "static"})


@router.post("/review/{entity_type}/{entity_id}")
async def review_entity_mapping(entity_type: str, entity_id: str, payload: Dict[str, Any]) -> JSONResponse:
    """Mark entity mapping review status manually."""
    if entity_type not in VALID_ENTITY_TYPES:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid entity type. Must be 'team' or 'league'."},
        )

    review_status = str(payload.get("review_status") or entity_mapping_sync_service.REVIEW_REVIEWED).strip()
    if review_status not in VALID_REVIEW_STATUS:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "message": "Invalid review_status.",
                "allowed": sorted(VALID_REVIEW_STATUS),
            },
        )

    _ensure_mapping_schema_ready()
    db = SessionLocal()
    try:
        row = (
            db.query(EntityMappingRecord)
            .filter(
                EntityMappingRecord.entity_type == entity_type,
                EntityMappingRecord.entity_ref_id == str(entity_id),
            )
            .first()
        )
        if not row:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Entity not found"})

        row.review_status = review_status
        row.updated_at = datetime.utcnow()
        db.commit()
        return JSONResponse(
            content={
                "status": "success",
                "data": {
                    "entity_type": entity_type,
                    "entity_id": str(entity_id),
                    "review_status": row.review_status,
                },
            }
        )
    except Exception as exc:  # pragma: no cover - defensive path
        db.rollback()
        logger.error("Failed to review mapping %s/%s: %s", entity_type, entity_id, exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})
    finally:
        db.close()


@router.get("/sync/status")
async def get_entity_mapping_sync_status() -> JSONResponse:
    """Return current status snapshot of entity mapping sync service."""
    db = SessionLocal()
    try:
        snapshot = entity_mapping_sync_service.get_status_snapshot(db)
        latest_failed_run = (
            db.query(EntityMappingSyncRun)
            .filter(EntityMappingSyncRun.status == "failed")
            .order_by(EntityMappingSyncRun.started_at.desc())
            .first()
        )
        if latest_failed_run:
            snapshot["last_error_message"] = latest_failed_run.error_message
            error_time = latest_failed_run.finished_at or latest_failed_run.started_at
            snapshot["last_error_at"] = error_time.isoformat() if error_time else None
        else:
            snapshot["last_error_message"] = None
            snapshot["last_error_at"] = None
        return JSONResponse(content={"status": "success", "data": snapshot})
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to fetch entity mapping sync status: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})
    finally:
        db.close()


@router.get("/ops/overview")
async def get_entity_mapping_ops_overview() -> JSONResponse:
    """Return operations overview for entity-mapping admin dashboards."""
    _ensure_mapping_schema_ready()
    db = SessionLocal()
    try:
        payload = _build_ops_overview_payload(db)
        return JSONResponse(content={"status": "success", "data": payload})
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to fetch entity mapping operations overview: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})
    finally:
        db.close()


@router.post("/sync/trigger")
async def trigger_entity_mapping_sync() -> JSONResponse:
    """Trigger an entity mapping synchronization run immediately."""
    try:
        payload = entity_mapping_sync_service.trigger_run_now(trigger_type="manual")
        return JSONResponse(content={"status": "success", "data": payload})
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to trigger entity mapping sync: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})
