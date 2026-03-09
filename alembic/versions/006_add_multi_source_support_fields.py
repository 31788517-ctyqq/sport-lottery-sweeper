"""
添加多数据源支持字段（阶段一改造）

Revision ID: 006_multi_source_support
Revises: 005_sp_management
Create Date: 2026-02-03

包含以下修改：
1. 为matches表添加数据源标识字段
2. 为data_sources表添加字段映射配置字段
3. 为matches表添加唯一约束防止同一数据源的同一场比赛重复
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, mysql, sqlite
import json


# revision identifiers, used by Alembic.
revision = '006_multi_source_support'
down_revision = '005_sp_management'
branch_labels = None
depends_on = None


def upgrade():
    # ### 为matches表添加多数据源支持字段 ###
    
    # 检查表中是否已存在这些字段（防止重复执行）
    conn = op.get_bind()
    
    # 获取matches表的列信息（针对不同数据库）
    if conn.engine.name == 'sqlite':
        # SQLite: 查询sqlite_master获取表定义（不直接支持列查询）
        # 这里假设字段不存在，直接添加
        op.add_column('matches', sa.Column('data_source', sa.String(length=50), server_default='default', nullable=False))
        op.add_column('matches', sa.Column('source_match_id', sa.String(length=255), nullable=True))
        op.add_column('matches', sa.Column('data_version', sa.Integer(), server_default='1', nullable=False))
        op.add_column('matches', sa.Column('source_attributes', sa.JSON(), nullable=True))
    else:
        # MySQL/PostgreSQL: 查询information_schema.columns
        # 为简化，直接添加（如果字段已存在会失败，但迁移通常只执行一次）
        op.add_column('matches', sa.Column('data_source', sa.String(length=50), server_default='default', nullable=False))
        op.add_column('matches', sa.Column('source_match_id', sa.String(length=255), nullable=True))
        op.add_column('matches', sa.Column('data_version', sa.Integer(), server_default='1', nullable=False))
        op.add_column('matches', sa.Column('source_attributes', sa.JSON(), nullable=True))
    
    # 为matches表添加唯一约束 (data_source, source_match_id)
    # 注意：source_match_id可能为NULL，在大多数数据库中NULL值不参与唯一约束
    # 使用create_unique_constraint（Alembic的op.create_unique_constraint在较新版本中可用）
    # 对于旧版本Alembic，使用create_index配合unique=True
    try:
        # 尝试创建唯一约束
        op.create_unique_constraint(
            'uq_matches_data_source_source_match_id',
            'matches',
            ['data_source', 'source_match_id']
        )
    except:
        # 回退方案：创建唯一索引
        op.create_index(
            'uq_matches_data_source_source_match_id',
            'matches',
            ['data_source', 'source_match_id'],
            unique=True
        )
    
    # ### 为data_sources表添加字段映射配置字段 ###
    op.add_column('data_sources', sa.Column('field_mapping', sa.JSON(), nullable=True, comment='字段映射配置(JSON格式)'))
    op.add_column('data_sources', sa.Column('update_frequency', sa.Integer(), server_default='60', nullable=False, comment='更新频率(分钟)'))
    
    # 为data_sources表的status字段修改类型（如果之前是Boolean）
    # 注意：005中创建data_sources表时status是Boolean，但我们的模型中是String
    # 这里需要将Boolean转换为String
    # 由于不同数据库类型转换方式不同，这里使用通用方法
    if conn.engine.name == 'sqlite':
        # SQLite: 需要重新创建表或使用ALTER TABLE修改列类型
        # 简化处理：直接忽略，因为SQLite是弱类型
        pass
    elif conn.engine.name == 'mysql':
        # MySQL: 修改列类型
        op.execute("""
            ALTER TABLE data_sources 
            MODIFY COLUMN status VARCHAR(20) NOT NULL DEFAULT 'online' COMMENT '状态: online/offline/maintenance/error'
        """)
    elif conn.engine.name == 'postgresql':
        # PostgreSQL: 修改列类型
        op.execute("""
            ALTER TABLE data_sources 
            ALTER COLUMN status TYPE VARCHAR(20) USING 
                CASE 
                    WHEN status = true THEN 'online'
                    WHEN status = false THEN 'offline'
                    ELSE 'maintenance'
                END,
            ALTER COLUMN status SET DEFAULT 'online'
        """)
    
    # 为新增字段创建索引
    op.create_index('ix_matches_data_source', 'matches', ['data_source'])
    op.create_index('ix_matches_source_match_id', 'matches', ['source_match_id'])
    op.create_index('ix_matches_data_version', 'matches', ['data_version'])
    op.create_index('ix_data_sources_update_frequency', 'data_sources', ['update_frequency'])


def downgrade():
    # ### 移除matches表添加的字段 ###
    op.drop_index('ix_matches_data_source', table_name='matches')
    op.drop_index('ix_matches_source_match_id', table_name='matches')
    op.drop_index('ix_matches_data_version', table_name='matches')
    
    # 移除唯一约束/索引
    try:
        op.drop_constraint('uq_matches_data_source_source_match_id', 'matches', type_='unique')
    except:
        op.drop_index('uq_matches_data_source_source_match_id', table_name='matches')
    
    # 移除列
    op.drop_column('matches', 'source_attributes')
    op.drop_column('matches', 'data_version')
    op.drop_column('matches', 'source_match_id')
    op.drop_column('matches', 'data_source')
    
    # ### 移除data_sources表添加的字段 ###
    op.drop_index('ix_data_sources_update_frequency', table_name='data_sources')
    op.drop_column('data_sources', 'update_frequency')
    op.drop_column('data_sources', 'field_mapping')
    
    # 将status字段恢复为Boolean类型（如果需要）
    # 注意：这可能会导致数据丢失，谨慎操作
    conn = op.get_bind()
    if conn.engine.name == 'mysql':
        op.execute("""
            ALTER TABLE data_sources 
            MODIFY COLUMN status BOOLEAN NOT NULL DEFAULT true COMMENT '启用状态'
        """)
    elif conn.engine.name == 'postgresql':
        op.execute("""
            ALTER TABLE data_sources 
            ALTER COLUMN status TYPE BOOLEAN USING 
                CASE 
                    WHEN status = 'online' THEN true
                    ELSE false
                END,
            ALTER COLUMN status SET DEFAULT true
        """)
    # SQLite不处理，因为它是弱类型