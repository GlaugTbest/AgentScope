from .trace import Trace
from .transport import HttpTransport
from .events import BackgroundExporter, event
from .privacy import sanitize
from uuid import uuid4

class AgentScope:
    def __init__(self, *, api_key="dev", endpoint="http://127.0.0.1:8000", capture_content=False, raise_on_error=False, transport=None, project_id="local", agent_id=None, export_buffer_size=1000, export_batch_size=100, export_max_retries=3, redact_fields=None):
        self.capture_content=capture_content; self.raise_on_error=raise_on_error; self.transport=transport or HttpTransport(endpoint,api_key,raise_on_error); self.project_id=project_id; self.agent_id=agent_id; self.instance_id=str(uuid4()); self.redact_fields=frozenset(field.lower() for field in (redact_fields or {"api_key", "authorization", "password", "secret", "token"})); self.exporter=BackgroundExporter(self.transport, export_buffer_size, export_batch_size, max_retries=export_max_retries) if hasattr(self.transport,"send_events") else None
    def trace(self, agent_name, *, metadata=None): return Trace(self,agent_name,metadata or {})
    def emit(self, kind, trace, payload=None):
        if self.exporter: self.exporter.submit(event(kind, project_id=self.project_id, agent_name=trace.agent_name, agent_id=self.agent_id, instance_id=self.instance_id, execution_id=trace.trace_id, payload=self.sanitize(payload or {})))
    def sanitize(self, value): return sanitize(value, self.redact_fields)
    def flush(self, timeout=None):
        return self.exporter.flush(timeout) if self.exporter else True
    def shutdown(self, timeout=2):
        return self.exporter.shutdown(timeout) if self.exporter else True
    @property
    def diagnostics(self):
        return self.exporter.diagnostics if self.exporter else {"enqueued": 0, "exported": 0, "dropped": 0, "failed": 0, "retries": 0, "pending": 0}
