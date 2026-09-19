# Etapa 0 — baseline, decisões e backlog

**Data da coleta:** 18 de setembro de 2026  
**Escopo:** primeira etapa do plano de implementação em `PLANO-DE-IMPLEMENTACAO.md`.

## Decisão de referência

`PLANO-DE-IMPLEMENTACAO.md` é a especificação vigente para a evolução do produto.
Os documentos `AGENTSCOPE-MVP.md`, `docs/implementation-plan.md`,
`docs/delivery-plan.md`, `STATUS.md` e `PRODUCT.md` descrevem o MVP já entregue ou
planos anteriores. Eles são fontes do estado existente, e não requisitos que
prevalecem sobre o novo plano.

| Documento anterior | Estado preservado | Reconciliação necessária |
| --- | --- | --- |
| `AGENTSCOPE-MVP.md` | API, SDK Python, SQLite e painel local constituem a base | A ingestão em batch ao fim do trace vira compatibilidade legada; o novo percurso usa eventos incrementais. |
| `STATUS.md` | Inventário do MVP e comandos locais | Afirmações de “pronto” só valem para o MVP; não devem ser usadas como prova das metas Alpha, Beta ou 1.0. |
| `PRODUCT.md` | Público local e princípio de dados reais | Atualizar quando as jornadas de agentes, execuções, eficiência e integrações substituírem a bancada de demo. |
| `docs/implementation-plan.md` e `docs/delivery-plan.md` | Histórico da sequência que levou ao MVP | Substituídos, para evolução futura, por este baseline e pelo plano principal. |

## Inventário confirmado

| Área | Há hoje | Lacuna em relação ao plano vigente |
| --- | --- | --- |
| API | FastAPI, SQLAlchemy, Alembic, SQLite, autenticação Bearer e consultas de traces | Não há projeto, versão, instância, execução, eventos incrementais, retenção ou OTLP. |
| Persistência | Trace e spans imutáveis, ingestão transacional e idempotência de batch | O modelo só aceita UUIDs e finalização completa; não suporta eventos fora de ordem ou uma execução aberta. |
| SDK Python | Context managers, spans aninhados, captura de exceções e transporte síncrono | Não há buffer, exportador em segundo plano, contexto assíncrono, atividade ou métricas de descarte. |
| Painel | Cadastro local, resumo, filtros simples, polling, waterfall e detalhe | Está em português e tema único; não há visão geral, páginas por agente/instância, eficiência, persistência de filtros ou estados de atividade. |
| Demo | Cenário sintético com LLM e ferramenta simulados | Não prova inferência, ferramentas ou colaboração reais. |
| Testes | API, SDK e testes unitários web; o comando de checagem passa | E2E é apenas um aviso e não existe teste de migração PostgreSQL, carga, recuperação ou contratos novos. |

## Ambiente verificado

| Recurso | Evidência |
| --- | --- |
| Sistema | Windows; Python 3.14.0 e Node.js 24.11.1 disponíveis. |
| Memória | 33.4 GB físicos (aprox. 31.1 GiB). |
| GPU | NVIDIA GeForce RTX 3060 Ti, 8 GiB; driver 610.88 / CUDA UMD 13.3. |
| Espaço livre | C: 50.0 GiB; D: 100.0 GiB durante a coleta. |
| Runtime local | Ollama não estava instalado no início da etapa; sua instalação e a medição são registradas abaixo quando concluídas. |
| Base local | `npm run setup` criou ambiente virtual, dependências web, arquivos de configuração não existentes e banco SQLite migrado. |

### Correção encontrada no baseline

O setup Windows não chegava à interface nem às migrations: `npm` era chamado como
executável sem o sufixo Windows e o Python virtual era relativo à pasta `apps/api`.
`scripts/setup.mjs` agora usa `npm.cmd` no Windows e um caminho absoluto para o
ambiente virtual. A correção é limitada ao bootstrap e foi validada pela conclusão
do próprio `npm run setup`.

## Convenções de identidade para a Etapa 2

Os IDs de interoperabilidade serão strings opacas no contrato novo: AgentScope não
converterá IDs OpenTelemetry válidos para UUID com hífens. Os IDs gerados pelo SDK
continuarão UUIDs, mas isso não será uma exigência do servidor.

| Entidade | Identificador e regra |
| --- | --- |
| Projeto | `project_id`; escopo local de agrupamento, com um projeto padrão para eventos legados. |
| Agente | `agent_id` estável dentro do projeto; `logical_name` é rótulo mutável e não chave global. |
| Versão | `agent_version_id`, com referência de código, prompt ou configuração sanitizada. |
| Instância | `instance_id` por processo/worker; registra runtime e início da instância. |
| Tarefa | `task_id` para objetivo de negócio que pode abranger execuções. |
| Execução | `execution_id` por participação de um agente em uma tarefa; pode estar aberta. |
| Trace e span | `trace_id` e `span_id` preservados como recebidos; vinculados à execução quando a origem informar a relação. |
| Evento | `event_id` único, `schema_version`, `source`, `occurred_at` e `received_at`; reenvio idêntico é idempotente e conteúdo incompatível é conflito. |

Compatibilidade: o batch atual será aceito durante a migração, mapeado para o
projeto local padrão e para uma execução encerrada. Um nome idêntico em projetos
diferentes nunca será usado como chave de identidade.

## Wireframes de referência

### Visão geral

```text
+--------------+----------------------------------------------------------+
| AgentScope    | Visão geral                         [intervalo] [tema] |
| Visão geral   +----------------------------------------------------------+
| Agentes       | Ativos  3 | Execuções  28 | Tokens  42k | Falhas  2     |
| Execuções     +--------------------------+-------------------------------+
| Eficiência    | atividade recente        | volume / latência              |
| Integrações   | Revisor aguardando ...   | gráfico com unidade e amostras |
| Configurações +--------------------------+-------------------------------+
|              | execuções recentes, filtros persistentes e paginação    |
+--------------+----------------------------------------------------------+
```

### Agente e execução

```text
+--------------+----------------------------------------------------------+
| Agentes       | Revisor v1.2  • instância worker-7 • executando         |
| > Revisor     | Tokens | p95 | recuperações | uso direto/inclusivo      |
|   Pesquisador +----------------------------------------------------------+
|   Redator     | 12:03 ferramenta excedeu limite → retry 2 (evento)     |
|              | 12:02 delegação recebida do Pesquisador (evento)        |
|              | timeline: spans, uso, resultado e erro sanitizado       |
+--------------+----------------------------------------------------------+
```

A tabela e a timeline permanecem as superfícies primárias; o mapa de colaboração
é complementar. Em telas estreitas a navegação vira menu e os cards são empilhados.

## Backlog em ordem de dependência

1. **Etapa 1:** fechar a instalação reprodutível, isolar bancos de teste, tornar
   o E2E executável e registrar CI.
2. **Etapa 2:** migration do domínio de identidade; contrato versionado de evento;
   persistência, idempotência, reconciliação e leitura de execuções abertas.
3. **Etapa 3:** exportador Python em segundo plano, contexto assíncrono, atividade
   baseada em regras e primeiro cenário Ollama com ferramenta real.
4. **Etapa 4:** shell internacionalizado, temas, overview, agente/instância,
   execução, séries, filtros persistidos e polling incremental.
5. **Etapa 5:** aplicações REAL-01 a REAL-03, delegação, LangGraph e cliente
   compatível com OpenAI apontado exclusivamente ao Ollama local.
6. **Etapa 6:** avaliações, comparações, preços simulados e recomendações ligadas
   a evidências.
7. **Etapa 7:** SDK TypeScript, OTLP/HTTP delimitado, execução distribuída,
   PostgreSQL opcional e operação de retenção/backup/restauração.
8. **Etapa 8:** sabatina, benchmarks, documentação de release e demonstração
   sanitizada.

Cada item só começa quando o anterior estiver testado e deixar o repositório
executável. Não serão anunciadas integrações externas ou métricas de desempenho
sem evidência registrada.

## Benchmark do modelo

O runtime instalado é Ollama **0.34.2**. O modelo baixado foi `qwen3:4b`, digest
`359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7`, GGUF
`Q4_K_M`, 4.0B parâmetros e 2 497 293 931 bytes. Os pedidos usaram temperatura
zero, contexto de 4 096 tokens, até 16 tokens de saída e `keep_alive=5m`.

| Cenário | Resultado observado |
| --- | --- |
| Primeira geração em streaming | Primeiro fragmento em 36 014 ms; término em 36 289 ms. |
| Geração com o modelo carregado | 453 ms totais; carregamento 1 ms; avaliação de prompt 51 ms; geração 367 ms; 16 tokens a 43,59 tokens/s. |
| Duas gerações simultâneas | 406 ms e 659 ms totais, respectivamente; não há afirmação de ganho de throughput com apenas uma rodada. |
| GPU durante o teste | 5 852 MiB / 8 192 MiB e 41% de uso numa amostra durante a primeira execução; 5 621 MiB e 96% numa amostra após o teste concorrente. |
| Ferramenta local | O endpoint de ferramentas respondeu; nesta primeira tentativa o modelo gerou 64 tokens de texto e não emitiu `tool_call`. Isso é uma falha de comportamento a investigar, não um resultado positivo. |

As medições cobrem apenas o runtime: ainda não há um agente AgentScope real nem
sobrecarga de observabilidade para comparar. A primeira latência inclui carregamento
e aquecimento, portanto não deve ser apresentada como a latência típica da demo.
O próximo benchmark deve repetir texto e ferramenta com prompts/dataset fixados,
registrar pico de RAM/VRAM e separar fila, inferência e sobrecarga do AgentScope.
