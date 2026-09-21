# Operação local

O modo padrão continua usando SQLite. Para validar PostgreSQL localmente, execute `docker compose up --build` e abra a API em `http://127.0.0.1:8000`.

## Backup e restauração SQLite

O backup usa a API nativa do SQLite, portanto é seguro enquanto a API estiver gravando em modo WAL. Escolha sempre um destino novo: os scripts se recusam a sobrescrever dados.

```text
.venv\Scripts\python.exe scripts/sqlite-backup.py sqlite:///C:/caminho/agentscope.db C:/backups/agentscope-2026-09-20.db
.venv\Scripts\python.exe scripts/sqlite-restore.py C:/backups/agentscope-2026-09-20.db C:/restore/agentscope.db
```

Depois da restauração, aponte `AGENTSCOPE_DATABASE_URL` ao arquivo recuperado e inicie a API. Consulte `/health` e uma execução conhecida antes de descartar qualquer cópia anterior.

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

Para restaurar em PostgreSQL, aplique antes as migrações da mesma versão do AgentScope e só então importe o dump em uma base nova. Não use o comando de restauração para substituir uma base que você ainda não verificou.
