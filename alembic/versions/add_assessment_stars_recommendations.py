"""Add stars_earned and recommendation to assessment_results

Revision ID: add_assessment_fields
Revises: f49c4d850656
Create Date: 2024-08-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_assessment_fields'
down_revision = 'f49c4d850656'
branch_labels = None
depends_on = None

def upgrade():
    # Add stars_earned column with default value of 3
    op.add_column('assessment_results', sa.Column('stars_earned', sa.Integer(), nullable=True))
    
    # Add recommendation column
    op.add_column('assessment_results', sa.Column('recommendation', sa.Text(), nullable=True))
    
    # Update existing records to have 3 stars
    op.execute("UPDATE assessment_results SET stars_earned = 3 WHERE stars_earned IS NULL")
    
    # Set the column to have a default value going forward
    op.alter_column('assessment_results', 'stars_earned', server_default='3')

def downgrade():
    op.drop_column('assessment_results', 'recommendation')
    op.drop_column('assessment_results', 'stars_earned')