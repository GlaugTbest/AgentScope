# Operação local

O modo padrão continua usando SQLite. Para validar PostgreSQL localmente, execute `docker compose up --build` e abra a API em `http://127.0.0.1:8000`.

## Backup e restauração PostgreSQL

Crie um backup consistente no diretório atual:

```text
docker compose exec -T postgres pg_dump -U agentscope -d agentscope > agentscope-backup.sql
```

Para restaurar em uma base vazia, use:

```text
Get-Content agentscope-backup.sql | docker compose exec -T postgres psql -U agentscope -d agentscope
```

O arquivo de backup pode conter telemetria; armazene-o como dado sensível. Para encerrar e preservar o volume, use `docker compose down`. Para descartar todos os dados locais, use `docker compose down -v`.
