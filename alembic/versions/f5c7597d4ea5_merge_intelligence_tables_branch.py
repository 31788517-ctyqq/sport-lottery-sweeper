"""Merge intelligence tables branch

Revision ID: f5c7597d4ea5
Revises: 010472eab443, 010_intelligence_tables
Create Date: 2026-02-12 00:05:31.379393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5c7597d4ea5'
down_revision: Union[str, None] = ('010472eab443', '010_intelligence_tables')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
