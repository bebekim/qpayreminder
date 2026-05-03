# Feature: Confirm, reject, and undo allocations

## Why

AI proposals are not accounting truth until an authorized organization user
confirms them. Confirmation, rejection, and undo must be auditable,
idempotent, transactional, and role-gated.

This is the core trust boundary between AI assistance and accounting state.

## What the system should do

- Given a proposed allocation and an authorized owner/bookkeeper, confirmation
  should atomically mark the allocation confirmed and update invoice/payment
  state.
- Given a viewer, confirmation and rejection should be denied.
- Given the same confirmation request twice, the second request should be
  idempotent and should not double-apply payment amounts.
- Given a rejection, the allocation should be marked rejected with reason and
  event metadata.
- Given undo of a confirmation, the system should create a compensating event
  and recalculate invoice/payment state without deleting historical events.
- Given partial and split allocations, confirmation should update each affected
  invoice balance correctly.

## Data flow

```
allocation proposal + actor role + idempotency key
    -> confirm/reject/undo use case
    -> AllocationEvent + Payment/Invoice state update
```

Events:

- `ALLOCATION_PROPOSED`
- `ALLOCATION_CONFIRMED`
- `ALLOCATION_REJECTED`
- `CONFIRMATION_UNDONE`

Actor metadata:

- organization ID
- user ID
- role
- timestamp
- idempotency key
- optional reason

## Acceptance criteria

- [ ] Owner can confirm and reject proposed allocations.
- [ ] Bookkeeper can confirm and reject proposed allocations.
- [ ] Viewer cannot confirm, reject, or undo allocations.
- [ ] Confirmation is idempotent for the same allocation and idempotency key.
- [ ] Confirmation does not double-increment invoice `amount_paid`.
- [ ] Partial allocation changes invoice status to partial.
- [ ] Full allocation changes invoice status to paid and sets paid timestamp.
- [ ] Overpayment preserves unapplied balance/credit.
- [ ] Rejection preserves the original proposal and records a rejection event.
- [ ] Undo creates a compensating event and recalculates invoice status.
- [ ] All state changes happen in one transaction.
- [ ] Unit tests cover role denial, idempotent confirm, partial, full,
      overpayment, rejection, and undo.

## Defaults

- Owner and bookkeeper can confirm, reject, and undo allocations.
- Viewer cannot confirm, reject, or undo allocations.
- Rejection and undo accept free-text reason for MVA, with optional enum reason
  codes added later.
- Undo is disallowed after external accounting export until an export policy
  exists.

## Test plan

Expected test files:

- `tests/unit/application/test_confirm_allocations.py`
- `tests/unit/application/test_reject_allocations.py`
- `tests/unit/application/test_undo_confirmation.py`
- `tests/unit/application/test_allocation_authorization.py`
- `tests/integration/test_allocation_transactionality.py`

Expected commands:

```bash
uv run pytest tests/unit/application/test_confirm_allocations.py -q
uv run pytest tests/unit/application/test_reject_allocations.py -q
uv run pytest tests/unit/application/test_undo_confirmation.py -q
uv run pytest tests/unit/application/test_allocation_authorization.py -q
uv run pytest tests/integration/test_allocation_transactionality.py -q
uv run ruff check src tests
```

The transactionality test should prove a failed multi-invoice confirmation does
not partially update invoice/payment state.

## What could go wrong

- **Risk**: Confirm is not idempotent.
  **How we'd notice**: Repeated request doubles `amount_paid`.
  **Mitigation**: Idempotency key and allocation status checks in transaction.

- **Risk**: Undo deletes audit history.
  **How we'd notice**: Confirmation event disappears after undo.
  **Mitigation**: Use compensating events only.

- **Risk**: Role checks live only in web controllers.
  **How we'd notice**: Hermes or CLI can confirm as viewer.
  **Mitigation**: Enforce authorization in application use case as well as
  interface layer.

## Constraints

- Confirmation is organization-level canonical accounting state.
- User-level dashboard seen state is not accounting state.
- Use case returns DTOs, not ORM objects.
- Do not call AI providers during confirmation.
- Do not implement notification side effects in this spec.

## Open questions

- Should owner/bookkeeper permissions become configurable per organization after MVA?
- What structured reason codes should replace free text after initial use?
- What export policy should govern undo after downstream accounting export?

## Spike vs Feature

**Feature**. The PRD defines the behavior and invariants clearly.
