"""
add_beidan_strategy_tables

Revision ID: add_beidan_strategy_tables
Revises: 
Create Date: 2025-01-15 10:00:00.000000

添加北单筛选器策略相关数据库表
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import datetime

# revision identifiers, used by Alembic.
revision = 'add_beidan_strategy_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """升级数据库"""
    
    # 创建北单策略表
    op.create_table(
        'beidan_strategies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('three_dimensional', sa.JSON(), nullable=False),
        sa.Column('other_conditions', sa.JSON(), nullable=False),
        sa.Column('sort_config', sa.JSON(), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False, server_default='default_user'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_rate', sa.String(length=10), nullable=False, server_default='0%'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_beidan_strategies_user_id', 'user_id'),
        sa.Index('ix_beidan_strategies_created_at', 'created_at'),
        sa.Index('ix_beidan_strategies_name_user', 'name', 'user_id', unique=True)
    )
    
    # 创建北单策略执行日志表
    op.create_table(
        'beidan_strategy_execution_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('strategy_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False, server_default='default_user'),
        sa.Column('execution_params', sa.JSON(), nullable=True),
        sa.Column('result_stats', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='success'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['strategy_id'], ['beidan_strategies.id'], ondelete='CASCADE'),
        sa.Index('ix_beidan_strategy_logs_strategy_id', 'strategy_id'),
        sa.Index('ix_beidan_strategy_logs_user_id', 'user_id'),
        sa.Index('ix_beidan_strategy_logs_executed_at', 'executed_at'),
        sa.Index('ix_beidan_strategy_logs_status', 'status')
    )
    
    # 插入默认示例策略
    op.execute("""
        INSERT INTO beidan_strategies (name, description, three_dimensional, other_conditions, sort_config, user_id, is_public, created_at, updated_at) VALUES 
        ('稳健型策略', '适合保守投资者，注重基本面分析', 
         '{"powerDifference": {"homeWeak": true, "homeBalanced": true, "homeStrong": false, "guestWeak": true, "guestBalanced": true, "guestStrong": false}, "winPanDifference": 0, "sizeBallDifference": 0}',
         '{"leagues": ["premier_league", "la_liga", "bundesliga"], "dateTime": "", "dateRange": {"startDate": "", "endDate": ""}, "strength": "balanced"}',
         '{"field": "match_time", "order": "asc"}', 'default_user', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        
        ('进取型策略', '适合激进投资者，追求高收益',
         '{"powerDifference": {"homeWeak": true, "homeBalanced": true, "homeStrong": true, "guestWeak": true, "guestBalanced": true, "guestStrong": true}, "winPanDifference": 1, "sizeBallDifference": 0}',
         '{"leagues": ["champions_league"], "dateTime": "", "dateRange": {"startDate": "", "endDate": ""}, "strength": "strong"}',
         '{"field": "match_time", "order": "desc"}', 'default_user', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """)


def downgrade():
    """降级数据库"""
    
    # 删除外键约束
    op.drop_constraint('beidan_strategy_execution_logs_strategy_id_fkey', 'beidan_strategy_execution_logs', type_='foreignkey')
    
    # 删除索引
    op.drop_index('ix_beidan_strategy_logs_status', table_name='beidan_strategy_execution_logs')
    op.drop_index('ix_beidan_strategy_logs_executed_at', table_name='beidan_strategy_execution_logs')
    op.drop_index('ix_beidan_strategy_logs_user_id', table_name='beidan_strategy_execution_logs')
    op.drop_index('ix_beidan_strategy_logs_strategy_id', table_name='beidan_strategy_execution_logs')
    op.drop_index('ix_beidan_strategies_name_user', table_name='beidan_strategies')
    op.drop_index('ix_beidan_strategies_created_at', table_name='beidan_strategies')
    op.drop_index('ix_beidan_strategies_user_id', table_name='beidan_strategies')
    
    # 删除表
    op.drop_table('beidan_strategy_execution_logs')
    op.drop_table('beidan_strategies')