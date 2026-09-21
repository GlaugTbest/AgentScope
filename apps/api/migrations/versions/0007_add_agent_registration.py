"""add agent registration metadata

Revision ID: 0007
Revises: 0006
"""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("agents", sa.Column("registration_source", sa.String(16), nullable=False, server_default="manual"))
    op.add_column("agents", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE agents SET last_seen_at = created_at")


def downgrade():
    op.drop_column("agents", "last_seen_at")
    op.drop_column("agents", "registration_source")
