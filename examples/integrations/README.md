# Integrações locais

Instale as dependências opcionais no ambiente virtual:

```text
.venv\Scripts\python.exe -m pip install -e "packages/sdk-python[integrations]"
```

Depois de iniciar Ollama local, API e dashboard, execute:

```text
.venv\Scripts\python.exe examples/integrations/langgraph_ollama.py
```

O adaptador `LangGraphObserver` envolve a chamada pública `graph.invoke`, sem patches globais. O cliente compatível com OpenAI rejeita URLs que não sejam loopback: ele é deliberadamente limitado ao Ollama local e não certifica a API hospedada da OpenAI.
