"""create calls and analytics tables for SQLite

Revision ID: 001
Revises: None
Create Date: 2025-07-28

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create calls table
    op.create_table('calls',
        sa.Column('id', sa.String(36), nullable=False),  # UUID as string for SQLite
        sa.Column('call_id', sa.String(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('transcript', sa.Text(), nullable=False),
        sa.Column('agent_talk_ratio', sa.Float(), nullable=True),
        sa.Column('customer_sentiment_score', sa.Float(), nullable=True),
        sa.Column('embedding', sa.Text(), nullable=True),  # Store as JSON string for SQLite
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('call_id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_calls_agent_id'), 'calls', ['agent_id'], unique=False)
    op.create_index(op.f('ix_calls_start_time'), 'calls', ['start_time'], unique=False)
    op.create_index(op.f('ix_calls_call_id'), 'calls', ['call_id'], unique=True)
    
    # Create analytics table
    op.create_table('analytics',
        sa.Column('id', sa.String(36), nullable=False),  # UUID as string for SQLite
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('avg_sentiment', sa.Float(), nullable=True),
        sa.Column('avg_talk_ratio', sa.Float(), nullable=True),
        sa.Column('total_calls', sa.Integer(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_id')
    )


def downgrade():
    op.drop_table('analytics')
    op.drop_index(op.f('ix_calls_call_id'), table_name='calls')
    op.drop_index(op.f('ix_calls_start_time'), table_name='calls')
    op.drop_index(op.f('ix_calls_agent_id'), table_name='calls')
    op.drop_table('calls')
