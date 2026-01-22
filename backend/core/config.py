"""
Configuration module using pydantic-settings.

Manages all application settings loaded from environment variables,
configuration files, or defaults.
"""
from functools import lru_cache

from ..config import settings  # 导入主配置


@lru_cache()
def get_settings():
    """
    Cached dependency to load settings once per application lifecycle.
    Using lru_cache ensures the settings are only read once,
    improving performance and consistency across the app.
    """
    return settings


# Example usage within the application:
# from backend.app.core.config import get_settings
# settings = get_settings()
# print(settings.PROJECT_NAME)