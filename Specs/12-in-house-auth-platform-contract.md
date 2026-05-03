# Feature: In-house reusable auth platform contract

State: ready-for-splitting

## Why

Auth will be built in-house and reused across projects. That means the reusable
asset must be stricter than a one-off login flow: it needs requirements,
interfaces, schemas, test fixtures, edge cases, CLI behavior, and preflight
checks that Night Shift agents can repeatedly run without improvising security
decisions.

The goal is not to copy PaymentReminder auth as-is. The goal is to adopt the
parts that worked, avoid the parts that leaked framework state into product
logic, and add the missing hard guarantees needed for new projects.

## Lessons to adopt

From PaymentReminder:

- Use framework sessions only at the web interface boundary.
- Keep login, signup, logout, and onboarding redirects covered by route tests.
- Keep a local user record and stable local IDs.
- Keep Google/OAuth account linking separate from the user primary key.
- Keep CSRF on form-based login/signup in production.
- Do not let `current_user`, Flask sessions, or route decorators become the only
  authorization mechanism.
- Do not keep admin auth as a separate env-password side channel long term.

From qnp-crm:

- Prefer small composable CLI commands with JSON output.
- Mutating commands should support plan-first behavior and require `--confirm`.
- Commands need stable exit codes: success, user error, and system error.
- Test command envelopes, idempotency, compatibility, and trace output.

From EmpatheEating:

- OAuth account linking must reject attempts to link one external account to
  multiple local users.
- OAuth token handling must avoid logging sensitive tokens.
- Auth/payment changes deserve explicit tests and review gates.

From nem-forecast:

- Specs must state observable behavior, acceptance criteria, edge cases, risks,
  constraints, and whether work is a spike or feature.

## What the system should do

- Given a new app, the in-house auth package should provide user registration,
  login, logout, session validation, password reset, email verification, MFA
  hooks, OAuth account linking, organization membership, role permissions,
  service accounts, API tokens, audit events, and CLI/Hermes actor resolution.
- Given a web request, CLI command, Hermes skill call, worker job, or webhook,
  the system should resolve a provider-independent `ActorContext`.
- Given application use cases, authorization should depend only on
  `ActorContext` and product permissions, never directly on Flask sessions,
  request objects, raw cookies, raw JWTs, or ORM user models.
- Given a mutation through CLI or Hermes, the command should produce a plan
  unless `--confirm` is supplied.
- Given an auth package update, existing downstream apps should be able to run
  the same auth contract tests before adopting it.

## Data flow

```text
web form/OAuth callback/API token/CLI token/channel identity
  -> auth interface adapter
  -> credential/session/token verification
  -> local identity + membership lookup
  -> ActorContext
  -> application use case authorization
  -> audit event
```

## Core data model

Use stable local primary keys. OAuth provider IDs, emails, and tokens are not
business primary keys.

Required records:

- `User`: login-capable human identity.
- `Credential`: password hash, password version, compromised/rotated state.
- `OAuthIdentity`: provider name, provider subject, linked user ID.
- `Session`: server-side session ID, user ID, org ID, expiry, revocation state.
- `Organization`: tenant/business account.
- `OrganizationMembership`: user, org, role, status.
- `PermissionGrant`: optional explicit permission overrides.
- `ServiceAccount`: non-human actor for workers and automations.
- `ApiToken`: hashed token for CLI/Hermes/API access.
- `EmailVerificationToken`: hashed one-time email verification token.
- `PasswordResetToken`: hashed one-time password reset token.
- `MfaFactor`: TOTP/WebAuthn/SMS/email factor metadata.
- `AuthAuditEvent`: immutable auth/security event log.

## ActorContext

Every authenticated action receives:

- `actor_id`: local user or service-account ID.
- `actor_type`: `human` or `service`.
- `organization_id`: local organization ID when org-scoped.
- `membership_id`: local membership ID when human/org-scoped.
- `role`: `owner`, `bookkeeper`, `viewer`, or app-specific role.
- `permissions`: resolved product permissions.
- `auth_channel`: `web`, `cli`, `hermes`, `worker`, `webhook`, or `test`.
- `auth_method`: `password`, `oauth`, `api_token`, `service_token`, or `test`.
- `auth_strength`: includes MFA status and session freshness.
- `session_id`: local session reference when session-backed.
- `request_id`: correlation ID for audit.

## AuthPort contract

Apps depend on a small in-house port:

```text
AuthPort
  register_user(email, password, terms, request_meta) -> RegistrationResult
  verify_email(token, request_meta) -> VerificationResult
  login_password(email, password, request_meta) -> LoginResult
  begin_oauth(provider, return_to, request_meta) -> RedirectInstruction
  complete_oauth(provider, callback, request_meta) -> LoginResult
  logout(session_id, request_meta) -> LogoutResult
  request_password_reset(email, request_meta) -> ResetRequestResult
  reset_password(token, new_password, request_meta) -> ResetResult
  resolve_web_actor(session_cookie, request_meta) -> ActorContext | AuthError
  resolve_cli_actor(api_token, request_meta) -> ActorContext | AuthError
  resolve_hermes_actor(channel_identity, request_meta) -> ActorContext | AuthError
  resolve_service_actor(service_token, request_meta) -> ActorContext | AuthError
  require_permission(actor, permission, resource) -> Authorized | AuthzError
```

Interface adapters call this port. Domain and application use cases receive
`ActorContext`, not auth storage objects.

## Password requirements

- Password hashes use Argon2id or another current memory-hard password hash.
- Password hashes include per-password salt and versioned parameters.
- Raw passwords are never logged, stored, emitted in test snapshots, or returned
  in command envelopes.
- Password reset and email verification tokens are stored hashed.
- Login compares passwords in a timing-safe path.
- Failed login attempts are rate limited by email, IP, and device/session
  fingerprint where available.
- Successful password reset invalidates active sessions unless explicitly
  configured otherwise.

## Session requirements

- Sessions are server-side or otherwise revocable.
- Session cookies are `HttpOnly`, `Secure` in non-local environments, and
  `SameSite=Lax` or stricter unless a spec requires otherwise.
- Session IDs are rotated on login, privilege elevation, password reset, and MFA
  completion.
- Logout revokes the current session.
- Global logout revokes all active sessions for the actor.
- Stale, expired, revoked, malformed, and unknown sessions fail closed.

## OAuth requirements

- OAuth identities are separate from user primary keys.
- One OAuth provider subject cannot link to multiple local users.
- A logged-in user can link an OAuth identity only after fresh auth.
- OAuth callback state is verified.
- OAuth scopes are explicit and minimal.
- OAuth tokens are encrypted at rest if stored.
- OAuth errors are user-visible but do not leak provider tokens or raw payloads.

## Organization and permission requirements

Minimum roles:

| Role | Must allow | Must deny |
| --- | --- | --- |
| `owner` | manage org, manage members, connect bank accounts, manage billing, confirm/reject/undo allocations, manage invoices, schedule reminders | cross-org access |
| `bookkeeper` | manage clients/invoices/payments, confirm/reject/undo allocations, view bank transactions, schedule reminders | manage billing, manage members, delete org |
| `viewer` | read dashboards, clients, invoices, payments, reminders, bank summaries | create/update/delete records, confirm allocations, schedule reminders, manage billing/members |

Use cases check permissions, not only route decorators. Route decorators are a
convenience layer, not the source of truth.

## CLI and Hermes requirements

Follow the qnp-crm pattern:

- Read commands execute immediately.
- Mutating commands return a JSON plan unless `--confirm` is supplied.
- High-risk auth commands, such as member removal, MFA reset, API token
  creation, and ownership transfer, require explicit confirmation.
- CLI output uses a stable envelope: `status`, `result`, `error`, `hints`,
  `trace`, and `audit_id`.
- Exit codes: `0` success, `1` user/input/authz error, `2` system error.
- Hermes skills call the same CLI/service functions as the web app. The auth
  implementation must not duplicate business authorization per channel.

## Acceptance criteria

- [ ] Auth package exposes `ActorContext` and `AuthPort`.
- [ ] Product use cases authorize only against `ActorContext` and permissions.
- [ ] Unit tests can run without OAuth providers, email services, SMS services,
      or network access.
- [ ] Password hashing, verification, reset, and session revocation are covered
      by tests.
- [ ] OAuth account linking and duplicate-provider-subject failures are covered
      by tests.
- [ ] Owner/bookkeeper/viewer authorization is tested at application use-case
      level.
- [ ] CLI/Hermes auth commands share the same auth service and permission checks
      as web routes.
- [ ] Mutating auth CLI commands support plan-first and `--confirm`.
- [ ] Auth audit events are emitted for login, logout, failed login, password
      reset, email verification, role change, token creation, token revocation,
      MFA changes, and denied authorization.
- [ ] The package has a migration guide for adopting it in a new repo.

## Required tests

Expected reusable test files:

- `tests/unit/auth/test_password_hashing.py`
- `tests/unit/auth/test_registration.py`
- `tests/unit/auth/test_email_verification.py`
- `tests/unit/auth/test_password_reset.py`
- `tests/unit/auth/test_sessions.py`
- `tests/unit/auth/test_oauth_identity_linking.py`
- `tests/unit/auth/test_actor_context.py`
- `tests/unit/auth/test_permissions.py`
- `tests/unit/auth/test_api_tokens.py`
- `tests/unit/auth/test_service_accounts.py`
- `tests/unit/auth/test_auth_audit_events.py`
- `tests/unit/auth/test_rate_limits.py`
- `tests/unit/auth/test_cli_envelope.py`
- `tests/unit/application/test_actor_authorization.py`
- `tests/integration/auth/test_auth_repository.py`
- `tests/integration/auth/test_session_repository.py`

Expected commands:

```bash
uv run pytest tests/unit/auth -q
uv run pytest tests/unit/application/test_actor_authorization.py -q
uv run pytest tests/integration/auth -q
uv run ruff check src tests
```

If the repo uses `app/` instead of `src/`, use:

```bash
uv run ruff check app tests
```

## Edge cases

- Empty email.
- Invalid email.
- Email case changes.
- Duplicate email registration.
- Registration while an unverified account already exists.
- Password below minimum length.
- Password above maximum accepted length.
- Password contains leading/trailing spaces.
- Password hash parameter migration is required.
- Password reset token reused.
- Password reset token expired.
- Password reset token unknown.
- Password reset requested for unknown email.
- Email verification token reused.
- Email verification token expired.
- Email verification token belongs to deleted user.
- Login with unverified email.
- Login with disabled user.
- Login with wrong password repeatedly.
- Login during rate-limit window.
- Login after password reset invalidated sessions.
- Session cookie missing.
- Session ID malformed.
- Session revoked.
- Session expired.
- Session belongs to deleted user.
- Session belongs to user with suspended membership.
- MFA required but not completed.
- MFA recovery code reused.
- OAuth state missing.
- OAuth state mismatch.
- OAuth provider returns no email.
- OAuth provider email is unverified.
- OAuth subject already linked to another user.
- Logged-in user tries to link OAuth without fresh auth.
- API token is shown only once.
- API token hash collision attempt.
- API token revoked.
- API token scoped to org A used for org B.
- Service account attempts human-only action.
- Actor belongs to org A but accesses org B.
- User has no active membership.
- Final owner removal is attempted.
- Owner transfer interrupted midway.
- Viewer attempts a mutation.
- Bookkeeper attempts billing/member management.
- Audit event write fails after auth succeeds.
- Clock skew around token/session expiry.
- Concurrent password reset and login.
- Concurrent membership role changes.
- CLI mutation run without `--confirm`.
- Hermes channel identity has no mapped local actor.

Fail closed for accounting, banking, calling, billing, member-management, token
creation, MFA reset, and ownership-transfer actions when state is ambiguous.

## Night Shift preflight

Before implementing auth work:

```bash
test -f Specs/12-in-house-auth-platform-contract.md
rg -n "ActorContext|AuthPort|Argon2id|OAuthIdentity|ApiToken|AuthAuditEvent" Specs/12-in-house-auth-platform-contract.md
rg -n "Password reset token reused|OAuth state mismatch|final owner|--confirm|Fail closed" Specs/12-in-house-auth-platform-contract.md
```

Dependency checks:

- password hashing tests before registration/login implementation
- session repository tests before web route integration
- permission tests before product use-case integration
- CLI envelope tests before Hermes skills call auth commands
- audit-event tests before high-risk auth mutations

## Constraints

- Do not copy PaymentReminder auth wholesale.
- Do not let Flask-Login or framework sessions cross into product use cases.
- Do not store raw passwords, raw reset tokens, raw verification tokens, or raw
  API tokens.
- Do not log passwords, bearer tokens, OAuth tokens, reset links, or API tokens.
- Do not rely only on route decorators for authorization.
- Do not build channel-specific authorization twice.
- Do not call external OAuth/email/SMS services from unit tests.

## Open questions

- Should the reusable auth package be a standalone repo under
  `~/repositories/individual`, or a package generated into each project?
- Should the first implementation target Flask first, or define a framework-free
  core with Flask/FastAPI adapters?
- Which MFA factors are required in the first version: TOTP, WebAuthn, email,
  SMS, or recovery codes?
- Should API tokens be first-class for Hermes from day one, or follow after web
  login and organization membership?

## Spike vs Feature

**Feature contract.** This spec defines the reusable acceptance surface. The
first implementation is split into:

- `Specs/13-auth-password-session-core.md`
- `Specs/14-auth-org-permission-core.md`
- `Specs/15-auth-oauth-identity-linking.md`
- `Specs/16-auth-api-tokens-cli-hermes.md`
- `Specs/17-auth-audit-and-risk-events.md`

MFA and adoption-guide specs should be added after these core slices are
accepted.
