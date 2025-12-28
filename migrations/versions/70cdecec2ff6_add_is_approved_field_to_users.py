"""Add is_approved field to users

Revision ID: 70cdecec2ff6
Revises: 5cc01a7b45a2
Create Date: 2025-12-28 17:01:28.113669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70cdecec2ff6'
down_revision = '5cc01a7b45a2'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_approved to users - simple migration for SQLite
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_approved', sa.Boolean(), nullable=True, default=False))
    
    # Set all existing users as approved (since they were already in the system)
    op.execute("UPDATE users SET is_approved = 1")


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_approved')
