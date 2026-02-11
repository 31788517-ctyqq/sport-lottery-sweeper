"""create llm providers table

Revision ID: 009_llm_providers
Revises: 008_add_header_bindings
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009_llm_providers'
down_revision = '008_add_header_bindings'
branch_labels = None
depends_on = None


def upgrade():
    # 定义枚举值（与backend/models/llm_provider.py保持一致）
    llm_provider_type_enum = sa.Enum(
        'openai', 'anthropic', 'google', 'azure', 'alibaba', 'ollama', 'vllm', 'custom',
        name='llmprovidertypeenum',
        native_enum=False
    )
    
    llm_provider_status_enum = sa.Enum(
        'healthy', 'unhealthy', 'checking', 'disabled',
        name='llmproviderstatusenum',
        native_enum=False
    )
    
    # 如果表已存在，先删除（开发环境）
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if inspector.has_table('llm_providers'):
        op.drop_table('llm_providers')
    
    # 创建LLM供应商表
    op.create_table(
        'llm_providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('provider_type', llm_provider_type_enum, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('api_key', sa.Text(), nullable=False),
        sa.Column('base_url', sa.String(length=500), nullable=True),
        sa.Column('default_model', sa.String(length=100), nullable=True),
        sa.Column('available_models', sa.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('priority', sa.Integer(), nullable=False, server_default=sa.text('5')),
        sa.Column('max_requests_per_minute', sa.Integer(), nullable=False, server_default=sa.text('60')),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False, server_default=sa.text('30')),
        sa.Column('cost_per_token', sa.JSON(), nullable=True),
        sa.Column('rate_limit_strategy', sa.String(length=50), nullable=False, server_default='fixed_window'),
        sa.Column('retry_policy', sa.JSON(), nullable=True),
        sa.Column('circuit_breaker_config', sa.JSON(), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        
        # 健康监控相关字段
        sa.Column('health_status', llm_provider_status_enum, nullable=False, server_default='checking'),
        sa.Column('last_checked_at', sa.DateTime(), nullable=True),
        sa.Column('last_success_at', sa.DateTime(), nullable=True),
        sa.Column('total_requests', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('successful_requests', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('failed_requests', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('total_cost', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('monthly_cost', sa.Integer(), nullable=False, server_default=sa.text('0')),
        
        # 审计字段
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.Index('ix_llm_providers_name', 'name'),
        sa.Index('ix_llm_providers_provider_type', 'provider_type'),
        sa.Index('ix_llm_providers_health_status', 'health_status'),
        sa.Index('ix_llm_providers_enabled', 'enabled'),
        sa.Index('ix_llm_providers_priority', 'priority'),
        sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['admin_users.id'], ondelete='SET NULL')
    )


def downgrade():
    # 删除表
    op.drop_table('llm_providers')
    
    # 删除枚举类型（如果存在）- SQLite不支持，但保留以兼容PostgreSQL
    try:
        op.execute('DROP TYPE IF EXISTS llmprovidertypeenum')
        op.execute('DROP TYPE IF EXISTS llmproviderstatusenum')
    except:
        pass  # SQLite忽略