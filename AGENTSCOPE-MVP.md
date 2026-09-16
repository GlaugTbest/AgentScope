# AgentScope — especificação do MVP e plano de implementação

Este documento define o MVP a ser implementado por um agente de IA. Ele substitui os requisitos anteriores que tornavam Docker e PostgreSQL obrigatórios.

Este documento é uma especificação e um plano de implementação; não indica que o MVP já foi implementado.

## 1. Objetivo e resultado esperado

AgentScope será uma plataforma open source de observabilidade para agentes de IA.

O usuário deverá conseguir:

1. Iniciar a API e o dashboard localmente.
2. Executar um agente de demonstração sem usar APIs pagas.
3. Ver a execução aparecer automaticamente no dashboard.
4. Abrir um trace, visualizar sua timeline e inspecionar seus spans.
5. Instrumentar seu próprio código Python com context managers.

O MVP precisa funcionar de ponta a ponta. Dados simulados pertencem exclusivamente ao agente de demonstração; o dashboard deve consumir dados reais persistidos pela API.

O firewall não será implementado. A organização do backend e os contratos de eventos devem permitir sua evolução futura sem introduzir agora gateway, policy engine ou sistema de aprovações.

## 2. Restrições obrigatórias

- Python 3.11 ou superior.
- Node.js 22 LTS ou superior, usando uma versão compatível com o Next.js escolhido.
- FastAPI, Pydantic 2 e SQLAlchemy 2.
- SQLite como banco padrão de desenvolvimento.
- Alembic para migrations.
- Next.js com App Router, React, TypeScript e Tailwind CSS.
- SDK Python instalável localmente.
- Execução em Windows, macOS e Linux.
- Nenhuma dependência obrigatória de Docker, PostgreSQL, Redis ou serviços externos.
- Nenhuma API de LLM paga necessária para executar ou testar o MVP.
- Sem filas, workers, WebSockets, biblioteca pesada de gráficos ou abstração genérica de repositórios.
- Dependências com versões compatíveis e reproduzíveis; o agente executor deve resolver e registrar versões concretas.
- Testes não devem usar nem modificar o banco de desenvolvimento.

PostgreSQL será uma possibilidade arquitetural, não um deployment entregue ou certificado neste MVP.

## 3. Arquitetura

### Decisão principal

Adotar um monorepo com três unidades:

| Unidade | Responsabilidade |
|---|---|
| API Python | Autenticar, validar, ingerir, persistir e consultar traces |
| Dashboard Next.js | Apresentar métricas, traces, waterfall e detalhes |
| SDK Python | Capturar execuções, spans, métricas e exceções; enviar eventos |

Fluxos:

```text
Agente Python → SDK → FastAPI → SQLAlchemy → SQLite

Navegador → Next.js → FastAPI → SQLAlchemy → SQLite
```

O navegador acessa apenas rotas de leitura do Next.js. O Next.js encaminha as consultas para a API, acrescentando a chave configurada no servidor.

### Alternativas consideradas

| Abordagem | Avaliação |
|---|---|
| API síncrona + SQLite + batch ao encerrar trace | Escolhida: simples, transacional e suficiente para o MVP |
| Persistência assíncrona desde o início | Acrescenta complexidade sem necessidade demonstrada |
| Fila de ingestão e workers | Reservada para crescimento; exige infraestrutura adicional |

Os endpoints que acessam SQLAlchemy síncrono serão funções síncronas do FastAPI, evitando executar operações bloqueantes diretamente no event loop.

O frontend não terá acesso ao banco nem reproduzirá regras de agregação.

## 4. Estrutura do projeto

```text
AgentScope/
  apps/
    api/
      pyproject.toml
      alembic.ini
      .env.example
      migrations/
        env.py
        versions/
          0001_create_traces_and_spans.py
      src/
        agentscope_api/
          __init__.py
          main.py
          config.py
          auth.py
          errors.py
          db.py
          models.py
          schemas.py
          routes/
            health.py
            ingestion.py
            traces.py
          services/
            ingestion.py
            queries.py
      tests/
        conftest.py
        test_auth.py
        test_validation.py
        test_ingestion.py
        test_queries.py
        test_migrations.py

    web/
      package.json
      package-lock.json
      .env.example
      next.config.ts
      tsconfig.json
      postcss.config.mjs
      eslint.config.mjs
      app/
        layout.tsx
        page.tsx
        globals.css
        traces/
          [traceId]/
            page.tsx
        api/
          traces/
            route.ts
            summary/
              route.ts
            [traceId]/
              route.ts
      components/
        app-shell.tsx
        dashboard.tsx
        metric-card.tsx
        trace-filters.tsx
        trace-table.tsx
        trace-detail.tsx
        trace-waterfall.tsx
        span-details.tsx
        status-badge.tsx
        empty-state.tsx
        error-state.tsx
      lib/
        api-server.ts
        api-client.ts
        types.ts
        format.ts
        waterfall.ts
      tests/
        waterfall.test.ts
        format.test.ts
      e2e/
        observability.spec.ts
      playwright.config.ts
      vitest.config.ts

  packages/
    sdk-python/
      pyproject.toml
      src/
        agentscope/
          __init__.py
          client.py
          trace.py
          span.py
          transport.py
          errors.py
      tests/
        test_contexts.py
        test_transport.py
        test_validation.py

  examples/
    demo-agent/
      main.py
      README.md

  scripts/
    setup.mjs
    dev.mjs
    check.mjs

  tests/
    integration/
      test_sdk_api.py

  docs/
    architecture.md
    implementation-plan.md

  data/
    .gitkeep

  package.json
  requirements-dev.lock
  pyproject.toml
  .gitignore
  LICENSE
  README.md
```

Regras:

- `data/agentscope.db` e arquivos auxiliares do SQLite ficam ignorados pelo Git.
- `.env` e `.venv` ficam ignorados pelo Git.
- O nome de distribuição do SDK será `agentscope-observability`; o import solicitado permanece `agentscope`.
- Documentar que pacotes distintos que exponham o mesmo import não devem compartilhar o ambiente virtual.
- Licença proposta: MIT. Não inventar titularidade ou identidade do autor.
- Não criar arquivos Docker neste MVP.

## 5. Modelo de dados

### Convenções

- IDs: UUIDs gerados pelo SDK, representados como strings canônicas.
- Timestamps: RFC 3339 com timezone na API; normalizados para UTC.
- Durações: milissegundos, campo `duration_ms`.
- Tokens: inteiros não negativos.
- Custos: USD.
- `metadata`: objeto JSON extensível, padrão `{}`.
- Entrada e saída: valores JSON opcionais.
- Todos os campos desconhecidos fora de `metadata` serão rejeitados pela validação.

Para manter comportamento consistente entre bancos:

- Persistir timestamps normalizados em UTC, com conversão explícita na fronteira da aplicação.
- Usar tipos portáveis do SQLAlchemy.
- Persistir custos como inteiros em nano-USD; expor valores decimais como strings com até nove casas na API.
- Não usar SQL específico de PostgreSQL, JSONB ou consultas SQL específicas de SQLite nas regras de negócio.

### Tabela `traces`

| Campo | Regra |
|---|---|
| `trace_id` | Chave primária |
| `agent_name` | Obrigatório, 1–200 caracteres |
| `start_time` | Obrigatório |
| `end_time` | Obrigatório |
| `duration_ms` | Derivado dos timestamps |
| `status` | `success` ou `error`, calculado na ingestão |
| `error` | Objeto de erro opcional do próprio trace |
| `metadata` | JSON |
| `created_at` | Horário de ingestão gerado pelo servidor |

### Tabela `spans`

| Campo | Regra |
|---|---|
| `span_id` | Chave primária global |
| `trace_id` | FK obrigatória |
| `parent_span_id` | FK opcional para outro span |
| `type` | String obrigatória, 1–64 caracteres |
| `name` | Obrigatório, 1–200 caracteres |
| `start_time`, `end_time` | Obrigatórios |
| `duration_ms` | Derivado |
| `status` | `success` ou `error` |
| `model`, `provider` | Strings opcionais |
| `input_tokens`, `output_tokens` | Inteiros, padrão zero |
| `estimated_cost_nano_usd` | Inteiro, padrão zero |
| `input`, `output` | JSON opcional |
| `metadata` | JSON |
| `error` | JSON opcional |
| `created_at` | Horário de ingestão |

Tipos conhecidos de span:

```text
llm
tool
retrieval
custom
error
retry
```

A API também aceitará outros tipos válidos. O frontend usará aparência neutra para tipos desconhecidos.

### Erros

Formato:

```json
{
  "type": "ValueError",
  "message": "Invalid search query",
  "stacktrace": "..."
}
```

`type` e `message` são obrigatórios quando houver erro; `stacktrace` é opcional.

### Índices

Além das chaves primárias:

- `traces(start_time, trace_id)`
- `traces(agent_name, start_time)`
- `traces(status, start_time)`
- `spans(trace_id, start_time)`
- `spans(parent_span_id)`
- `spans(type, trace_id)`
- `spans(status, trace_id)`

### Agregações

Totais serão calculados em consultas SQL sobre spans, sem duplicar contadores persistidos no MVP.

Para cada trace:

```text
total_input_tokens  = soma de input_tokens
total_output_tokens = soma de output_tokens
total_tokens        = total_input_tokens + total_output_tokens
estimated_cost      = soma dos custos
llm_calls           = quantidade de spans type=llm
tool_calls          = quantidade de spans type=tool
span_count          = quantidade de spans
error_count         = quantidade de spans status=error
```

O status do trace será `error` se seu contexto terminar com erro ou existir qualquer span com status `error`.

Consequências deliberadas:

- Um erro capturado pela aplicação continua visível no trace.
- Um trace pode ter status `error` e `error_count=0` quando a exceção ocorre fora de um span.
- Falhas propagadas por spans aninhados podem marcar vários spans; `error_count` mede spans com erro, não exceções únicas.
- Tokens e custos devem ser registrados apenas no span que realizou a operação. Spans de agrupamento não devem repetir os totais dos filhos.

## 6. Contrato de ingestão

### Endpoint principal

```text
POST /v1/ingest
```

O SDK enviará um trace completo e seus spans ao sair do contexto do trace:

```json
{
  "trace": {
    "trace_id": "a1a7e509-f905-4fbc-b840-3d5fe450c4df",
    "agent_name": "research-agent",
    "start_time": "2026-09-16T12:00:00.000Z",
    "end_time": "2026-09-16T12:00:00.600Z",
    "status": "success",
    "metadata": {},
    "error": null
  },
  "spans": [
    {
      "span_id": "44e7cc18-5591-4e8c-955a-01fdba99beb9",
      "trace_id": "a1a7e509-f905-4fbc-b840-3d5fe450c4df",
      "parent_span_id": null,
      "type": "llm",
      "name": "generate-plan",
      "start_time": "2026-09-16T12:00:00.000Z",
      "end_time": "2026-09-16T12:00:00.600Z",
      "status": "success",
      "model": "gpt-example",
      "provider": "mock",
      "input_tokens": 120,
      "output_tokens": 80,
      "estimated_cost": "0.000040000",
      "input": null,
      "output": null,
      "metadata": {},
      "error": null
    }
  ]
}
```

Durações e totais não são aceitos como valores autoritativos do cliente: serão derivados pelo servidor.

Respostas:

- `201`: batch novo persistido.
- `200`: reenvio semanticamente idêntico, sem duplicação.
- `409`: IDs já usados com conteúdo diferente.

O MVP usará este endpoint em substituição aos dois POSTs separados permitidos no briefing. Não implementar simultaneamente caminhos de escrita redundantes.

### Atomicidade e idempotência

- Um batch corresponde a um trace completo.
- Trace e spans serão persistidos em uma única transação.
- Falha em qualquer item impede toda a gravação.
- A ordem dos spans no array não altera a identidade do batch.
- O reenvio será comparado após normalização dos dados.
- Não serão aceitos acréscimos ou atualizações parciais a traces já ingeridos.
- Conflitos concorrentes serão resolvidos também por constraints do banco, não apenas por consulta prévia.
- Pais serão inseridos antes dos filhos após validação topológica.

### Validações obrigatórias

- `end_time >= start_time`.
- Todos os spans pertencem ao trace enviado.
- Pais existem no mesmo batch.
- Nenhum span é pai de si mesmo.
- Não existem ciclos.
- Spans estão contidos no intervalo do trace.
- Filhos estão contidos no intervalo do pai.
- IDs de spans não se repetem.
- Tokens e custos são não negativos e respeitam limites numéricos definidos.
- `error != null` exige `status=error`.
- `status=error` sem detalhes de erro é permitido.
- Máximo de 1.000 spans por batch.
- Máximo de 2 MiB por corpo de requisição, aplicado antes do parsing completo e sem depender apenas de `Content-Length`.

Payload inválido retorna `422`; corpo excedido retorna `413`.

## 7. Consultas e métricas

### Endpoints

| Método e rota | Finalidade |
|---|---|
| `GET /health` | Verificar aplicação e conectividade com banco |
| `POST /v1/ingest` | Ingerir trace completo |
| `GET /v1/traces` | Listar traces com agregações |
| `GET /v1/traces/summary` | Métricas do conjunto filtrado |
| `GET /v1/traces/{trace_id}` | Trace completo e spans |

A rota `summary` deverá ser registrada antes da rota dinâmica.

### Listagem

Parâmetros:

- `agent_name`: correspondência exata.
- `status`: `success` ou `error`.
- `span_type`: traces que contêm pelo menos um span desse tipo.
- `start_from`: início inclusivo.
- `start_to`: fim exclusivo.
- `limit`: padrão 25, máximo 100.
- `offset`: padrão zero.

Ordenação: `start_time DESC`, depois `trace_id DESC`.

Resposta:

```json
{
  "items": [],
  "total": 0,
  "limit": 25,
  "offset": 0
}
```

Cada item inclui identidade, horários, duração, status e todos os agregados definidos anteriormente.

O filtro por tipo seleciona traces; os totais de cada trace continuam incluindo todos os seus spans.

### Summary

Usa os mesmos filtros da listagem, ignorando paginação:

- `total_traces`
- `success_rate`: proporção entre zero e um; `null` sem traces.
- `average_latency_ms`: `null` sem traces.
- `total_input_tokens`
- `total_output_tokens`
- `total_tokens`
- `estimated_cost`
- `error_count`: soma de spans com erro.
- `failed_traces`: quantidade de traces com status `error`.

O frontend exibirá “—” para médias e taxas sem amostras.

As consultas devem evitar N+1 e dupla contagem causada por joins. Usar uma subconsulta de agregação por `trace_id` e `EXISTS` para filtros de spans quando necessário.

### Detalhe

Retorna:

```text
{
  trace: TraceSummary com metadata e error,
  spans: SpanDetail[]
}
```

Spans ordenados por horário de início e ID. Trace ausente retorna `404`.

## 8. Autenticação e configuração

### Autenticação real e simples

Toda rota `/v1/*` exige:

```http
Authorization: Bearer dev
```

- Chave configurável por `AGENTSCOPE_API_KEY`.
- Valor padrão local: `dev`.
- Chave vazia impede inicialização.
- Comparação por `secrets.compare_digest`.
- Chave ausente ou incorreta retorna `401`.
- `/health` é público e não revela chave, caminhos locais ou stack traces.

### Configuração da API

```dotenv
AGENTSCOPE_API_KEY=dev
AGENTSCOPE_DATABASE_URL=sqlite:///./data/agentscope.db
```

O caminho relativo do SQLite será resolvido em relação à raiz do projeto, de maneira idêntica pela API e pelo Alembic.

SQLite deverá usar:

- Foreign keys ativadas.
- WAL para o banco de desenvolvimento em arquivo.
- `busy_timeout` de cinco segundos.
- Sessão por requisição.
- Transações curtas.
- Um processo de API no fluxo padrão local.

A API não criará tabelas automaticamente. O setup executará migrations.

### Configuração do Next.js

```dotenv
AGENTSCOPE_API_URL=http://127.0.0.1:8000
AGENTSCOPE_API_KEY=dev
```

Essas variáveis serão exclusivas do servidor, sem prefixo `NEXT_PUBLIC_`.

O proxy:

- Expõe somente as três consultas necessárias.
- Encaminha apenas parâmetros conhecidos.
- Não aceita URL arbitrária.
- Usa timeout de cinco segundos e `no-store`.
- Retorna `502` se a API estiver indisponível e `504` em timeout.
- Não devolve segredos nem detalhes internos de falhas.

O MVP é local e monousuário. A chave protege a API de ingestão e consulta, mas o dashboard não possui login. Portanto, os processos padrão escutarão apenas em loopback; autenticação de usuários será necessária antes de publicar o dashboard.

## 9. SDK Python

### Interface pública

```python
from agentscope import AgentScope

scope = AgentScope(
    api_key="dev",
    endpoint="http://127.0.0.1:8000",
)

with scope.trace("research-agent") as trace:
    with trace.span(
        type="llm",
        name="generate-plan",
        model="gpt-example",
        provider="mock",
    ) as span:
        span.set_usage(
            input_tokens=120,
            output_tokens=80,
            estimated_cost="0.000040000",
        )
        span.set_metadata({"attempt": 1})

    with trace.span(type="tool", name="search-web"):
        pass
```

Métodos públicos:

- `AgentScope.trace(agent_name, *, metadata=None)`
- `Trace.span(*, type, name, model=None, provider=None, metadata=None)`
- `Span.set_usage(*, input_tokens, output_tokens, estimated_cost)`
- `Span.set_metadata(metadata)`
- `Span.set_input(value)`
- `Span.set_output(value)`

`set_usage` substitui os valores atuais; não acumula. `set_metadata` mescla superficialmente as chaves.

### Captura automática

O SDK gera:

- IDs.
- Timestamps UTC.
- Duração.
- Status.
- Relação de parentesco.
- Tipo, mensagem e stack trace de exceções.

Usar `ContextVar` para identificar o span ativo, com restauração por token ao sair do contexto.

O pai automático deve pertencer ao mesmo trace. Contextos de traces diferentes não podem contaminar a hierarquia.

A temporização usará relógio monotônico para duração e uma origem UTC para produzir timestamps consistentes.

### Exceções

Ao sair de um span com exceção:

1. Marcar o span como `error`.
2. Registrar detalhes.
3. Encerrar o span.
4. Propagar a exceção original sem substituí-la.

Ao sair do trace, enviar também execuções que terminaram com erro.

Se a aplicação capturar a exceção e continuar, o span permanece em erro e o trace será classificado como erro pela API.

### Transporte

- Biblioteca padrão Python para HTTP.
- Uma requisição por trace concluído.
- Timeout padrão de dois segundos por tentativa.
- Até uma repetição para falha de conexão, timeout, `429`, `502`, `503` ou `504`.
- A repetição envia os mesmos IDs e conteúdo.
- Não repetir erros de validação, autenticação ou conflito.
- Falhas de envio geram log, sem imprimir payloads ou chave.
- Por padrão, falhas de observabilidade não interrompem o agente.
- `raise_on_error=True` permite expor falhas de transporte em testes e no demo.
- Mesmo nesse modo, uma exceção original do código instrumentado tem prioridade.

### Privacidade e limites

- Entrada e saída desabilitadas por padrão; habilitadas por `capture_content=True`.
- Não capturar automaticamente argumentos, variáveis locais ou credenciais.
- Metadata e mensagens de erro podem conter dados sensíveis; documentar essa responsabilidade.
- Não haverá armazenamento local de batches pendentes.
- Traces só serão visíveis após o encerramento.
- Ao exceder o limite de spans, registrar perda de eventos em `trace.metadata["agentscope.dropped_spans"]`; não criar filhos com pais inexistentes.
- Batch acima do limite de bytes não será enviado parcialmente.

Instrumentação assíncrona dedicada, flush em background e propagação entre threads ficam fora do MVP.

## 10. Dashboard

### Direção visual

Interface escura, densa e legível, com:

- Fundo grafite.
- Superfícies discretamente diferenciadas.
- Tipografia de sistema.
- Fonte monoespaçada para IDs e dados técnicos.
- Cor de destaque contida.
- Bordas e espaçamento para hierarquia.
- Cor acompanhada de texto ou ícone nos status.
- Sem gráficos decorativos, gradientes dominantes ou fontes externas obrigatórias.

### Página principal

Cards:

```text
Total traces
Success rate
Average latency
Total tokens
Estimated cost
Errors
```

“Errors” mostra spans com erro e informa a quantidade de traces com falha como informação secundária.

Filtros:

- Agent name.
- Status.
- Span type.
- Intervalo: última hora, últimas 24 horas, últimos sete dias, todo o período.

Padrão: todo o período.

Tabela:

```text
Agent | Status | Duration | Tokens | Cost | Spans | Started at
```

Comportamento:

- Paginação de 25 itens.
- Clique abre `/traces/{trace_id}`.
- Filtros preservados na URL.
- Mudança de filtro volta à primeira página.
- Atualização automática a cada três segundos enquanto a aba estiver visível.
- Não sobrepor requisições; ignorar respostas obsoletas.
- Manter dados anteriores se uma atualização falhar e mostrar aviso.
- Pausar polling em aba oculta.
- Mostrar horário da última atualização.

O estado vazio apresenta os comandos para executar o demo. Não inventar dados para preencher a tela.

### Página do trace

Mostrar:

- Agent.
- Trace ID copiável.
- Status.
- Início.
- Duração.
- Tokens.
- Custo.
- Contagem de spans e erros.
- Metadata e erro do próprio trace.
- Waterfall.
- Detalhes do span selecionado.

### Waterfall

Implementação em HTML/CSS:

```text
left  = (span.start - trace.start) / trace.duration
width = span.duration / trace.duration
```

Regras:

- Reconstruir árvore por `parent_span_id`.
- Ordenar irmãos por início e ID.
- Usar indentação para profundidade.
- Diferenciar tipos e erros.
- Dar largura visual mínima a spans muito curtos.
- Preservar duração real no texto e nos detalhes.
- Tratar trace com duração zero sem divisão por zero.
- Marcar separadamente o maior span por duração inclusiva.
- Permitir navegação por teclado.
- Não calcular “tempo exclusivo” no MVP.

Em telas estreitas, a timeline terá rolagem horizontal e os detalhes aparecerão abaixo.

### Detalhes do span

Exibir todos os campos disponíveis, com JSON e stack trace em blocos de texto escapados. Não renderizar conteúdo enviado como HTML.

Entrada e saída ausentes devem aparecer como “Não capturado”, não como erro de carregamento.

## 11. Demo agent

Comando padrão:

```text
npm run demo
```

Execução:

```text
research-agent
  generate-plan          llm
  search-web             tool
    retrieve-document    retrieval
  analyze-results        llm
  generate-answer        llm
```

O demo terá:

- Latências diferentes e determinísticas.
- Tokens simulados.
- Custos explícitos em USD.
- Metadata ilustrativa.
- Input/output sintéticos.
- Span aninhado.
- Nenhuma chamada externa.

Modo de falha:

```text
npm run demo -- --error
```

Nesse modo, uma ferramenta lançará uma exceção. O trace deverá ser persistido e a exceção original produzirá saída não zero.

Usar `raise_on_error=True` para que o comando não anuncie envio bem-sucedido quando a API estiver indisponível.

Ao terminar com sucesso, imprimir o ID e o endereço do trace no dashboard.

## 12. Execução local

Fluxo que o projeto entregue deverá oferecer:

```text
npm run setup
npm run dev
```

Em outro terminal:

```text
npm run demo
```

`setup` deverá:

1. Detectar Python compatível, incluindo `py -3` no Windows.
2. Criar `.venv` sem depender de ativação manual.
3. Instalar dependências Python e os dois pacotes locais.
4. Instalar dependências web pelo lockfile.
5. Criar `.env` a partir dos exemplos somente se não existirem.
6. Criar `data/`.
7. Executar `alembic upgrade head`.

`dev` deverá iniciar:

- API em `127.0.0.1:8000`.
- Web em `127.0.0.1:3000`.

O script usará APIs de processos do Node.js, encerrará os filhos ao receber interrupção e informará falhas de inicialização.

O README também incluirá os comandos manuais equivalentes para executar cada serviço separadamente.

## 13. Plano de implementação

O agente executor deverá seguir esta ordem. Cada etapa termina com evidências verificáveis antes da seguinte. Não substituir funcionalidades por placeholders nem ampliar o escopo para itens do roadmap.

### Etapa 1 — Base executável e banco migrado

Arquivos: manifests da raiz, `scripts/setup.mjs`, configuração da API, `db.py`, `models.py`, Alembic e testes de migrations.

- [ ] Registrar esta especificação e o plano em `docs/`.
- [ ] Criar os pacotes e diretórios definidos.
- [ ] Fixar dependências compatíveis.
- [ ] Implementar configuração compartilhada entre API e Alembic.
- [ ] Criar modelos e migration inicial.
- [ ] Configurar foreign keys, WAL e timeout do SQLite.
- [ ] Implementar `/health`, incluindo consulta simples ao banco.
- [ ] Implementar setup sem sobrescrever configuração existente.

Aceite:

- Banco vazio recebe todas as tabelas e índices.
- `upgrade head` pode ser repetido.
- Downgrade e novo upgrade funcionam em banco temporário.
- API e Alembic resolvem o mesmo caminho a partir de diretórios de trabalho diferentes.
- `/health` retorna `200` com banco acessível e `503` em falha.

### Etapa 2 — Schemas e autenticação

Arquivos: `schemas.py`, `auth.py`, `errors.py`, testes correspondentes.

- [ ] Definir schemas de entrada, saída e erro.
- [ ] Implementar UUIDs, timestamps, JSON, limites e decimais.
- [ ] Implementar autenticação Bearer.
- [ ] Padronizar erros sem ecoar payloads sensíveis.
- [ ] Implementar limite real do corpo da requisição.

Aceite:

- Chave correta funciona.
- Ausente ou incorreta retorna `401`.
- Tokens negativos, datas inválidas e campos desconhecidos retornam `422`.
- Corpo excedido retorna `413`, inclusive sem `Content-Length`.
- `/health` permanece público.

### Etapa 3 — Ingestão transacional

Arquivos: `services/ingestion.py`, `routes/ingestion.py`, `test_ingestion.py`.

Interface interna:

```text
ingest_batch(session, batch) → IngestResult
```

`IngestResult` contém `trace_id`, `span_count` e `created`.

- [ ] Validar pertencimento, intervalos e grafo.
- [ ] Normalizar timestamps e custos.
- [ ] Derivar status e durações.
- [ ] Ordenar spans para inserção.
- [ ] Persistir em transação única.
- [ ] Implementar reenvio idempotente e conflito.
- [ ] Traduzir falhas esperadas sem vazar exceções SQL.

Aceite:

- Batch válido persiste trace e spans.
- Pai ausente, ciclo ou intervalo inválido não deixa registros.
- Reenvio idêntico retorna `200`.
- Reenvio reordenado permanece idempotente.
- Mesmo ID com conteúdo diferente retorna `409`.
- Envios concorrentes não duplicam registros.

### Etapa 4 — Consultas e agregações

Arquivos: `services/queries.py`, `routes/traces.py`, `test_queries.py`.

Interfaces:

```text
list_traces(session, filters, limit, offset) → TraceListResponse
summarize_traces(session, filters) → TraceSummaryResponse
get_trace(session, trace_id) → TraceDetailResponse
```

- [ ] Implementar agregação SQL por trace.
- [ ] Implementar filtros e paginação.
- [ ] Implementar summary sem paginação.
- [ ] Implementar detalhe e `404`.
- [ ] Testar traces sem spans e conjuntos vazios.

Fixture obrigatória: dois traces, três spans no primeiro e um no segundo, incluindo tokens, custos e erro conhecidos.

Aceite:

- Totais correspondem exatamente à fixture.
- Joins não multiplicam tokens ou custos.
- Filtro por tipo não recorta os totais internos.
- Summary não muda com `limit` e `offset`.
- Ordenação permanece determinística em timestamps iguais.

### Etapa 5 — SDK

Arquivos: todo `packages/sdk-python/` e seus testes.

- [ ] Implementar API pública.
- [ ] Implementar context managers e parentesco com `ContextVar`.
- [ ] Implementar temporização consistente.
- [ ] Capturar e propagar exceções.
- [ ] Implementar conteúdo opt-in, uso e metadata.
- [ ] Implementar transporte, retry e limites.
- [ ] Exportar somente interfaces públicas necessárias.

Aceite:

- Exceção recebida fora do contexto é o mesmo objeto lançado dentro.
- Exceção capturada pelo agente permanece registrada no span.
- Falha de transporte não mascara exceção original.
- Span aninhado recebe o pai correto.
- Traces independentes não compartilham estado.
- Input/output ficam ausentes por padrão.
- Retry preserva IDs e payload.
- `401` e `422` não geram retry.

### Etapa 6 — Demo e integração Python

Arquivos: `examples/demo-agent/`, `tests/integration/test_sdk_api.py`.

- [ ] Implementar cenário normal.
- [ ] Implementar cenário de erro.
- [ ] Executar SDK contra API real com SQLite temporário.
- [ ] Consultar o trace enviado e conferir agregados.
- [ ] Expor comandos `demo` na raiz.

Aceite:

- Demo normal cria um trace consultável.
- Demo com erro cria um trace em erro e termina com código não zero.
- API indisponível resulta em mensagem clara.
- Nenhuma API paga é chamada.

### Etapa 7 — Dashboard e proxy

Arquivos: configuração web, rotas `/api/traces`, `lib/`, componentes da página principal.

- [ ] Implementar tipos TypeScript alinhados aos schemas.
- [ ] Implementar proxy restrito de leitura.
- [ ] Implementar shell visual e cards.
- [ ] Implementar tabela, filtros e paginação.
- [ ] Implementar atualização automática e estados de interface.
- [ ] Garantir que a chave só seja usada no servidor.

Aceite:

- Dados vêm da API.
- Filtros alteram cards e tabela.
- Navegação preserva filtros.
- Falha de atualização mantém dados anteriores.
- Navegador não envia a chave da API.
- Layout funciona em desktop e largura de 390 px.

### Etapa 8 — Trace e waterfall

Arquivos: página dinâmica, `trace-detail.tsx`, `trace-waterfall.tsx`, `span-details.tsx`, `waterfall.ts`.

- [ ] Implementar carregamento e `404`.
- [ ] Construir árvore e geometria como funções puras.
- [ ] Renderizar timeline e hierarquia.
- [ ] Implementar seleção acessível.
- [ ] Exibir metadata, conteúdo e erros.
- [ ] Tratar spans instantâneos e tipos desconhecidos.

Aceite:

- Barras representam os intervalos persistidos.
- Filhos têm indentação correta.
- Maior span é identificável.
- Falhas são distinguíveis sem depender apenas de cor.
- Seleção por teclado abre detalhes.
- Trace de duração zero não quebra a página.

### Etapa 9 — Inicialização e testes de ponta a ponta

Arquivos: `scripts/dev.mjs`, `scripts/check.mjs`, configuração e testes Playwright.

- [ ] Integrar inicialização dos dois serviços.
- [ ] Implementar encerramento dos processos.
- [ ] Criar comando único de verificação.
- [ ] Executar E2E com banco temporário e portas dedicadas.
- [ ] Inspecionar visualmente dashboard, detalhe, vazio, erro e versão móvel.

Fluxo E2E obrigatório:

```text
Iniciar serviços
→ executar demo
→ aguardar trace aparecer sem reload manual
→ abrir trace
→ selecionar span
→ conferir detalhes
→ executar demo com erro
→ conferir falha no dashboard
```

Aceite:

- Todo o fluxo funciona usando apenas Python e Node.js.
- Testes não alteram `data/agentscope.db`.
- Não há erros de console ou falhas de hidratação.
- Encerrar o comando de desenvolvimento encerra seus serviços.

### Etapa 10 — Documentação e entrega

Arquivos: `README.md`, documentação do demo e `docs/`.

- [ ] Documentar arquitetura e estrutura.
- [ ] Documentar setup, execução e migrations.
- [ ] Documentar SDK, autenticação e endpoints.
- [ ] Documentar semântica de status, custos e erros.
- [ ] Documentar limitações e troubleshooting.
- [ ] Incluir roadmap, marcando apenas funcionalidades verificadas.
- [ ] Executar novamente as verificações afetadas pelas correções finais.
- [ ] Entregar relatório com comandos executados e resultados reais.

O agente não deverá declarar sucesso em testes que não executou.

## 14. Verificação final obrigatória

O comando `npm run check` deverá coordenar:

- Testes Python de API, SDK e integração.
- Lint Python.
- Typecheck TypeScript.
- ESLint.
- Testes unitários do frontend.
- Build de produção do Next.js.

Os testes E2E poderão ter comando separado, `npm run test:e2e`, mas deverão ser executados antes da entrega.

Critérios finais:

- Setup reproduzível em ambiente limpo.
- Demo normal e demo com erro funcionando.
- Persistência mantida após reiniciar a API.
- Dashboard atualizado automaticamente.
- Waterfall e detalhes corretos.
- Chave inválida recusada.
- Migrations verificadas.
- Nenhum requisito de Docker ou PostgreSQL.
- Nenhuma funcionalidade central substituída por mock no frontend.
- Nenhum teste dependente de serviços pagos.

## 15. Limitações assumidas

- Uso local, monousuário e sem login.
- Traces aparecem somente após encerrar a execução.
- Processo encerrado abruptamente pode perder o trace em memória.
- Sem armazenamento offline ou fila durável no SDK.
- SQLite limita concorrência de escrita.
- Paginação por offset; cursor fica para evolução.
- Custos informados explicitamente pelo agente, sem catálogo de preços.
- Sem streaming, instrumentação automática, exportação ou retenção automática.
- Compatibilidade arquitetural com PostgreSQL, ainda sem validação operacional nesse banco.
- Sem firewall, políticas ou aprovações.

A evolução para segurança poderá adicionar novos tipos de eventos e metadata como `security.decision` e `security.policy_id`. O backend de observabilidade não executará ferramentas nem tomará decisões de autorização neste MVP.

## 16. Roadmap e próximos três passos

Após verificação, marcar como concluídos: coleta de traces e spans, dashboard, waterfall, token tracking e cost tracking.

Manter pendentes: integrações OpenAI, Anthropic e LangGraph; compatibilidade OpenTelemetry; evaluations; loop detection; cost anomaly detection; Agent Firewall; policy engine; human approvals.

Os três passos recomendados após o MVP são:

1. Implementar instrumentação automática de um provedor, incluindo testes de captura de tokens e erros.
2. Validar migrations, tipos e ingestão concorrente em PostgreSQL, adicionando deployment opcional.
3. Definir o contrato do gateway de ferramentas e das decisões de política antes de implementar o firewall.

Este desenho e a sequência de execução foram organizados com as skills `brainstorming` e `writing-plans`, respeitando a orientação de apenas descrever o projeto na etapa de planejamento.

