"""
??????????HTTP?????????????????????
"""

from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from .logging_middleware import LoggingMiddleware
from .null_safety_middleware import NullSafetyMiddleware, add_null_safety_middleware

# ?? backend/middleware.py ? backend/middleware/ ????????????????
# ?????????????????????
_middleware_file = Path(__file__).resolve().parent.parent / "middleware.py"
_spec = spec_from_file_location("backend._middleware_file", _middleware_file)
_mod = module_from_spec(_spec)  # type: ignore[arg-type]
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)

SecurityHeadersMiddleware = _mod.SecurityHeadersMiddleware
RequestLoggingMiddleware = _mod.RequestLoggingMiddleware
AuthenticationMiddleware = _mod.AuthenticationMiddleware
CompressionMiddleware = _mod.CompressionMiddleware
CacheControlMiddleware = _mod.CacheControlMiddleware
RequestIDMiddleware = _mod.RequestIDMiddleware
DatabaseSessionMiddleware = _mod.DatabaseSessionMiddleware

__all__ = [
    "LoggingMiddleware",
    "NullSafetyMiddleware",
    "add_null_safety_middleware",
    "SecurityHeadersMiddleware",
    "RequestLoggingMiddleware",
    "AuthenticationMiddleware",
    "CompressionMiddleware",
    "CacheControlMiddleware",
    "RequestIDMiddleware",
    "DatabaseSessionMiddleware",
]
