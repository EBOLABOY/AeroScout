"""add is_admin to users table

Revision ID: 76db113d9a1e
Revises: c47909388e6b
Create Date: 2023-05-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76db113d9a1e'
down_revision: Union[str, None] = 'c47909388e6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_admin column to users table."""
    # First, check if the users table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'users' not in tables:
        # Create the users table if it doesn't exist
        print("Creating users table...")
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
            sa.Column('email', sa.String(255), nullable=False, unique=True),
            sa.Column('hashed_password', sa.String(255), nullable=False),
            sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='0'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('last_login_at', sa.DateTime(), nullable=True),
            sa.Column('api_call_count_today', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('last_api_call_date', sa.DateTime(), nullable=True)
        )
        print("Users table created with is_admin column")
    else:
        # Check if the column already exists before adding it
        # This makes the migration more robust and idempotent
        columns = [col['name'] for col in inspector.get_columns('users')]

        if 'is_admin' not in columns:
            op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='0'))
            print("Added is_admin column to users table")
        else:
            print("is_admin column already exists in users table")


def downgrade() -> None:
    """Remove is_admin column from users table."""
    # First, check if the users table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'users' in tables:
        # Check if the column exists before dropping it
        columns = [col['name'] for col in inspector.get_columns('users')]

        if 'is_admin' in columns:
            op.drop_column('users', 'is_admin')
            print("Removed is_admin column from users table")
        else:
            print("is_admin column does not exist in users table")
    else:
        print("Users table does not exist, nothing to downgrade")
