# Auth API Tokens For CLI And Hermes

Priority: medium
State: blocked
Blocked by:

- `Specs/13-auth-password-session-core.md`
- `Specs/14-auth-org-permission-core.md`

## Problem

PayCall will expose the same actions through web UI, Hermes channels, and CLI
programs. Auth must not be duplicated per channel. The reusable auth platform
needs hashed API tokens and channel actor resolution that produce the same
`ActorContext` shape as web sessions.

This spec adopts qnp-crm's command discipline: stable JSON envelopes,
plan-first mutating commands, explicit `--confirm`, stable exit codes, and
trace/audit output.

## Desired Behavior

- Given an owner requests an API token, the CLI returns a plan unless
  `--confirm` is supplied.
- Given `--confirm`, the auth core creates a hashed API token, stores only the
  hash, shows the raw token once, and emits an audit event.
- Given a valid API token, CLI and Hermes adapters resolve an `ActorContext`
  with token scope, organization, actor, and permissions.
- Given a revoked, expired, malformed, or wrong-org token, actor resolution fails
  closed.
- Given a mutating CLI/Hermes command, the command returns a plan unless
  `--confirm` is supplied.
- Given a high-risk auth command, such as token creation, token revocation, MFA
  reset, or ownership transfer, explicit confirmation is required.

## Non-Goals

- Do not implement every PayCall command.
- Do not implement LLM intent parsing.
- Do not implement Telegram/WhatsApp adapters.
- Do not store raw API tokens.
- Do not bypass application permission checks for CLI or Hermes.

## Likely Files

- `src/auth/api_tokens.py`
- `src/auth/cli.py`
- `src/auth/hermes.py`
- `src/auth/command_envelope.py`
- `src/auth/service.py`
- `src/auth/repositories.py`
- `tests/unit/auth/test_api_tokens.py`
- `tests/unit/auth/test_cli_envelope.py`
- `tests/unit/auth/test_cli_actor_resolution.py`
- `tests/unit/auth/test_hermes_actor_resolution.py`
- `tests/unit/auth/test_token_commands.py`
- `tests/integration/auth/test_api_token_repository.py`

## Edge Cases

- Token shown more than once.
- Raw token accidentally logged.
- Token hash collision attempt.
- Token malformed.
- Token expired.
- Token revoked.
- Token belongs to deleted actor.
- Token belongs to suspended membership.
- Token scoped to org A used for org B.
- Token has read-only scope but command mutates.
- Viewer tries to create a token.
- Service token attempts human-only action.
- Hermes channel identity has no mapped local actor.
- CLI mutation run without `--confirm`.
- CLI command exits with wrong exit code.
- Command envelope omits audit ID or trace.

Fail closed for token ambiguity, scope mismatch, membership ambiguity, and
high-risk auth commands without confirmation.

## Test Expectations

Expected tests:

```bash
uv run pytest tests/unit/auth/test_api_tokens.py -q
uv run pytest tests/unit/auth/test_cli_envelope.py -q
uv run pytest tests/unit/auth/test_cli_actor_resolution.py -q
uv run pytest tests/unit/auth/test_hermes_actor_resolution.py -q
uv run pytest tests/unit/auth/test_token_commands.py -q
uv run pytest tests/integration/auth/test_api_token_repository.py -q
```

Expected lint:

```bash
uv run ruff check src tests
```

If this repo still uses `app/` instead of `src/`, run:

```bash
uv run ruff check app tests
```

## Acceptance Criteria

- [ ] API tokens are generated securely and stored only as hashes.
- [ ] Raw API tokens are displayed once and never logged.
- [ ] API token actor resolution returns the same `ActorContext` shape as web
      session resolution.
- [ ] Token scopes and organization scope are enforced.
- [ ] Token creation and revocation are audited.
- [ ] Mutating auth CLI commands return a plan unless `--confirm` is supplied.
- [ ] CLI envelopes include `status`, `result`, `error`, `hints`, `trace`, and
      `audit_id`.
- [ ] Exit codes are stable: `0` success, `1` user/input/authz error, `2`
      system error.
- [ ] Hermes actor resolution uses the same auth service as CLI and web.
- [ ] `CHANGELOG.md` is updated if code behavior is implemented.

## Known Risks

- **Risk**: CLI and Hermes become separate authorization paths.
  **How we'd notice**: Token commands check roles directly instead of calling
  the permission resolver.
  **Mitigation**: Require CLI/Hermes actor resolution tests with shared
  `ActorContext`.

- **Risk**: Token leakage through logs or envelopes.
  **How we'd notice**: Snapshot tests include raw token values.
  **Mitigation**: Add redaction assertions to token command tests.
