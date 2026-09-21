from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from typing import Literal
from sqlalchemy.exc import IntegrityError
from .body_limit import BodyLimitMiddleware
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker
from .auth import require_key
from .config import Settings
from .db import make_engine, session_dependency
from .models import AgentModel, AgentVersionModel, DelegationModel, InstanceModel, ProjectModel, TaskModel
from .schemas import AgentCreate, AgentVersionCreate, DelegationCreate, EventBatch, IngestBatch, InstanceCreate, ProjectCreate, TaskCreate
from .services.events import EventConflict, get_execution, ingest_events, list_executions
from .services.ingestion import BatchConflict, BatchInvalid, ingest_batch
from .services.otlp import batches as otlp_batches
from .services.operations import export_trace, prune_traces
from .services.queries import get_trace, latency_percentiles, list_traces, summarize_traces

def create_app():
    settings=Settings.from_env(); engine=make_engine(settings.database_url); factory=sessionmaker(engine, expire_on_commit=False)
    @asynccontextmanager
    async def lifespan(app):
        app.state.engine=engine; app.state.session_factory=factory; yield; engine.dispose()
    app=FastAPI(lifespan=lifespan)
    def session(): yield from session_dependency(factory)
    app.add_middleware(BodyLimitMiddleware)
    @app.get("/health")
    def health(db: Session=Depends(session)):
        try: db.execute(text("SELECT 1")); return {"status":"ok"}
        except Exception: raise HTTPException(503,"database unavailable")
    protected=[Depends(require_key(settings))]
    @app.get("/v1/projects", dependencies=protected)
    def projects(db: Session=Depends(session)):
        items = db.query(ProjectModel).order_by(ProjectModel.created_at.desc()).all()
        return {"items": [{"project_id": item.project_id, "name": item.name, "description": item.description, "created_at": item.created_at.isoformat()} for item in items]}
    @app.post("/v1/projects", dependencies=protected)
    def create_project(project: ProjectCreate, db: Session=Depends(session)):
        item = ProjectModel(project_id=project.project_id, name=project.name.strip(), description=project.description)
        db.add(item)
        try: db.commit()
        except IntegrityError:
            db.rollback(); raise HTTPException(409, "project id or name already exists")
        return JSONResponse({"project_id": item.project_id, "name": item.name, "description": item.description, "created_at": item.created_at.isoformat()}, status_code=201)
    @app.get("/v1/agent-versions", dependencies=protected)
    def agent_versions(project_id: str, db: Session=Depends(session)):
        items = db.query(AgentVersionModel).filter(AgentVersionModel.project_id == project_id).order_by(AgentVersionModel.created_at.desc()).all()
        return {"items": [{"agent_version_id": item.agent_version_id, "agent_id": item.agent_id, "project_id": item.project_id, "reference": item.reference, "metadata": item.metadata_, "created_at": item.created_at.isoformat()} for item in items]}
    @app.post("/v1/agent-versions", dependencies=protected)
    def create_agent_version(version: AgentVersionCreate, db: Session=Depends(session)):
        item = AgentVersionModel(agent_version_id=version.agent_version_id, agent_id=version.agent_id, project_id=version.project_id, reference=version.reference, metadata_=version.metadata); db.add(item)
        try: db.commit()
        except IntegrityError: db.rollback(); raise HTTPException(409, "agent version, project, or agent is invalid")
        return JSONResponse({"agent_version_id": item.agent_version_id, "agent_id": item.agent_id, "project_id": item.project_id, "reference": item.reference, "metadata": item.metadata_}, status_code=201)
    @app.get("/v1/instances", dependencies=protected)
    def instances(project_id: str, db: Session=Depends(session)):
        items = db.query(InstanceModel).filter(InstanceModel.project_id == project_id).order_by(InstanceModel.started_at.desc()).all()
        return {"items": [{"instance_id": item.instance_id, "agent_id": item.agent_id, "agent_version_id": item.agent_version_id, "runtime": item.runtime, "started_at": item.started_at.isoformat(), "metadata": item.metadata_} for item in items]}
    @app.post("/v1/instances", dependencies=protected)
    def create_instance(instance: InstanceCreate, db: Session=Depends(session)):
        item = InstanceModel(instance_id=instance.instance_id, project_id=instance.project_id, agent_id=instance.agent_id, agent_version_id=instance.agent_version_id, runtime=instance.runtime, metadata_=instance.metadata); db.add(item)
        try: db.commit()
        except IntegrityError: db.rollback(); raise HTTPException(409, "instance, project, or agent version is invalid")
        return JSONResponse({"instance_id": item.instance_id, "project_id": item.project_id, "runtime": item.runtime, "metadata": item.metadata_}, status_code=201)
    @app.get("/v1/tasks", dependencies=protected)
    def tasks(project_id: str, limit: int = 25, offset: int = 0, db: Session=Depends(session)):
        if not 1 <= limit <= 100 or offset < 0: raise HTTPException(422, "invalid pagination")
        query = db.query(TaskModel).filter(TaskModel.project_id == project_id).order_by(TaskModel.created_at.desc())
        return {"items": [{"task_id": item.task_id, "project_id": item.project_id, "title": item.title, "state": item.state, "metadata": item.metadata_, "created_at": item.created_at.isoformat()} for item in query.limit(limit).offset(offset)], "total": query.count(), "limit": limit, "offset": offset}
    @app.post("/v1/tasks", dependencies=protected)
    def create_task(task: TaskCreate, db: Session=Depends(session)):
        item = TaskModel(task_id=task.task_id, project_id=task.project_id, title=task.title, metadata_=task.metadata); db.add(item)
        try: db.commit()
        except IntegrityError: db.rollback(); raise HTTPException(409, "task id or project is invalid")
        return JSONResponse({"task_id": item.task_id, "project_id": item.project_id, "title": item.title, "state": item.state, "metadata": item.metadata_}, status_code=201)
    @app.get("/v1/delegations", dependencies=protected)
    def delegations(task_id: str | None = None, limit: int = 25, offset: int = 0, db: Session = Depends(session)):
        if not 1 <= limit <= 100 or offset < 0: raise HTTPException(422, "invalid pagination")
        query = db.query(DelegationModel)
        if task_id: query = query.filter(DelegationModel.task_id == task_id)
        query = query.order_by(DelegationModel.occurred_at.desc())
        return {"items": [{"delegation_id": item.delegation_id, "task_id": item.task_id, "source_execution_id": item.source_execution_id, "target_execution_id": item.target_execution_id, "occurred_at": item.occurred_at.isoformat() + "Z", "metadata": item.metadata_} for item in query.limit(limit).offset(offset)], "total": query.count(), "limit": limit, "offset": offset}
    @app.post("/v1/delegations", dependencies=protected)
    def create_delegation(delegation: DelegationCreate, db: Session = Depends(session)):
        item = DelegationModel(delegation_id=delegation.delegation_id, task_id=delegation.task_id, source_execution_id=delegation.source_execution_id, target_execution_id=delegation.target_execution_id, occurred_at=delegation.occurred_at.replace(tzinfo=None), metadata_=delegation.metadata)
        db.add(item)
        try: db.commit()
        except IntegrityError: db.rollback(); raise HTTPException(409, "delegation id, task, or execution is invalid")
        return JSONResponse({"delegation_id": item.delegation_id, "task_id": item.task_id, "source_execution_id": item.source_execution_id, "target_execution_id": item.target_execution_id, "occurred_at": item.occurred_at.isoformat() + "Z", "metadata": item.metadata_}, status_code=201)
    @app.get("/v1/agents", dependencies=protected)
    def agents(db: Session=Depends(session)):
        items = db.query(AgentModel).order_by(AgentModel.created_at.desc()).all()
        return {"items": [{"agent_id": item.agent_id, "name": item.name, "description": item.description, "created_at": item.created_at} for item in items]}
    @app.post("/v1/agents", dependencies=protected)
    def create_agent(agent: AgentCreate, db: Session=Depends(session)):
        existing = db.query(AgentModel).filter(AgentModel.name == agent.name).first()
        if existing: raise HTTPException(409, "agent name already exists")
        item = AgentModel(agent_id=str(uuid4()), name=agent.name, description=agent.description)
        db.add(item)
        try: db.commit()
        except IntegrityError:
            db.rollback(); raise HTTPException(409, "agent name already exists")
        db.refresh(item)
        return JSONResponse({"agent_id": item.agent_id, "name": item.name, "description": item.description, "created_at": item.created_at.isoformat()}, status_code=201)
    @app.post("/v1/agents/{agent_id}/demo", dependencies=protected)
    def demo_agent(agent_id: str, scenario: Literal['success', 'error'] = 'success', db: Session=Depends(session)):
        agent = db.get(AgentModel, agent_id)
        if not agent: raise HTTPException(404, "agent not found")
        start = datetime.now(UTC); trace_id = uuid4(); root_id = uuid4(); tool_id = uuid4()
        def timestamp(ms): return (start + timedelta(milliseconds=ms)).isoformat().replace("+00:00", "Z")
        payload = IngestBatch.model_validate({"trace":{"trace_id":str(trace_id),"agent_name":agent.name,"start_time":timestamp(0),"end_time":timestamp(860),"status":"success","metadata":{"agentscope.demo":True,"agent_id":agent.agent_id},"error":None},"spans":[
            {"span_id":str(root_id),"trace_id":str(trace_id),"parent_span_id":None,"type":"llm","name":"plan-research","start_time":timestamp(0),"end_time":timestamp(260),"status":"success","model":"demo-reasoner","provider":"local","input_tokens":124,"output_tokens":88,"estimated_cost":"0.000042000","metadata":{"demo":True},"error":None},
            {"span_id":str(tool_id),"trace_id":str(trace_id),"parent_span_id":None,"type":"tool","name":"search-knowledge","start_time":timestamp(300),"end_time":timestamp(690),"status":"success","input_tokens":0,"output_tokens":0,"estimated_cost":"0","metadata":{"demo":True},"error":None},
            {"span_id":str(uuid4()),"trace_id":str(trace_id),"parent_span_id":str(tool_id),"type":"retrieval","name":"retrieve-context","start_time":timestamp(390),"end_time":timestamp(610),"status":"success","input_tokens":0,"output_tokens":0,"estimated_cost":"0","metadata":{"documents":3},"error":None},
            {"span_id":str(uuid4()),"trace_id":str(trace_id),"parent_span_id":None,"type":"llm","name":"compose-answer","start_time":timestamp(710),"end_time":timestamp(860),"status":"success","model":"demo-reasoner","provider":"local","input_tokens":220,"output_tokens":146,"estimated_cost":"0.000071000","metadata":{"demo":True},"error":None}]})
        for span in payload.spans:
            span.input = {'task': 'Comparar documentos sobre observabilidade de agentes'}
            span.output = {'result': 'Conteúdo sintético para teste', 'step': span.name}
        payload.trace.metadata['scenario'] = scenario
        if scenario == 'error':
            from .schemas import ErrorInfo
            payload.trace.status = 'error'
            payload.trace.error = ErrorInfo(type='TimeoutError', message='A execução foi interrompida porque a fonte de documentos excedeu o tempo limite.', stacktrace='demo.retrieve_context: simulated timeout')
            payload.spans[2].status = 'error'
            payload.spans[2].error = ErrorInfo(type='TimeoutError', message='Fonte de documentos excedeu o tempo limite (falha simulada).', stacktrace='demo.retrieve_context: simulated timeout')
            payload.spans[2].output = None
        try: result = ingest_batch(db, payload)
        except BatchConflict: raise HTTPException(409, "demo trace conflict")
        return JSONResponse({"trace_id":result.trace_id,"span_count":result.span_count,"created":result.created}, status_code=201)
    @app.post("/v1/ingest", dependencies=protected)
    def ingest(batch: IngestBatch, db: Session=Depends(session)):
        try: result=ingest_batch(db,batch)
        except BatchInvalid as exc: raise HTTPException(422,str(exc))
        except BatchConflict: raise HTTPException(409,"trace id already exists with different content")
        return JSONResponse({"trace_id":result.trace_id,"span_count":result.span_count,"created":result.created}, status_code=201 if result.created else 200)
    @app.post("/v1/otlp/v1/traces", dependencies=protected)
    def otlp_traces(payload: dict, db: Session=Depends(session)):
        results = []
        try:
            for batch in otlp_batches(payload): results.append(ingest_batch(db, batch))
        except (BatchConflict, BatchInvalid) as exc: raise HTTPException(422, str(exc))
        return {"accepted": len(results), "traces": [result.trace_id for result in results]}
    @app.post("/v1/events", dependencies=protected)
    def events(batch: EventBatch, db: Session=Depends(session)):
        try: result = ingest_events(db, batch)
        except EventConflict: raise HTTPException(409, "event id already exists with different content")
        return JSONResponse({"accepted": result.accepted, "duplicate": result.duplicate}, status_code=201 if result.accepted else 200)
    @app.get("/v1/executions", dependencies=protected)
    def executions(project_id: str = "local", state: str | None = None, db: Session=Depends(session)):
        return list_executions(db, project_id, state)
    @app.get("/v1/executions/{execution_id}", dependencies=protected)
    def execution(execution_id: str, db: Session=Depends(session)):
        result = get_execution(db, execution_id)
        if not result: raise HTTPException(404, "execution not found")
        return result
    @app.get("/v1/traces/summary", dependencies=protected)
    def summary(agent_name:str|None=None,status:Literal['success','error']|None=None,span_type:str|None=None,start_from:datetime|None=None,start_to:datetime|None=None, db:Session=Depends(session)):
        return summarize_traces(db,**filters(agent_name,status,span_type,start_from,start_to))
    @app.get("/v1/metrics/latency", dependencies=protected)
    def latency_metrics(agent_name:str|None=None,status:Literal['success','error']|None=None,span_type:str|None=None,start_from:datetime|None=None,start_to:datetime|None=None, db:Session=Depends(session)):
        return latency_percentiles(db, **filters(agent_name,status,span_type,start_from,start_to))
    @app.get("/v1/traces", dependencies=protected)
    def traces(agent_name:str|None=None,status:Literal['success','error']|None=None,span_type:str|None=None,start_from:datetime|None=None,start_to:datetime|None=None,limit:int=25,offset:int=0,db:Session=Depends(session)):
        if not 1<=limit<=100 or offset<0: raise HTTPException(422,"invalid pagination")
        return list_traces(db,**filters(agent_name,status,span_type,start_from,start_to),limit=limit,offset=offset)
    @app.get("/v1/traces/{trace_id}", dependencies=protected)
    def detail(trace_id:str,db:Session=Depends(session)):
        result=get_trace(db,trace_id)
        if not result: raise HTTPException(404,"trace not found")
        return result
    @app.get("/v1/traces/{trace_id}/export", dependencies=protected)
    def export(trace_id:str, db:Session=Depends(session)):
        result = export_trace(db, trace_id)
        if not result: raise HTTPException(404, "trace not found")
        return result
    @app.delete("/v1/operations/retention", dependencies=protected)
    def retention(before: datetime, db: Session=Depends(session)):
        if before.tzinfo is None: raise HTTPException(422, "retention date requires timezone")
        return prune_traces(db, before.astimezone(UTC).replace(tzinfo=None))
    return app

app=create_app()

def filters(agent_name, status, span_type, start_from, start_to):
    for value in (start_from, start_to):
        if value and value.tzinfo is None: raise HTTPException(422, 'date filter requires timezone')
    if start_from and start_to and start_to <= start_from: raise HTTPException(422, 'invalid date interval')
    return dict(agent_name=agent_name, status=status, span_type=span_type, start_from=start_from.astimezone(UTC).replace(tzinfo=None) if start_from else None, start_to=start_to.astimezone(UTC).replace(tzinfo=None) if start_to else None)
