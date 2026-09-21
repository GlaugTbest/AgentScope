# Auto-descoberta local de agentes

## Objetivo

Eliminar a necessidade de cadastrar um agente antes de observar sua primeira execução, sem remover o cadastro manual nem transformar o AgentScope em um scanner de processos locais.

## Comportamento

- A API assegura a existência de um agente ao receber o primeiro lote de trace ou evento incremental com `agent_name` válido.
- Um agente criado dessa forma recebe origem `discovered`, uma descrição explícita de descoberta local e a data do último registro recebido.
- O cadastro manual continua criando agentes inéditos. Quando o nome já pertence a um agente `discovered`, o mesmo formulário assume esse registro: atualiza a descrição, muda a origem para `manual` e retorna o mesmo `agent_id` sem criar duplicata.
- Um nome já configurado manualmente continua retornando conflito para evitar uma troca silenciosa de identidade.
- Trace e evento preservam o nome que os originou; não haverá inspeção de processos, arquivos ou prompts fora da telemetria que o agente optou por enviar.

## Dados e API

- A tabela `agents` ganha `registration_source` (`manual` ou `discovered`) e `last_seen_at`.
- Uma migração preenche os agentes existentes como `manual` e usa sua data de criação como último registro inicial.
- A rotina compartilhada `ensure_agent` é chamada tanto na ingestão de traces quanto na ingestão de eventos; ela atualiza `last_seen_at` e cria somente quando não encontra o nome.
- `GET /v1/agents` expõe origem e último registro. `POST /v1/agents` responde 201 para um novo cadastro manual, 200 quando assume um agente descoberto e 409 para nome manual já existente.

## Dashboard e onboarding

- A lista de agentes mostra uma origem curta e não confunde descoberta com consentimento para capturar conteúdo.
- Um botão sempre visível, “Como conectar um agente”, abre um diálogo acessível no dashboard.
- O diálogo explica que o nome do formulário deve ser igual ao nome usado em `scope.trace("research-agent")`; o exemplo usa `research-agent` nos dois lados.
- Ele informa que um agente instrumentado aparece automaticamente ao enviar seu primeiro trace, enquanto o formulário é útil para descrição e preparação antecipada.
- O diálogo ressalta que `capture_content=True` é opcional e que entradas/saídas sensíveis devem ser redigidas.

## Limites e estados

- Sem registros, o diálogo orienta cadastro manual ou primeira execução instrumentada.
- Falhas de API preservam o aviso existente no dashboard; não há tentativa de descobrir processos do sistema como alternativa.
- O fluxo funciona em português e inglês, respeita navegação por teclado e se adapta ao layout móvel.

## Verificação

- Testes de API cobrem criação por trace, criação por evento, atualização de último registro e tomada de posse manual de agente descoberto.
- Testes web cobrem a cópia de orientação e a distinção da origem.
- E2E cria um agente por telemetria, confirma sua presença no dashboard e abre o diálogo de ajuda.
