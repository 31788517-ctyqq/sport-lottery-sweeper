"""
Store per-issue execution records for automatic source sync.
"""

from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from .base import Base


class SourceIssueFetchRun(Base):
    """Execution record for one source_type + issue_no."""

    __tablename__ = "source_issue_fetch_runs"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(32), nullable=False)
    issue_no = Column(String(16), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    trigger_type = Column(String(20), nullable=False, default="scheduler")
    source_id = Column(Integer, nullable=True)
    request_url = Column(String(500), nullable=True)
    response_code = Column(Integer, nullable=True)
    records_count = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("source_type", "issue_no", name="uq_source_issue_fetch_runs_source_issue"),
        Index("idx_source_issue_fetch_runs_status_created", "status", "created_at"),
    )

