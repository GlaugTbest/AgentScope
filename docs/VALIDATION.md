# Final validation matrix

| Area | Command or scenario | Expected evidence |
| --- | --- | --- |
| Recovery | Stop the API during an SDK trace, restart it, then flush | Agent continues; unconfirmed telemetry is retried or counted as dropped. |
| Migration | `alembic upgrade head` on an empty SQLite file | Every revision, including 0006, completes. |
| Backup/restore | `sqlite-backup.py` then `sqlite-restore.py` to a new path | Restored database opens and contains tables/executions. |
| Load | `pytest -q` plus repeated ingest batches against an isolated database | Idempotency and pagination remain correct; record throughput separately. |
| Offline | Disconnect Ollama after dependencies/model download, run deterministic tool paths | No paid endpoint is contacted; unavailable inference is reported honestly. |
| Usability | Create an agent, run demo, filter traces, open detail, toggle theme/language | First trace and its failure cause are discoverable without logs. |
| Privacy | Ingest fake `token` and `authorization` metadata; export the trace | Values are `[REDACTED]`. |
| Cross-process | Send OTLP trace IDs from independent producers | Opaque trace/span identifiers remain correlated. |

These are acceptance scenarios, not claims that an unrecorded run has occurred. Keep a dated report for each release candidate.
