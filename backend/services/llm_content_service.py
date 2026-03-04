from typing import Any, Dict, Optional


class LLMContentService:
    @staticmethod
    def explain(payload: Dict[str, Any]) -> Dict[str, Any]:
        suggestion_id = payload.get("suggestion_id")
        return {
            "ok": True,
            "data": {
                "suggestion_id": suggestion_id,
                "explanation": "当前为模板解读：建议基于edge、窗口与风控状态综合生成。",
                "risk_note": "若进入STOP状态将强制SKIP。",
                "provider": "stub",
                "model": "stub",
                "prompt_version": payload.get("prompt_version") or "v1",
                "request_id": f"local_explain_{suggestion_id or 'na'}",
            },
        }

    @staticmethod
    def alert_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
        state = payload.get("state") or "WARN"
        return {
            "ok": True,
            "data": {
                "title": f"风控状态：{state}",
                "summary": "当前告警摘要为模板输出，请接入LLM供应商后替换。",
                "actions": ["核验指标", "检查数据源", "评估是否手动停机"],
                "provider": "stub",
                "model": "stub",
                "prompt_version": payload.get("prompt_version") or "v1",
                "request_id": "local_alert_summary",
            },
        }

    @staticmethod
    def report(payload: Dict[str, Any]) -> Dict[str, Any]:
        report_type = payload.get("report_type") or "daily"
        date_value: Optional[str] = payload.get("date")
        return {
            "ok": True,
            "data": {
                "title": f"平局建议{report_type}报告（{date_value or 'N/A'}）",
                "content_markdown": "模板报告：请接入LLM供应商后输出完整运营文案。",
                "highlights": ["建议生成链路正常", "风控状态可用"],
                "provider": "stub",
                "model": "stub",
                "prompt_version": payload.get("prompt_version") or "v1",
                "request_id": "local_report",
            },
        }
