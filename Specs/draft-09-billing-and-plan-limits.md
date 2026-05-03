# Feature: Billing and plan limits parity

## Why

PaymentReminder currently includes Stripe billing, subscriptions, trial state,
and plan-based limits. A new repo needs to decide which billing behavior is
MVA-critical and make those limits enforceable in application use cases rather
than only in web routes.

## What the system should do

- Given a new user or organization, the system should represent trial state and
  subscription state explicitly.
- Given a plan, the system should enforce invoice, bank feed, reminder, and call
  limits through application policy.
- Given a subscription checkout request, the system should create a Stripe
  checkout session through a billing provider port.
- Given a Stripe webhook, the system should verify the signature and update
  subscription state idempotently.
- Given a read-only or expired account state, write actions should be denied by
  use cases, not only by web decorators.

Known current tiers from README:

- Basic: invoice limit 10, SMS reminders, bank feed, QR invoices.
- Plus: invoice limit 50, SMS alerts, AI voice calls, VCAT docs.

## Data flow

```
plan config + subscription provider events -> subscription state
    -> policy checks in application use cases
```

Provider data:

- Stripe customer ID
- Stripe subscription ID
- plan/price ID
- subscription status
- current period/trial timestamps
- webhook event ID for idempotency

## Acceptance criteria

- [ ] Plan limits are represented in configuration or domain policy, not
      hardcoded in web routes.
- [ ] Invoice creation checks applicable plan/trial limits.
- [ ] Voice call initiation checks plan entitlement.
- [ ] Expired trial/read-only state denies write commands consistently through
      web, CLI, and Hermes command paths.
- [ ] Stripe checkout creation uses a provider port.
- [ ] Stripe webhook handling verifies signature before mutation.
- [ ] Stripe webhook handling is idempotent by event ID.
- [ ] Unit tests cover allowed plan, denied plan, expired trial, checkout
      request, webhook success, invalid signature, and duplicate webhook.

## Test plan

Expected test files:

- `tests/unit/domain/test_plan_policy.py`
- `tests/unit/application/test_plan_limit_enforcement.py`
- `tests/unit/application/test_create_checkout_session.py`
- `tests/unit/application/test_billing_webhook.py`
- `tests/unit/infrastructure/test_fake_billing_provider.py`

Expected commands:

```bash
uv run pytest tests/unit/domain/test_plan_policy.py -q
uv run pytest tests/unit/application/test_plan_limit_enforcement.py -q
uv run pytest tests/unit/application/test_create_checkout_session.py -q
uv run pytest tests/unit/application/test_billing_webhook.py -q
uv run pytest tests/unit/infrastructure/test_fake_billing_provider.py -q
uv run ruff check src tests
```

Tests must use a fake billing provider and fake webhook verifier. Live Stripe
validation belongs in a provider-specific integration spec.

## What could go wrong

- **Risk**: Billing checks live only in Flask decorators.
  **How we'd notice**: CLI/Hermes can create invoices despite plan limits.
  **Mitigation**: Put policy checks in application use cases.

- **Risk**: Duplicate webhooks mutate subscription state twice.
  **How we'd notice**: Duplicate event causes repeated side effects.
  **Mitigation**: Store processed event IDs.

- **Risk**: Price IDs or plan names drift between environments.
  **How we'd notice**: Checkout works locally but not staging/production.
  **Mitigation**: Validate plan config at startup and in tests with fixtures.

## Constraints

- Do not call live Stripe in unit tests.
- Provider secrets must not appear in specs, fixtures, or committed code.
- Billing provider details belong in infrastructure.
- This spec may be deferred if billing is not part of new-repo MVA.

## Default Scope

- Defer billing for the first private-beta MVA unless paid access is explicitly
  required before launch.
- Treat Basic/Plus/VCAT tiers as historical parity inputs, not committed product
  scope.

## Open questions

- Is billing required before private beta?
- If billing is required, what are the current plans, prices, and entitlements?
- Is VCAT documentation still in product scope?

## Spike vs Feature

**Feature** if billing is in MVA; otherwise keep this as a draft parity spec
until product scope is confirmed.
