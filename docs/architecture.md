# Arquitetura

O SDK envia um batch de trace completo para a API FastAPI; a API o valida e persiste atomicalmente em SQLite via SQLAlchemy. O dashboard consulta somente a API por rotas proxy do Next.js, mantendo a chave no servidor.

Custos são armazenados como nano-USD inteiros e retornados como strings decimais. Traces e spans são imutáveis após a ingestão para garantir idempotência.
