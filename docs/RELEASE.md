# Release procedure — 1.0

1. Start from a clean checkout and run `npm run setup` followed by `npm run check` and `npm run test:e2e`.
2. Run an empty-database migration through `alembic upgrade head`; test a backup and restore against a separate SQLite destination.
3. Run the three local reference applications with Ollama, retaining their sanitized evidence and model digest.
4. Run the failure, migration, offline and load scenarios in [VALIDATION.md](VALIDATION.md). Record commit, hardware, configuration and negative results.
5. Confirm [COMPATIBILITY.md](COMPATIBILITY.md) matches actual validation; update the changelog and version numbers before tagging.
6. Inspect `git status`, the release archive and screenshots for secrets or private telemetry. Publish only the sanitized demo dataset.

No hosted model API, paid service, public dashboard or external user-test claim is part of this release procedure.
