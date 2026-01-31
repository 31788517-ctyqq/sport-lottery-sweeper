"""create departments table

Revision ID: 002
Revises: 001
Create Date: 2026-01-28 01:55:57.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.sql import expression

from backend.core.database import GUID

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建部门表
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("parent_id", sa.Integer(), nullable=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("leader_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.Boolean(), default=True, nullable=False, index=True),
        sa.Column("sort_order", sa.Integer(), default=0, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now(), nullable=False, index=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.ForeignKeyConstraint(["parent_id"], ["departments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["leader_id"], ["admin_users.id"], ondelete="SET NULL"),
        sa.CheckConstraint("id != parent_id", name="check_not_self_parent"),
        sa.Index("ix_departments_parent_id", "parent_id"),
        sa.Index("ix_departments_status", "status"),
        sa.UniqueConstraint("name", name="uq_department_name")
    )


def downgrade() -> None:
    # 删除部门表
    op.drop_table("departments")