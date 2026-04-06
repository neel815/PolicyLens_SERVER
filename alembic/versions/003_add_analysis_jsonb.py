"""Add analysis JSONB column to policies table

Revision ID: 003_add_analysis_jsonb
Revises: 002_add_policy
Create Date: 2026-04-06

This migration adds a flexible JSONB column to store complete AI responses
while maintaining backward compatibility with existing structured columns.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_analysis_jsonb'
down_revision = '002_add_policy'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add analysis column to store full AI response
    op.add_column(
        'policies',
        sa.Column('analysis', sa.JSON(), nullable=True)
    )


def downgrade() -> None:
    # Remove analysis column
    op.drop_column('policies', 'analysis')
