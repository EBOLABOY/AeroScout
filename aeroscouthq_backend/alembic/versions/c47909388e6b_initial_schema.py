"""initial schema

Revision ID: c47909388e6b
Revises: 76db113d9a1e
Create Date: 2025-05-18 22:21:34.514777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c47909388e6b'
down_revision: Union[str, None] = '76db113d9a1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass