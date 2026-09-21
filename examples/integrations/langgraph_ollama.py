"""LangGraph + AgentScope + OpenAI-compatible client, all pointed at local Ollama."""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from agentscope import AgentScope, LangGraphObserver, local_ollama_openai_client


class State(TypedDict):
    question: str
    answer: str


client = local_ollama_openai_client()  # rejects any endpoint outside loopback


def answer(state: State):
    completion = client.chat.completions.create(
        model="qwen3:4b",
        messages=[{"role": "user", "content": state["question"]}],
    )
    return {"answer": completion.choices[0].message.content or ""}


builder = StateGraph(State)
builder.add_node("answer", answer)
builder.add_edge(START, "answer")
builder.add_edge("answer", END)
graph = builder.compile()

scope = AgentScope(capture_content=True, project_id="integration-langgraph")
try:
    result = LangGraphObserver(scope, "langgraph-local-agent").invoke(graph, {"question": "Explique em uma frase o que é observabilidade."})
    print(result["answer"])
finally:
    scope.shutdown()
