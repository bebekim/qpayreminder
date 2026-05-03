# Feature: PayCall domain core

## Why

The current repo has domain-looking modules, but the real behavior is spread
across Flask routes, SQLAlchemy models, service modules, and provider-specific
code. A new repo needs a framework-free domain core before web routes, CLI
commands, or Hermes skills are implemented.

This domain core is the contract for invoice-only accounts receivable behavior:
money, invoices, bank transactions, AI proposals, allocations, confirmation,
and audit events.

## What the system should do

- Given an invoice, the system should preserve the original invoice amount and
  compute balance from confirmed allocations/payments.
- Given a bank transaction, the system should preserve raw provider data as
  immutable evidence.
- Given a proposed match, the system should represent it as an allocation
  proposal that is not accounting truth until confirmed.
- Given a confirmed allocation, the system should update accounting state at
  organization level, not per-user level.
- Given a rejected allocation, the system should preserve the rejection as an
  event and keep the source transaction available for future proposals.
- Given an undo action, the system should create a compensating event rather
  than deleting historical confirmation state.
- Given an AI decision, the system should persist governance metadata:
  model identifier, prompt/template version, feature schema version, policy
  version, decision trace ID, normalized input hash, confidence score, and
  explanation/evidence.

Domain concepts:

- `Organization`
- `OrganizationMembership`
- `User`
- `Customer`
- `Invoice`
- `BankAccount`
- `BankTransaction`
- `Payment`
- `Allocation`
- `AllocationEvent`
- `SyncRun`
- `AIDecisionEnvelope`
- Value objects: `Money`, `PhoneNumber`, `EmailAddress`, `DueDate`,
  `MatchConfidence`, `Timezone`

## Data flow

```
provider transaction -> BankTransaction -> AI proposal -> Allocation
    -> confirmation/rejection/undo event -> invoice/payment state
```

Required fields:

- Money: amount as decimal, currency fixed to AUD.
- Bank transaction: provider ID, dedupe fingerprint, amount, direction,
  description, counterparty, posted timestamp, first-seen timestamp, raw payload.
- Invoice: organization/customer ownership, invoice number, issue date, due
  date, original amount, status.
- Allocation: transaction ID, invoice ID, customer ID, allocated amount,
  status, proposed/confirmed/rejected timestamps.
- Payment: settlement state derived from confirmed allocations or explicit
  manual payments, not from raw bank transactions or unconfirmed proposals.

Known quirks:

- Basiq or other bank providers may deliver duplicate or revised transactions.
- `posted_at` and `first_seen_at` are different business timestamps.
- Partial, split, and overpayments are in scope.
- Cross-customer allocations are explicitly disallowed.

## Acceptance criteria

- [ ] Domain objects do not import Flask, SQLAlchemy, provider SDKs, or web
      request/session objects.
- [ ] `Money` rejects non-AUD currencies for MVA behavior.
- [ ] Allocation validation rejects cross-customer allocation.
- [ ] Allocation validation rejects allocated sum greater than payment amount
      plus configured tolerance.
- [ ] Overpayment is represented as preserved credit/unapplied balance, not
      discarded.
- [ ] User roles are represented as organization membership roles, not global
      user roles.
- [ ] Payment state is derived only from confirmed allocations or manual
      payments, not raw bank transactions or proposals.
- [ ] Confirmation is idempotent.
- [ ] Undo creates a compensating event and does not delete the original event.
- [ ] Invoice status recalculation is deterministic after confirmation and
      undo.
- [ ] AI decision metadata is required for AI-generated allocation proposals.
- [ ] Unit tests cover partial payment, split payment, overpayment, rejection,
      and undo.

## Test plan

Expected test files:

- `tests/unit/domain/test_money.py`
- `tests/unit/domain/test_invoice.py`
- `tests/unit/domain/test_allocation.py`
- `tests/unit/domain/test_ai_decision_envelope.py`
- `tests/unit/domain/test_clean_architecture.py`

Expected commands:

```bash
uv run pytest tests/unit/domain -q
uv run ruff check src tests
```

Architecture checks should fail if domain code imports Flask, SQLAlchemy,
provider SDKs, request/session objects, or repository implementations.

## What could go wrong

- **Risk**: ORM models become the domain model again.
  **How we'd notice**: Domain imports SQLAlchemy or repository code.
  **Mitigation**: Add architecture tests that fail on forbidden imports.

- **Risk**: User-level "seen" state leaks into accounting state.
  **How we'd notice**: Marking dashboard viewed changes allocation status.
  **Mitigation**: Keep per-user dashboard state separate from org-level
  allocation state.

- **Risk**: AI confidence is treated as permission to mutate accounting truth.
  **How we'd notice**: High-confidence proposal confirms without policy.
  **Mitigation**: Keep proposal and confirmation as separate domain actions.

## Constraints

- AUD only.
- Australia/Sydney is the default display timezone, but timestamps are stored in
  UTC.
- Domain layer must be deterministic and provider-independent.
- No external API calls from domain code.
- Do not design for multi-currency in this spec.
- MVA behavior may auto-propose AI matches but must not auto-confirm them.

## Open questions

- Is customer identity an inferred attribute of a bank transaction, or only of
  an allocation proposal?
- What tolerance should be used for fees and near matches in MVA?

## Spike vs Feature

**Feature**. The behavior is known from the PRD. Implementation should be
test-driven and framework-free.
