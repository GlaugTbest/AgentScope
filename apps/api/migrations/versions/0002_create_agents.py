"""create local agents

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("agents", sa.Column("agent_id", sa.String(36), primary_key=True), sa.Column("name", sa.String(200), nullable=False, unique=True), sa.Column("description", sa.String(500)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))

def downgrade():
    op.drop_table("agents")
