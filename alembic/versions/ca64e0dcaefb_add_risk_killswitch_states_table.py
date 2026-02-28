"""add risk killswitch states table

Revision ID: ca64e0dcaefb
Revises: rename_date_time_int_to_date_time
Create Date: 2026-02-27 20:47:45.247341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca64e0dcaefb'
down_revision: Union[str, None] = 'rename_date_time_int_to_date_time'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = 'risk_killswitch_states'

    if inspector.has_table(table_name):
        return

    op.create_table(
        table_name,
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('state', sa.String(length=16), nullable=False, server_default='RUN'),
        sa.Column('reason_json', sa.JSON(), nullable=True),
        sa.Column('manual_override', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('operator', sa.String(length=64), nullable=True),
        sa.Column('operator_note', sa.String(length=500), nullable=True),
        sa.Column('triggered_at', sa.DateTime(), nullable=True),
        sa.Column('released_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_risk_killswitch_states_state', table_name, ['state'])
    op.create_index('ix_risk_killswitch_states_created_at', table_name, ['created_at'])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = 'risk_killswitch_states'

    if not inspector.has_table(table_name):
        return

    op.drop_index('ix_risk_killswitch_states_created_at', table_name=table_name)
    op.drop_index('ix_risk_killswitch_states_state', table_name=table_name)
    op.drop_table(table_name)
