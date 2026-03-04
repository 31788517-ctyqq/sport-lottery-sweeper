"""
添加爬虫告警配置和记录表

Revision ID: 004_add_crawler_alert_tables
Revises: 003_add_crawler_tasks_table.py
Create Date: 2026-01-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import datetime

# revision identifiers, used by Alembic.
revision = '004_add_crawler_alert_tables'
down_revision = '003_add_crawler_tasks_table'
branch_labels = None
depends_on = None


def upgrade():
    # 创建爬虫告警规则表
    op.create_table('crawler_alert_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metric_type', sa.String(length=50), nullable=False),  # error_rate, response_time, consecutive_failures, data_quality
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('comparison_operator', sa.String(length=10), nullable=False),  # gt, lt, eq, gte, lte
        sa.Column('time_window_minutes', sa.Integer(), nullable=False, default=60),
        sa.Column('source_ids', sa.JSON(), nullable=True),  # 指定数据源ID列表，null表示所有源
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('alert_level', sa.String(length=20), nullable=False, default='warning'),  # warning, error, critical
        sa.Column('cooldown_minutes', sa.Integer(), nullable=False, default=30),  # 告警冷却时间
        sa.Column('notification_channels', sa.JSON(), nullable=False, default=['email']),  # 通知渠道
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建爬虫告警记录表
    op.create_table('crawler_alert_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('alert_level', sa.String(length=20), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='active'),  # active, resolved, acknowledged
        sa.Column('triggered_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('acknowledged_by', sa.Integer(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['rule_id'], ['crawler_alert_rules.id'], ),
        sa.ForeignKeyConstraint(['source_id'], ['crawler_configs.id'], )
    )
    
    # 创建爬虫监控指标表
    op.create_table('crawler_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('metric_type', sa.String(length=50), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_id'], ['crawler_configs.id'], )
    )
    
    # 创建索引
    op.create_index('idx_crawler_alert_rules_metric_type', 'crawler_alert_rules', ['metric_type'])
    op.create_index('idx_crawler_alert_rules_is_active', 'crawler_alert_rules', ['is_active'])
    op.create_index('idx_crawler_alert_records_rule_id', 'crawler_alert_records', ['rule_id'])
    op.create_index('idx_crawler_alert_records_source_id', 'crawler_alert_records', ['source_id'])
    op.create_index('idx_crawler_alert_records_status', 'crawler_alert_records', ['status'])
    op.create_index('idx_crawler_alert_records_triggered_at', 'crawler_alert_records', ['triggered_at'])
    op.create_index('idx_crawler_metrics_source_id', 'crawler_metrics', ['source_id'])
    op.create_index('idx_crawler_metrics_metric_type', 'crawler_metrics', ['metric_type'])
    op.create_index('idx_crawler_metrics_recorded_at', 'crawler_metrics', ['recorded_at'])


def downgrade():
    # 删除索引
    op.drop_index('idx_crawler_metrics_recorded_at', table_name='crawler_metrics')
    op.drop_index('idx_crawler_metrics_metric_type', table_name='crawler_metrics')
    op.drop_index('idx_crawler_metrics_source_id', table_name='crawler_metrics')
    op.drop_index('idx_crawler_alert_records_triggered_at', table_name='crawler_alert_records')
    op.drop_index('idx_crawler_alert_records_status', table_name='crawler_alert_records')
    op.drop_index('idx_crawler_alert_records_source_id', table_name='crawler_alert_records')
    op.drop_index('idx_crawler_alert_records_rule_id', table_name='crawler_alert_records')
    op.drop_index('idx_crawler_alert_rules_is_active', table_name='crawler_alert_rules')
    op.drop_index('idx_crawler_alert_rules_metric_type', table_name='crawler_alert_rules')
    
    # 删除表
    op.drop_table('crawler_metrics')
    op.drop_table('crawler_alert_records')
    op.drop_table('crawler_alert_rules')
