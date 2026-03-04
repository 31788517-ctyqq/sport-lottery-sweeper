"""
Entity mapping and official-info management APIs.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Tuple

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.database import SessionLocal
from backend.config.entity_mappings import LEAGUE_MAPPINGS, TEAM_MAPPINGS
from backend.models.entity_mapping_record import EntityMappingRecord
from backend.services.data_processor import MatchDataProcessor
from backend.services.entity_mapping_sync_service import entity_mapping_sync_service
from backend.services.official_info_service import official_info_service
from backend.utils.logger import get_logger

router = APIRouter(prefix="/entity-mapping", tags=["entity-mapping"])
logger = get_logger(__name__)

VALID_ENTITY_TYPES = {"team", "league"}


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
    return {
        "zh": row.zh_names or [],
        "en": row.en_names or [],
        "jp": row.jp_names or [],
        "source_aliases": row.source_aliases or {},
        "official_info": row.official_info or {},
        "canonical_key": row.canonical_key,
        "display_name": row.display_name,
        "confidence_score": row.confidence_score,
        "auto_generated": bool(row.auto_generated),
        "last_seen_at": row.last_seen_at.isoformat() if row.last_seen_at else None,
    }


def _load_db_mappings(entity_type: str) -> Dict[str, Dict[str, Any]]:
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
        return JSONResponse(content={"status": "success", "data": {"summary": summary}})
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to get official-info summary: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})


@router.post("/official-info/verify/{entity_type}/{entity_id}")
async def verify_official_info(entity_type: str, entity_id: str) -> JSONResponse:
    """Verify official links for a single entity."""
    if entity_type not in VALID_ENTITY_TYPES:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid entity type"})

    mappings, _ = _get_entity_mapping(entity_type)
    entity_data = (mappings or {}).get(entity_id)
    if not entity_data or "official_info" not in entity_data:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Entity not found"})

    try:
        result = await official_info_service.verify_entity_official_info(entity_type, entity_id, entity_data["official_info"])
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

    targets: list[tuple[str, str]]
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


@router.get("/mappings/{entity_type}")
async def get_entity_mappings(entity_type: str) -> JSONResponse:
    """Return entity mapping config (DB first, static fallback)."""
    if entity_type not in VALID_ENTITY_TYPES:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid entity type. Must be 'team' or 'league'."},
        )

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


@router.put("/mappings/{entity_type}/{entity_id}")
async def update_entity_mapping(entity_type: str, entity_id: str, updates: Dict[str, Any]) -> JSONResponse:
    """Update mapping fields for an entity."""
    if entity_type not in VALID_ENTITY_TYPES:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid entity type. Must be 'team' or 'league'."},
        )

    # Try DB update first.
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
            if "zh" in updates:
                row.zh_names = _normalize_text_list(updates.get("zh"))
            if "en" in updates:
                row.en_names = _normalize_text_list(updates.get("en"))
            if "jp" in updates:
                row.jp_names = _normalize_text_list(updates.get("jp"))
            if "source_aliases" in updates:
                row.source_aliases = _normalize_source_aliases(updates.get("source_aliases"))
            if "official_info" in updates and isinstance(updates.get("official_info"), dict):
                merged = dict(row.official_info or {})
                merged.update(updates.get("official_info") or {})
                row.official_info = merged
            if "display_name" in updates:
                row.display_name = str(updates.get("display_name") or row.display_name or "")
            if "canonical_key" in updates:
                row.canonical_key = str(updates.get("canonical_key") or row.canonical_key or "")
            if "confidence_score" in updates:
                try:
                    row.confidence_score = float(updates.get("confidence_score"))
                except (TypeError, ValueError):
                    pass
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


@router.get("/sync/status")
async def get_entity_mapping_sync_status() -> JSONResponse:
    """Return current status snapshot of entity mapping sync service."""
    db = SessionLocal()
    try:
        snapshot = entity_mapping_sync_service.get_status_snapshot(db)
        return JSONResponse(content={"status": "success", "data": snapshot})
    except Exception as exc:  # pragma: no cover - defensive path
        logger.error("Failed to fetch entity mapping sync status: %s", exc, exc_info=True)
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
