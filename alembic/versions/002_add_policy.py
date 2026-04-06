"""Add Policy model

Revision ID: 002_add_policy
Revises: 001_initial
Create Date: 2026-04-03

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_policy'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create policies table
    op.create_table(
        'policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.String(length=50), nullable=False),
        sa.Column('policy_type', sa.String(length=100), nullable=False),
        sa.Column('covered_events', sa.JSON(), nullable=False),
        sa.Column('exclusions', sa.JSON(), nullable=False),
        sa.Column('risky_clauses', sa.JSON(), nullable=False),
        sa.Column('coverage_score', sa.Integer(), nullable=False),
        sa.Column('score_reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_policies_user_id'), 'policies', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_policies_user_id'), table_name='policies')
    op.drop_table('policies')
