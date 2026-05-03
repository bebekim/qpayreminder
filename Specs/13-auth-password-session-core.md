# Auth Password And Session Core

Priority: high
State: ready

## Problem

PayCall needs reusable in-house auth primitives before any product use case,
Hermes command, or web route can rely on a stable authenticated actor. The
existing PaymentReminder auth is useful behaviorally, but it stores password
hash behavior on the product `User` model and lets Flask-Login/session state act
as the main boundary.

This spec creates the first reusable auth slice: registration, password hashing,
password login, server-side session lifecycle, session-backed `ActorContext`,
and fake/test auth fixtures.

## Desired Behavior

- Given a new email/password registration, the auth core creates a local user,
  credential record, default organization, owner membership, server-side session,
  and auth audit events.
- Given a valid email/password login, the auth core verifies a memory-hard
  password hash and creates a fresh revocable session.
- Given an invalid login, the auth core returns a user-safe error, records an
  audit event, and does not reveal whether the email exists.
- Given a session cookie or session ID, the auth core resolves an `ActorContext`
  containing actor ID, organization ID, membership ID, role, permissions,
  auth channel, auth method, auth strength, session ID, and request ID.
- Given logout, password change, password reset completion, or session
  revocation, the relevant session can no longer resolve an actor.
- Given application use cases, tests can construct fake `ActorContext` objects
  without Flask, cookies, network access, OAuth providers, email, or SMS.

## Non-Goals

- Do not implement OAuth identity linking.
- Do not implement API tokens, CLI tokens, Hermes channel auth, or service
  accounts.
- Do not implement MFA factors beyond the `auth_strength` shape and a
  `mfa_satisfied=false` default.
- Do not build billing, invitations, or member-management UI.
- Do not migrate existing PaymentReminder production users.
- Do not use hosted auth providers.

## Likely Files

These names are illustrative; prefer the new repo's package layout if different.

- `src/auth/entities.py`
- `src/auth/passwords.py`
- `src/auth/sessions.py`
- `src/auth/actor_context.py`
- `src/auth/permissions.py`
- `src/auth/repositories.py`
- `src/auth/service.py`
- `src/auth/fakes.py`
- `src/auth/audit.py`
- `tests/unit/auth/test_password_hashing.py`
- `tests/unit/auth/test_registration.py`
- `tests/unit/auth/test_password_login.py`
- `tests/unit/auth/test_sessions.py`
- `tests/unit/auth/test_actor_context.py`
- `tests/unit/auth/test_fake_auth_context.py`
- `tests/integration/auth/test_session_repository.py`

If the implementation starts inside this Flask repo before extraction, use
`app/auth_core/` and `tests/unit/auth/` instead of `src/auth/`.

## Edge Cases

- Empty email.
- Invalid email.
- Email case changes.
- Duplicate email registration.
- Registration while an unverified or disabled account already exists.
- Password below minimum length.
- Password above maximum accepted length.
- Password with leading or trailing spaces.
- Password hash parameter migration is required.
- Login with wrong password.
- Login with disabled user.
- Login during rate-limit window.
- Session cookie missing.
- Session ID malformed.
- Session revoked.
- Session expired.
- Session belongs to deleted user.
- Session belongs to user with suspended membership.
- Password change invalidates previous sessions.
- Clock skew around session expiry.
- Audit event write fails after login succeeds.

Fail closed for actor resolution when identity, membership, session, or role
state is ambiguous.

## Test Expectations

Expected tests:

```bash
uv run pytest tests/unit/auth/test_password_hashing.py -q
uv run pytest tests/unit/auth/test_registration.py -q
uv run pytest tests/unit/auth/test_password_login.py -q
uv run pytest tests/unit/auth/test_sessions.py -q
uv run pytest tests/unit/auth/test_actor_context.py -q
uv run pytest tests/unit/auth/test_fake_auth_context.py -q
uv run pytest tests/integration/auth/test_session_repository.py -q
```

Expected lint:

```bash
uv run ruff check src tests
```

If this repo still uses `app/` instead of `src/`, run:

```bash
uv run ruff check app tests
```

No unit test may call OAuth, email, SMS, hosted auth, or live network services.

## Acceptance Criteria

- [ ] Password hashes use Argon2id or another current memory-hard hash with
      versioned parameters.
- [ ] Raw passwords are never stored, logged, returned, snapshotted, or included
      in command/test envelopes.
- [ ] Registration creates local user, credential, organization, owner
      membership, session, and audit events transactionally or with documented
      compensating behavior.
- [ ] Login rotates/creates a fresh session and emits an audit event.
- [ ] Logout revokes the current session.
- [ ] Revoked, expired, malformed, unknown, and deleted-user sessions fail
      closed.
- [ ] `ActorContext` is resolved from auth core and contains no Flask/session
      objects.
- [ ] Fake actor/auth fixtures are available for product use-case tests.
- [ ] Product use cases do not import Flask-Login or read `current_user`.
- [ ] `CHANGELOG.md` is updated if code behavior is implemented.

## Known Risks

- **Risk**: Password/session logic becomes app-specific.
  **How we'd notice**: Product models own password hash methods or route code
  creates sessions directly.
  **Mitigation**: Keep auth core in a package boundary and expose `AuthPort`.

- **Risk**: Route decorators become the only authorization check.
  **How we'd notice**: Application tests pass without `ActorContext`.
  **Mitigation**: Require fake actor use-case tests in dependent specs.

- **Risk**: Tests pass with in-memory behavior but repository revocation fails.
  **How we'd notice**: Integration session repository tests are missing.
  **Mitigation**: Include repository integration tests before web integration.
