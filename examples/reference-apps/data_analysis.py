"""REAL-03: deterministic local SQLite query plus an Ollama explanation."""
import argparse
import sqlite3

from agentscope import AgentScope
from common import ollama, usage

ROWS = [("2026-01", 120), ("2026-02", 180), ("2026-03", 200)]


def query_local_data():
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("create table sales (month text primary key, revenue integer not null)")
        connection.executemany("insert into sales values (?, ?)", ROWS)
        return connection.execute("select sum(revenue) as q1_revenue from sales").fetchone()[0]
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description="Análise de dados local observável")
    parser.add_argument("--model", default="qwen3:4b")
    args = parser.parse_args()
    scope = AgentScope(capture_content=True, project_id="reference-data")
    try:
        with scope.trace("data-analyst", metadata={"application": "REAL-03", "model": args.model}) as trace:
            trace.activity("Consultando SQLite local", dataset="sales")
            with trace.span(type="tool", name="sqlite-q1-revenue") as span:
                revenue = query_local_data()
                span.set_input({"sql": "select sum(revenue) as q1_revenue from sales"})
                span.set_output({"q1_revenue": revenue})
            prompt = f"Em português, explique em uma frase que a receita do primeiro trimestre é {revenue}. Não invente números."
            with trace.span(type="llm", name="explain-query-result", model=args.model, provider="ollama") as span:
                result = ollama(args.model, prompt)
                span.set_input({"prompt": prompt})
                span.set_output({"answer": result.get("response", ""), "q1_revenue": revenue})
                span.set_usage(**usage(result))
            trace.activity("Análise concluída", q1_revenue=revenue)
            print(result.get("response", ""))
    finally:
        scope.shutdown()


if __name__ == "__main__": main()
