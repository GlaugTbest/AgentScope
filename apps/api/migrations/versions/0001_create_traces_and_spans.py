"""create trace storage

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa
revision="0001"; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("traces",sa.Column("trace_id",sa.String(36),primary_key=True),sa.Column("agent_name",sa.String(200),nullable=False),sa.Column("start_time",sa.DateTime(timezone=True),nullable=False),sa.Column("end_time",sa.DateTime(timezone=True),nullable=False),sa.Column("duration_ms",sa.Integer,nullable=False),sa.Column("status",sa.String(7),nullable=False),sa.Column("error",sa.JSON),sa.Column("metadata",sa.JSON,nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("spans",sa.Column("span_id",sa.String(36),primary_key=True),sa.Column("trace_id",sa.String(36),sa.ForeignKey("traces.trace_id"),nullable=False),sa.Column("parent_span_id",sa.String(36),sa.ForeignKey("spans.span_id")),sa.Column("type",sa.String(64),nullable=False),sa.Column("name",sa.String(200),nullable=False),sa.Column("start_time",sa.DateTime(timezone=True),nullable=False),sa.Column("end_time",sa.DateTime(timezone=True),nullable=False),sa.Column("duration_ms",sa.Integer,nullable=False),sa.Column("status",sa.String(7),nullable=False),sa.Column("model",sa.String(200)),sa.Column("provider",sa.String(200)),sa.Column("input_tokens",sa.Integer,nullable=False),sa.Column("output_tokens",sa.Integer,nullable=False),sa.Column("estimated_cost_nano_usd",sa.Integer,nullable=False),sa.Column("input",sa.JSON),sa.Column("output",sa.JSON),sa.Column("metadata",sa.JSON,nullable=False),sa.Column("error",sa.JSON),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    for table,cols in [("traces",["start_time","trace_id"]),("traces",["agent_name","start_time"]),("traces",["status","start_time"]),("spans",["trace_id","start_time"]),("spans",["parent_span_id"]),("spans",["type","trace_id"]),("spans",["status","trace_id"])]: op.create_index("ix_"+table+"_"+"_".join(cols),table,cols)
def downgrade(): op.drop_table("spans"); op.drop_table("traces")
