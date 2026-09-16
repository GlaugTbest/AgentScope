# AgentScope — status da implementação

## O que foi iniciado

Este repositório começou como a implementação do MVP descrito em `AGENTSCOPE-MVP.md`: uma plataforma local de observabilidade para agentes de IA, com API FastAPI, SDK Python e dashboard Next.js.

Também foi adicionada uma bancada operacional para demonstração: cadastro de agentes, seleção do agente ativo, execução de um cenário sintético e visualização dos traces persistidos.

## O que está pronto

- API com FastAPI, Pydantic 2, SQLAlchemy 2, SQLite e Alembic.
- Autenticação Bearer configurável por `AGENTSCOPE_API_KEY`.
- Ingestão transacional de traces e spans com validação de hierarquia, limites, custos e idempotência.
- Consultas de traces, filtros, agregações, resumo e detalhe de execução.
- SDK Python com context managers, spans aninhados, captura de erros, uso de tokens, custos e conteúdo opt-in.
- Dashboard em Next.js com seleção/cadastro de agentes, filtros, métricas, atualização automática e estado vazio.
- Demo local sem APIs pagas, com cenários de sucesso e falha.
- Waterfall de spans e página de detalhe.
- Banco de desenvolvimento separado dos bancos de testes.
- Build de produção isolado dos artefatos do servidor de desenvolvimento.
- Documentação de arquitetura, setup e limitações.

## O que falta antes de uma publicação pública

- Configurar deploy em um provedor real, domínio, TLS e observabilidade do próprio serviço.
- Adicionar autenticação de usuários e autorização por workspace antes de expor o dashboard na internet.
- Executar E2E em navegador em CI com banco e portas temporários.
- Validar concorrência e migrations em PostgreSQL como deployment opcional.
- Adicionar instrumentação oficial para provedores de LLM e frameworks, compatibilidade OpenTelemetry e retenção.
- Definir e implementar o contrato futuro de gateway, políticas e aprovações; esses itens não fazem parte deste MVP.

## Verificação local

O comando `npm run check` coordena os testes Python, lint Python, typecheck, ESLint, testes Vitest e build do Next.js. Avisos de depreciação das dependências podem aparecer, mas falhas interrompem o comando.

Para executar:

```text
npm run setup
npm run dev
npm run demo
```

Abra `http://127.0.0.1:3000` e use o painel para cadastrar um agente e rodar a demo.
