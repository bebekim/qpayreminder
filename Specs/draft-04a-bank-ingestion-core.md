# Feature: Bank ingestion core with fake provider

State: draft

## Why

PayCall's dashboard and matching workflow depend on fresh incoming payments
from connected bank accounts. This split spec covers the provider-agnostic
application contract with a fake/dev provider. Live Basiq/Wych behavior belongs
in `Specs/draft-04b-live-bank-provider-integration.md`.

## What the system should do

- Given an organization with a bank connection, the system should ingest
  provider transactions into immutable raw transaction records.
- Given duplicate provider transaction IDs or dedupe fingerprints, the system
  should not create duplicate raw transactions.
- Given a sync run, the system should record start time, finish time, status,
  provider, cursor/window, imported count, skipped duplicate count, and error
  details if any.
- Given a dashboard request, the dashboard should read only database state and
  should not call bank APIs.
- Given a provider failure, the system should keep previous transactions and
  mark sync status as delayed or failed.

## Data flow

```text
scheduled job/login trigger -> bank provider port -> raw provider payload
    -> BankTransaction records + SyncRun -> matching pipeline
```

Provider transaction fields needed:

- provider transaction ID
- account ID
- amount
- direction: credit/debit
- description
- counterparty if available
- transaction date
- posted timestamp if available
- raw payload

## Acceptance criteria

- [ ] Bank provider is represented by an application port/interface.
- [ ] Provider details do not leak into domain objects.
- [ ] Raw bank transaction payload is persisted immutably.
- [ ] Ingesting the same provider transaction twice is idempotent.
- [ ] Sync runs record success, delayed, and failed outcomes.
- [ ] Dashboard query path does not call the provider port.
- [ ] Sync freshness DTO reports last successful sync timestamp and status.
- [ ] Unit tests cover first sync, incremental sync, duplicate transaction,
      provider failure, and empty result.
- [ ] Integration tests can run against a fake provider without network access.

## Test plan

Expected test files:

- `tests/unit/application/test_sync_bank_transactions.py`
- `tests/unit/domain/test_bank_transaction.py`
- `tests/unit/infrastructure/test_fake_bank_provider.py`
- `tests/integration/test_bank_sync_repository.py`

Expected commands:

```bash
uv run pytest tests/unit/application/test_sync_bank_transactions.py -q
uv run pytest tests/unit/domain/test_bank_transaction.py -q
uv run pytest tests/unit/infrastructure/test_fake_bank_provider.py -q
uv run pytest tests/integration/test_bank_sync_repository.py -q
uv run ruff check src tests
```

Integration tests should use a fake provider and local test database only.

## Defaults

- First implementation uses a fake/dev provider.
- Sync freshness is `OK <= 5 minutes`, `DELAYED > 5 minutes and <= 60 minutes`,
  and `FAILED` after latest sync failure or no successful sync for more than 60
  minutes.
- Webhook ingestion and polling share one ingestion use case unless the live
  provider integration spec proves that they need separate adapters.

## Constraints

- AUD-only MVA.
- Raw bank data is immutable.
- No direct provider calls from dashboard read use cases.
- Live provider tests are out of scope.
- Background worker choice must not leak into domain logic.

## Open questions

- Should the fake/dev provider simulate pending/revised transactions in MVA, or
  only duplicate/failure cases?

## Spike vs Feature

**Feature** after domain core exists.
