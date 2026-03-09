#!/usr/bin/env python3
"""
Legacy import check script.

This file is kept for manual diagnostics and must not fail during pytest
collection.
"""

from __future__ import annotations

from sqlalchemy.orm import class_mapper

__test__ = False


def run_import_check() -> int:
    from backend.models.user import User
    from backend.models.predictions import Prediction, UserPrediction

    print("OK: User imported")
    print("OK: UserPrediction imported")
    print("OK: Prediction imported")

    print(f"OK: User mapper configured: {class_mapper(User)}")
    print(f"OK: UserPrediction mapper configured: {class_mapper(UserPrediction)}")
    print(f"OK: Prediction mapper configured: {class_mapper(Prediction)}")

    print(f"User.user_predictions exists: {hasattr(User, 'user_predictions')}")
    print(f"UserPrediction.user exists: {hasattr(UserPrediction, 'user')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_import_check())
