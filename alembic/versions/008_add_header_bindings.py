"""add header bindings tables

Revision ID: 008_add_header_bindings
Revises: 007_add_ip_pool_metrics
Create Date: 2026-02-08
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_add_header_bindings'
down_revision = '007_add_ip_pool_metrics'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'data_source_headers',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('data_source_id', sa.Integer(), sa.ForeignKey('data_sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('header_id', sa.Integer(), sa.ForeignKey('request_headers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('priority_override', sa.Integer(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('data_source_id', 'header_id', name='uq_data_source_header'),
    )
    op.create_index('ix_data_source_headers_data_source_id', 'data_source_headers', ['data_source_id'])
    op.create_index('ix_data_source_headers_header_id', 'data_source_headers', ['header_id'])

    op.create_table(
        'crawler_task_headers',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('crawler_tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('header_id', sa.Integer(), sa.ForeignKey('request_headers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('priority_override', sa.Integer(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('task_id', 'header_id', name='uq_task_header'),
    )
    op.create_index('ix_crawler_task_headers_task_id', 'crawler_task_headers', ['task_id'])
    op.create_index('ix_crawler_task_headers_header_id', 'crawler_task_headers', ['header_id'])


def downgrade():
    op.drop_index('ix_crawler_task_headers_header_id', table_name='crawler_task_headers')
    op.drop_index('ix_crawler_task_headers_task_id', table_name='crawler_task_headers')
    op.drop_table('crawler_task_headers')

    op.drop_index('ix_data_source_headers_header_id', table_name='data_source_headers')
    op.drop_index('ix_data_source_headers_data_source_id', table_name='data_source_headers')
    op.drop_table('data_source_headers')
