"""create evaluations, experiments and simulated price catalog

Revision ID: 0006
Revises: 0005
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("price_catalogs", sa.Column("catalog_id", sa.String(200), primary_key=True), sa.Column("model", sa.String(200), nullable=False), sa.Column("provider", sa.String(200), nullable=False), sa.Column("input_per_million_nano_usd", sa.Integer, nullable=False), sa.Column("output_per_million_nano_usd", sa.Integer, nullable=False), sa.Column("simulated", sa.Boolean, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("evaluations", sa.Column("evaluation_id", sa.String(200), primary_key=True), sa.Column("project_id", sa.String(200), sa.ForeignKey("projects.project_id"), nullable=False), sa.Column("task_id", sa.String(200), sa.ForeignKey("tasks.task_id")), sa.Column("agent_version_id", sa.String(200), sa.ForeignKey("agent_versions.agent_version_id")), sa.Column("criterion", sa.String(200), nullable=False), sa.Column("score", sa.Float, nullable=False), sa.Column("passed", sa.Boolean, nullable=False), sa.Column("evidence", sa.JSON, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("experiments", sa.Column("experiment_id", sa.String(200), primary_key=True), sa.Column("project_id", sa.String(200), sa.ForeignKey("projects.project_id"), nullable=False), sa.Column("baseline_version_id", sa.String(200), sa.ForeignKey("agent_versions.agent_version_id"), nullable=False), sa.Column("variant_version_id", sa.String(200), sa.ForeignKey("agent_versions.agent_version_id"), nullable=False), sa.Column("baseline", sa.JSON, nullable=False), sa.Column("variant", sa.JSON, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_evaluations_project_created", "evaluations", ["project_id", "created_at"])
    op.create_index("ix_experiments_project_created", "experiments", ["project_id", "created_at"])


def downgrade():
    op.drop_table("experiments")
    op.drop_table("evaluations")
    op.drop_table("price_catalogs")
