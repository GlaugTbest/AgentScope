"""Orquestra três agentes instrumentados usando a API local do Ollama."""
import argparse
import json
import urllib.request

from agentscope import AgentScope


parser = argparse.ArgumentParser()
parser.add_argument("--model", default="qwen3:0.6b")
args = parser.parse_args()


def ask(prompt: str) -> str:
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps({"model": args.model, "prompt": prompt, "stream": False, "think": False}).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.loads(response.read())["response"].strip()


def worker(name: str, prompt: str) -> tuple[str, str]:
    scope = AgentScope(capture_content=True, raise_on_error=True)
    with scope.trace(name, metadata={"orchestration": "local", "model": args.model}) as trace:
        trace.activity("Recebeu uma delegação do coordenador")
        with trace.span(type="llm", name="answer-delegated-task", model=args.model, provider="ollama") as span:
            span.set_input({"prompt": prompt})
            answer = ask(prompt)
            span.set_output({"answer": answer})
        trace.activity("Entregou o resultado ao coordenador")
    scope.flush(5); scope.shutdown(5)
    return trace.trace_id, answer


coordinator = AgentScope(capture_content=True, raise_on_error=True)
with coordinator.trace("orchestrator-agent", metadata={"orchestration": "local", "model": args.model}) as trace:
    trace.activity("Delegando pesquisa e revisão")
    researcher_id, research = worker("research-agent", "Em uma frase, descreva por que traces ajudam a depurar agentes de IA.")
    reviewer_id, review = worker("review-agent", "Em uma frase, diga qual cuidado de privacidade importa ao registrar agentes de IA.")
    trace.activity("Sintetizando as respostas dos agentes", delegated_agents=2)
    with trace.span(type="llm", name="synthesize-delegations", model=args.model, provider="ollama") as span:
        prompt = f"Una estas duas observações em uma frase clara. Pesquisa: {research}\nPrivacidade: {review}"
        span.set_input({"research": research, "review": review})
        answer = ask(prompt)
        span.set_output({"answer": answer, "delegated_trace_ids": [researcher_id, reviewer_id]})
    trace.activity("Orquestração concluída", delegated_trace_ids=[researcher_id, reviewer_id])
coordinator.flush(5); coordinator.shutdown(5)
print(json.dumps({"coordinator_trace_id": trace.trace_id, "researcher_trace_id": researcher_id, "reviewer_trace_id": reviewer_id, "answer": answer}, ensure_ascii=False))
