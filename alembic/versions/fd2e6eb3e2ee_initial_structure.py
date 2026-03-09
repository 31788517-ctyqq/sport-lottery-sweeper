"""initial_structure

Revision ID: fd2e6eb3e2ee
Revises: 005_sp_management
Create Date: 2026-01-22 12:13:57.955130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd2e6eb3e2ee'
down_revision: Union[str, None] = '005_sp_management'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
