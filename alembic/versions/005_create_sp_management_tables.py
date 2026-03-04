"""
创建足球SP管理模块数据表

Revision ID: 005_sp_management
Revises: 004_add_crawler_alert_tables
Create Date: 2026-01-21

包含以下数据表：
1. data_sources - 数据源配置表
2. matches - 比赛信息表（足球SP管理专用）
3. odds_companies - 赔率公司表
4. sp_records - SP值记录表
5. sp_modification_logs - SP值修改日志表
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, mysql, sqlite
import json

# revision identifiers, used by Alembic.
revision = '005_sp_management'
down_revision = '004_add_crawler_alert_tables'
branch_labels = None
depends_on = None


def upgrade():
    # 创建数据源配置表
    op.create_table(
        'data_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='数据源名称'),
        sa.Column('type', sa.String(length=20), nullable=False, comment='类型: api/file'),
        sa.Column('status', sa.Boolean(), nullable=False, server_default='1', comment='启用状态'),
        sa.Column('url', sa.String(length=500), nullable=True, comment='接口地址或文件路径'),
        sa.Column('config', sa.Text(), nullable=True, comment='配置信息(JSON格式)'),
        sa.Column('last_update', sa.DateTime(), nullable=True, comment='最后更新时间'),
        sa.Column('error_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0', comment='错误率'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='创建人ID'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("type IN ('api', 'file')", name='check_data_source_type'),
        sa.CheckConstraint("error_rate >= 0 AND error_rate <= 100", name='check_error_rate_range')
    )
    
    # 创建数据源表索引
    op.create_index('ix_data_sources_name', 'data_sources', ['name'])
    op.create_index('ix_data_sources_type', 'data_sources', ['type'])
    op.create_index('ix_data_sources_status', 'data_sources', ['status'])
    op.create_index('ix_data_sources_last_update', 'data_sources', ['last_update'])
    op.create_index('ix_data_sources_created_by', 'data_sources', ['created_by'])
    
    # 创建比赛信息表（足球SP管理专用）
    op.create_table(
        'matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.String(length=50), nullable=False, comment='比赛唯一标识'),
        sa.Column('home_team', sa.String(length=100), nullable=False, comment='主队名称'),
        sa.Column('away_team', sa.String(length=100), nullable=False, comment='客队名称'),
        sa.Column('match_time', sa.DateTime(), nullable=False, comment='比赛时间'),
        sa.Column('league', sa.String(length=100), nullable=True, comment='联赛/杯赛'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending', comment='比赛状态: pending/ongoing/finished'),
        sa.Column('home_score', sa.Integer(), nullable=True, comment='主队得分'),
        sa.Column('away_score', sa.Integer(), nullable=True, comment='客队得分'),
        sa.Column('final_result', sa.String(length=20), nullable=True, comment='最终赛果'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id', name='uq_matches_match_id'),
        sa.CheckConstraint("status IN ('pending', 'ongoing', 'finished')", name='check_match_status'),
        sa.Index('ix_matches_match_id', 'match_id'),
        sa.Index('ix_matches_match_time', 'match_time'),
        sa.Index('ix_matches_league', 'league'),
        sa.Index('ix_matches_status', 'status')
    )
    
    # 创建赔率公司表
    op.create_table(
        'odds_companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='公司名称'),
        sa.Column('short_name', sa.String(length=20), nullable=True, comment='简称'),
        sa.Column('logo_url', sa.String(length=200), nullable=True, comment='Logo地址'),
        sa.Column('status', sa.Boolean(), nullable=False, server_default='1', comment='启用状态'),
        sa.Column('weight', sa.Numeric(precision=3, scale=2), nullable=False, server_default='1.00', comment='权重/优先级'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("weight >= 0 AND weight <= 10", name='check_weight_range'),
        sa.Index('ix_odds_companies_name', 'name'),
        sa.Index('ix_odds_companies_short_name', 'short_name'),
        sa.Index('ix_odds_companies_status', 'status'),
        sa.Index('ix_odds_companies_weight', 'weight')
    )
    
    # 创建SP值记录表
    op.create_table(
        'sp_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False, comment='比赛ID'),
        sa.Column('company_id', sa.Integer(), nullable=False, comment='公司ID'),
        sa.Column('handicap_type', sa.String(length=20), nullable=False, comment='盘口类型: handicap/no_handicap'),
        sa.Column('handicap_value', sa.Numeric(precision=4, scale=1), nullable=True, comment='让球数值'),
        sa.Column('sp_value', sa.Numeric(precision=8, scale=2), nullable=False, comment='SP值'),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, comment='记录时间'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], name='fk_sp_records_match_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['odds_companies.id'], name='fk_sp_records_company_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("handicap_type IN ('handicap', 'no_handicap')", name='check_handicap_type'),
        sa.CheckConstraint("sp_value > 0", name='check_sp_value_positive'),
        sa.Index('ix_sp_records_match_id', 'match_id'),
        sa.Index('ix_sp_records_company_id', 'company_id'),
        sa.Index('ix_sp_records_handicap_type', 'handicap_type'),
        sa.Index('ix_sp_records_recorded_at', 'recorded_at'),
        sa.Index('idx_match_time', 'match_id', 'recorded_at'),
        sa.Index('idx_company_time', 'company_id', 'recorded_at')
    )
    
    # 创建SP值修改日志表
    op.create_table(
        'sp_modification_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sp_record_id', sa.Integer(), nullable=False, comment='SP记录ID'),
        sa.Column('original_value', sa.Numeric(precision=8, scale=2), nullable=False, comment='原值'),
        sa.Column('modified_value', sa.Numeric(precision=8, scale=2), nullable=False, comment='修改后的值'),
        sa.Column('modified_by', sa.Integer(), nullable=False, comment='修改人ID'),
        sa.Column('reason', sa.Text(), nullable=True, comment='修改原因'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.ForeignKeyConstraint(['sp_record_id'], ['sp_records.id'], name='fk_sp_modification_logs_sp_record_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("original_value >= 0", name='check_original_value_non_negative'),
        sa.CheckConstraint("modified_value >= 0", name='check_modified_value_non_negative'),
        sa.Index('ix_sp_modification_logs_sp_record_id', 'sp_record_id'),
        sa.Index('ix_sp_modification_logs_modified_by', 'modified_by'),
        sa.Index('ix_sp_modification_logs_created_at', 'created_at')
    )
    
    # 插入默认的赔率公司数据
    default_companies = [
        {'name': '竞彩官方', 'short_name': '竞彩', 'weight': 10.00},
        {'name': '威廉希尔', 'short_name': '威廉', 'weight': 9.50},
        {'name': '立博', 'short_name': '立博', 'weight': 9.00},
        {'name': 'Bet365', 'short_name': '365', 'weight': 8.50},
        {'name': '澳门彩票', 'short_name': '澳门', 'weight': 8.00},
        {'name': '香港马会', 'short_name': '马会', 'weight': 8.50},
        {'name': 'Bwin', 'short_name': 'Bwin', 'weight': 7.50},
        {'name': 'Interwetten', 'short_name': 'Inter', 'weight': 7.00}
    ]
    
    for company in default_companies:
        op.execute(f"""
            INSERT INTO odds_companies (name, short_name, weight, status, created_at, updated_at)
            VALUES ('{company['name']}', '{company['short_name']}', {company['weight']}, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """)
    
    # 插入默认的数据源配置
    default_sources = [
        {
            'name': '竞彩官方API',
            'type': 'api',
            'url': 'https://api.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry',
            'config': json.dumps({'timeout': 30, 'retry_times': 3, 'rate_limit': 10})
        },
        {
            'name': '本地CSV文件导入',
            'type': 'file',
            'url': '/data/imports/',
            'config': json.dumps({'allowed_extensions': ['.csv', '.xlsx'], 'max_file_size': 10485760})
        }
    ]
    
    for source in default_sources:
        config_json = source['config'].replace("'", "''")
        op.execute(f"""
            INSERT INTO data_sources (name, type, url, config, status, created_at, updated_at)
            VALUES ('{source['name']}', '{source['type']}', '{source['url']}', '{config_json}', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """)


def downgrade():
    # 删除SP值修改日志表
    op.drop_table('sp_modification_logs')
    
    # 删除SP值记录表
    op.drop_table('sp_records')
    
    # 删除赔率公司表
    op.drop_table('odds_companies')
    
    # 删除比赛信息表
    op.drop_table('matches')
    
    # 删除数据源配置表
    op.drop_table('data_sources')