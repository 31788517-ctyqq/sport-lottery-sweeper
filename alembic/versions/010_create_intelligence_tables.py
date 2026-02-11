"""create intelligence tables

Revision ID: 010_intelligence_tables
Revises: 009_llm_providers
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010_intelligence_tables'
down_revision = '009_llm_providers'
branch_labels = None
depends_on = None


def upgrade():
    # 定义枚举类型
    intelligence_type_enum = sa.Enum(
        'injury', 'suspension', 'lineup', 'tactics', 'weather', 'referee', 'venue',
        'odds', 'transfer', 'rumor', 'prediction', 'statistics', 'preview', 'review',
        'motivation', 'history', 'form', 'other',
        name='intelligencetypeenum',
        native_enum=False
    )
    
    intelligence_source_enum = sa.Enum(
        'official', 'bookmaker', 'media', 'social_media', 'expert', 'ai_analysis',
        'user_submission', 'system',
        name='intelligencesourceenum',
        native_enum=False
    )
    
    confidence_level_enum = sa.Enum(
        'very_low', 'low', 'medium', 'high', 'very_high', 'confirmed',
        name='confidencelevelenum',
        native_enum=False
    )
    
    importance_level_enum = sa.Enum(
        'low', 'medium', 'high', 'critical',
        name='importancelevelenum',
        native_enum=False
    )
    
    # 创建情报类型表
    op.create_table(
        'intelligence_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('subcategory', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('default_weight', sa.Float(), nullable=False, server_default=sa.text('0.5')),
        sa.Column('default_confidence', confidence_level_enum, nullable=False, server_default='medium'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_intelligence_types_name', 'intelligence_types', ['name'], unique=True)
    op.create_index('ix_intelligence_types_code', 'intelligence_types', ['code'], unique=True)
    op.create_index('ix_intelligence_types_is_active', 'intelligence_types', ['is_active'])
    op.create_index('ix_intelligence_types_category', 'intelligence_types', ['category'])
    op.create_index('idx_intel_types_active_category', 'intelligence_types', ['is_active', 'category'])
    op.create_index('idx_intel_types_system', 'intelligence_types', ['is_system'])
    
    # 创建信息来源表
    op.create_table(
        'intelligence_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('reliability_score', sa.Float(), nullable=False, server_default=sa.text('0.5')),
        sa.Column('update_frequency', sa.String(length=50), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_official', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('last_crawled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('config', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('total_items', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('success_rate', sa.Float(), nullable=False, server_default=sa.text('0.0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code'),
        sa.CheckConstraint('reliability_score >= 0.0 AND reliability_score <= 1.0', name='ck_reliability_score_range'),
        sa.CheckConstraint('success_rate >= 0.0 AND success_rate <= 1.0', name='ck_success_rate_range')
    )
    op.create_index('ix_intelligence_sources_name', 'intelligence_sources', ['name'], unique=True)
    op.create_index('ix_intelligence_sources_code', 'intelligence_sources', ['code'], unique=True)
    op.create_index('ix_intelligence_sources_is_active', 'intelligence_sources', ['is_active'])
    op.create_index('ix_intelligence_sources_is_verified', 'intelligence_sources', ['is_verified'])
    op.create_index('ix_intelligence_sources_is_official', 'intelligence_sources', ['is_official'])
    op.create_index('ix_intelligence_sources_source_type', 'intelligence_sources', ['source_type'])
    op.create_index('idx_intel_sources_active_reliable', 'intelligence_sources', ['is_active', 'is_verified'])
    op.create_index('idx_intel_sources_type', 'intelligence_sources', ['source_type'])
    
    # 创建情报数据表
    op.create_table(
        'intelligence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('player_id', sa.Integer(), nullable=True),
        sa.Column('type_id', sa.Integer(), nullable=True),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('keywords', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('tags', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('confidence', confidence_level_enum, nullable=False, server_default='medium'),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default=sa.text('0.5')),
        sa.Column('importance', importance_level_enum, nullable=False, server_default='medium'),
        sa.Column('base_weight', sa.Float(), nullable=False, server_default=sa.text('0.5')),
        sa.Column('weight_multiplier', sa.Float(), nullable=False, server_default=sa.text('1.0')),
        sa.Column('calculated_weight', sa.Float(), nullable=False, server_default=sa.text('0.0')),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('event_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expiration_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_duplicate', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('duplicate_of', sa.Integer(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('external_url', sa.String(length=500), nullable=True),
        sa.Column('external_data', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('odds_data', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('stats_data', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('prediction_data', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('attachments', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('images', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('comment_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('share_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('popularity_score', sa.Float(), nullable=False, server_default=sa.text('0.0')),
        sa.Column('trending_score', sa.Float(), nullable=False, server_default=sa.text('0.0')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['type_id'], ['intelligence_types.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['source_id'], ['intelligence_sources.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['duplicate_of'], ['intelligence.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0', name='ck_confidence_score_range'),
        sa.CheckConstraint('base_weight >= 0.0 AND base_weight <= 1.0', name='ck_base_weight_range'),
        sa.CheckConstraint('weight_multiplier >= 0.5 AND weight_multiplier <= 2.0', name='ck_weight_multiplier_range'),
        sa.CheckConstraint('popularity_score >= 0.0', name='ck_popularity_score_positive'),
        sa.CheckConstraint('trending_score >= 0.0', name='ck_trending_score_positive')
    )
    op.create_index('ix_intelligence_match_id', 'intelligence', ['match_id'])
    op.create_index('ix_intelligence_team_id', 'intelligence', ['team_id'])
    op.create_index('ix_intelligence_player_id', 'intelligence', ['player_id'])
    op.create_index('ix_intelligence_type_id', 'intelligence', ['type_id'])
    op.create_index('ix_intelligence_source_id', 'intelligence', ['source_id'])
    op.create_index('ix_intelligence_title', 'intelligence', ['title'])
    op.create_index('ix_intelligence_confidence', 'intelligence', ['confidence'])
    op.create_index('ix_intelligence_importance', 'intelligence', ['importance'])
    op.create_index('ix_intelligence_calculated_weight', 'intelligence', ['calculated_weight'])
    op.create_index('ix_intelligence_published_at', 'intelligence', ['published_at'])
    op.create_index('ix_intelligence_event_time', 'intelligence', ['event_time'])
    op.create_index('ix_intelligence_expiration_at', 'intelligence', ['expiration_at'])
    op.create_index('ix_intelligence_status', 'intelligence', ['status'])
    op.create_index('ix_intelligence_is_verified', 'intelligence', ['is_verified'])
    op.create_index('ix_intelligence_is_duplicate', 'intelligence', ['is_duplicate'])
    op.create_index('ix_intelligence_reviewed_by', 'intelligence', ['reviewed_by'])
    op.create_index('ix_intelligence_reviewed_at', 'intelligence', ['reviewed_at'])
    op.create_index('ix_intelligence_external_id', 'intelligence', ['external_id'])
    op.create_index('ix_intelligence_view_count', 'intelligence', ['view_count'])
    op.create_index('ix_intelligence_like_count', 'intelligence', ['like_count'])
    op.create_index('ix_intelligence_comment_count', 'intelligence', ['comment_count'])
    op.create_index('ix_intelligence_share_count', 'intelligence', ['share_count'])
    op.create_index('ix_intelligence_popularity_score', 'intelligence', ['popularity_score'])
    op.create_index('ix_intelligence_is_deleted', 'intelligence', ['is_deleted'])
    op.create_index('ix_intelligence_deleted_at', 'intelligence', ['deleted_at'])
    op.create_index('ix_intelligence_created_by', 'intelligence', ['created_by'])
    op.create_index('ix_intelligence_updated_by', 'intelligence', ['updated_by'])
    op.create_index('ix_intelligence_deleted_by', 'intelligence', ['deleted_by'])
    op.create_index('ix_intelligence_created_at', 'intelligence', ['created_at'])
    op.create_index('ix_intelligence_updated_at', 'intelligence', ['updated_at'])
    op.create_index('idx_intelligence_match_type', 'intelligence', ['match_id', 'type_id'])
    op.create_index('idx_intelligence_match_source', 'intelligence', ['match_id', 'source_id'])
    op.create_index('idx_intelligence_published_weight', 'intelligence', ['published_at', 'calculated_weight'])
    op.create_index('idx_intelligence_status_verified', 'intelligence', ['status', 'is_verified'])
    op.create_index('idx_intelligence_tags', 'intelligence', ['tags'])
    op.create_index('idx_intelligence_keywords', 'intelligence', ['keywords'])
    op.create_index('idx_intelligence_popularity', 'intelligence', ['popularity_score'])
    op.create_index('idx_intelligence_event_time', 'intelligence', ['event_time'])
    op.create_index('idx_intelligence_expiration', 'intelligence', ['expiration_at'])
    op.create_index('idx_intelligence_reviewed', 'intelligence', ['reviewed_by', 'reviewed_at'])
    op.create_index('idx_intelligence_external_id', 'intelligence', ['external_id'])
    
    # 创建情报关联表
    op.create_table(
        'intelligence_relations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('intelligence_id', sa.Integer(), nullable=False),
        sa.Column('related_intelligence_id', sa.Integer(), nullable=False),
        sa.Column('relation_type', sa.String(length=50), nullable=False),
        sa.Column('relation_strength', sa.Float(), nullable=False, server_default=sa.text('0.5')),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['intelligence_id'], ['intelligence.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_intelligence_id'], ['intelligence.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('relation_strength >= 0.0 AND relation_strength <= 1.0', name='ck_relation_strength_range'),
        sa.CheckConstraint('intelligence_id != related_intelligence_id', name='ck_no_self_reference'),
        sa.UniqueConstraint('intelligence_id', 'related_intelligence_id', name='uq_intelligence_relation')
    )
    op.create_index('ix_intelligence_relations_intelligence_id', 'intelligence_relations', ['intelligence_id'])
    op.create_index('ix_intelligence_relations_related_intelligence_id', 'intelligence_relations', ['related_intelligence_id'])
    op.create_index('ix_intelligence_relations_relation_type', 'intelligence_relations', ['relation_type'])
    op.create_index('ix_intelligence_relations_created_at', 'intelligence_relations', ['created_at'])
    op.create_index('ix_intelligence_relations_created_by', 'intelligence_relations', ['created_by'])
    op.create_index('idx_intel_relations_intel_type', 'intelligence_relations', ['intelligence_id', 'relation_type'])
    op.create_index('idx_intel_relations_both', 'intelligence_relations', ['intelligence_id', 'related_intelligence_id'], unique=True)
    op.create_index('idx_intel_relations_created', 'intelligence_relations', ['created_at'])
    op.create_index('idx_intel_relations_creator', 'intelligence_relations', ['created_by'])
    
    # 创建情报分析表
    op.create_table(
        'intelligence_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('hour', sa.Integer(), nullable=True),
        sa.Column('intelligence_type', sa.String(length=50), nullable=True),
        sa.Column('intelligence_source', sa.String(length=50), nullable=True),
        sa.Column('league_id', sa.Integer(), nullable=True),
        sa.Column('total_items', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('verified_items', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('high_importance_items', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('avg_response_time', sa.Float(), nullable=False, server_default=sa.text('0.0')),
        sa.Column('items_within_1h', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('items_within_24h', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('avg_confidence_score', sa.Float(), nullable=False, server_default=sa.text('0.0')),
        sa.Column('avg_weight', sa.Float(), nullable=False, server_default=sa.text('0.0')),
        sa.Column('total_views', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('total_likes', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('total_comments', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('total_shares', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('avg_popularity_score', sa.Float(), nullable=False, server_default=sa.text('0.0')),
        sa.Column('trending_items', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_intelligence_analytics_date', 'intelligence_analytics', ['date'])
    op.create_index('ix_intelligence_analytics_hour', 'intelligence_analytics', ['hour'])
    op.create_index('ix_intelligence_analytics_intelligence_type', 'intelligence_analytics', ['intelligence_type'])
    op.create_index('ix_intelligence_analytics_intelligence_source', 'intelligence_analytics', ['intelligence_source'])
    op.create_index('ix_intelligence_analytics_league_id', 'intelligence_analytics', ['league_id'])
    op.create_index('idx_intelligence_analytics_date_type', 'intelligence_analytics', ['date', 'intelligence_type'])
    op.create_index('idx_intelligence_analytics_date_source', 'intelligence_analytics', ['date', 'intelligence_source'])
    op.create_index('idx_intelligence_analytics_date_league', 'intelligence_analytics', ['date', 'league_id'])


def downgrade():
    # 删除表（按依赖关系反向顺序）
    op.drop_table('intelligence_analytics')
    op.drop_table('intelligence_relations')
    op.drop_table('intelligence')
    op.drop_table('intelligence_sources')
    op.drop_table('intelligence_types')
    
    # 删除枚举类型（如果存在）- SQLite不支持，但保留以兼容PostgreSQL
    try:
        op.execute('DROP TYPE IF EXISTS intelligencetypeenum')
    except:
        pass
    
    try:
        op.execute('DROP TYPE IF EXISTS intelligencesourceenum')
    except:
        pass
    
    try:
        op.execute('DROP TYPE IF EXISTS confidencelevelenum')
    except:
        pass
    
    try:
        op.execute('DROP TYPE IF EXISTS importancelevelenum')
    except:
        pass