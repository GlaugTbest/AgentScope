"""create incremental execution events

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "executions",
        sa.Column("execution_id", sa.String(200), primary_key=True),
        sa.Column("project_id", sa.String(200), nullable=False),
        sa.Column("agent_id", sa.String(200)),
        sa.Column("agent_name", sa.String(200), nullable=False),
        sa.Column("instance_id", sa.String(200)),
        sa.Column("task_id", sa.String(200)),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", sa.JSON, nullable=False),
    )
    op.create_table(
        "activity_events",
        sa.Column("event_id", sa.String(200), primary_key=True),
        sa.Column("execution_id", sa.String(200), sa.ForeignKey("executions.execution_id"), nullable=False),
        sa.Column("schema_version", sa.String(32), nullable=False),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("source", sa.String(200), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
    )
    op.create_index("ix_executions_project_state", "executions", ["project_id", "state"])
    op.create_index("ix_executions_agent_last_event", "executions", ["agent_name", "last_event_at"])
    op.create_index("ix_activity_events_execution_time", "activity_events", ["execution_id", "occurred_at"])


def downgrade():
    op.drop_table("activity_events")
    op.drop_table("executions")
