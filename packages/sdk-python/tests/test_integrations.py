import pytest

from agentscope import LangGraphObserver, local_ollama_openai_client


class Trace:
    def __init__(self): self.activities = []; self.inputs = []; self.outputs = []
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def activity(self, message): self.activities.append(message)
    def span(self, **kwargs): return self
    def set_input(self, value): self.inputs.append(value)
    def set_output(self, value): self.outputs.append(value)


class Scope:
    def __init__(self): self.trace_value = Trace()
    def trace(self, *args, **kwargs): return self.trace_value


class Graph:
    def invoke(self, value): return {"answer": value["question"].upper()}


def test_langgraph_observer_wraps_public_invoke_api():
    scope = Scope()
    assert LangGraphObserver(scope).invoke(Graph(), {"question": "ok"}) == {"answer": "OK"}
    assert scope.trace_value.activities == ["Iniciando grafo LangGraph", "Grafo LangGraph concluído"]


def test_openai_compatible_client_refuses_remote_endpoints():
    with pytest.raises(ValueError, match="loopback"):
        local_ollama_openai_client("https://api.openai.com/v1")
