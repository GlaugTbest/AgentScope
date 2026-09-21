from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from ..models import SpanModel, TraceModel
from .queries import get_trace

SENSITIVE = {"api_key", "authorization", "password", "secret", "token"}


def sanitize(value):
    if isinstance(value, dict): return {key: "[REDACTED]" if key.lower() in SENSITIVE else sanitize(item) for key, item in value.items()}
    if isinstance(value, list): return [sanitize(item) for item in value]
    return value


def export_trace(session: Session, trace_id: str):
    item = get_trace(session, trace_id)
    if not item: return None
    return sanitize(item)


def prune_traces(session: Session, before):
    identifiers = list(session.scalars(select(TraceModel.trace_id).where(TraceModel.end_time < before)))
    if not identifiers: return {"deleted_traces": 0, "deleted_spans": 0}
    # A trace can contain nested spans. Unlink parent references first so this
    # works on databases which enforce self-referential foreign keys eagerly.
    session.execute(update(SpanModel).where(SpanModel.trace_id.in_(identifiers)).values(parent_span_id=None))
    deleted_spans = session.execute(delete(SpanModel).where(SpanModel.trace_id.in_(identifiers))).rowcount or 0
    deleted_traces = session.execute(delete(TraceModel).where(TraceModel.trace_id.in_(identifiers))).rowcount or 0
    session.commit()
    return {"deleted_traces": deleted_traces, "deleted_spans": deleted_spans}
