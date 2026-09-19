"""Agente de demonstração local: Ollama + ferramenta, sem API paga."""
import argparse
import json
import urllib.error
import urllib.request

from agentscope import AgentScope

parser = argparse.ArgumentParser()
parser.add_argument("--error", action="store_true")
parser.add_argument("--model", default="qwen3:4b")
args = parser.parse_args()


def call_ollama(model: str, prompt: str) -> dict:
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps({"model": model, "prompt": prompt, "stream": False, "think": False}).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.loads(response.read())


def local_knowledge(query: str) -> dict:
    return {"query": query, "documents": [
        "AgentScope registra traces, spans, tokens, duração e eventos de atividade.",
        "A ingestão incremental mantém execuções abertas visíveis no painel local.",
    ], "source": "local-demo"}


scope = AgentScope(capture_content=True, raise_on_error=True)
try:
    with scope.trace("local-research-agent", metadata={"demo": "real", "model": args.model}) as trace:
        trace.activity("Consultando a base local", completed=0, total=1)
        with trace.span(type="tool", name="search-local-knowledge") as span:
            knowledge = local_knowledge("Como observar agentes de IA?")
            span.set_input({"query": knowledge["query"]})
            span.set_output(knowledge)
        if args.error:
            raise RuntimeError("Falha de demonstração solicitada")
        trace.activity("Gerando resposta no modelo local", documents=len(knowledge["documents"]))
        with trace.span(type="llm", name="answer-with-ollama", model=args.model, provider="ollama") as span:
            prompt = "Resuma em uma frase: " + " ".join(knowledge["documents"])
            try:
                result = call_ollama(args.model, prompt)
            except urllib.error.URLError as error:
                raise RuntimeError("Ollama não está disponível em http://127.0.0.1:11434") from error
            span.set_usage(input_tokens=result.get("prompt_eval_count", 0), output_tokens=result.get("eval_count", 0), estimated_cost="0")
            span.set_output({"answer": result.get("response", ""), "done_reason": result.get("done_reason")})
        trace.activity("Resposta concluída", status="success")
    scope.flush()
    print(f"Trace sent: {trace.trace_id}\nOpen: http://127.0.0.1:3000/traces/{trace.trace_id}")
finally:
    scope.shutdown()
