"""Merge branches 002 and fd2e6eb3e2ee into main

Revision ID: 010472eab443
Revises: 002, fd2e6eb3e2ee
Create Date: 2026-02-12 00:05:26.484692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '010472eab443'
down_revision: Union[str, None] = ('002', 'fd2e6eb3e2ee')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
