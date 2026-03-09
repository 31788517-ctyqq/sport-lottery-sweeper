"""
添加爬虫日志和统计表

Revision ID: 002_add_crawler_logs_tables
Revises: 001_create_admin_users_tables.py
Create Date: 2026-01-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import datetime

# revision identifiers, used by Alembic.
revision = '002_add_crawler_logs_tables'
down_revision = '001_admin_users'
branch_labels = None
depends_on = None


def upgrade():
    # 创建爬虫任务执行日志表
    op.create_table('crawler_task_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=True),
        sa.Column('records_success', sa.Integer(), nullable=True),
        sa.Column('records_failed', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('response_time_ms', sa.Float(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['crawler_configs.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['crawler_tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建数据源统计表
    op.create_table('crawler_source_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_requests', sa.Integer(), nullable=False, default=0),
        sa.Column('successful_requests', sa.Integer(), nullable=False, default=0),
        sa.Column('failed_requests', sa.Integer(), nullable=False, default=0),
        sa.Column('avg_response_time_ms', sa.Float(), nullable=True),
        sa.Column('total_records', sa.Integer(), nullable=False, default=0),
        sa.Column('last_success_at', sa.DateTime(), nullable=True),
        sa.Column('last_failure_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['crawler_configs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_id', 'date', name='uq_source_date')
    )
    
    # 创建索引
    op.create_index('idx_crawler_task_logs_task_id', 'crawler_task_logs', ['task_id'])
    op.create_index('idx_crawler_task_logs_source_id', 'crawler_task_logs', ['source_id'])
    op.create_index('idx_crawler_task_logs_status', 'crawler_task_logs', ['status'])
    op.create_index('idx_crawler_task_logs_started_at', 'crawler_task_logs', ['started_at'])
    op.create_index('idx_crawler_source_stats_source_id', 'crawler_source_stats', ['source_id'])
    op.create_index('idx_crawler_source_stats_date', 'crawler_source_stats', ['date'])


def downgrade():
    # 删除索引
    op.drop_index('idx_crawler_source_stats_date', table_name='crawler_source_stats')
    op.drop_index('idx_crawler_source_stats_source_id', table_name='crawler_source_stats')
    op.drop_index('idx_crawler_task_logs_started_at', table_name='crawler_task_logs')
    op.drop_index('idx_crawler_task_logs_status', table_name='crawler_task_logs')
    op.drop_index('idx_crawler_task_logs_source_id', table_name='crawler_task_logs')
    op.drop_index('idx_crawler_task_logs_task_id', table_name='crawler_task_logs')
    
    # 删除表
    op.drop_table('crawler_source_stats')
    op.drop_table('crawler_task_logs')
