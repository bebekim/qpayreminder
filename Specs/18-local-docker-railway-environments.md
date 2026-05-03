# Local Docker And Railway Environments

Priority: high
State: ready

## Problem

QPayReminder needs repeatable environment separation before deployment work
starts in earnest. Local development should be cheap, inspectable, and resettable
with Docker. Testing and production should run on Railway as separate
environments with isolated variables, databases, Redis instances, domains, and
deployment controls.

The Railway MCP server has been added to the toolchain, so deployment operations
should be expressible through Railway MCP where available, with Railway CLI as
the fallback.

## Desired Behavior

- Local development runs with Docker Compose, using local Postgres and Redis.
- Local app commands can run through `uv` against local service URLs.
- Railway has a dedicated `testing` environment for smoke tests and staging
  validation.
- Railway has a dedicated `production` environment for live customers and
  stricter deploy controls.
- Testing and production variables are isolated; no local `.env` file is copied
  into Railway wholesale.
- Testing and production databases are separate Railway Postgres services.
- Testing and production Redis instances are separate Railway Redis services.
- Railway deploys are linked to the `qpayreminder` repo and service explicitly.
- The app exposes a health endpoint suitable for Railway health checks.
- Deployment runbooks describe how to inspect logs, variables, migrations, and
  rollback/redeploy actions.

## Environment Model

| Environment | Runtime | Database | Redis | Purpose |
| --- | --- | --- | --- | --- |
| `local` | Docker Compose + uv | Docker Postgres | Docker Redis | Fast dev and TDD |
| `testing` | Railway | Railway Postgres | Railway Redis | Smoke tests, webhook dry runs, release validation |
| `production` | Railway | Railway Postgres | Railway Redis | Live system |

## Railway MCP Expectations

Use Railway MCP tools when available:

- `check-railway-status` to verify CLI/auth status.
- `create-project-and-link` or `link-service` to bind this repo to Railway.
- `create-environment` and `link-environment` for `testing` and `production`.
- `set-variables` for environment-specific settings.
- `deploy` for service deploys.
- `generate-domain` for Railway domains.
- `get-logs` for deploy/runtime diagnostics.

If Railway MCP tools are not visible in the active Codex session, restart Codex
or use Railway CLI manually until the MCP server is loaded.

## Non-Goals

- Do not deploy live customer traffic before auth, org permissions, invoice
  intake, bank ingestion, and reminder safeguards are ready.
- Do not share databases between testing and production.
- Do not store secrets in Git.
- Do not build a custom deployment control plane.
- Do not rely on local Docker as a production-equivalent security boundary.

## Likely Files

- `Dockerfile`
- `docker-compose.yml`
- `.env.example`
- `.env.local.example`
- `railway.json` or Railway config-as-code equivalent
- `src/qpayreminder/web/health.py`
- `docs/environments.md`
- `docs/deployment-runbook.md`
- `tests/unit/config/test_environment_config.py`
- `tests/integration/test_health_endpoint.py`

## Edge Cases

- Railway MCP installed but not loaded in the current agent session.
- Railway CLI installed but not authenticated.
- Local Docker daemon unavailable.
- Port collision for local Postgres, Redis, or app service.
- Missing required environment variable at startup.
- Production accidentally linked while intending testing.
- Testing deploy reads production variables.
- Migrations run against the wrong database.
- Health endpoint passes while dependencies are unreachable.
- Redis private networking differs between local Docker and Railway.
- Webhook callback URLs point to local or testing while production is active.

## Test Expectations

Expected local checks:

```bash
uv run pytest tests/unit/config -q
uv run pytest tests/integration/test_health_endpoint.py -q
uv run ruff check src tests
docker compose config
```

Expected Railway checks once MCP/CLI is active:

```bash
railway status
railway variables --environment testing
railway variables --environment production
```

No test may require production secrets.

## Acceptance Criteria

- [ ] `docker compose up` starts the local app dependencies.
- [ ] `.env.example` documents every required app variable without secrets.
- [ ] The app fails fast with a clear error when required config is missing.
- [ ] Testing and production Railway environments are created separately.
- [ ] Testing and production database/Redis variables point to distinct services.
- [ ] A health endpoint exists and is covered by tests.
- [ ] Deployment docs explain local, testing, and production workflows.
- [ ] Railway MCP usage and CLI fallback are documented.
- [ ] Production deploy steps include an explicit environment confirmation.

## Known Risks

- **Risk**: Environment drift hides bugs until production.
  **How we'd notice**: Testing variables or services differ materially from
  production beyond safe names/domains/secrets.
  **Mitigation**: Keep an environment variable inventory and compare required
  keys between Railway environments.

- **Risk**: Agents mutate production while intending testing.
  **How we'd notice**: Railway status shows production linked during testing
  commands.
  **Mitigation**: Require explicit environment confirmation before production
  deploys or variable writes.

- **Risk**: Local Docker setup becomes stale.
  **How we'd notice**: New developers or agents cannot run tests locally without
  Railway.
  **Mitigation**: Keep Docker Compose checks in preflight and document reset
  commands.
