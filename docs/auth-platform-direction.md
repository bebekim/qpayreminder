# Auth Platform Direction

Date: 2026-05-03
Specs:

- `Specs/10-auth-provider-selection.md`
- `Specs/12-in-house-auth-platform-contract.md`

Status: in-house reusable auth selected

## Decision

Build auth in-house as a reusable platform/package for future projects.

Do not treat Kinde, Clerk, Auth0, WorkOS, Supabase, Keycloak, or Better Auth as
the primary implementation path. They remain useful references for capability
coverage and future interoperability, but PayCall should start from a local
contract, local data model, and local test harness.

## Reusable Boundary

The stable contract is:

```text
web/session/OAuth/API token/CLI/Hermes/channel identity
  -> AuthPort
  -> ActorContext
  -> application use case authorization
```

Application use cases receive `ActorContext`, not Flask `current_user`, raw
sessions, raw JWTs, raw cookies, or ORM user models.

## What To Adopt From PaymentReminder

- Email/password and Google OAuth are useful behavior references.
- Login, signup, logout, OAuth callback, onboarding redirect, and protected route
  behavior should have tests.
- Keep local stable user IDs.
- Keep CSRF protection for form posts.
- Keep OAuth identity separate from local user identity.

## What To Avoid From PaymentReminder

- Do not put password hashing directly on the product `User` model.
- Do not let Flask-Login become the application authorization boundary.
- Do not use `current_user.id` as the only authorization input in use cases.
- Do not keep admin auth as a separate env-password session system.
- Do not mix billing/trial/product flags into the reusable auth core.

## What To Adopt From qnp-crm

- Auth CLI commands should emit stable JSON envelopes.
- Mutating commands should produce a plan unless `--confirm` is supplied.
- High-risk auth commands need explicit confirmation.
- Contract tests should cover idempotency, compatibility, command schema, and
  trace output.

## What To Adopt From EmpatheEating

- OAuth account linking must reject one external account linked to multiple
  local users.
- OAuth token storage and logging need explicit tests.
- Auth changes need review gates and focused tests.

## First Implementation Slices

1. Password/session core.
2. Email verification and password reset.
3. Organization membership and permission resolver.
4. OAuth identity linking.
5. API tokens for CLI/Hermes.
6. MFA factors and recovery codes.
7. Adoption guide for new repos.

## Non-Negotiables

- Store only hashed passwords and hashed one-time/API tokens.
- Use memory-hard password hashing such as Argon2id.
- Rotate sessions on login, privilege elevation, password reset, and MFA.
- Emit audit events for auth and authorization decisions.
- Unit tests must not require external OAuth, email, SMS, or provider services.
- Product use cases must authorize through `ActorContext`.
