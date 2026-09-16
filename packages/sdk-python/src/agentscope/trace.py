from datetime import UTC, datetime, timedelta
import time, traceback, uuid
from .span import Span
from .context import active_span

class Trace:
    def __init__(self,scope,agent_name,metadata): self.scope=scope; self.agent_name=agent_name; self.metadata=metadata; self.trace_id=str(uuid.uuid4()); self.spans=[]
    def __enter__(self): self.start=datetime.now(UTC); self.clock=time.monotonic(); return self
    def span(self, *, type, name, model=None, provider=None, metadata=None): return Span(self,type,name,model,provider,metadata or {})
    def __exit__(self,typ,value,tb):
        end=self.start+timedelta(seconds=time.monotonic()-self.clock); error=None
        if value: error={"type":type(value).__name__,"message":str(value) or type(value).__name__,"stacktrace":"".join(traceback.format_exception(typ,value,tb))}
        payload={"trace":{"trace_id":self.trace_id,"agent_name":self.agent_name,"start_time":self.start.isoformat().replace('+00:00','Z'),"end_time":end.isoformat().replace('+00:00','Z'),"status":"error" if error else "success","metadata":self.metadata,"error":error},"spans":[s.payload() for s in self.spans]}
        try: self.scope.transport.send(payload)
        except Exception:
            if not value and self.scope.raise_on_error: raise
        return False
