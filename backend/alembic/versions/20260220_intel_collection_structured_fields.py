"""
Add queue persistence and structured quality fields for intelligence collection.

Revision ID: 20260220_intel_collection_structured_fields
Revises: add_beidan_strategy_tables
Create Date: 2026-02-20 21:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260220_intel_collection_structured_fields"
down_revision = "add_beidan_strategy_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("intel_collection_tasks", schema=None) as batch_op:
        batch_op.add_column(sa.Column("success_rate", sa.Float(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("queue_job_id", sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column("request_payload_json", sa.Text(), nullable=False, server_default="{}"))
        batch_op.add_column(sa.Column("config_snapshot_json", sa.Text(), nullable=False, server_default="{}"))
        batch_op.create_index("ix_intel_collection_tasks_queue_job_id", ["queue_job_id"], unique=False)

    with op.batch_alter_table("intel_collection_match_subtasks", schema=None) as batch_op:
        batch_op.add_column(sa.Column("candidate_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("parsed_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("matched_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("accepted_count", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("blocked_count", sa.Integer(), nullable=False, server_default="0"))

    with op.batch_alter_table("intel_collection_items", schema=None) as batch_op:
        batch_op.add_column(sa.Column("quality_status", sa.String(length=20), nullable=False, server_default="source_view"))
        batch_op.add_column(sa.Column("quality_score", sa.Float(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("quality_pass_reason", sa.Text(), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("quality_block_reason", sa.Text(), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("source_parser", sa.String(length=128), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("article_url", sa.String(length=600), nullable=True))
        batch_op.add_column(sa.Column("match_hit_terms_json", sa.Text(), nullable=False, server_default="[]"))
        batch_op.create_index("ix_intel_collection_items_quality_status", ["quality_status"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("intel_collection_items", schema=None) as batch_op:
        batch_op.drop_index("ix_intel_collection_items_quality_status")
        batch_op.drop_column("match_hit_terms_json")
        batch_op.drop_column("article_url")
        batch_op.drop_column("source_parser")
        batch_op.drop_column("quality_block_reason")
        batch_op.drop_column("quality_pass_reason")
        batch_op.drop_column("quality_score")
        batch_op.drop_column("quality_status")

    with op.batch_alter_table("intel_collection_match_subtasks", schema=None) as batch_op:
        batch_op.drop_column("blocked_count")
        batch_op.drop_column("accepted_count")
        batch_op.drop_column("matched_count")
        batch_op.drop_column("parsed_count")
        batch_op.drop_column("candidate_count")

    with op.batch_alter_table("intel_collection_tasks", schema=None) as batch_op:
        batch_op.drop_index("ix_intel_collection_tasks_queue_job_id")
        batch_op.drop_column("config_snapshot_json")
        batch_op.drop_column("request_payload_json")
        batch_op.drop_column("queue_job_id")
        batch_op.drop_column("success_rate")

