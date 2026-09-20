"""create projects

Revision ID: 0004_create_projects
Revises: 0003
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_create_projects"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("projects", sa.Column("project_id", sa.String(200), primary_key=True), sa.Column("name", sa.String(200), nullable=False, unique=True), sa.Column("description", sa.String(500)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))


def downgrade():
    op.drop_table("projects")
