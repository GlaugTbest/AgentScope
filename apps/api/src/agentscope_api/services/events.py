from dataclasses import dataclass

from sqlalchemy.orm import Session

from ..models import ActivityEventModel, ExecutionModel
from ..schemas import EventBatch, IncrementalEvent


TERMINAL = {"completed", "failed", "cancelled"}


@dataclass(frozen=True)
class EventIngestResult:
    accepted: int
    duplicate: int


class EventConflict(Exception):
    pass


def _time(event: IncrementalEvent):
    return event.occurred_at.replace(tzinfo=None)


def _state(event: IncrementalEvent) -> str:
    return {
        "execution.completed": "completed",
        "execution.failed": "failed",
        "execution.cancelled": "cancelled",
    }.get(event.type, "executing")


def _matches(existing: ActivityEventModel, event: IncrementalEvent) -> bool:
    return (
        existing.execution_id == event.execution_id
        and existing.schema_version == event.schema_version
        and existing.type == event.type
        and existing.source == event.source
        and existing.occurred_at == _time(event)
        and existing.payload == event.payload
    )


def _execution(session: Session, event: IncrementalEvent) -> ExecutionModel:
    current = session.get(ExecutionModel, event.execution_id)
    when = _time(event)
    if current is None:
        state = _state(event)
        current = ExecutionModel(
            execution_id=event.execution_id,
            project_id=event.project_id,
            agent_id=event.agent_id,
            agent_name=event.agent_name,
            instance_id=event.instance_id,
            task_id=event.task_id,
            state=state,
            started_at=when,
            ended_at=when if state in TERMINAL else None,
            last_event_at=when,
            metadata_=event.payload.get("metadata", {}),
        )
        session.add(current)
        return current
    if when >= current.last_event_at and current.state not in TERMINAL:
        state = _state(event)
        current.last_event_at = when
        current.agent_id = event.agent_id or current.agent_id
        current.instance_id = event.instance_id or current.instance_id
        current.task_id = event.task_id or current.task_id
        current.state = state
        if state in TERMINAL:
            current.ended_at = when
    return current


def ingest_events(session: Session, batch: EventBatch) -> EventIngestResult:
    accepted = duplicate = 0
    try:
        with session.begin():
            for event in batch.events:
                existing = session.get(ActivityEventModel, event.event_id)
                if existing:
                    if not _matches(existing, event):
                        raise EventConflict(event.event_id)
                    duplicate += 1
                    continue
                _execution(session, event)
                session.flush()
                session.add(ActivityEventModel(
                    event_id=event.event_id,
                    execution_id=event.execution_id,
                    schema_version=event.schema_version,
                    type=event.type,
                    source=event.source,
                    occurred_at=_time(event),
                    payload=event.payload,
                ))
                accepted += 1
        return EventIngestResult(accepted=accepted, duplicate=duplicate)
    except Exception:
        session.rollback()
        raise


def list_executions(session: Session, project_id: str = "local", state: str | None = None):
    query = session.query(ExecutionModel).filter(ExecutionModel.project_id == project_id)
    if state:
        query = query.filter(ExecutionModel.state == state)
    items = query.order_by(ExecutionModel.last_event_at.desc()).all()
    return {"items": [_execution_response(item) for item in items]}


def get_execution(session: Session, execution_id: str):
    item = session.get(ExecutionModel, execution_id)
    if not item:
        return None
    events = session.query(ActivityEventModel).filter(
        ActivityEventModel.execution_id == execution_id
    ).order_by(ActivityEventModel.occurred_at, ActivityEventModel.event_id).all()
    return {
        "execution": _execution_response(item),
        "events": [{
            "event_id": event.event_id, "type": event.type, "source": event.source,
            "occurred_at": event.occurred_at.isoformat() + "Z", "received_at": event.received_at.isoformat() + "Z",
            "payload": event.payload,
        } for event in events],
    }


def _execution_response(item: ExecutionModel):
    def timestamp(value):
        return value.isoformat() + "Z" if value else None
    return {
        "execution_id": item.execution_id, "project_id": item.project_id,
        "agent_id": item.agent_id, "agent_name": item.agent_name, "instance_id": item.instance_id,
        "task_id": item.task_id, "state": item.state, "started_at": timestamp(item.started_at),
        "ended_at": timestamp(item.ended_at), "last_event_at": timestamp(item.last_event_at),
        "metadata": item.metadata_,
    }
