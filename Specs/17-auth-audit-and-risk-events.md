# Auth Audit And Risk Events

Priority: medium
State: blocked
Blocked by:

- `Specs/13-auth-password-session-core.md`
- `Specs/14-auth-org-permission-core.md`
- `Specs/16-auth-api-tokens-cli-hermes.md`

## Problem

Reusable auth needs durable security visibility. Login, logout, failed login,
authorization denial, password reset, role change, token creation, token
revocation, MFA changes, ownership transfer, and high-risk CLI/Hermes actions
must emit consistent audit events that later product workflows can query.

PaymentReminder has logs, but reusable auth needs structured audit events with
actor, organization, request, channel, decision, and metadata.

## Desired Behavior

- Given any auth lifecycle event, the auth core writes an immutable audit event.
- Given an authorization denial, the audit event records actor, organization,
  permission, resource reference, channel, and safe reason.
- Given token creation or revocation, the audit event records token ID/scope but
  never the raw token.
- Given password reset or email verification, the audit event records safe
  lifecycle state but never raw one-time tokens.
- Given audit persistence failure during high-risk mutations, the auth core
  fails closed unless the spec explicitly marks the event non-blocking.
- Given audit queries, support filtering by actor, organization, event type,
  request ID, and time window.

## Non-Goals

- Do not build a full admin audit UI.
- Do not implement SIEM export.
- Do not implement anomaly detection or automated account lockout unless already
  required by the password/session core.
- Do not log raw credentials, tokens, reset links, or OAuth payloads.

## Likely Files

- `src/auth/audit.py`
- `src/auth/risk_events.py`
- `src/auth/repositories.py`
- `src/auth/redaction.py`
- `tests/unit/auth/test_auth_audit_events.py`
- `tests/unit/auth/test_auth_event_redaction.py`
- `tests/unit/auth/test_auth_risk_events.py`
- `tests/integration/auth/test_auth_audit_repository.py`

## Edge Cases

- Audit event write fails after successful login.
- Audit event write fails before high-risk mutation.
- Request ID missing.
- Actor ID missing for failed anonymous login.
- Organization ID missing for pre-login event.
- Authorization denial has no concrete resource ID.
- Redaction misses bearer token.
- Redaction misses password reset token.
- Redaction misses OAuth access token.
- Duplicate audit event retry.
- Audit query time window is empty.
- Audit event references deleted actor.
- Audit event references deleted organization.

Fail closed for high-risk auth mutations when the audit trail cannot be written.

## Test Expectations

Expected tests:

```bash
uv run pytest tests/unit/auth/test_auth_audit_events.py -q
uv run pytest tests/unit/auth/test_auth_event_redaction.py -q
uv run pytest tests/unit/auth/test_auth_risk_events.py -q
uv run pytest tests/integration/auth/test_auth_audit_repository.py -q
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

- [ ] Auth lifecycle and authorization decisions produce structured audit
      events.
- [ ] Audit events include actor, organization, channel, request ID, event type,
      safe reason, and relevant safe metadata when available.
- [ ] Raw passwords, API tokens, reset tokens, verification tokens, OAuth tokens,
      cookies, and bearer tokens are redacted.
- [ ] High-risk mutations fail closed if the required audit event cannot be
      persisted.
- [ ] Audit repository supports actor/org/type/request/time filtering.
- [ ] Duplicate audit event retries are idempotent or safely distinguishable.
- [ ] Tests cover anonymous, human, service, CLI, Hermes, and denied-action
      events.
- [ ] `CHANGELOG.md` is updated if code behavior is implemented.

## Known Risks

- **Risk**: Audit becomes ordinary application logging.
  **How we'd notice**: Events are unstructured strings or missing stable event
  types.
  **Mitigation**: Use typed audit event objects and repository tests.

- **Risk**: Sensitive auth material leaks into audit metadata.
  **How we'd notice**: Redaction tests fail on password/token fixtures.
  **Mitigation**: Centralize redaction and test known token/password shapes.
