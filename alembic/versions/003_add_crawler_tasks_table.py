"""
添加爬虫任务表

Revision ID: 003_add_crawler_tasks_table
Revises: 002_add_crawler_logs_tables.py
Create Date: 2026-01-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import datetime

# revision identifiers, used by Alembic.
revision = '003_add_crawler_tasks_table'
down_revision = '002_add_crawler_logs_tables'
branch_labels = None
depends_on = None


def upgrade():
    # 创建爬虫任务表
    op.create_table('crawler_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=False, default='crawl'),
        sa.Column('cron_expression', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='stopped'),
        sa.Column('last_run_time', sa.DateTime(), nullable=True),
        sa.Column('next_run_time', sa.DateTime(), nullable=True),
        sa.Column('run_count', sa.Integer(), nullable=False, default=0),
        sa.Column('success_count', sa.Integer(), nullable=False, default=0),
        sa.Column('error_count', sa.Integer(), nullable=False, default=0),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['crawler_configs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('idx_crawler_tasks_source_id', 'crawler_tasks', ['source_id'])
    op.create_index('idx_crawler_tasks_status', 'crawler_tasks', ['status'])
    op.create_index('idx_crawler_tasks_is_active', 'crawler_tasks', ['is_active'])
    op.create_index('idx_crawler_tasks_next_run_time', 'crawler_tasks', ['next_run_time'])
    op.create_index('idx_crawler_tasks_created_at', 'crawler_tasks', ['created_at'])


def downgrade():
    # 删除索引
    op.drop_index('idx_crawler_tasks_created_at', table_name='crawler_tasks')
    op.drop_index('idx_crawler_tasks_next_run_time', table_name='crawler_tasks')
    op.drop_index('idx_crawler_tasks_is_active', table_name='crawler_tasks')
    op.drop_index('idx_crawler_tasks_status', table_name='crawler_tasks')
    op.drop_index('idx_crawler_tasks_source_id', table_name='crawler_tasks')
    
    # 删除表
    op.drop_table('crawler_tasks')