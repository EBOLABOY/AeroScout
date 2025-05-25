"""create initial database schema

Revision ID: 0001
Revises: 
Create Date: 2025-05-17 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Add the project root directory to the Python path
import os
import sys
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_dir)

# Import the metadata from the application
# Ensure this path matches your project structure
from app.database.connection import metadata
from app.database import models  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Applies the initial database schema."""
    print("Applying initial database schema based on metadata...")
    print(f"DEBUG: Tables known to metadata in 0001_create_initial_database_schema.py before create_all: {list(metadata.tables.keys())}")
    # Create all tables defined in the metadata
    # Ensure all your models are imported somewhere so they register with metadata
    # (This is typically done in connection.py or models.py)
    try:
        # 所有单独的 op.create_table(...) 调用都应被删除
        metadata.create_all(bind=op.get_bind()) # 只保留这个
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        # Depending on the error, you might want to raise it or handle it
        raise


def downgrade() -> None:
    """Reverts the initial database schema."""
    print("Reverting initial database schema (dropping all tables)...")
    # Drop all tables defined in the metadata
    # Be cautious with this in production environments
    try:
        op.drop_table("potential_hubs")
        op.drop_table("airports")
        op.drop_table("locations")
        op.drop_table("invitation_codes")
        op.drop_table("users")
        metadata.drop_all(bind=op.get_bind())
        print("Tables dropped successfully.")
    except Exception as e:
        print(f"Error dropping tables: {e}")
        # Depending on the error, you might want to raise it or handle it
        raise