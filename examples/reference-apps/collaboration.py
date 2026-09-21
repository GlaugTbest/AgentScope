"""REAL-02: researcher, writer and reviewer using a local Ollama model."""
import argparse

from agentscope import AgentScope
from common import ollama, usage
from rag import search


def ask(scope, agent: str, model: str, instruction: str, context: str) -> str:
    with scope.trace(agent, metadata={"application": "REAL-02", "role": agent, "model": model}) as trace:
        trace.activity("Recebeu delegação", role=agent)
        with trace.span(type="llm", name=f"{agent}-local-inference", model=model, provider="ollama") as span:
            result = ollama(model, f"{instruction}\n\nContexto:\n{context}")
            answer = result.get("response", "")
            span.set_input({"instruction": instruction, "context": context})
            span.set_output({"answer": answer})
            span.set_usage(**usage(result))
        trace.activity("Entregou resultado ao próximo agente", role=agent)
        return answer


def main():
    parser = argparse.ArgumentParser(description="Colaboração local observável")
    parser.add_argument("--task", default="Explique como investigar falhas de agentes sem expor segredos.")
    parser.add_argument("--model", default="qwen3:4b")
    args = parser.parse_args()
    scope = AgentScope(capture_content=True, project_id="reference-collaboration")
    try:
        evidence = "\n".join(item["text"] for item in search(args.task))
        research = ask(scope, "researcher", args.model, "Extraia fatos úteis para a tarefa: " + args.task, evidence)
        draft = ask(scope, "writer", args.model, "Escreva uma resposta curta com base na pesquisa para: " + args.task, research)
        review = ask(scope, "reviewer", args.model, "Revise o texto, preserve apenas alegações apoiadas e devolva versão final.", draft)
        print(review)
    finally:
        scope.shutdown()


if __name__ == "__main__": main()
