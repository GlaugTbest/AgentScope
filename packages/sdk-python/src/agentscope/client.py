from .trace import Trace
from .transport import HttpTransport

class AgentScope:
    def __init__(self, *, api_key="dev", endpoint="http://127.0.0.1:8000", capture_content=False, raise_on_error=False, transport=None):
        self.capture_content=capture_content; self.raise_on_error=raise_on_error; self.transport=transport or HttpTransport(endpoint,api_key,raise_on_error)
    def trace(self, agent_name, *, metadata=None): return Trace(self,agent_name,metadata or {})
