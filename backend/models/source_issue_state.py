"""
Track latest discovered/success issue numbers per source.
"""

from sqlalchemy import Column, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from .base import Base


class SourceIssueState(Base):
    """State table for issue-driven source synchronization."""

    __tablename__ = "source_issue_state"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(32), nullable=False)
    latest_discovered_issue = Column(String(16), nullable=True)
    last_success_issue = Column(String(16), nullable=True)
    last_discovered_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("source_type", name="uq_source_issue_state_source_type"),
        Index("idx_source_issue_state_latest_discovered_issue", "latest_discovered_issue"),
    )

