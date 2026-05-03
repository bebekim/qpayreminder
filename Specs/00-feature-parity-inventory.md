# Spike: Feature parity inventory for PayCall migration

State: done

## Why

We want to build a new repository instead of continuing to harden the current
PaymentReminder monolith. Before implementation starts, we need an explicit
inventory of behavior that must either be migrated, redesigned, or deliberately
dropped.

Without this inventory, the new repo will either copy accidental implementation
details or miss user-facing behavior that exists today.

## What the system should do

- Given the existing PaymentReminder repo, the migration inventory should list
  every user-facing and operator-facing behavior by product area.
- Given a behavior that is only partially implemented, the inventory should mark
  it as `partial` and link to the relevant source files or docs.
- Given a behavior that is documented but not implemented, the inventory should
  mark it as `target-only`.
- Given a behavior that is legacy ToodlelooMe or unrelated to PayCall, the
  inventory should mark it as `legacy-review`.
- Given a behavior that requires external services, the inventory should name
  whether parity can be verified with mocks, sandbox, staging, or live provider
  access.

Expected product areas:

- Authentication and onboarding
- Organization/user roles and permissions
- Client/customer management
- Invoice creation, upload, extraction, and review
- Payment recording and invoice status transitions
- Bank connection, transaction ingestion, and reconciliation
- AI match proposal, allocation, confirmation, rejection, and undo
- Dashboard freshness and "new since last visit" behavior
- Reminder scheduling, voice calls, SMS/email, and call outcomes
- Subscription billing and plan limits
- Admin/operator workflows
- Webhooks and background jobs
- Hermes/agent command surface

## Data flow

```
PaymentReminder docs + code + tests -> feature inventory -> new repo specs
```

Data sources:

- `docs/PRD_PayCall.md`: canonical product requirements.
- `docs/IMPLEMENTATION_PLAN_PayCall.md`: useful implementation notes, not
  authoritative when it conflicts with code.
- `docs/ARCHITECTURE_SUMMARY_PayCall.md`: target architecture notes.
- `README.md`: current user-facing product summary.
- `app/domain`, `app/services`, `app/application`, `app/interfaces`: current
  behavior and implementation boundaries.
- `tests/`: current regression expectations.

## Acceptance criteria

- [ ] `docs/feature-parity.md` exists and groups behavior by product area.
- [ ] Each behavior is marked as `implemented`, `partial`, `target-only`,
      `legacy-review`, or `drop`.
- [ ] Each behavior has at least one source reference: doc path, test path, or
      code path.
- [ ] Each external-service behavior names the verification mode: mocked,
      sandbox, staging, or live.
- [ ] Each retained or redesigned behavior links to a target new-repo spec path
      or is marked `needs-spec`.
- [ ] The inventory identifies the minimum MVA parity set for a new repo.
- [ ] The inventory identifies behavior that should not be ported.
- [ ] No production code is changed by this spike.

## Test plan

This is a documentation spike, so validation is structural rather than a
production test suite.

Expected checks:

```bash
test -f docs/feature-parity.md
rg -n "implemented|partial|target-only|legacy-review|drop" docs/feature-parity.md
rg -n "mocked|sandbox|staging|live" docs/feature-parity.md
git diff -- app migrations
```

Expected result:

- `docs/feature-parity.md` exists.
- Every product area has status labels.
- External-service behaviors name a verification mode.
- There are no application or migration code changes.

## What could go wrong

- **Risk**: The inventory treats current code as product truth.
  **How we'd notice**: Legacy or accidental workflows appear as required parity.
  **Mitigation**: Prefer PRD behavior over code when they conflict, and mark
  code-only behavior as `legacy-review`.

- **Risk**: External-service flows are underspecified.
  **How we'd notice**: Later specs require live provider details that were never
  captured.
  **Mitigation**: Require verification mode and credential assumptions for each
  provider flow.

- **Risk**: The inventory becomes a backlog dump.
  **How we'd notice**: It lists modules instead of observable user behavior.
  **Mitigation**: Phrase each item as a behavior with input, effect, and owner.

## Constraints

- This is a spike. It should produce knowledge and specs, not application code.
- Do not run live Stripe, Twilio, Vapi, Basiq, Anthropic, or webhook scripts.
- Do not mutate migrations or database state.
- Do not attempt to fix discovered bugs; record them in `TODO.md` or the
  inventory.

## Open questions

- What is the name and location of the new repository?
- Which legacy ToodlelooMe phone-call behavior should be retained for PayCall?
- Is Hermes required in the first MVA or only after core AR workflows exist?
- Should subscription/billing parity be part of MVA or deferred?

## Spike vs Feature

**Spike**. The output is a feature inventory and follow-up specs. No production
code or database migrations should be written.
