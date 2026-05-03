# Feature: Live bank provider integration

State: draft

## Why

The bank ingestion core must eventually connect to a real provider, but the
provider decision, webhook shape, sandbox behavior, and production verification
should not block the fake-provider ingestion contract.

## What the system should do

- Given a selected bank provider, the system should connect provider auth,
  account listing, transaction sync, and webhook/callback handling through the
  bank provider port.
- Given sandbox/staging provider credentials, integration tests should verify
  consent/callback and transaction import behavior.
- Given provider webhook events, the adapter should map them into the shared
  ingestion use case without mutating domain objects directly.

## Candidate providers

- Basiq
- Wych
- Fake/dev provider for local use
- Another provider if selected before implementation

## Acceptance criteria

- [ ] Provider decision is documented before implementation.
- [ ] Provider adapter implements the same port used by fake-provider tests.
- [ ] Sandbox/staging tests are separate from unit tests.
- [ ] Webhook signature verification is implemented before accepting provider events.
- [ ] Provider payloads are stored as raw immutable evidence.
- [ ] Provider failures map to sync run failure/delay state.

## Test plan

Expected test files:

- `tests/integration/test_bank_provider_consent.py`
- `tests/integration/test_bank_provider_webhooks.py`
- `tests/integration/test_bank_provider_transaction_sync.py`

Expected commands:

```bash
uv run pytest tests/integration/test_bank_provider_consent.py -q
uv run pytest tests/integration/test_bank_provider_webhooks.py -q
uv run pytest tests/integration/test_bank_provider_transaction_sync.py -q
uv run ruff check src tests
```

These tests require sandbox/staging credentials and must not run in the default
unit test suite.

## Open questions

- Which provider is first in the new repo: Basiq, Wych, or another provider?
- Which provider events are required for MVA freshness guarantees?
- What sandbox data set should be used for repeatable integration tests?

## Spike vs Feature

**Feature** after provider selection; otherwise keep as draft.
