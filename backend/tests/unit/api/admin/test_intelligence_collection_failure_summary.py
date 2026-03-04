from unittest.mock import AsyncMock

import pytest

from backend.api.v1.admin import intelligence_collection as ic
from backend.models.intelligence_collection import (
    IntelligenceCollectionItem,
    IntelligenceCollectionMatchSubtask,
    IntelligenceCollectionTask,
)


class _ScalarResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def all(self):
        return self._rows


@pytest.mark.asyncio
async def test_build_task_failure_summary_aggregates_reasons_and_sources():
    task = IntelligenceCollectionTask(
        task_uuid="task-failure-summary",
        task_name="failure-summary",
        mode="immediate",
        status="failed",
        match_ids_json="[]",
        sources_json="[]",
        intel_types_json="[]",
        offset_hours_json="[]",
        logs_json=ic._json_dumps(
            [
                {
                    "time": "2026-02-20 10:00:01",
                    "level": "warning",
                    "message": (
                        "source_runtime source=500w; requests=8; ok=3; timeout=2; "
                        "errors=1; retries=2; circuit_skipped=1"
                    ),
                },
                {
                    "time": "2026-02-20 10:00:02",
                    "level": "warning",
                    "message": (
                        "decision match_id=1001; source=500w; intel_type=injury; "
                        "decision=blocked; reason=time-window-miss;"
                    ),
                },
                {
                    "time": "2026-02-20 10:00:03",
                    "level": "error",
                    "message": "collect failed: timeout",
                },
            ]
        ),
    )
    task.id = 901
    subtask = IntelligenceCollectionMatchSubtask(
        task_id=task.id,
        match_id=1001,
        status="failed",
        last_error="network-timeout",
    )

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=_ScalarResult([subtask]))

    summary = await ic._build_task_failure_summary(mock_db, task)

    assert summary["task_id"] == 901
    assert summary["task_status"] == "failed"
    reason_tokens = {row["reason"] for row in summary["top_reasons"]}
    assert "timeout" in reason_tokens
    assert "time-window-miss" in reason_tokens
    assert "network-timeout" in reason_tokens

    source_failures = {row["source"]: row for row in summary["source_failures"]}
    assert "500w" in source_failures
    assert source_failures["500w"]["timeout"] == 2
    assert source_failures["500w"]["errors"] == 1
    assert source_failures["500w"]["blocked_decisions"] == 1


def test_extract_quality_from_item_prefers_structured_fields():
    item = IntelligenceCollectionItem(
        task_id=1,
        match_id=123,
        source_code="500w",
        intel_category="prediction",
        intel_type="win_draw_lose",
        title="Structured field precedence",
        content_raw=(
            "[match-article-fallback] source=500w; quality_score=0; "
            "quality_block_reason=legacy-block; source_parser=legacy-parser; "
            "article_url=https://legacy.example.com/a; hit_terms=legacyA|legacyB;"
        ),
        quality_status="accepted",
        quality_score=2.66,
        quality_pass_reason="structured-hit",
        quality_block_reason="",
        source_parser="structured-parser",
        article_url="https://structured.example.com/a",
        match_hit_terms_json='["home","away"]',
        source_url="https://source.example.com",
    )

    quality = ic._extract_quality_from_item(item)

    assert quality["quality_status"] == "accepted"
    assert quality["quality_score"] == 2.66
    assert quality["quality_pass_reason"] == "structured-hit"
    assert quality["quality_block_reason"] == ""
    assert quality["source_parser"] == "structured-parser"
    assert quality["article_url"] == "https://structured.example.com/a"
    assert quality["match_hit_terms"] == ["home", "away"]


def test_task_event_runtime_context_and_stage_parsing():
    logs = [
        {
            "time": "2026-02-20 10:00:01",
            "level": "info",
            "message": "task created",
        },
        {
            "time": "2026-02-20 10:00:03",
            "level": "debug",
            "message": (
                "decision match_id=2001; source=500w; intel_type=injury; "
                "decision=accepted; reason=ok;"
            ),
        },
    ]

    runtime_ctx = ic._extract_task_runtime_context(logs)
    stage = ic._infer_task_stage_from_logs("running", logs)

    assert runtime_ctx["current_source"] == "500w"
    assert runtime_ctx["current_match_id"] == 2001
    assert runtime_ctx["current_intel_type"] == "injury"
    assert runtime_ctx["last_log"]["message"].startswith("decision match_id=2001")
    assert stage == "collecting"


def test_task_event_fingerprint_ignores_generated_at_timestamp():
    base_payload = {
        "task_id": 7,
        "status": "running",
        "stage": "collecting",
        "progress_percent": 42.0,
        "success_rate": 0.42,
        "completed_count": 21,
        "failed_count": 3,
        "total_count": 50,
        "total_matches": 5,
        "success_matches": 2,
        "failed_matches": 1,
        "partial_matches": 2,
        "coverage_rate": 0.8,
        "current_source": "500w",
        "current_match_id": 1234,
        "current_intel_type": "injury",
        "terminal": False,
        "error_message": "",
        "last_log": {"time": "2026-02-20 10:00:03", "level": "debug", "message": "decision match_id=1234"},
    }
    payload_a = {**base_payload, "generated_at": "2026-02-20T10:00:03"}
    payload_b = {**base_payload, "generated_at": "2026-02-20T10:00:04"}

    assert ic._build_task_events_fingerprint(payload_a) == ic._build_task_events_fingerprint(payload_b)
