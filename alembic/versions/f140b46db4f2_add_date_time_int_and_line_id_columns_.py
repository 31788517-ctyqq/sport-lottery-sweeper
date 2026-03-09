"""Add date_time_int and line_id columns to football_matches

Revision ID: f140b46db4f2
Revises: f5c7597d4ea5
Create Date: 2026-02-12 00:06:06.574791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f140b46db4f2'
down_revision: Union[str, None] = 'f5c7597d4ea5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands for adding date_time_int and line_id columns ###
    op.add_column('football_matches', 
                  sa.Column('date_time_int', sa.Integer(), nullable=False, 
                           server_default='0', comment='期号，如 26024'))
    op.add_column('football_matches', 
                  sa.Column('line_id', sa.Integer(), nullable=False, 
                           server_default='0', comment='该期内的序号，如 1'))


def downgrade() -> None:
    # ### commands to drop the columns ###
    op.drop_column('football_matches', 'line_id')
    op.drop_column('football_matches', 'date_time_int')
