# Auth Organization And Permission Core

Priority: high
State: blocked
Blocked by: `Specs/13-auth-password-session-core.md`

## Problem

PayCall needs authorization to be enforced in application use cases, not only in
web route decorators or Flask `current_user` checks. The first auth slice creates
users, sessions, memberships, and actor contexts; this slice makes
owner/bookkeeper/viewer permissions deterministic and reusable across web, CLI,
Hermes, workers, and tests.

## Desired Behavior

- Given an `ActorContext`, the permission resolver returns product permissions
  for the actor's active organization membership.
- Given an owner, the actor can manage org settings, members, billing,
  bank-connection setup, invoices, payments, allocations, and reminders within
  the actor's organization.
- Given a bookkeeper, the actor can manage clients, invoices, payments,
  allocations, bank transaction review, and reminders, but cannot manage members,
  billing, ownership transfer, or organization deletion.
- Given a viewer, the actor can read dashboards, clients, invoices, payments,
  reminders, and bank summaries, but cannot mutate business records or confirm
  allocations.
- Given an actor from org A trying to access org B data, authorization fails.
- Given the final owner would be removed or downgraded, authorization fails.

## Non-Goals

- Do not implement UI for member management.
- Do not implement invitations.
- Do not implement OAuth or API-token authentication.
- Do not implement billing plan enforcement beyond permission names.
- Do not duplicate permission logic separately for web, CLI, and Hermes.

## Likely Files

- `src/auth/permissions.py`
- `src/auth/memberships.py`
- `src/auth/actor_context.py`
- `src/auth/repositories.py`
- `src/application/authorization.py`
- `tests/unit/auth/test_permissions.py`
- `tests/unit/auth/test_memberships.py`
- `tests/unit/application/test_actor_authorization.py`
- `tests/integration/auth/test_membership_repository.py`

If this repo is the first target, use `app/auth_core/` or the established new
repo package layout.

## Edge Cases

- Actor has no active membership.
- Actor membership is suspended.
- Actor membership is pending invitation.
- Actor role is unknown.
- Actor role has no permissions.
- Actor belongs to org A but accesses org B.
- User belongs to multiple organizations and selected org is missing.
- Viewer attempts mutation.
- Bookkeeper attempts billing or member management.
- Owner attempts cross-org access.
- Final owner removal is attempted.
- Concurrent role changes occur while an actor is using an old session.
- Local membership is deleted while session remains active.

Fail closed when role or membership state is ambiguous.

## Test Expectations

Expected tests:

```bash
uv run pytest tests/unit/auth/test_permissions.py -q
uv run pytest tests/unit/auth/test_memberships.py -q
uv run pytest tests/unit/application/test_actor_authorization.py -q
uv run pytest tests/integration/auth/test_membership_repository.py -q
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

- [ ] Permissions are resolved from `ActorContext` and active local membership.
- [ ] Owner/bookkeeper/viewer permissions match the role table in
      `Specs/12-in-house-auth-platform-contract.md`.
- [ ] Use cases reject unauthorized actors without needing Flask route
      decorators.
- [ ] Cross-org access is denied at the application boundary.
- [ ] Final owner removal/downgrade is denied.
- [ ] Permission tests use fake actors and do not require web sessions.
- [ ] Audit events are emitted for role changes and denied authorization.
- [ ] `CHANGELOG.md` is updated if code behavior is implemented.

## Known Risks

- **Risk**: Permissions drift between web, CLI, and Hermes paths.
  **How we'd notice**: Channel-specific authorization branches appear.
  **Mitigation**: Keep one resolver and require all channels to pass
  `ActorContext`.

- **Risk**: Role names are checked directly everywhere.
  **How we'd notice**: Product use cases compare `role == "owner"` repeatedly.
  **Mitigation**: Use permission names except in role-management workflows.
