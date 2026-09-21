"""REAL-01: local lexical RAG with a real Ollama response and telemetry."""
import argparse
import json
from pathlib import Path

from agentscope import AgentScope
from common import ollama, usage

ROOT = Path(__file__).parent
CORPUS = json.loads((ROOT / "data" / "rag-corpus.json").read_text(encoding="utf-8"))


def search(query: str):
    terms = {term.lower().strip("?.!,") for term in query.split() if len(term) > 3}
    ranked = sorted(CORPUS, key=lambda item: len(terms & set(item["text"].lower().split())), reverse=True)
    return ranked[:3]


def main():
    parser = argparse.ArgumentParser(description="RAG local observável")
    parser.add_argument("--question", default="Como o AgentScope protege conteúdo sensível?")
    parser.add_argument("--model", default="qwen3:4b")
    args = parser.parse_args()
    scope = AgentScope(capture_content=True, project_id="reference-rag")
    try:
        with scope.trace("document-assistant", metadata={"application": "REAL-01", "model": args.model}) as trace:
            trace.activity("Buscando no corpus local", question=args.question)
            with trace.span(type="retrieval", name="lexical-local-search") as span:
                sources = search(args.question)
                span.set_input({"question": args.question})
                span.set_output({"source_ids": [item["id"] for item in sources]})
            context = "\n".join(f"[{item['id']}] {item['text']}" for item in sources)
            prompt = f"Responda em português usando apenas o contexto e cite os IDs.\nPergunta: {args.question}\nContexto:\n{context}"
            trace.activity("Gerando resposta com Ollama", sources=len(sources))
            with trace.span(type="llm", name="grounded-answer", model=args.model, provider="ollama") as span:
                result = ollama(args.model, prompt)
                span.set_input({"prompt": prompt})
                span.set_output({"answer": result.get("response", ""), "source_ids": [item["id"] for item in sources]})
                span.set_usage(**usage(result))
            trace.activity("Resposta com fontes concluída", status="success")
            print(result.get("response", ""))
    finally:
        scope.shutdown()


if __name__ == "__main__": main()
