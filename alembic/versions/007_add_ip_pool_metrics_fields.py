"""add ip pool metrics fields

Revision ID: 007_add_ip_pool_metrics
Revises: 006_add_multi_source_support_fields
Create Date: 2026-02-08
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_add_ip_pool_metrics'
down_revision = '006_multi_source_support'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ip_pools', sa.Column('latency_ms', sa.Integer(), nullable=True))
    op.add_column('ip_pools', sa.Column('success_rate', sa.Integer(), nullable=True))
    op.add_column('ip_pools', sa.Column('last_checked', sa.DateTime(), nullable=True))
    op.add_column('ip_pools', sa.Column('source', sa.String(length=100), nullable=True))
    op.add_column('ip_pools', sa.Column('anonymity', sa.String(length=50), nullable=True))
    op.add_column('ip_pools', sa.Column('score', sa.Integer(), nullable=True))
    op.add_column('ip_pools', sa.Column('banned_until', sa.DateTime(), nullable=True))
    op.add_column('ip_pools', sa.Column('fail_reason', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('ip_pools', 'fail_reason')
    op.drop_column('ip_pools', 'banned_until')
    op.drop_column('ip_pools', 'score')
    op.drop_column('ip_pools', 'anonymity')
    op.drop_column('ip_pools', 'source')
    op.drop_column('ip_pools', 'last_checked')
    op.drop_column('ip_pools', 'success_rate')
    op.drop_column('ip_pools', 'latency_ms')
