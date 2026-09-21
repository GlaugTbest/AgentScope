# Aplicações locais de referência

Estas aplicações usam exclusivamente `http://127.0.0.1:11434` para inferência com Ollama e enviam telemetria ao AgentScope local. Não usam APIs pagas.

Com a API, o dashboard e o Ollama ativos, execute a partir da raiz:

```text
npm run demo:rag
npm run demo:collaboration
npm run demo:data
.venv/Scripts/python.exe examples/reference-apps/orchestrated_local.py --model qwen3:0.6b
```

- `rag.py` (REAL-01) busca em um corpus lexical local e exige que a resposta cite fontes.
- `collaboration.py` (REAL-02) executa pesquisador, redator e revisor como agentes observáveis individualmente.
- `data_analysis.py` (REAL-03) consulta uma base SQLite em memória e pede ao modelo apenas a explicação do resultado numérico determinado pela consulta.
- `orchestrated_local.py` executa coordenador, pesquisador e revisor com chamadas reais para a API local do Ollama.

O corpus sanitizado contém dez documentos. Para repetir com outras perguntas, passe `--question` ao script RAG. Os exemplos preservam prompts, resultado de ferramentas, tokens e métricas somente quando `capture_content=True`, como configurado explicitamente em cada aplicação.
