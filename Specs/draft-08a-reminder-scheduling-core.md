# Feature: Reminder scheduling core with fake call provider

State: draft

## Why

PayCall helps SMBs follow up on unpaid invoices without awkward manual chasing.
This split spec covers scheduling, state transitions, and fake-provider call
initiation. Live Vapi/Twilio behavior belongs in
`Specs/draft-08b-live-call-provider-integration.md`.

## What the system should do

- Given an unpaid invoice and callable customer, the system should schedule a
  reminder for a future time.
- Given a paid or cancelled invoice, the system should reject new reminder
  scheduling.
- Given a customer marked do-not-call, the system should reject voice call
  scheduling and initiation.
- Given a scheduled reminder due for execution, the worker should initiate the
  configured delivery channel through a fake provider port.
- Given a call initiation request from Hermes or UI, the system should return a
  plan unless explicit `CALL` tier confirmation is present.
- Given provider callback data, the system should update reminder/call status
  and preserve outcome metadata.

## Data flow

```text
invoice + customer + schedule request -> ReminderTask
    -> due reminder worker -> call provider port
    -> provider callback -> call outcome update
```

Reminder fields:

- invoice ID
- customer ID
- scheduled timestamp
- channel
- status: scheduled, in_progress, completed, failed, cancelled
- provider call/message ID
- duration/outcome if call
- notes/transcript summary if available

## Acceptance criteria

- [ ] Reminder scheduling rejects paid invoices.
- [ ] Reminder scheduling rejects cancelled invoices.
- [ ] Voice reminder scheduling rejects do-not-call customers.
- [ ] Scheduled time must be in the future.
- [ ] Call initiation is a `CALL` tier command and returns a plan without
      explicit confirmation.
- [ ] Confirmed call initiation records provider call ID and marks reminder in progress.
- [ ] Provider failure marks reminder failed without losing schedule/audit data.
- [ ] Provider completion records outcome and duration.
- [ ] Unit tests use fake provider and cover paid invoice, do-not-call, past
      schedule, plan-only call, confirmed call, failure callback, and completion
      callback.

## Test plan

Expected test files:

- `tests/unit/application/test_schedule_reminder.py`
- `tests/unit/application/test_initiate_call.py`
- `tests/unit/application/test_call_callbacks.py`
- `tests/unit/commands/test_call_tier.py`
- `tests/unit/infrastructure/test_fake_call_provider.py`

Expected commands:

```bash
uv run pytest tests/unit/application/test_schedule_reminder.py -q
uv run pytest tests/unit/application/test_initiate_call.py -q
uv run pytest tests/unit/application/test_call_callbacks.py -q
uv run pytest tests/unit/commands/test_call_tier.py -q
uv run pytest tests/unit/infrastructure/test_fake_call_provider.py -q
uv run ruff check src tests
```

No live Vapi/Twilio credentials should be needed.

## Defaults

- Voice-only fake provider for MVA scheduling.
- Email/SMS reminders are follow-up scope.
- Live calling-provider compliance remains follow-up scope.
- Reminder cadence is a single scheduled reminder at a user-selected future
  time for MVA; recurring cadence is follow-up scope.

## Constraints

- Australia/Sydney timezone rules apply for display and scheduling UX.
- Do not store full call recordings unless a later privacy/compliance spec
  explicitly permits it.
- The worker should re-check invoice state before initiating a call.

## Open questions

- Should reminders be organization-configurable by cadence and channel after MVA?

## Spike vs Feature

**Feature** after confirmation/payment state is reliable.
