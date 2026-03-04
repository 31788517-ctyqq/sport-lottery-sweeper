"""
Official info verification/discovery/enrichment service.
"""

from __future__ import annotations

import asyncio
import re
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from backend.config import settings
from backend.config.entity_mappings import LEAGUE_MAPPINGS, TEAM_MAPPINGS
from backend.database import SessionLocal
from backend.models.entity_mapping_record import EntityMappingRecord
from backend.utils.logger import get_logger

logger = get_logger(__name__)


PLATFORM_VALIDATION_RULES = {
    "website": r"^https?://[\w\-\.]+(?:/.*)?$",
    "twitter": r"^https?://(?:www\.)?twitter\.com/[\w_]+/?$",
    "facebook": r"^https?://(?:www\.)?facebook\.com/[\w\.\-]+/?$",
    "instagram": r"^https?://(?:www\.)?instagram\.com/[\w\.\-]+/?$",
    "weibo": r"^https?://(?:www\.)?weibo\.com/[\w\.\-]+/?$",
}


class OfficialInfoService:
    OFFICIAL_KEYS = ("website", "twitter", "facebook", "instagram", "weibo")
    ENRICH_PENDING = "pending"
    ENRICH_RUNNING = "running"
    ENRICH_SUCCESS = "success"
    ENRICH_FAILED = "failed"

    def __init__(self, timeout: int = 10, max_retries: int = 3) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self._batch_lock = threading.Lock()
        self._batch_running = False
        self._batch_started_at: Optional[datetime] = None
        self._batch_finished_at: Optional[datetime] = None
        self._last_batch_result: Dict[str, Any] = {}

    async def verify_all_official_links(self, entity_type: str = "all") -> Dict[str, Any]:
        """Verify official links for DB records (fallback to static config)."""
        rows = self._load_target_rows_from_db(entity_type=entity_type, limit=5000, only_missing=False)
        results: Dict[str, Any] = {
            "teams": {},
            "leagues": {},
            "summary": {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "needs_update": 0,
                "last_verified": datetime.utcnow().isoformat(),
            },
        }

        if rows:
            db = SessionLocal()
            try:
                for row in rows:
                    bucket = "teams" if row.entity_type == "team" else "leagues"
                    info = dict(row.official_info or {})
                    verification = await self.verify_entity_official_info(row.entity_type, str(row.entity_ref_id), info)
                    results[bucket][str(row.entity_ref_id)] = verification
                    self._update_summary(results["summary"], verification)

                    info["verified"] = verification["status"] == "valid"
                    info["last_verified"] = datetime.utcnow().isoformat()
                    row.official_info = info
                    row.official_last_attempt_at = datetime.utcnow()
                    if verification["status"] == "valid":
                        row.official_last_success_at = datetime.utcnow()
                        row.official_enrich_status = self.ENRICH_SUCCESS
                        row.official_enrich_error = None
                    else:
                        row.official_enrich_status = self.ENRICH_FAILED
                        row.official_enrich_error = verification.get("message")
                db.commit()
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()
            return results

        return await self._verify_from_static(entity_type)

    async def verify_entity_official_info(
        self,
        entity_type: str,
        entity_id: str,
        official_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Verify one entity's official links."""
        verification_result = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "status": "valid",
            "details": {},
            "last_verified": datetime.utcnow().isoformat(),
            "verification_time": time.time(),
        }

        checked_count = 0
        valid_count = 0
        for platform in self.OFFICIAL_KEYS:
            url = (official_info or {}).get(platform)
            if not url:
                continue
            checked_count += 1
            if not self._validate_url_format(platform, str(url)):
                verification_result["details"][platform] = {
                    "url": url,
                    "status": "invalid_format",
                    "message": "URL 格式无效",
                }
                continue

            try:
                verify_detail = await self._verify_platform_url(platform, str(url))
                verification_result["details"][platform] = verify_detail
                if verify_detail["status"] == "valid":
                    valid_count += 1
            except Exception as exc:  # pragma: no cover - defensive path
                verification_result["details"][platform] = {
                    "url": url,
                    "status": "error",
                    "message": str(exc),
                }

        if checked_count == 0:
            verification_result["status"] = "missing"
            verification_result["message"] = "暂无可验证官方链接"
        elif valid_count == checked_count:
            verification_result["status"] = "valid"
            verification_result["message"] = "全部链接验证通过"
        elif valid_count > 0:
            verification_result["status"] = "partial"
            verification_result["message"] = "部分链接可用"
        else:
            verification_result["status"] = "invalid"
            verification_result["message"] = "链接验证失败"

        return verification_result

    def _validate_url_format(self, platform: str, url: str) -> bool:
        rule = PLATFORM_VALIDATION_RULES.get(platform, PLATFORM_VALIDATION_RULES["website"])
        return bool(re.match(rule, url.strip()))

    async def _verify_platform_url(self, platform: str, url: str) -> Dict[str, Any]:
        result = {
            "url": url,
            "status": "valid",
            "message": "验证成功",
            "http_status": None,
            "redirect_url": None,
            "verification_time": time.time(),
        }
        response = await self._make_request_with_retry(url)
        result["http_status"] = response.status_code
        result["redirect_url"] = str(response.url)
        if response.status_code != 200:
            result["status"] = "unreachable"
            result["message"] = f"HTTP 状态码: {response.status_code}"
            return result

        if platform == "website":
            return self._verify_website(response)
        if platform == "twitter":
            return self._verify_twitter(response, url)
        if platform == "facebook":
            return self._verify_facebook(response, url)
        if platform == "instagram":
            return self._verify_instagram(response, url)
        if platform == "weibo":
            return self._verify_weibo(response, url)
        return result

    async def _make_request_with_retry(self, url: str) -> httpx.Response:
        last_error: Optional[Exception] = None
        headers = {
            "User-Agent": "SportLotterySweeper/1.0 (+https://sweeper365.cn)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers=headers) as client:
                    return await client.get(url)
            except Exception as exc:  # pragma: no cover - defensive path
                last_error = exc
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))
        raise RuntimeError(f"请求失败: {last_error}")

    def _verify_website(self, response: httpx.Response) -> Dict[str, Any]:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        result = {
            "url": str(response.url),
            "status": "valid",
            "message": "验证成功",
            "http_status": response.status_code,
            "title": title[:120] if title else "",
            "has_meta_desc": bool(meta_desc),
            "verification_time": time.time(),
        }
        if "404" in response.text.lower() or not title or len(title) < 3:
            result["status"] = "invalid_content"
            result["message"] = "页面内容无效"
        return result

    def _verify_twitter(self, response: httpx.Response, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(response.text, "html.parser")
        result = {
            "url": url,
            "status": "valid",
            "message": "验证成功",
            "http_status": response.status_code,
            "verification_time": time.time(),
        }
        if not soup.find("meta", property="og:site_name", content="Twitter"):
            result["status"] = "invalid_content"
            result["message"] = "非 Twitter 页面特征"
        return result

    def _verify_facebook(self, response: httpx.Response, url: str) -> Dict[str, Any]:
        result = {
            "url": url,
            "status": "valid",
            "message": "验证成功",
            "http_status": response.status_code,
            "verification_time": time.time(),
        }
        if "facebook.com" not in str(response.url):
            result["status"] = "invalid_content"
            result["message"] = "非 Facebook 域名"
        return result

    def _verify_instagram(self, response: httpx.Response, url: str) -> Dict[str, Any]:
        result = {
            "url": url,
            "status": "valid",
            "message": "验证成功",
            "http_status": response.status_code,
            "verification_time": time.time(),
        }
        if "instagram.com" not in str(response.url):
            result["status"] = "invalid_content"
            result["message"] = "非 Instagram 域名"
        return result

    def _verify_weibo(self, response: httpx.Response, url: str) -> Dict[str, Any]:
        result = {
            "url": url,
            "status": "valid",
            "message": "验证成功",
            "http_status": response.status_code,
            "verification_time": time.time(),
        }
        if "weibo.com" not in str(response.url):
            result["status"] = "invalid_content"
            result["message"] = "非微博域名"
        return result

    def _update_summary(self, summary: Dict[str, Any], verification: Dict[str, Any]) -> None:
        summary["total"] += 1
        status = verification.get("status")
        if status == "valid":
            summary["valid"] += 1
        else:
            summary["invalid"] += 1
        last_verified = verification.get("last_verified")
        if last_verified:
            try:
                parsed = datetime.fromisoformat(str(last_verified).replace("Z", "+00:00").replace("+00:00", ""))
                if datetime.utcnow() - parsed > timedelta(days=30):
                    summary["needs_update"] += 1
            except ValueError:
                summary["needs_update"] += 1

    async def update_official_info(self, entity_type: str, entity_id: str, new_info: Dict[str, Any]) -> bool:
        """Update official info, DB first then static fallback."""
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
                merged = dict(row.official_info or {})
                merged.update(new_info or {})
                merged["last_verified"] = datetime.utcnow().isoformat()
                # Manual updates always win over automatic enrichment.
                merged["source_tag"] = "manual"
                merged["last_enriched_at"] = datetime.utcnow().isoformat()
                if "verified" in (new_info or {}):
                    merged["verified"] = bool(new_info.get("verified"))
                else:
                    merged["verified"] = bool(merged.get("verified", False))

                row.official_info = merged
                row.official_last_attempt_at = datetime.utcnow()
                if merged.get("verified"):
                    row.official_last_success_at = datetime.utcnow()
                    row.official_enrich_status = self.ENRICH_SUCCESS
                    row.official_enrich_error = None
                else:
                    row.official_enrich_status = self.ENRICH_PENDING
                row.updated_at = datetime.utcnow()
                db.commit()
                return True
            db.rollback()
        except Exception as exc:
            db.rollback()
            logger.error("更新官方信息失败 %s/%s: %s", entity_type, entity_id, exc, exc_info=True)
            return False
        finally:
            db.close()

        # Static fallback for compatibility.
        current = TEAM_MAPPINGS.get(entity_id) if entity_type == "team" else LEAGUE_MAPPINGS.get(entity_id)
        if not current:
            return False
        if "official_info" not in current:
            current["official_info"] = {}
        current["official_info"].update(new_info or {})
        current["official_info"]["last_verified"] = datetime.utcnow().isoformat()
        if "verified" in (new_info or {}):
            current["official_info"]["verified"] = bool(new_info.get("verified"))
        else:
            current["official_info"]["verified"] = bool(current["official_info"].get("verified", False))
        return True

    async def discover_official_links(
        self,
        entity_type: str,
        entity_id: str,
        seed_aliases: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Discover official links using DB aliases and conservative heuristics."""
        row = self._load_mapping_row(entity_type, entity_id)
        if not row:
            return {
                "website": None,
                "twitter": None,
                "facebook": None,
                "instagram": None,
                "weibo": None,
                "confidence": 0.0,
                "sources": [],
                "message": "entity_not_found",
            }

        result: Dict[str, Any] = {
            "website": None,
            "twitter": None,
            "facebook": None,
            "instagram": None,
            "weibo": None,
            "confidence": 0.0,
            "sources": [],
        }

        existing_info = dict(row.official_info or {})
        for key in self.OFFICIAL_KEYS:
            if existing_info.get(key):
                result[key] = existing_info[key]
                result["confidence"] = max(result["confidence"], 0.95)
                result["sources"].append("existing_info")

        # If website missing, infer from logo_url domain when available.
        logo_url = str(existing_info.get("logo_url") or "").strip()
        if not result["website"] and logo_url:
            inferred_website = self._infer_website_from_logo(logo_url)
            if inferred_website:
                result["website"] = inferred_website
                result["confidence"] = max(result["confidence"], 0.72)
                result["sources"].append("logo_domain")

        # Parse aliases for explicit URLs.
        alias_urls = self._extract_urls_from_aliases(row.source_aliases)
        if not result["website"] and alias_urls:
            result["website"] = alias_urls[0]
            result["confidence"] = max(result["confidence"], 0.68)
            result["sources"].append("source_alias_url")

        # Optional weak heuristic: english slug -> domain.
        if not result["website"]:
            slug = self._build_slug_from_names(row, seed_aliases or [])
            if slug:
                result["website"] = f"https://www.{slug}.com"
                result["confidence"] = max(result["confidence"], 0.45)
                result["sources"].append("slug_guess")

        # De-duplicate sources.
        result["sources"] = sorted(set(result["sources"]))
        return result

    async def auto_enrich_official_info(
        self,
        entity_type: str,
        entity_id: str,
        seed_aliases: Optional[List[str]] = None,
        min_confidence: float = 0.6,
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        """Enrich one entity's official info and write DB status."""
        db = SessionLocal()
        now = datetime.utcnow()
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
                return {"success": False, "entity_type": entity_type, "entity_id": entity_id, "message": "not_found"}

            row.official_last_attempt_at = now
            row.official_enrich_status = self.ENRICH_RUNNING
            row.official_enrich_error = None
            db.commit()

            discovered = await self.discover_official_links(entity_type, entity_id, seed_aliases=seed_aliases)
            candidate_links = {k: discovered.get(k) for k in self.OFFICIAL_KEYS if discovered.get(k)}
            confidence = float(discovered.get("confidence") or 0.0)
            if not candidate_links:
                row.official_enrich_status = self.ENRICH_FAILED
                row.official_enrich_error = "no_candidate_links"
                row.updated_at = datetime.utcnow()
                db.commit()
                return {
                    "success": False,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "message": "no_candidate_links",
                    "confidence": confidence,
                }

            if confidence < min_confidence:
                row.official_enrich_status = self.ENRICH_FAILED
                row.official_enrich_error = f"low_confidence:{confidence:.2f}"
                row.updated_at = datetime.utcnow()
                db.commit()
                return {
                    "success": False,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "message": "low_confidence",
                    "confidence": confidence,
                }

            merged = dict(row.official_info or {})
            existing_source_tag = str(merged.get("source_tag") or "").strip().lower()
            updated_fields: List[str] = []
            for key, value in candidate_links.items():
                if overwrite or not merged.get(key):
                    merged[key] = value
                    updated_fields.append(key)

            if updated_fields:
                # Do not downgrade manually curated records to auto.
                if existing_source_tag != "manual":
                    merged["source_tag"] = "auto"
                merged["last_enriched_at"] = datetime.utcnow().isoformat()

            verification = await self.verify_entity_official_info(entity_type, entity_id, merged)
            is_success = verification.get("status") in {"valid", "partial"}
            merged["verified"] = verification.get("status") == "valid"
            merged["last_verified"] = datetime.utcnow().isoformat()

            row.official_info = merged
            row.official_enrich_status = self.ENRICH_SUCCESS if is_success else self.ENRICH_FAILED
            row.official_enrich_error = None if is_success else verification.get("message", "verification_failed")
            if is_success:
                row.official_last_success_at = datetime.utcnow()
            row.updated_at = datetime.utcnow()
            db.commit()

            return {
                "success": is_success,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "confidence": confidence,
                "status": verification.get("status"),
                "updated_fields": sorted(updated_fields),
                "sources": discovered.get("sources") or [],
            }
        except Exception as exc:
            db.rollback()
            logger.error("自动补全官方信息失败 %s/%s: %s", entity_type, entity_id, exc, exc_info=True)
            return {"success": False, "entity_type": entity_type, "entity_id": entity_id, "message": str(exc)}
        finally:
            db.close()

    async def batch_auto_enrich(
        self,
        entity_type: str = "all",
        limit: int = 100,
        only_missing: bool = True,
        min_confidence: float = 0.6,
    ) -> Dict[str, Any]:
        """Run batch auto enrichment and persist progress snapshot."""
        rows = self._load_target_rows_from_db(entity_type=entity_type, limit=limit, only_missing=only_missing)
        summary = {
            "entity_type": entity_type,
            "total": len(rows),
            "success": 0,
            "failed": 0,
            "started_at": datetime.utcnow().isoformat(),
            "finished_at": None,
            "details": [],
        }
        for row in rows:
            result = await self.auto_enrich_official_info(
                entity_type=row.entity_type,
                entity_id=str(row.entity_ref_id),
                seed_aliases=[],
                min_confidence=min_confidence,
                overwrite=False,
            )
            summary["details"].append(result)
            if result.get("success"):
                summary["success"] += 1
            else:
                summary["failed"] += 1

        summary["finished_at"] = datetime.utcnow().isoformat()
        return summary

    def trigger_batch_auto_enrich(
        self,
        entity_type: str = "all",
        limit: int = 100,
        only_missing: bool = True,
        min_confidence: float = 0.6,
    ) -> Dict[str, Any]:
        """Trigger batch enrichment asynchronously."""
        if self._batch_running:
            return {
                "started": False,
                "message": "official enrich task is already running",
                "last_result": self._last_batch_result,
            }

        def _runner() -> None:
            if not self._batch_lock.acquire(blocking=False):
                return
            self._batch_running = True
            self._batch_started_at = datetime.utcnow()
            try:
                result = asyncio.run(
                    self.batch_auto_enrich(
                        entity_type=entity_type,
                        limit=limit,
                        only_missing=only_missing,
                        min_confidence=min_confidence,
                    )
                )
                self._last_batch_result = result
            except Exception as exc:  # pragma: no cover - defensive path
                logger.error("官方信息自动补全批任务失败: %s", exc, exc_info=True)
                self._last_batch_result = {
                    "entity_type": entity_type,
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                    "message": str(exc),
                    "started_at": datetime.utcnow().isoformat(),
                    "finished_at": datetime.utcnow().isoformat(),
                }
            finally:
                self._batch_finished_at = datetime.utcnow()
                self._batch_running = False
                self._batch_lock.release()

        thread = threading.Thread(target=_runner, daemon=True, name=f"official-info-enrich-{entity_type}")
        thread.start()
        return {
            "started": True,
            "message": "official enrich task triggered",
            "entity_type": entity_type,
            "limit": limit,
            "only_missing": only_missing,
            "min_confidence": min_confidence,
        }

    def get_enrich_status_snapshot(self, entity_type: str = "all") -> Dict[str, Any]:
        """Return current enrich runtime and DB aggregate status."""
        db = SessionLocal()
        try:
            query = db.query(EntityMappingRecord)
            if entity_type in {"team", "league"}:
                query = query.filter(EntityMappingRecord.entity_type == entity_type)
            rows = query.all()
        finally:
            db.close()

        total = len(rows)
        status_counter = {
            self.ENRICH_PENDING: 0,
            self.ENRICH_RUNNING: 0,
            self.ENRICH_SUCCESS: 0,
            self.ENRICH_FAILED: 0,
        }
        missing_count = 0
        for row in rows:
            status = str(row.official_enrich_status or self.ENRICH_PENDING)
            if status not in status_counter:
                status_counter[status] = 0
            status_counter[status] += 1
            if self._is_missing_official_links(row.official_info):
                missing_count += 1

        return {
            "is_running": self._batch_running,
            "last_started_at": self._batch_started_at.isoformat() if self._batch_started_at else None,
            "last_finished_at": self._batch_finished_at.isoformat() if self._batch_finished_at else None,
            "last_result": self._last_batch_result,
            "entity_type": entity_type,
            "summary": {
                "total": total,
                "missing": missing_count,
                "pending": status_counter.get(self.ENRICH_PENDING, 0),
                "running": status_counter.get(self.ENRICH_RUNNING, 0),
                "success": status_counter.get(self.ENRICH_SUCCESS, 0),
                "failed": status_counter.get(self.ENRICH_FAILED, 0),
            },
        }

    def _load_mapping_row(self, entity_type: str, entity_id: str) -> Optional[EntityMappingRecord]:
        db = SessionLocal()
        try:
            return (
                db.query(EntityMappingRecord)
                .filter(
                    EntityMappingRecord.entity_type == entity_type,
                    EntityMappingRecord.entity_ref_id == str(entity_id),
                )
                .first()
            )
        finally:
            db.close()

    def _load_target_rows_from_db(
        self,
        entity_type: str,
        limit: int,
        only_missing: bool,
    ) -> List[EntityMappingRecord]:
        db = SessionLocal()
        try:
            query = db.query(EntityMappingRecord)
            if entity_type == "teams":
                query = query.filter(EntityMappingRecord.entity_type == "team")
            elif entity_type == "leagues":
                query = query.filter(EntityMappingRecord.entity_type == "league")
            elif entity_type in {"team", "league"}:
                query = query.filter(EntityMappingRecord.entity_type == entity_type)
            else:
                query = query.filter(EntityMappingRecord.entity_type.in_(["team", "league"]))
            query = query.order_by(EntityMappingRecord.updated_at.asc(), EntityMappingRecord.id.asc())
            rows = query.limit(max(1, int(limit))).all()
        finally:
            db.close()
        if not only_missing:
            return rows
        return [row for row in rows if self._is_missing_official_links(row.official_info)]

    @staticmethod
    def _is_missing_official_links(official_info: Any) -> bool:
        if not isinstance(official_info, dict):
            return True
        for key in ("website", "twitter", "facebook", "instagram", "weibo"):
            if str(official_info.get(key) or "").strip():
                return False
        return True

    @staticmethod
    def _extract_urls_from_aliases(source_aliases: Any) -> List[str]:
        if not isinstance(source_aliases, dict):
            return []
        url_pattern = re.compile(r"https?://[^\s,;]+")
        found: List[str] = []
        for aliases in source_aliases.values():
            if isinstance(aliases, list):
                values = aliases
            elif aliases:
                values = [aliases]
            else:
                values = []
            for item in values:
                text = str(item or "").strip()
                if not text:
                    continue
                if url_pattern.match(text):
                    found.append(text)
        return sorted(set(found))

    @staticmethod
    def _infer_website_from_logo(logo_url: str) -> Optional[str]:
        try:
            parsed = urlparse(logo_url)
            if not parsed.scheme or not parsed.netloc:
                return None
            netloc = parsed.netloc.lower()
            if any(host in netloc for host in ("qlogo.cn", "qpic.cn", "img", "cdn")):
                return None
            return f"{parsed.scheme}://{parsed.netloc}/"
        except Exception:
            return None

    @staticmethod
    def _build_slug_from_names(row: EntityMappingRecord, seed_aliases: Iterable[str]) -> Optional[str]:
        candidates: List[str] = []
        candidates.extend(row.en_names or [])
        candidates.append(row.display_name or "")
        candidates.extend(seed_aliases or [])
        for text in candidates:
            value = str(text or "").strip()
            if not value:
                continue
            slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
            slug = re.sub(r"-{2,}", "-", slug)
            if len(slug) >= 4 and any(ch.isalpha() for ch in slug):
                return slug
        return None

    async def _verify_from_static(self, entity_type: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {
            "teams": {},
            "leagues": {},
            "summary": {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "needs_update": 0,
                "last_verified": datetime.utcnow().isoformat(),
            },
        }
        if entity_type in {"all", "teams"}:
            for team_id, team_data in TEAM_MAPPINGS.items():
                if "official_info" not in team_data:
                    continue
                verification = await self.verify_entity_official_info("team", team_id, team_data["official_info"])
                results["teams"][team_id] = verification
                self._update_summary(results["summary"], verification)
        if entity_type in {"all", "leagues"}:
            for league_id, league_data in LEAGUE_MAPPINGS.items():
                if "official_info" not in league_data:
                    continue
                verification = await self.verify_entity_official_info("league", league_id, league_data["official_info"])
                results["leagues"][league_id] = verification
                self._update_summary(results["summary"], verification)
        return results


official_info_service = OfficialInfoService()
