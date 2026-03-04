"""
Celery tasks for intelligence collection queue dispatch.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, List, Optional

from backend.tasks.intelligence_collection_queue_app import celery_app


logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="backend.tasks.intelligence_collection_tasks.run_intelligence_collection_task",
)
def run_intelligence_collection_task(
    self,
    task_id: int,
    trigger: str = "collect",
    run_match_ids: Optional[List[int]] = None,
    run_sources: Optional[List[str]] = None,
    run_intel_types: Optional[List[str]] = None,
) -> Any:
    """
    Execute intelligence collection pipeline in Celery worker process.
    """
    from backend.api.v1.admin.intelligence_collection import _run_collection_task_async

    clean_match_ids = [int(x) for x in (run_match_ids or []) if str(x).isdigit()] or None
    clean_sources = [str(x) for x in (run_sources or []) if str(x).strip()] or None
    clean_intel_types = [str(x) for x in (run_intel_types or []) if str(x).strip()] or None

    logger.info(
        "[intelligence.collection.task.worker] start task_id=%s trigger=%s queue_id=%s",
        task_id,
        trigger,
        self.request.id,
    )
    asyncio.run(
        _run_collection_task_async(
            int(task_id),
            trigger=str(trigger or "collect"),
            run_match_ids=clean_match_ids,
            run_sources=clean_sources,
            run_intel_types=clean_intel_types,
        )
    )
    logger.info(
        "[intelligence.collection.task.worker] done task_id=%s trigger=%s queue_id=%s",
        task_id,
        trigger,
        self.request.id,
    )
    return {"task_id": int(task_id), "queue_job_id": str(self.request.id or ""), "status": "done"}
