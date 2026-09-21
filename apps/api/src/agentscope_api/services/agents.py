from datetime import datetime
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import AgentModel


def ensure_agent(session: Session, name: str, observed_at: datetime) -> AgentModel:
    agent = session.scalar(select(AgentModel).where(AgentModel.name == name))
    if agent is None:
        agent = AgentModel(
            agent_id=str(uuid5(NAMESPACE_URL, f"agentscope:{name}")), name=name,
            description="Detectado localmente pela telemetria", registration_source="discovered",
            last_seen_at=observed_at,
        )
        session.add(agent)
    elif agent.last_seen_at is None or observed_at > agent.last_seen_at:
        agent.last_seen_at = observed_at
    return agent
