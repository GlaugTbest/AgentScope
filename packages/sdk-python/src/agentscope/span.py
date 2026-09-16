from datetime import timedelta
import time, traceback, uuid
from .context import active_span

class Span:
    def __init__(self,trace,type,name,model,provider,metadata): self.trace=trace; self.type=type; self.name=name; self.model=model; self.provider=provider; self.metadata=metadata; self.span_id=str(uuid.uuid4()); self.input_tokens=self.output_tokens=0; self.cost="0"; self.input=self.output=None
    def __enter__(self):
        self.parent=active_span.get(); self.parent_id=self.parent.span_id if self.parent and self.parent.trace is self.trace else None; self.start=self.trace.start+timedelta(seconds=time.monotonic()-self.trace.clock); self.clock=time.monotonic(); self.token=active_span.set(self)
        if len(self.trace.spans) < 1000: self.trace.spans.append(self)
        else: self.trace.metadata['agentscope.dropped_spans'] = self.trace.metadata.get('agentscope.dropped_spans', 0) + 1
        return self
    def __exit__(self,typ,value,tb):
        self.end=self.trace.start+timedelta(seconds=time.monotonic()-self.trace.clock); self.status="error" if value else "success"; self.error={"type":typ.__name__,"message":str(value) or typ.__name__,"stacktrace":"".join(traceback.format_exception(typ,value,tb))} if value else None; active_span.reset(self.token); return False
    def set_usage(self, *, input_tokens, output_tokens, estimated_cost): self.input_tokens=input_tokens; self.output_tokens=output_tokens; self.cost=str(estimated_cost)
    def set_metadata(self, metadata): self.metadata.update(metadata)
    def set_input(self,value):
        if self.trace.scope.capture_content: self.input=value
    def set_output(self,value):
        if self.trace.scope.capture_content: self.output=value
    def payload(self): return {"span_id":self.span_id,"trace_id":self.trace.trace_id,"parent_span_id":self.parent_id,"type":self.type,"name":self.name,"start_time":self.start.isoformat().replace('+00:00','Z'),"end_time":self.end.isoformat().replace('+00:00','Z'),"status":self.status,"model":self.model,"provider":self.provider,"input_tokens":self.input_tokens,"output_tokens":self.output_tokens,"estimated_cost":self.cost,"input":self.input,"output":self.output,"metadata":self.metadata,"error":self.error}
