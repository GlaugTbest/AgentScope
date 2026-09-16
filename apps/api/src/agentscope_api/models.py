from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class AgentModel(Base):
    __tablename__ = "agents"
    agent_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[Any] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class TraceModel(Base):
    __tablename__ = "traces"
    trace_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    agent_name: Mapped[str] = mapped_column(String(200), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(7), nullable=False)
    error: Mapped[Any] = mapped_column(JSON, nullable=True)
    metadata_: Mapped[Any] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class SpanModel(Base):
    __tablename__ = "spans"
    span_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trace_id: Mapped[str] = mapped_column(ForeignKey("traces.trace_id"), nullable=False)
    parent_span_id: Mapped[Any] = mapped_column(ForeignKey("spans.span_id"), nullable=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(7), nullable=False)
    model: Mapped[Any] = mapped_column(String(200), nullable=True)
    provider: Mapped[Any] = mapped_column(String(200), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_nano_usd: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    input: Mapped[Any] = mapped_column(JSON, nullable=True)
    output: Mapped[Any] = mapped_column(JSON, nullable=True)
    metadata_: Mapped[Any] = mapped_column("metadata", JSON, default=dict, nullable=False)
    error: Mapped[Any] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


Index("ix_traces_start_id", TraceModel.start_time, TraceModel.trace_id)
Index("ix_traces_agent_start", TraceModel.agent_name, TraceModel.start_time)
Index("ix_traces_status_start", TraceModel.status, TraceModel.start_time)
Index("ix_spans_trace_start", SpanModel.trace_id, SpanModel.start_time)
Index("ix_spans_parent", SpanModel.parent_span_id)
Index("ix_spans_type_trace", SpanModel.type, SpanModel.trace_id)
Index("ix_spans_status_trace", SpanModel.status, SpanModel.trace_id)
