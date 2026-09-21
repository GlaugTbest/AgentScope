# Compatibility matrix — 1.0

| Component | Status | Scope and limitation |
| --- | --- | --- |
| Windows + SQLite | Verified | Native setup, migrations, API, SDKs and dashboard are exercised locally. |
| Linux + SQLite | Supported | CI runs the portable Python/Node path; a full desktop visual pass is not claimed. |
| PostgreSQL 16 Compose | Supported | Compose configuration and migrations are provided; requires a running Docker daemon. |
| Python SDK | Verified | Manual traces, async-safe contexts, background event export and sanitization. |
| TypeScript SDK | Verified | Typecheck/build and local example are included. |
| Ollama `qwen3:4b` | Verified locally | Loopback-only reference model; behavior depends on local model digest and hardware. |
| OpenAI-compatible client | Verified against local Ollama only | The adapter rejects non-loopback URLs. It does not certify hosted OpenAI APIs. |
| LangGraph | Verified locally | Public `graph.invoke` wrapper; no global monkey patching. |
| OTLP/HTTP traces | Supported | JSON `resourceSpans` trace intake. gRPC, generic logs and metrics are out of scope. |

The project deliberately has no cloud service, account system or multi-tenant isolation in 1.0.
