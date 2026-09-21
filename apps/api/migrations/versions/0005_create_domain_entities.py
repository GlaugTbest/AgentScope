"""create domain entities

Revision ID: 0005
Revises: 0004_create_projects
"""
from alembic import op
import sqlalchemy as sa
revision = "0005"
down_revision = "0004_create_projects"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table("agent_versions", sa.Column("agent_version_id", sa.String(200), primary_key=True), sa.Column("agent_id", sa.String(36), sa.ForeignKey("agents.agent_id"), nullable=False), sa.Column("project_id", sa.String(200), sa.ForeignKey("projects.project_id"), nullable=False), sa.Column("reference", sa.String(500)), sa.Column("metadata", sa.JSON, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("agent_instances", sa.Column("instance_id", sa.String(200), primary_key=True), sa.Column("project_id", sa.String(200), sa.ForeignKey("projects.project_id"), nullable=False), sa.Column("agent_id", sa.String(200)), sa.Column("agent_version_id", sa.String(200), sa.ForeignKey("agent_versions.agent_version_id")), sa.Column("runtime", sa.String(200)), sa.Column("started_at", sa.DateTime(timezone=True), nullable=False), sa.Column("metadata", sa.JSON, nullable=False))
    op.create_table("tasks", sa.Column("task_id", sa.String(200), primary_key=True), sa.Column("project_id", sa.String(200), sa.ForeignKey("projects.project_id"), nullable=False), sa.Column("title", sa.String(500), nullable=False), sa.Column("state", sa.String(32), nullable=False), sa.Column("metadata", sa.JSON, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("delegations", sa.Column("delegation_id", sa.String(200), primary_key=True), sa.Column("task_id", sa.String(200), sa.ForeignKey("tasks.task_id")), sa.Column("source_execution_id", sa.String(200), sa.ForeignKey("executions.execution_id"), nullable=False), sa.Column("target_execution_id", sa.String(200), sa.ForeignKey("executions.execution_id"), nullable=False), sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False), sa.Column("metadata", sa.JSON, nullable=False))
    op.create_index("ix_agent_versions_project_agent", "agent_versions", ["project_id", "agent_id"]); op.create_index("ix_instances_project_agent", "agent_instances", ["project_id", "agent_id"]); op.create_index("ix_tasks_project_created", "tasks", ["project_id", "created_at"]); op.create_index("ix_delegations_task_time", "delegations", ["task_id", "occurred_at"])
def downgrade():
    op.drop_table("delegations"); op.drop_table("tasks"); op.drop_table("agent_instances"); op.drop_table("agent_versions")
