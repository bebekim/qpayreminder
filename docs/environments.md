# Environments

QPayReminder uses three separated environments:

- `local`: Docker Compose for Postgres and Redis, with app commands run through
  `uv`.
- `testing`: Railway environment for smoke tests, staging validation, and safe
  webhook/provider experiments.
- `production`: Railway environment for live customers.

## Local

Local development should not depend on Railway secrets. It should use checked-in
examples plus developer-owned `.env` files ignored by Git.

Expected local dependencies:

- Postgres in Docker.
- Redis in Docker.
- App command via `uv run`.

## Railway Testing

Testing is the first remote deploy target. It should have its own Railway
environment, database, Redis instance, generated domain, and environment
variables.

Use testing for:

- Smoke tests.
- Migration dry runs.
- Webhook endpoint validation with non-production providers.
- Release candidate checks.

## Railway Production

Production must stay isolated from testing. Production variable writes and
deploys require an explicit confirmation of the linked Railway environment.

Use production for:

- Live customer traffic.
- Production domains.
- Production provider credentials.
- Live reminder delivery only after safeguards are ready.

## Railway MCP

Use Railway MCP when visible in the active Codex session. If it is not visible,
restart Codex or use Railway CLI fallback.

Useful MCP tool intents:

- Check Railway CLI/auth status.
- Link the repo to a project and service.
- Create/link `testing` and `production` environments.
- Set environment-specific variables.
- Deploy and inspect logs.

Do not copy local `.env` files wholesale into Railway.
