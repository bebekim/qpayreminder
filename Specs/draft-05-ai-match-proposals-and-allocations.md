# Feature: AI match proposals and allocations

## Why

PayCall's core value is filtering bank noise and surfacing only invoice-relevant
payments. AI may propose dedupe, matching, and allocation decisions, but hard
business invariants must remain deterministic and non-overridable.

This spec defines proposal behavior before accounting confirmation.

## What the system should do

- Given unmatched incoming credit transactions, the system should compare them
  against open invoices for the same organization.
- Given a likely invoice payment, the system should create one or more
  allocation proposals with confidence and evidence.
- Given a transaction that does not relate to an invoice, the system should not
  surface it on the invoice-only dashboard.
- Given partial payment, split payment, or overpayment scenarios, the system
  should preserve the correct allocation proposal shape.
- Given multiple plausible matches, the system should surface alternatives or
  mark the proposal as requiring review.
- Given any AI proposal, the system should persist an AI decision envelope with
  trace metadata and normalized input hash.

Hard invariants:

- A single payment cannot allocate across customers.
- Currency must be AUD.
- Allocated sum cannot exceed transaction amount plus configured tolerance.
- Overpayments must be preserved as credit or unapplied balance.
- AI cannot bypass these invariants.

## Data flow

```
unmatched credit transactions + open invoices -> deterministic features
    -> AI matcher port -> decision envelope -> allocation proposals
    -> dashboard/review workflow
```

Features sent to AI should include:

- transaction amount, description, counterparty, posted/first-seen timestamps
- candidate invoice numbers, customer names, balances, due dates
- organization policy/tolerance version
- no unrelated raw bank statement rows beyond candidate context

## Acceptance criteria

- [ ] Matching use case considers only organization-scoped invoices and
      transactions.
- [ ] Debit transactions are ignored for payment matching.
- [ ] Exact invoice number + exact balance creates a high-confidence proposal.
- [ ] Exact amount only with one candidate creates a medium-confidence proposal.
- [ ] Multiple exact amount candidates require review and do not auto-resolve.
- [ ] Partial payment creates an allocation for less than invoice balance.
- [ ] Split payment can allocate one transaction to multiple invoices for the
      same customer.
- [ ] Cross-customer split is rejected by deterministic validation even if AI
      suggests it.
- [ ] Every AI-created proposal stores model, prompt/template version, feature
      schema version, policy version, decision trace ID, normalized input hash,
      confidence score, and evidence.
- [ ] Unit tests use a fake AI matcher and cover exact, partial, split,
      overpayment, no-match, and cross-customer rejection cases.

## Defaults

- Deterministic exact matches may bypass live AI, but they must still create a
  governance envelope with `model=deterministic-rules`, a policy version, a
  feature schema version, and an explanation/evidence trace.
- Confidence bands are `high >= 0.90`, `medium >= 0.70 and < 0.90`, and
  `review < 0.70`.
- First prompt/template version naming scheme is `paycall-match-v1`.

## Test plan

Expected test files:

- `tests/unit/application/test_propose_matches_and_allocations.py`
- `tests/unit/domain/test_allocation_invariants.py`
- `tests/unit/domain/test_ai_decision_envelope.py`
- `tests/unit/infrastructure/test_fake_ai_matcher.py`

Expected commands:

```bash
uv run pytest tests/unit/application/test_propose_matches_and_allocations.py -q
uv run pytest tests/unit/domain/test_allocation_invariants.py -q
uv run pytest tests/unit/domain/test_ai_decision_envelope.py -q
uv run pytest tests/unit/infrastructure/test_fake_ai_matcher.py -q
uv run ruff check src tests
```

Tests must use deterministic fake AI responses. Live prompt quality, model
behavior, and evals belong in a later AI-provider spec.

## What could go wrong

- **Risk**: AI sees too much irrelevant bank data.
  **How we'd notice**: Prompt includes broad raw bank statement context.
  **Mitigation**: Candidate generation should reduce context before AI call.

- **Risk**: False positives become accounting truth.
  **How we'd notice**: Proposal creation marks invoices paid.
  **Mitigation**: Keep proposals separate from confirmations.

- **Risk**: AI governance data is optional.
  **How we'd notice**: Proposal records without model/policy trace.
  **Mitigation**: Make decision envelope required for AI proposals.

## Constraints

- AI provider is behind a port and mocked in unit tests.
- Domain invariants are deterministic and tested without AI.
- No cross-customer allocations.
- No multi-currency support.
- Do not implement dashboard UI in this spec.

## Open questions

- Should live AI be introduced before or after the first fake-AI matcher MVA?

## Spike vs Feature

**Feature** using a fake AI matcher. Live prompt quality and evals should be a
separate spike.
