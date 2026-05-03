# Feature: Live call provider integration and compliance

State: draft

## Why

Production reminder calls require provider integration, consent/compliance
rules, retry policy, privacy decisions, and callback handling. Those concerns
should not block the fake-provider scheduling core.

## What the system should do

- Given a selected call provider, the system should initiate calls through the
  same provider port used by the fake-provider scheduling core.
- Given provider callbacks/webhooks, the adapter should update reminder/call
  status using the shared callback use case.
- Given Australian reminder-call policy, the system should enforce allowed
  calling windows, retry limits, opt-out, and consent requirements before live
  calls.
- Given provider recordings or transcripts, the system should store only data
  permitted by the privacy/compliance policy.

## Candidate providers

- Vapi
- Twilio
- Another provider selected before implementation

## Acceptance criteria

- [ ] Provider decision is documented before implementation.
- [ ] Allowed calling hours for Australian SMB debt reminders are documented and enforced.
- [ ] Retry cadence and maximum attempts are documented and enforced.
- [ ] Opt-out/do-not-call behavior is enforced before provider calls.
- [ ] Provider callback signature verification is implemented before accepting callbacks.
- [ ] Provider payload compatibility is covered by sandbox/staging tests.
- [ ] Recording/transcript retention policy is explicit.

## Test plan

Expected test files:

- `tests/integration/test_call_provider_initiation.py`
- `tests/integration/test_call_provider_callbacks.py`
- `tests/unit/application/test_calling_policy.py`

Expected commands:

```bash
uv run pytest tests/unit/application/test_calling_policy.py -q
uv run pytest tests/integration/test_call_provider_initiation.py -q
uv run pytest tests/integration/test_call_provider_callbacks.py -q
uv run ruff check src tests
```

Integration tests require sandbox/staging provider configuration and must not
run in the default unit test suite.

## Open questions

- What are the allowed calling hours for Australian SMB debt reminders?
- What retry policy is acceptable for first production use?
- Are SMS or email reminders in the first new-repo MVA?
- What call recording/transcript retention policy is acceptable?

## Spike vs Feature

**Feature** after provider and compliance decisions are made; otherwise keep as
draft.
