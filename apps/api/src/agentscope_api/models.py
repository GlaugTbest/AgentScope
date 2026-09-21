from datetime import datetime
from typing import Any
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class AgentModel(Base):
    __tablename__ = "agents"
    agent_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[Any] = mapped_column(String(500), nullable=True)
    registration_source: Mapped[str] = mapped_column(String(16), default="manual", nullable=False)
    last_seen_at: Mapped[Any] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ProjectModel(Base):
    __tablename__ = "projects"
    project_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[Any] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class AgentVersionModel(Base):
    __tablename__ = "agent_versions"
    agent_version_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.agent_id"), nullable=False)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    reference: Mapped[Any] = mapped_column(String(500), nullable=True)
    metadata_: Mapped[Any] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class InstanceModel(Base):
    __tablename__ = "agent_instances"
    instance_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    agent_id: Mapped[Any] = mapped_column(String(200), nullable=True)
    agent_version_id: Mapped[Any] = mapped_column(ForeignKey("agent_versions.agent_version_id"), nullable=True)
    runtime: Mapped[Any] = mapped_column(String(200), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    metadata_: Mapped[Any] = mapped_column("metadata", JSON, default=dict, nullable=False)


class TaskModel(Base):
    __tablename__ = "tasks"
    task_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    state: Mapped[str] = mapped_column(String(32), default="created", nullable=False)
    metadata_: Mapped[Any] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class DelegationModel(Base):
    __tablename__ = "delegations"
    delegation_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    task_id: Mapped[Any] = mapped_column(ForeignKey("tasks.task_id"), nullable=True)
    source_execution_id: Mapped[str] = mapped_column(ForeignKey("executions.execution_id"), nullable=False)
    target_execution_id: Mapped[str] = mapped_column(ForeignKey("executions.execution_id"), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metadata_: Mapped[Any] = mapped_column("metadata", JSON, default=dict, nullable=False)


class PriceCatalogModel(Base):
    __tablename__ = "price_catalogs"
    catalog_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    model: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(200), nullable=False)
    input_per_million_nano_usd: Mapped[int] = mapped_column(Integer, nullable=False)
    output_per_million_nano_usd: Mapped[int] = mapped_column(Integer, nullable=False)
    simulated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class EvaluationModel(Base):
    __tablename__ = "evaluations"
    evaluation_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    task_id: Mapped[Any] = mapped_column(ForeignKey("tasks.task_id"), nullable=True)
    agent_version_id: Mapped[Any] = mapped_column(ForeignKey("agent_versions.agent_version_id"), nullable=True)
    criterion: Mapped[str] = mapped_column(String(200), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    evidence: Mapped[Any] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ExperimentModel(Base):
    __tablename__ = "experiments"
    experiment_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    baseline_version_id: Mapped[str] = mapped_column(ForeignKey("agent_versions.agent_version_id"), nullable=False)
    variant_version_id: Mapped[str] = mapped_column(ForeignKey("agent_versions.agent_version_id"), nullable=False)
    baseline: Mapped[Any] = mapped_column(JSON, nullable=False)
    variant: Mapped[Any] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ExecutionModel(Base):
    __tablename__ = "executions"
    execution_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(200), nullable=False, default="local")
    agent_id: Mapped[Any] = mapped_column(String(200), nullable=True)
    agent_name: Mapped[str] = mapped_column(String(200), nullable=False)
    instance_id: Mapped[Any] = mapped_column(String(200), nullable=True)
    task_id: Mapped[Any] = mapped_column(String(200), nullable=True)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[Any] = mapped_column(DateTime(timezone=True), nullable=True)
    last_event_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metadata_: Mapped[Any] = mapped_column("metadata", JSON, default=dict, nullable=False)


class ActivityEventModel(Base):
    __tablename__ = "activity_events"
    event_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    execution_id: Mapped[str] = mapped_column(ForeignKey("executions.execution_id"), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(200), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    payload: Mapped[Any] = mapped_column(JSON, default=dict, nullable=False)


Index("ix_executions_project_state", ExecutionModel.project_id, ExecutionModel.state)
Index("ix_executions_agent_last_event", ExecutionModel.agent_name, ExecutionModel.last_event_at)
Index("ix_activity_events_execution_time", ActivityEventModel.execution_id, ActivityEventModel.occurred_at)
Index("ix_agent_versions_project_agent", AgentVersionModel.project_id, AgentVersionModel.agent_id)
Index("ix_instances_project_agent", InstanceModel.project_id, InstanceModel.agent_id)
Index("ix_tasks_project_created", TaskModel.project_id, TaskModel.created_at)
Index("ix_delegations_task_time", DelegationModel.task_id, DelegationModel.occurred_at)
Index("ix_evaluations_project_created", EvaluationModel.project_id, EvaluationModel.created_at)
Index("ix_experiments_project_created", ExperimentModel.project_id, ExperimentModel.created_at)


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
