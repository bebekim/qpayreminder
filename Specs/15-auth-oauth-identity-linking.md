# Auth OAuth Identity Linking

Priority: medium
State: blocked
Blocked by: `Specs/13-auth-password-session-core.md`

## Problem

PaymentReminder and EmpatheEating both show that Google OAuth is valuable, but
OAuth account linking is easy to get wrong. The reusable in-house auth platform
needs OAuth identities as links to local users, not as primary identities, and
must prevent one external account from being linked to multiple local users.

## Desired Behavior

- Given a user starts OAuth login, the auth core creates and verifies callback
  state.
- Given a valid OAuth callback for an existing linked identity, the auth core
  logs in the linked local user and creates a fresh session.
- Given a valid OAuth callback for an email matching an existing local user, the
  auth core links the OAuth identity only when the policy allows it and required
  freshness checks pass.
- Given a logged-in user links OAuth, the auth core requires a fresh session or
  recent password/MFA verification.
- Given an OAuth provider subject is already linked to another local user, the
  auth core rejects the link.
- Given OAuth provider errors, the user sees a safe error and raw provider
  tokens/payloads are not logged.

## Non-Goals

- Do not implement every OAuth provider.
- Do not implement calendar or provider-specific API access.
- Do not implement enterprise SSO.
- Do not store OAuth tokens unless a later product feature needs provider API
  access.
- Do not add UI beyond minimal adapter hooks required by tests.

## Likely Files

- `src/auth/oauth.py`
- `src/auth/oauth_state.py`
- `src/auth/oauth_identity.py`
- `src/auth/service.py`
- `src/auth/repositories.py`
- `tests/unit/auth/test_oauth_state.py`
- `tests/unit/auth/test_oauth_identity_linking.py`
- `tests/unit/auth/test_oauth_login.py`
- `tests/integration/auth/test_oauth_identity_repository.py`

## Edge Cases

- OAuth state missing.
- OAuth state mismatch.
- OAuth state reused.
- OAuth callback expired.
- OAuth provider returns no subject.
- OAuth provider returns no email.
- OAuth provider email is unverified.
- OAuth provider subject already linked to another local user.
- Logged-in user tries to link OAuth without fresh auth.
- Existing email matches disabled user.
- Existing email differs only by case.
- Provider token is absent.
- Provider token contains unexpected scopes.
- Provider returns an error.
- Local commit fails after provider callback succeeds.

Fail closed for duplicate or ambiguous identity links.

## Test Expectations

Expected tests:

```bash
uv run pytest tests/unit/auth/test_oauth_state.py -q
uv run pytest tests/unit/auth/test_oauth_identity_linking.py -q
uv run pytest tests/unit/auth/test_oauth_login.py -q
uv run pytest tests/integration/auth/test_oauth_identity_repository.py -q
```

Expected lint:

```bash
uv run ruff check src tests
```

If this repo still uses `app/` instead of `src/`, run:

```bash
uv run ruff check app tests
```

OAuth tests must use fake provider payloads. They must not call Google or any
other live OAuth provider.

## Acceptance Criteria

- [ ] OAuth identity links are separate records from local users.
- [ ] OAuth callback state is generated, persisted or signed, verified, and
      single-use.
- [ ] One provider subject cannot link to multiple local users.
- [ ] Linking OAuth to a logged-in account requires fresh auth.
- [ ] Safe errors are returned for provider failures without logging tokens.
- [ ] Successful OAuth login creates a fresh server-side session.
- [ ] OAuth account linking emits audit events.
- [ ] `CHANGELOG.md` is updated if code behavior is implemented.

## Known Risks

- **Risk**: OAuth becomes a parallel auth stack.
  **How we'd notice**: OAuth callback bypasses `AuthPort` or session creation.
  **Mitigation**: OAuth completion returns the same `LoginResult` shape as
  password login.

- **Risk**: Account takeover through email matching.
  **How we'd notice**: Tests allow linking by email without freshness checks or
  verified email policy.
  **Mitigation**: Require explicit linking policy and tests for every branch.
