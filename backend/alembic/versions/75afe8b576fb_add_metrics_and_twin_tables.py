"""Add metrics and twin tables

Revision ID: 75afe8b576fb
Revises: f68be6710ca6
Create Date: 2026-09-24 11:58:29.622582
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '75afe8b576fb'

down_revision = 'f68be6710ca6'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade schema."""
    # Create metrics table
    op.create_table(
        'metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('infrastructure.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cpu_usage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('memory_usage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('disk_usage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('network_usage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('latency', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metrics_service_id'), 'metrics', ['service_id'], unique=False)
    op.create_index(op.f('ix_metrics_timestamp'), 'metrics', ['timestamp'], unique=False)

    # Create twins table
    op.create_table(
        'twins',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('infrastructure.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('current_state', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('predicted_state', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('health_score', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('failure_probability', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('last_sync', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_twins_service_id'), 'twins', ['service_id'], unique=True)

    # Create twin_history table
    op.create_table(
        'twin_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('twin_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('twins.id', ondelete='CASCADE'), nullable=False),
        sa.Column('state', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('health_score', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_twin_history_twin_id'), 'twin_history', ['twin_id'], unique=False)
    op.create_index(op.f('ix_twin_history_timestamp'), 'twin_history', ['timestamp'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_twin_history_timestamp'), table_name='twin_history')
    op.drop_index(op.f('ix_twin_history_twin_id'), table_name='twin_history')
    op.drop_table('twin_history')
    op.drop_index(op.f('ix_twins_service_id'), table_name='twins')
    op.drop_table('twins')
    op.drop_index(op.f('ix_metrics_timestamp'), table_name='metrics')
    op.drop_index(op.f('ix_metrics_service_id'), table_name='metrics')
    op.drop_table('metrics')
