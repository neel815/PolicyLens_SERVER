"""Add claim_simulations table for storing simulation results

Revision ID: 004_add_claim_simulations
Revises: 003_add_analysis_jsonb
Create Date: 2026-04-06

This migration adds a new claim_simulations table to store policy simulation
and claim test results, with foreign key relationship to policies table.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_claim_simulations'
down_revision = '003_add_analysis_jsonb'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'claim_simulations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('scenario', sa.Text(), nullable=False),
        sa.Column('coverage_result', sa.Boolean(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_claim_simulations_policy_id', 'claim_simulations', ['policy_id'], unique=False)


def downgrade():
    op.drop_index('ix_claim_simulations_policy_id', table_name='claim_simulations')
    op.drop_table('claim_simulations')
