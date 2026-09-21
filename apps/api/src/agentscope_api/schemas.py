from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


NANO = Decimal("1000000000")

def utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return value.astimezone(timezone.utc)

def to_nano(value: Decimal) -> int:
    if value < 0 or value > Decimal("1000000"):
        raise ValueError("estimated_cost out of range")
    return int((value * NANO).to_integral_value(rounding=ROUND_HALF_UP))

def cost_string(nano: int) -> str:
    return f"{Decimal(nano) / NANO:.9f}"

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class ErrorInfo(StrictModel):
    type: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=4000)
    stacktrace: str | None = Field(default=None, max_length=20000)

class TraceInput(StrictModel):
    trace_id: str = Field(min_length=1, max_length=200)
    agent_name: str = Field(min_length=1, max_length=200)
    start_time: datetime
    end_time: datetime
    status: Literal["success", "error"]
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: ErrorInfo | None = None
    _timestamps = field_validator("start_time", "end_time")(utc)
    @field_validator("error")
    @classmethod
    def error_status(cls, value, info):
        if value and info.data.get("status") != "error": raise ValueError("error requires error status")
        return value

class SpanInput(StrictModel):
    span_id: str = Field(min_length=1, max_length=200)
    trace_id: str = Field(min_length=1, max_length=200)
    parent_span_id: str | None = Field(default=None, max_length=200)
    type: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    start_time: datetime
    end_time: datetime
    status: Literal["success", "error"]
    model: str | None = Field(default=None, max_length=200)
    provider: str | None = Field(default=None, max_length=200)
    input_tokens: int = Field(default=0, ge=0, le=2_147_483_647)
    output_tokens: int = Field(default=0, ge=0, le=2_147_483_647)
    estimated_cost: Decimal = Field(default=Decimal(0), ge=0, le=1000000, max_digits=16, decimal_places=9)
    input: Any | None = None
    output: Any | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: ErrorInfo | None = None
    _timestamps = field_validator("start_time", "end_time")(utc)
    @field_validator("error")
    @classmethod
    def error_status(cls, value, info):
        if value and info.data.get("status") != "error": raise ValueError("error requires error status")
        return value

class IngestBatch(StrictModel):
    trace: TraceInput
    spans: list[SpanInput] = Field(max_length=1000)


EventType = Literal[
    "execution.started", "activity.updated", "span.started", "span.ended",
    "usage.recorded", "execution.completed", "execution.failed", "execution.cancelled",
]


class IncrementalEvent(StrictModel):
    event_id: str = Field(min_length=1, max_length=200)
    schema_version: Literal["1.0"] = "1.0"
    type: EventType
    source: str = Field(min_length=1, max_length=200)
    project_id: str = Field(default="local", min_length=1, max_length=200)
    agent_name: str = Field(min_length=1, max_length=200)
    execution_id: str = Field(min_length=1, max_length=200)
    agent_id: str | None = Field(default=None, max_length=200)
    instance_id: str | None = Field(default=None, max_length=200)
    task_id: str | None = Field(default=None, max_length=200)
    occurred_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)
    _timestamp = field_validator("occurred_at")(utc)


class EventBatch(StrictModel):
    events: list[IncrementalEvent] = Field(min_length=1, max_length=1000)


class AgentCreate(StrictModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if not value: raise ValueError("name cannot be blank")
        return value


class ProjectCreate(StrictModel):
    project_id: str = Field(min_length=1, max_length=200, pattern=r"^[a-zA-Z0-9_.-]+$")
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)


class AgentVersionCreate(StrictModel):
    agent_version_id: str = Field(min_length=1, max_length=200)
    agent_id: str = Field(min_length=1, max_length=200)
    project_id: str = Field(min_length=1, max_length=200)
    reference: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InstanceCreate(StrictModel):
    instance_id: str = Field(min_length=1, max_length=200)
    project_id: str = Field(min_length=1, max_length=200)
    agent_id: str | None = Field(default=None, max_length=200)
    agent_version_id: str | None = Field(default=None, max_length=200)
    runtime: str | None = Field(default=None, max_length=200)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskCreate(StrictModel):
    task_id: str = Field(min_length=1, max_length=200)
    project_id: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)
