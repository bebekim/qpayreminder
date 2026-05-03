# Spike: Auth direction and reusable auth boundary

State: superseded by `Specs/12-in-house-auth-platform-contract.md`

## Why

PayCall authentication is a cross-project concern that needs secure login,
OAuth, sessions/tokens, organizations, roles, invitations, and eventually
agent/CLI access. The original spike compared hosted and open-source auth
providers.

The direction changed: auth will be built in-house as a reusable platform
contract. Hosted providers may still be useful for reference or future
integration, but they are not the first implementation target.

## What the system should do

- Given a new PayCall app, the system should use the reusable in-house auth
  package rather than reimplementing app-specific login.
- Given a logged-in identity, the PayCall app should map it to local
  `Organization`, `UserProfile`, membership, and role records.
- Given an organization role from the local membership table,
  PayCall use cases should enforce owner/bookkeeper/viewer permissions.
- Given Hermes, CLI, or machine-to-machine access, the auth solution should
  support verifiable tokens or API keys without duplicating authorization per
  channel.
- Given a future second product, the chosen auth approach should be reusable
  without copying PayCall business code.

Reference categories for learning, not first implementation:

- Commercial hosted auth: Clerk, Kinde, Auth0, WorkOS.
- Hosted/open-source platform: Supabase Auth.
- Self-hosted open source IAM: Keycloak, ZITADEL, Ory, Better Auth depending on
  stack.

## Data flow

```
in-house auth login/API token/channel identity
    -> verified identity/session/token
    -> local identity mapping -> PayCall membership/role policy
    -> application use case authorization
```

Local data PayCall still owns:

- organization ID
- user profile/display preferences
- membership role: owner, bookkeeper, viewer
- last viewed dashboard timestamp
- billing/subscription linkage if not delegated to provider billing
- audit actor ID for allocation confirmation/rejection/undo

In-house auth owns:

- credentials
- OAuth provider connection
- password reset / magic link / MFA / passkeys
- session issuance and revocation
- user invitation flow when supported

## Acceptance criteria

- [ ] `Specs/12-in-house-auth-platform-contract.md` exists.
- [ ] The contract covers password login, sessions, OAuth account linking,
      organizations, roles/permissions, invitations or membership management,
      MFA hooks, API/CLI token story, data portability, and audit events.
- [ ] Password hashes are owned by the reusable in-house auth package, not by
      product-specific business code.
- [ ] PayCall application use cases receive an authenticated actor DTO rather
      than Flask/session objects.
- [ ] Owner/bookkeeper/viewer authorization is enforced in application use
      cases, not only in route decorators.
- [ ] Unit tests use fake actor/auth context and do not call OAuth/email/SMS
      providers.

## Test plan

This spike is superseded. Validate the current auth direction with the in-house
contract checks.

Expected direction checks:

```bash
test -f Specs/12-in-house-auth-platform-contract.md
rg -n "ActorContext|AuthPort|Argon2id|OAuthIdentity|ApiToken|AuthAuditEvent" Specs/12-in-house-auth-platform-contract.md
rg -n "Password reset token reused|OAuth state mismatch|final owner|--confirm|Fail closed" Specs/12-in-house-auth-platform-contract.md
```

Expected future test files:

- `tests/unit/application/test_actor_authorization.py`
- `tests/unit/interface/test_auth_adapter_contract.py`
- `tests/unit/interface/test_fake_auth_context.py`

Expected future commands:

```bash
uv run pytest tests/unit/application/test_actor_authorization.py -q
uv run pytest tests/unit/interface/test_auth_adapter_contract.py -q
uv run pytest tests/unit/interface/test_fake_auth_context.py -q
uv run ruff check src tests
```

No unit test should call OAuth, email, SMS, or live auth services.

## What could go wrong

- **Risk**: Flask/session convenience leaks into domain/application code.
  **How we'd notice**: Domain or use cases import Flask-Login or use
  `current_user`.
  **Mitigation**: Use an auth port and actor DTO.

- **Risk**: Organization roles are split inconsistently between sessions and
  local DB.
  **How we'd notice**: Web UI says a user is admin but use case sees viewer.
  **Mitigation**: Pick a single source of truth for role assignment and document
  synchronization rules.

- **Risk**: In-house auth becomes app-specific and hard to reuse.
  **How we'd notice**: New repos copy/paste route code or invent different auth
  tables.
  **Mitigation**: Package the core and require contract tests before adoption.

## Constraints

- Do not implement password storage in product-specific modules.
- Do not build OAuth callback handling without state verification and account
  linking tests.
- Unit tests must not depend on OAuth, email, SMS, or provider network access.
- Framework specifics stay at the interface/infrastructure boundary.
- The auth package must support reusable auth across multiple repositories.

## Open questions

- Should the reusable auth package be a standalone repo or generated into each
  project?
- Should the first implementation target Flask first or a framework-free core
  with Flask/FastAPI adapters?
- Which MFA factor is first: TOTP, WebAuthn, email, SMS, or recovery codes?
- Should API tokens for Hermes be in the first auth slice?

## Spike vs Feature

**Superseded spike**. The output is the in-house contract in
`Specs/12-in-house-auth-platform-contract.md`. Production auth implementation
should be split into smaller feature specs from that contract.
