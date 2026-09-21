from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..models import SpanModel, TraceModel
from ..schemas import IngestBatch, to_nano
from .agents import ensure_agent

@dataclass(frozen=True)
class IngestResult:
    trace_id: str
    span_count: int
    created: bool

class BatchConflict(Exception): pass
class BatchInvalid(Exception): pass

def _validate(batch: IngestBatch):
    trace = batch.trace
    if trace.end_time < trace.start_time: raise BatchInvalid("trace end precedes start")
    ids = {str(span.span_id) for span in batch.spans}
    if len(ids) != len(batch.spans): raise BatchInvalid("duplicate span id")
    by_id = {str(span.span_id): span for span in batch.spans}
    for span in batch.spans:
        if str(span.trace_id) != str(trace.trace_id): raise BatchInvalid("span trace mismatch")
        if span.end_time < span.start_time or span.start_time < trace.start_time or span.end_time > trace.end_time: raise BatchInvalid("span outside trace")
        if span.parent_span_id:
            parent = by_id.get(str(span.parent_span_id))
            if not parent or parent.span_id == span.span_id: raise BatchInvalid("invalid parent")
            if span.start_time < parent.start_time or span.end_time > parent.end_time: raise BatchInvalid("span outside parent")
    ordered, visited = [], set()
    for identifier in by_id:
        chain, active = [], set()
        while identifier and identifier not in visited:
            if identifier in active: raise BatchInvalid("span cycle")
            active.add(identifier); chain.append(identifier)
            parent = by_id[identifier].parent_span_id
            identifier = str(parent) if parent else None
        for identifier in reversed(chain):
            ordered.append(by_id[identifier]); visited.add(identifier)
    return ordered

def _same(existing: TraceModel, batch: IngestBatch, spans: list[SpanModel]) -> bool:
    trace = batch.trace
    derived_status = "error" if trace.status == "error" or any(s.status == "error" for s in batch.spans) else "success"
    if existing.status != derived_status: return False
    if (existing.agent_name, existing.start_time, existing.end_time, existing.metadata_, existing.error) != (trace.agent_name, trace.start_time.replace(tzinfo=None), trace.end_time.replace(tzinfo=None), trace.metadata, trace.error.model_dump() if trace.error else None): return False
    by_id = {s.span_id: s for s in spans}
    for s in batch.spans:
        stored_span = by_id.get(str(s.span_id))
        if not stored_span or (stored_span.status, stored_span.model, stored_span.provider, stored_span.input, stored_span.output) != (s.status, s.model, s.provider, s.input, s.output): return False
    incoming = sorted((str(s.span_id), str(s.parent_span_id) if s.parent_span_id else None, s.type, s.name, s.start_time.replace(tzinfo=None), s.end_time.replace(tzinfo=None), s.input_tokens, s.output_tokens, to_nano(s.estimated_cost), s.metadata, s.error.model_dump() if s.error else None) for s in batch.spans)
    stored = sorted((s.span_id, s.parent_span_id, s.type, s.name, s.start_time, s.end_time, s.input_tokens, s.output_tokens, s.estimated_cost_nano_usd, s.metadata_, s.error) for s in spans)
    return incoming == stored

def ingest_batch(session: Session, batch: IngestBatch) -> IngestResult:
    ordered = _validate(batch); trace_id = str(batch.trace.trace_id)
    existing = session.get(TraceModel, trace_id)
    if existing:
        spans = session.scalars(select(SpanModel).where(SpanModel.trace_id == trace_id)).all()
        if _same(existing, batch, spans): return IngestResult(trace_id, len(spans), False)
        raise BatchConflict()
    status = "error" if batch.trace.status == "error" or any(s.status == "error" for s in ordered) else "success"
    # The idempotency lookup starts SQLAlchemy's implicit read transaction.
    # Close it before opening the single atomic write transaction.
    session.rollback()
    try:
        with session.begin():
            trace = batch.trace
            ensure_agent(session, trace.agent_name, trace.end_time.replace(tzinfo=None))
            session.flush()
            session.add(TraceModel(trace_id=trace_id, agent_name=trace.agent_name, start_time=trace.start_time, end_time=trace.end_time, duration_ms=round((trace.end_time-trace.start_time).total_seconds()*1000), status=status, metadata_=trace.metadata, error=trace.error.model_dump() if trace.error else None))
            session.flush()
            for span in ordered:
                session.add(SpanModel(span_id=str(span.span_id), trace_id=trace_id, parent_span_id=str(span.parent_span_id) if span.parent_span_id else None, type=span.type, name=span.name, start_time=span.start_time, end_time=span.end_time, duration_ms=round((span.end_time-span.start_time).total_seconds()*1000), status=span.status, model=span.model, provider=span.provider, input_tokens=span.input_tokens, output_tokens=span.output_tokens, estimated_cost_nano_usd=to_nano(span.estimated_cost), input=span.input, output=span.output, metadata_=span.metadata, error=span.error.model_dump() if span.error else None))
                session.flush()
        return IngestResult(trace_id, len(ordered), True)
    except IntegrityError as error:
        session.rollback()
        existing = session.get(TraceModel, trace_id)
        if existing:
            spans = session.scalars(select(SpanModel).where(SpanModel.trace_id == trace_id)).all()
            if _same(existing, batch, spans): return IngestResult(trace_id, len(spans), False)
        raise BatchConflict() from error
