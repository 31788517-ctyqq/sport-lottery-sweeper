#!/usr/bin/env python3
"""Restore 4 historically successful LLM providers into current DB (idempotent)."""

from backend.database import SessionLocal
from backend.models.llm_provider import (
    LLMProvider,
    LLMProviderTypeEnum,
    LLMProviderStatusEnum,
)


RESTORE_PROVIDERS = [
    {
        "name": "OpenAI Official",
        "provider_type": LLMProviderTypeEnum.OPENAI,
        "description": "Recovered from historical successful creation logs.",
        "api_key": "sk-restore-openai-placeholder",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4-turbo",
    },
    {
        "name": "QWEN",
        "provider_type": LLMProviderTypeEnum.ALIBABA,
        "description": "Recovered from historical successful creation logs.",
        "api_key": "sk-restore-qwen-placeholder",
        "base_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        "default_model": "qwen-turbo",
    },
    {
        "name": "MY_ZP_BIGMODLE",
        "provider_type": LLMProviderTypeEnum.CUSTOM,
        "description": "Recovered from historical successful creation logs (zhipu model).",
        "api_key": "sk-restore-zhipu-placeholder",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4",
    },
    {
        "name": "Test Frontend Provider",
        "provider_type": LLMProviderTypeEnum.OPENAI,
        "description": "Recovered from historical successful creation logs.",
        "api_key": "sk-restore-frontend-placeholder",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-3.5-turbo",
    },
]


def main() -> None:
    db = SessionLocal()
    created = []
    skipped = []
    try:
        for item in RESTORE_PROVIDERS:
            exists = db.query(LLMProvider).filter(LLMProvider.name == item["name"]).first()
            if exists:
                skipped.append(item["name"])
                continue

            provider = LLMProvider(
                name=item["name"],
                provider_type=item["provider_type"],
                description=item["description"],
                api_key=item["api_key"],
                base_url=item["base_url"],
                default_model=item["default_model"],
                available_models=[item["default_model"]],
                enabled=True,
                priority=8,
                max_requests_per_minute=60,
                timeout_seconds=30,
                health_status=LLMProviderStatusEnum.CHECKING,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                total_cost=0,
                monthly_cost=0,
                rate_limit_strategy="fixed_window",
                retry_policy={},
                circuit_breaker_config={},
                version="1.0",
                tags=["recovered", "log-history"],
                created_by=1,
                updated_by=1,
            )
            db.add(provider)
            created.append(item["name"])

        db.commit()

        print("restore complete")
        print("created:", created)
        print("skipped:", skipped)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
