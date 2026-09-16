from sqlalchemy import case, func, select
from sqlalchemy.orm import Session
from types import SimpleNamespace
from datetime import UTC
from ..models import SpanModel, TraceModel
from ..schemas import cost_string

def _filters(statement, agent_name=None, status=None, span_type=None, start_from=None, start_to=None):
    if agent_name: statement = statement.where(TraceModel.agent_name == agent_name)
    if status: statement = statement.where(TraceModel.status == status)
    if start_from: statement = statement.where(TraceModel.start_time >= start_from)
    if start_to: statement = statement.where(TraceModel.start_time < start_to)
    if span_type: statement = statement.where(select(SpanModel.span_id).where(SpanModel.trace_id == TraceModel.trace_id, SpanModel.type == span_type).exists())
    return statement

def _aggregate():
    return select(SpanModel.trace_id.label("trace_id"), func.coalesce(func.sum(SpanModel.input_tokens),0).label("input"), func.coalesce(func.sum(SpanModel.output_tokens),0).label("output"), func.coalesce(func.sum(SpanModel.estimated_cost_nano_usd),0).label("cost"), func.count(SpanModel.span_id).label("spans"), func.coalesce(func.sum(case((SpanModel.type == "llm",1), else_=0)),0).label("llm"), func.coalesce(func.sum(case((SpanModel.type == "tool",1), else_=0)),0).label("tool"), func.coalesce(func.sum(case((SpanModel.status == "error",1), else_=0)),0).label("errors")).group_by(SpanModel.trace_id).subquery()

def timestamp(value):
    return value.replace(tzinfo=UTC).isoformat().replace('+00:00', 'Z') if value else None

def _item(trace, agg):
    input_tokens, output_tokens = int(agg.input or 0), int(agg.output or 0)
    return {"trace_id": trace.trace_id, "agent_name": trace.agent_name, "start_time": timestamp(trace.start_time), "end_time": timestamp(trace.end_time), "duration_ms": trace.duration_ms, "status": trace.status, "total_input_tokens": input_tokens, "total_output_tokens": output_tokens, "total_tokens": input_tokens+output_tokens, "estimated_cost": cost_string(int(agg.cost or 0)), "llm_calls": int(agg.llm or 0), "tool_calls": int(agg.tool or 0), "span_count": int(agg.spans or 0), "error_count": int(agg.errors or 0)}

def list_traces(session: Session, **kwargs):
    limit, offset = kwargs.pop("limit",25), kwargs.pop("offset",0); agg = _aggregate()
    base = _filters(select(TraceModel, agg).outerjoin(agg, agg.c.trace_id == TraceModel.trace_id), **kwargs)
    total = session.scalar(_filters(select(func.count()).select_from(TraceModel), **kwargs)) or 0
    rows = session.execute(base.order_by(TraceModel.start_time.desc(), TraceModel.trace_id.desc()).limit(limit).offset(offset)).all()
    items = []
    for row in rows:
        aggregate = SimpleNamespace(
            input=row[2], output=row[3], cost=row[4], spans=row[5],
            llm=row[6], tool=row[7], errors=row[8],
        )
        items.append(_item(row[0], aggregate))
    return {"items": items, "total": total, "limit": limit, "offset": offset}

def summarize_traces(session: Session, **kwargs):
    agg = _aggregate()
    statement = select(func.count(TraceModel.trace_id), func.sum(case((TraceModel.status == 'success', 1), else_=0)), func.avg(TraceModel.duration_ms), func.sum(agg.c.input), func.sum(agg.c.output), func.sum(agg.c.cost), func.sum(agg.c.errors)).select_from(TraceModel).outerjoin(agg, agg.c.trace_id == TraceModel.trace_id)
    total, success, latency, inputs, outputs, cost, errors = session.execute(_filters(statement, **kwargs)).one()
    inputs, outputs = int(inputs or 0), int(outputs or 0)
    return {"total_traces": total, "success_rate": success / total if total else None, "average_latency_ms": latency, "total_input_tokens": inputs, "total_output_tokens": outputs, "total_tokens": inputs + outputs, "estimated_cost": cost_string(int(cost or 0)), "error_count": int(errors or 0), "failed_traces": total - int(success or 0)}

def get_trace(session: Session, trace_id: str):
    trace = session.get(TraceModel, trace_id)
    if not trace: return None
    aggregates = _aggregate()
    agg = session.execute(select(aggregates).where(aggregates.c.trace_id == trace_id)).first()
    item = _item(trace, agg or SimpleNamespace(input=0, output=0, cost=0, llm=0, tool=0, spans=0, errors=0))
    item.update({"metadata": trace.metadata_, "error": trace.error})
    spans = session.scalars(select(SpanModel).where(SpanModel.trace_id==trace_id).order_by(SpanModel.start_time, SpanModel.span_id)).all()
    return {"trace": item, "spans": [{"span_id":s.span_id,"trace_id":s.trace_id,"parent_span_id":s.parent_span_id,"type":s.type,"name":s.name,"start_time":timestamp(s.start_time),"end_time":timestamp(s.end_time),"duration_ms":s.duration_ms,"status":s.status,"model":s.model,"provider":s.provider,"input_tokens":s.input_tokens,"output_tokens":s.output_tokens,"estimated_cost":cost_string(s.estimated_cost_nano_usd),"input":s.input,"output":s.output,"metadata":s.metadata_,"error":s.error} for s in spans]}
