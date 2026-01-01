"""Add Orthodox-specific profile fields

Revision ID: add_orthodox_fields
Revises: 70cdecec2ff6
Create Date: 2025-12-31 22:06:49

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_orthodox_fields'
down_revision = '70cdecec2ff6'
branch_labels = None
depends_on = None


def upgrade():
    # Church Attire & Modesty
    op.add_column('profiles', sa.Column('church_attire_women', sa.String(30), nullable=True))
    op.add_column('profiles', sa.Column('modesty_level', sa.String(30), nullable=True))
    
    # Orthodox Sacraments & Practices
    op.add_column('profiles', sa.Column('confession_frequency', sa.String(30), nullable=True))
    op.add_column('profiles', sa.Column('communion_frequency', sa.String(30), nullable=True))
    op.add_column('profiles', sa.Column('icons_in_home', sa.Boolean(), server_default='1', nullable=True))
    op.add_column('profiles', sa.Column('saints_nameday', sa.String(100), nullable=True))
    
    # Marital History
    op.add_column('profiles', sa.Column('marital_history', sa.String(30), nullable=True))
    
    # Family Planning
    op.add_column('profiles', sa.Column('desired_children_count', sa.String(20), nullable=True))
    op.add_column('profiles', sa.Column('children_education_preference', sa.String(50), nullable=True))
    
    # Additional preference
    op.add_column('profiles', sa.Column('seeks_modest_spouse', sa.Boolean(), server_default='0', nullable=True))


def downgrade():
    op.drop_column('profiles', 'seeks_modest_spouse')
    op.drop_column('profiles', 'children_education_preference')
    op.drop_column('profiles', 'desired_children_count')
    op.drop_column('profiles', 'marital_history')
    op.drop_column('profiles', 'saints_nameday')
    op.drop_column('profiles', 'icons_in_home')
    op.drop_column('profiles', 'communion_frequency')
    op.drop_column('profiles', 'confession_frequency')
    op.drop_column('profiles', 'modesty_level')
    op.drop_column('profiles', 'church_attire_women')

