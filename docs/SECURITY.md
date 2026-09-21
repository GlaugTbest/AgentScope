# Security guide

AgentScope binds to local loopback by default. Keep it there: the local API key is a development control, not a multi-user authorization system.

- Never commit `.env`, model credentials, backups or exported production telemetry.
- Leave content capture disabled unless investigation needs it. Inputs and outputs can contain personal or confidential data.
- The SDK sanitizes common credential field names before export. Add application-specific names through `redact_fields`; do not rely on a denylist as the sole privacy control.
- Treat JSON exports and database backups as sensitive. Store them encrypted where appropriate and use a new destination for restores.
- The dashboard renders received values as text. Do not add untrusted HTML rendering for span input/output.
- Use the retention endpoint only with a timezone-aware cutoff and verify exports/backups first. Retention deletes trace records and spans permanently.
- Ollama integration is loopback-only. Do not expose the configured port through an internet-facing proxy.

To report a vulnerability, open a private security advisory in the repository rather than publishing credentials or a working exploit in an issue.
