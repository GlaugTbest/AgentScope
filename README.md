# AgentScope

Observabilidade local para agentes de IA: API FastAPI, SDK Python e dashboard Next.js.

## Início rápido

```text
npm run setup
npm run dev
# em outro terminal
npm run demo
```

Abra `http://127.0.0.1:3000`. Para registrar uma execução com erro use `npm run demo -- --error`.

O SDK é distribuído como `agentscope-observability`, mas o import é `agentscope`. Não instale outro pacote que exponha o mesmo import no mesmo ambiente.

## SDK

```python
from agentscope import AgentScope
scope = AgentScope(api_key='dev')
with scope.trace('my-agent') as trace:
    with trace.span(type='tool', name='search'):
        pass
```

`capture_content=True` habilita input/output. Metadata e erros podem conter dados sensíveis; evite registrar credenciais. A chave padrão é `dev` e todas as rotas `/v1/*` exigem Bearer authentication. SQLite é local, monousuário e não é indicado para alta concorrência.

## Aplicações de referência

Há três aplicações locais executáveis: RAG, colaboração entre pesquisador/redator/revisor e análise de dados SQLite. Veja [o guia dos exemplos](examples/reference-apps/README.md) e execute `npm run demo:rag`, `npm run demo:collaboration` ou `npm run demo:data` após iniciar o produto e o Ollama local.
