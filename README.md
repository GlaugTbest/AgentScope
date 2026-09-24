# AgentScope

> Observabilidade local e offline para aplicações com agentes de IA.

[![CI](https://github.com/GlaugTbest/AgentScope/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/GlaugTbest/AgentScope/actions/workflows/ci.yml)

O AgentScope permite registrar, explorar e avaliar o trabalho de agentes sem enviar telemetria para um serviço externo. Ele combina uma API FastAPI, armazenamento local em SQLite ou PostgreSQL, dashboard Next.js, SDKs Python e TypeScript e entrada OTLP/HTTP. Tudo é executado na máquina do operador.

## O que o produto entrega

- Rastreamento de traces, spans, eventos, ferramentas, erros, tokens, custo simulado e duração.
- Cadastro automático de agentes a partir da telemetria recebida, com opção de gerenciamento manual.
- Modelo de domínio para projetos, versões de agente, instâncias, tarefas, delegações e execuções.
- Dashboard em português e inglês, com tema claro/escuro, filtros persistentes e histórico paginado.
- Métricas de latência p50, p95 e p99, além de comparação entre baseline e variante.
- Avaliações de qualidade, recomendações sustentadas pelos dados e preços inteiramente simulados.
- Aplicações de referência locais: RAG, colaboração entre agentes e análise de dados SQLite.
- Integrações com LangGraph, cliente compatível com OpenAI restrito ao Ollama local e OTLP/HTTP.
- Retenção, exportação, backup e restauração para a operação local.

## Arquitetura

```text
Aplicação instrumentada
  ├─ SDK Python
  ├─ SDK TypeScript
  └─ OTLP/HTTP JSON
          │
          ▼
   API FastAPI (127.0.0.1:8000)
          │
          ├─ SQLite local (padrão)
          └─ PostgreSQL via Compose (opcional)
          │
          ▼
Dashboard Next.js (127.0.0.1:3000)
```

Os dados permanecem no ambiente local. O produto não exige conta, chave de provedor de IA nem conexão com a nuvem para operar.

## Início rápido

Pré-requisitos: Python 3.11 ou superior, Node.js com npm e Git. O Ollama é necessário apenas para executar os exemplos que chamam um modelo local.

No diretório do projeto:

```powershell
npm run setup
npm run dev
```

O primeiro comando instala as dependências, cria o ambiente Python e prepara os pacotes locais. O segundo inicia API e dashboard. Abra [http://127.0.0.1:3000](http://127.0.0.1:3000).

Em outro terminal, gere uma execução de exemplo:

```powershell
npm run demo
```

Para registrar uma execução com falha intencional:

```powershell
npm run demo -- --error
```

O dashboard mostrará a execução, os spans e os eventos. O agente usado pela demonstração também será descoberto automaticamente ao receber a telemetria.

## Configuração

As configurações de exemplo ficam em `apps/api/.env.example` e `apps/web/.env.example`.

| Variável | Onde é usada | Padrão | Finalidade |
| --- | --- | --- |
| `AGENTSCOPE_API_KEY` | API, dashboard e SDKs | `dev` | Chave Bearer para as rotas `/v1/*`. |
| `AGENTSCOPE_DATABASE_URL` | API | `sqlite:///./data/agentscope.db` | URL do banco SQLite ou PostgreSQL. |
| `AGENTSCOPE_API_URL` | Dashboard e SDKs | `http://127.0.0.1:8000` | Endereço da API local. |

Para uma instalação diferente do modo de demonstração, defina uma chave própria e mantenha-a fora do controle de versão. Todas as rotas `/v1/*` exigem `Authorization: Bearer <AGENTSCOPE_API_KEY>`.

## Instrumentando uma aplicação Python

O pacote Python se chama `agentscope-observability`, mas o import é `agentscope`.

```python
from agentscope import AgentScope

scope = AgentScope(
    endpoint="http://127.0.0.1:8000",
    api_key="dev",
    capture_content=False,
)

with scope.trace("assistente-local") as trace:
    with trace.span(type="tool", name="buscar_documentos"):
        # Execute a ferramenta ou etapa do agente aqui.
        pass

scope.flush()
scope.shutdown()
```

`capture_content=False` é a opção segura para o uso normal. Habilite a captura de entrada e saída somente quando os dados forem adequados para armazenamento local. Nunca registre tokens, senhas, cabeçalhos de autorização ou material sensível em metadata e mensagens de erro.

## SDK TypeScript

O SDK TypeScript está em `packages/sdk-typescript` e é compilado durante o setup.

```js
import { AgentScope } from './packages/sdk-typescript/dist/index.js';

const scope = new AgentScope({
  endpoint: 'http://127.0.0.1:8000',
  apiKey: 'dev',
});

const trace = scope.trace('agente-typescript', { origem: 'exemplo' });
const span = trace.startSpan('tool', 'normalizar-texto');
trace.endSpan(span, { outputTokens: 42 });
await trace.end();
```

Execute o exemplo pronto com:

```powershell
node examples/demo-agent-typescript/main.mjs
```

Os SDKs removem campos comuns de credenciais antes do envio. Isso é uma proteção complementar, não substitui a decisão de não coletar segredos.

## Dashboard

O dashboard oferece:

- Visão geral da saúde operacional e das execuções recentes.
- Páginas para agentes, instâncias, execuções, traces, tarefas e delegações.
- Detalhe de trace com hierarquia de spans e histórico de eventos paginado.
- Percentis de latência p50/p95/p99 e filtros por período, agente, status, evento, branch e ator.
- Tela de eficiência para avaliações, experimentos baseline/variante, preços simulados e recomendações.
- Exportação de traces, alternância de idioma português/inglês e preferências locais persistentes.

## Aplicações de referência

Inicie o produto com `npm run dev` e, quando o exemplo fizer inferência, tenha o Ollama local em execução.

| Exemplo | O que demonstra | Comando |
| --- | --- | --- |
| RAG | Recuperação lexical local sobre documentos de exemplo. | `npm run demo:rag` |
| Colaboração | Fluxo pesquisador → redator → revisor. | `npm run demo:collaboration` |
| Análise de dados | Consultas e análise sobre banco SQLite local. | `npm run demo:data` |
| Orquestração | Coordenador, pesquisador e revisor com chamadas ao Ollama. | `.venv\\Scripts\\python.exe examples/reference-apps/orchestrated_local.py --model qwen3:0.6b` |

Veja [o guia completo dos exemplos](examples/reference-apps/README.md). Eles usam apenas dados e serviços locais; não há APIs pagas envolvidas.

## Integrações locais

### LangGraph

Instale os extras de integração e execute o exemplo:

```powershell
.venv\\Scripts\\python.exe -m pip install -e "packages/sdk-python[integrations]"
.venv\\Scripts\\python.exe examples/integrations/langgraph_example.py
```

O observador envolve uma chamada pública a `graph.invoke`, preserva o grafo do usuário e cria spans de execução sem depender de estado global.

### Cliente compatível com OpenAI para Ollama

O adaptador compatível com OpenAI aceita apenas um endpoint Ollama em loopback. Essa restrição é intencional: impede o envio acidental de prompts para provedores remotos.

```python
from agentscope.integrations import OpenAICompatibleOllamaClient

client = OpenAICompatibleOllamaClient(
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama",
)
```

Consulte [as instruções e o exemplo executável](examples/integrations/README.md).

### OTLP/HTTP

Envie traces OTLP no formato JSON para:

```text
POST /v1/otlp/v1/traces
Authorization: Bearer <chave>
Content-Type: application/json
```

O suporte atual cobre `resourceSpans` de traces por HTTP e correlaciona processos por trace e parent span. gRPC, logs e métricas OTLP não fazem parte do escopo da versão 1.0.

## API e modelo de domínio

Além da ingestão, a API expõe recursos para administrar e consultar o domínio.

| Área | Rotas principais |
| --- | --- |
| Ingestão | `/v1/ingest`, `/v1/events`, `/v1/otlp/v1/traces` |
| Observabilidade | `/v1/traces`, `/v1/executions`, `/v1/metrics/latency` |
| Catálogo | `/v1/projects`, `/v1/agents`, `/v1/agent-versions`, `/v1/instances` |
| Orquestração | `/v1/tasks`, `/v1/delegations` |
| Eficiência | `/v1/prices`, `/v1/evaluations`, `/v1/experiments` |
| Operação | `/v1/operations/retention` |

Listagens usam paginação e filtros. A documentação interativa da API está disponível em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) quando a API estiver ativa.

## Banco de dados e operação

### SQLite

SQLite é o padrão e atende ao uso local monousuário. Faça backup e restauração com os scripts fornecidos:

```powershell
.venv\\Scripts\\python.exe scripts/sqlite-backup.py sqlite:///C:/caminho/agentscope.db C:/backups/agentscope.db
.venv\\Scripts\\python.exe scripts/sqlite-restore.py C:/backups/agentscope.db C:/restore/agentscope.db
```

### PostgreSQL opcional

Para executar a API com PostgreSQL local via Docker Compose:

```powershell
docker compose up --build
```

Backup:

```powershell
docker compose exec -T postgres pg_dump -U agentscope -d agentscope > agentscope-backup.sql
```

Restauração:

```powershell
Get-Content agentscope-backup.sql | docker compose exec -T postgres psql -U agentscope -d agentscope
```

O comando de restauração substitui dados do banco de destino conforme o conteúdo do backup; confirme o ambiente antes de executá-lo. Veja o [guia operacional](docs/operation.md) para retenção, exportação, recuperação e procedimentos de falha.

## Verificação e desenvolvimento

| Objetivo | Comando |
| --- | --- |
| Preparar o ambiente | `npm run setup` |
| Iniciar API e dashboard | `npm run dev` |
| Executar verificações de qualidade | `npm run check` |
| Executar testes end-to-end do dashboard | `npm run test:e2e` |
| Gerar telemetria de demonstração | `npm run demo` |

Antes de contribuir, execute `npm run check`. A integração contínua verifica o código, os testes e os cenários relevantes de integração local.

## Estrutura do repositório

```text
apps/api/                 API FastAPI, migrações e testes
apps/web/                 Dashboard Next.js
packages/sdk-python/      SDK Python: agentscope-observability
packages/sdk-typescript/  SDK TypeScript
examples/                 Demonstrações, integrações e apps de referência
docs/                     Arquitetura, operação, segurança, release e validação
scripts/                  Setup, verificação, backup e restauração
```

## Compatibilidade e limites

O AgentScope 1.0 foi pensado para operação local e offline. SQLite no Windows e Linux, PostgreSQL 16 via Compose, SDKs Python/TypeScript, LangGraph, Ollama local e OTLP/HTTP são os caminhos suportados. A matriz detalhada está em [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

Não é um serviço SaaS, não implementa multi-tenancy, autenticação de usuários, ingestão remota, gRPC OTLP, logs/métricas OTLP ou conectores para provedores externos. O adaptador OpenAI-compatible é deliberadamente limitado ao Ollama local.

## Documentação

| Documento | Conteúdo |
| --- | --- |
| [Arquitetura](docs/architecture.md) | Componentes, fluxos de dados e decisões de persistência. |
| [Operação](docs/operation.md) | Backup, restauração, retenção, exportação e recuperação. |
| [Segurança](docs/SECURITY.md) | Modelo de segurança local e boas práticas de telemetria. |
| [Release 1.0](docs/RELEASE.md) | Escopo, critérios de publicação e notas de release. |
| [Validação](docs/VALIDATION.md) | Cenários de carga, falhas, migrações, offline e usabilidade. |
| [Compatibilidade](docs/COMPATIBILITY.md) | Plataformas, integrações e limites suportados. |

## Licença

Distribuído sob a [licença MIT](LICENSE).
