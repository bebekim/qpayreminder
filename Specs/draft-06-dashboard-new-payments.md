# Feature: Dashboard new payments and freshness

## Why

The PayCall dashboard should be noise-free and action-oriented. Users should
see only invoice-related payments requiring attention, not raw bank statements
or arbitrary "today" activity.

The PRD defines the key rule: dashboard "new payments" are proposed allocations
where `proposed_at > last_viewed_dashboard_at` for that user.

## What the system should do

- Given proposed allocations, the dashboard should show payments that require
  user action.
- Given a user's `last_viewed_dashboard_at`, the dashboard should calculate
  "new" from proposal time, not bank posted time or first seen time.
- Given multiple users in the same organization, each user should have their
  own seen state.
- Given organization-level confirmation, the allocation should no longer appear
  as needing confirmation for any user.
- Given sync state, the dashboard should display last synced time and sync
  status.
- Given more than 50 unreviewed items, the dashboard should show a catch-up
  banner.

## Data flow

```
Allocation(status=PROPOSED) + UserDashboardState + SyncRun
    -> dashboard query DTO -> web/Hermes/channel response
```

Display fields:

- new payment count
- total proposed amount in AUD
- customer name
- invoice number(s)
- allocated amount(s)
- payment received time in user-local timezone
- optional confidence/evidence hint
- status: needs confirmation
- last synced timestamp and status

## Acceptance criteria

- [ ] Dashboard never displays unrelated raw bank transactions.
- [ ] New count uses `allocation.status = PROPOSED` and
      `allocation.proposed_at > user.last_viewed_dashboard_at`.
- [ ] If `last_viewed_dashboard_at` is null, all proposed allocations for the
      organization are considered new for that user.
- [ ] Marking dashboard viewed updates only the user's seen timestamp.
- [ ] Marking dashboard viewed does not confirm, reject, or mutate allocation
      accounting state.
- [ ] Confirmed or rejected allocations are excluded from "needs confirmation".
- [ ] Catch-up list is sorted by oldest unconfirmed proposal first.
- [ ] Dashboard sync status is derived from stored sync runs, not provider API
      calls.
- [ ] Unit tests cover null last-viewed timestamp, per-user seen state,
      confirmed exclusion, rejected exclusion, catch-up sorting, and sync status.

## Defaults

- The UI should call an explicit `dashboard.mark-viewed` action after successful
  render; a failed or partial render must not mark items viewed.
- Sync freshness uses the same thresholds as bank ingestion core: `OK <= 5
  minutes`, `DELAYED > 5 minutes and <= 60 minutes`, and `FAILED` after latest
  sync failure or no successful sync for more than 60 minutes.
- Show confidence as an evidence-only label for MVA, not a raw numeric score.

## Test plan

Expected test files:

- `tests/unit/application/test_get_dashboard_new_payments.py`
- `tests/unit/application/test_mark_dashboard_viewed.py`
- `tests/unit/application/test_sync_freshness.py`
- `tests/unit/interface/test_dashboard_dto.py`

Expected commands:

```bash
uv run pytest tests/unit/application/test_get_dashboard_new_payments.py -q
uv run pytest tests/unit/application/test_mark_dashboard_viewed.py -q
uv run pytest tests/unit/application/test_sync_freshness.py -q
uv run pytest tests/unit/interface/test_dashboard_dto.py -q
uv run ruff check src tests
```

Dashboard tests should use repositories/fakes seeded with stored sync state.
They must not require a bank provider fake unless testing stored sync data.

## What could go wrong

- **Risk**: "New" is based on bank `posted_at`.
  **How we'd notice**: Old bank transactions newly proposed by AI are not shown
  as new.
  **Mitigation**: Test proposed-at behavior explicitly.

- **Risk**: Per-user seen state changes org-level accounting truth.
  **How we'd notice**: Viewing dashboard removes proposals for other users or
  changes status.
  **Mitigation**: Separate dashboard state from allocation state.

- **Risk**: Dashboard calls bank provider for freshness.
  **How we'd notice**: Provider fake/mock is required for dashboard unit tests.
  **Mitigation**: Dashboard reads persisted `SyncRun` only.

## Constraints

- Store timestamps in UTC.
- Display timestamps in Australia/Sydney by default.
- Dashboard read model returns DTOs only.
- No live bank provider calls in dashboard use cases.
- UI details can be server-rendered or API-backed; behavior is the contract.

## Open questions

- Should the catch-up banner threshold remain 50 items after usability testing?

## Spike vs Feature

**Feature**. The PRD defines the behavior clearly enough for TDD.
