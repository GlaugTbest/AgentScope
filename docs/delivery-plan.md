# Plano de fechamento e auditoria

Escopo: cumprir AGENTSCOPE-MVP.md, preservar o modo local e acrescentar cadastro/demo autorizado pelo usuário. Entregar execução de produção monousuário protegida por autenticação HTTP no dashboard; publicação externa depende de host/domínio/TLS do operador.

1. Corrigir ingestão, idempotência completa, limites, UTC, filtros e resumo SQL.
2. Completar SDK e setup multiplataforma, migrations e integração isolada.
3. Completar dashboard, filtros na URL, paginação, cenários demo, waterfall e detalhes acessíveis.
4. Proteger proxy, isolar artefatos de desenvolvimento/build e fornecer comando de produção.
5. Executar testes de API/SDK/migrations/integração e E2E em banco temporário, inspeção desktop/mobile.
6. Documentar resultados reais, limites operacionais e preparar publicação LinkedIn e roteiro de demonstração.
