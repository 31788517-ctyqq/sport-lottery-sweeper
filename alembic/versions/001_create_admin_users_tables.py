"""create admin users tables

Revision ID: 001_admin_users
Revises: 
Create Date: 2026-01-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_admin_users'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建后台用户表
    op.create_table(
        'admin_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('real_name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('role', sa.Enum('SUPER_ADMIN', 'ADMIN', 'MODERATOR', 'AUDITOR', 'OPERATOR', 
                                   name='adminroleenum'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', 'LOCKED', 
                                    name='adminstatusenum'), nullable=False),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('two_factor_secret', sa.String(length=32), nullable=True),
        sa.Column('login_allowed_ips', sa.Text(), nullable=True),
        sa.Column('password_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('must_change_password', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('last_failed_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_ip', sa.String(length=45), nullable=True),
        sa.Column('login_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('preferences', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_admin_users_username', 'admin_users', ['username'], unique=True)
    op.create_index('ix_admin_users_email', 'admin_users', ['email'], unique=True)
    op.create_index('ix_admin_users_role', 'admin_users', ['role'])
    op.create_index('ix_admin_users_status', 'admin_users', ['status'])
    op.create_index('ix_admin_users_department', 'admin_users', ['department'])
    op.create_index('ix_admin_users_created_by', 'admin_users', ['created_by'])

    # 创建后台操作日志表
    op.create_table(
        'admin_operation_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=50), nullable=True),
        sa.Column('resource_name', sa.String(length=255), nullable=True),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('path', sa.String(length=500), nullable=False),
        sa.Column('query_params', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('request_body', sa.Text(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('response_data', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('changes_before', sa.Text(), nullable=True),
        sa.Column('changes_after', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_admin_operation_logs_admin_id', 'admin_operation_logs', ['admin_id'])
    op.create_index('ix_admin_operation_logs_action', 'admin_operation_logs', ['action'])
    op.create_index('ix_admin_operation_logs_resource_type', 'admin_operation_logs', ['resource_type'])
    op.create_index('ix_admin_operation_logs_created_at', 'admin_operation_logs', ['created_at'])
    op.create_index('ix_admin_operation_logs_status_code', 'admin_operation_logs', ['status_code'])

    # 创建后台登录日志表
    op.create_table(
        'admin_login_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('login_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('login_ip', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, default=True),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('device_type', sa.String(length=50), nullable=True),
        sa.Column('os', sa.String(length=50), nullable=True),
        sa.Column('browser', sa.String(length=50), nullable=True),
        sa.Column('two_factor_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('ip_whitelisted', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_admin_login_logs_admin_id', 'admin_login_logs', ['admin_id'])
    op.create_index('ix_admin_login_logs_login_at', 'admin_login_logs', ['login_at'])
    op.create_index('ix_admin_login_logs_login_ip', 'admin_login_logs', ['login_ip'])
    op.create_index('ix_admin_login_logs_success', 'admin_login_logs', ['success'])


def downgrade():
    op.drop_table('admin_login_logs')
    op.drop_table('admin_operation_logs')
    op.drop_table('admin_users')
    op.execute('DROP TYPE IF EXISTS adminroleenum')
    op.execute('DROP TYPE IF EXISTS adminstatusenum')
