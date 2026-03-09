#!/usr/bin/env python3
"""
Legacy model registration check script.

This file is intended for manual execution and should not break pytest
collection.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import class_mapper, sessionmaker

from models.base import Base
from models.predictions import Prediction, UserPrediction
from models.user import User

__test__ = False


def run_model_registration_check() -> int:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    print("OK: created tables")

    for model in (User, UserPrediction, Prediction):
        print(f"OK: mapper configured for {model.__name__}: {class_mapper(model)}")

    print(f"User.user_predictions exists: {hasattr(User, 'user_predictions')}")
    print(f"UserPrediction.user exists: {hasattr(UserPrediction, 'user')}")
    print(
        "Prediction.user_predictions exists: "
        f"{hasattr(Prediction, 'user_predictions')}"
    )

    session = sessionmaker(bind=engine)()
    try:
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="fakehash",
            status="active",
        )
        session.add(test_user)
        session.commit()
        print(f"OK: user created id={test_user.id}")
    finally:
        session.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(run_model_registration_check())
