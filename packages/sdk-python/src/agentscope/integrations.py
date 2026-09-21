"""Opt-in adapters for public framework APIs; no global monkey patches."""
from dataclasses import dataclass
from urllib.parse import urlparse


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def local_ollama_openai_client(endpoint: str = "http://127.0.0.1:11434/v1"):
    """Create an OpenAI-compatible client that refuses non-loopback endpoints."""
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in LOCAL_HOSTS:
        raise ValueError("only a loopback Ollama endpoint is supported")
    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError("install agentscope-observability[integrations] to use the OpenAI-compatible client") from error
    return OpenAI(base_url=endpoint.rstrip("/") + "/", api_key="ollama")


@dataclass
class LangGraphObserver:
    """Wrap `graph.invoke` while preserving LangGraph's normal execution model."""
    scope: object
    agent_name: str = "langgraph-agent"

    def invoke(self, graph, graph_input, *, config=None):
        with self.scope.trace(self.agent_name, metadata={"integration": "langgraph"}) as trace:
            trace.activity("Iniciando grafo LangGraph")
            with trace.span(type="tool", name="langgraph.invoke") as span:
                span.set_input({"input_keys": sorted(graph_input) if isinstance(graph_input, dict) else []})
                output = graph.invoke(graph_input, config=config) if config is not None else graph.invoke(graph_input)
                span.set_output({"output_keys": sorted(output) if isinstance(output, dict) else []})
            trace.activity("Grafo LangGraph concluído")
            return output
