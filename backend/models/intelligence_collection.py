from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from .base import Base


class IntelligenceCollectionTask(Base):
    __tablename__ = "intel_collection_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_uuid = Column(String(64), unique=True, nullable=False, index=True)
    task_name = Column(String(200), nullable=False, default="情报采集任务")
    mode = Column(String(20), nullable=False, default="immediate")  # immediate/scheduled
    status = Column(String(20), nullable=False, default="pending")  # pending/running/success/failed/cancelled
    match_ids_json = Column(Text, nullable=False, default="[]")
    sources_json = Column(Text, nullable=False, default="[]")
    intel_types_json = Column(Text, nullable=False, default="[]")
    offset_hours_json = Column(Text, nullable=False, default="[]")
    logs_json = Column(Text, nullable=False, default="[]")
    total_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failed_count = Column(Integer, nullable=False, default=0)
    retry_count = Column(Integer, nullable=False, default=0)
    late_run = Column(Boolean, nullable=False, default=False)
    planned_at = Column(DateTime(timezone=True), nullable=True, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_by = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), index=True)


class IntelligenceCollectionMatchSubtask(Base):
    __tablename__ = "intel_collection_match_subtasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, nullable=False, index=True)
    match_id = Column(Integer, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending")  # pending/running/success/failed/partial/cancelled
    expected_count = Column(Integer, nullable=False, default=0)
    item_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failed_count = Column(Integer, nullable=False, default=0)
    retry_count = Column(Integer, nullable=False, default=0)
    logs_json = Column(Text, nullable=False, default="[]")
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), index=True)


class IntelligenceCollectionItem(Base):
    __tablename__ = "intel_collection_items"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, nullable=True, index=True)
    match_id = Column(Integer, nullable=False, index=True)
    source_code = Column(String(64), nullable=False, index=True)
    intel_category = Column(String(20), nullable=False, index=True)  # off_field/prediction
    intel_type = Column(String(64), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    content_raw = Column(Text, nullable=False)
    source_url = Column(String(600), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    crawled_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    confidence = Column(Float, nullable=False, default=0.6)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)


class IntelligenceUserSubscription(Base):
    __tablename__ = "intel_user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    leagues_json = Column(Text, nullable=False, default="[]")
    teams_json = Column(Text, nullable=False, default="[]")
    intel_types_json = Column(Text, nullable=False, default="[]")
    risk_profile = Column(String(20), nullable=False, default="balanced")
    push_frequency = Column(String(20), nullable=False, default="milestone")
    info_density = Column(String(20), nullable=False, default="standard")
    daily_limit = Column(Integer, nullable=False, default=5)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)


class IntelligenceChannelBinding(Base):
    __tablename__ = "intel_channel_bindings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    channel = Column(String(30), nullable=False, default="dingtalk")
    webhook = Column(String(600), nullable=False)
    secret = Column(String(300), nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    last_test_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), index=True)


class IntelligencePushTask(Base):
    __tablename__ = "intel_push_tasks"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, nullable=False, index=True)
    preview_json = Column(Text, nullable=False, default="{}")
    channel = Column(String(30), nullable=False, default="dingtalk")
    target_users_json = Column(Text, nullable=False, default="[]")
    status = Column(String(20), nullable=False, default="pending")  # pending/success/failed
    error_message = Column(Text, nullable=True)
    pushed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), index=True)
