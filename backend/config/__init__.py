"""Compatibility bridge for `backend.config` imports.

This package coexists with the legacy module file `backend/config.py`.
Most runtime code imports `from backend.config import settings` expecting
the module-level settings object from `backend/config.py`.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType


def _load_legacy_config_module() -> ModuleType:
    legacy_file = Path(__file__).resolve().parents[1] / "config.py"
    spec = spec_from_file_location("backend._legacy_config_module", legacy_file)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load legacy config module: {legacy_file}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_legacy = _load_legacy_config_module()

# Re-export commonly used settings/constants from legacy module.
settings = getattr(_legacy, "settings")

for _name in dir(_legacy):
    if _name.isupper():
        globals()[_name] = getattr(_legacy, _name)

__all__ = ["settings"] + [x for x in globals().keys() if x.isupper()]

# Entity mappings configuration package
from .entity_mappings import *

# Import settings from the main config module
from ..config import settings
