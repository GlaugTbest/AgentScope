"""mark legacy auto-discovered agents as discovered

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-21
"""

from alembic import op


revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE agents SET registration_source = 'discovered' "
        "WHERE description = 'Identificado automaticamente pela ingestão'"
    )


def downgrade():
    op.execute(
        "UPDATE agents SET registration_source = 'manual' "
        "WHERE description = 'Identificado automaticamente pela ingestão'"
    )
