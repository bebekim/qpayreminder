# Feature: Channel and email invoice intake adapters

State: draft

## Why

PayCall should accept invoices through channels users already use: Hermes chat
channels and BCC/forwarded email. This spec covers interface adapters only. The
shared draft extraction, review, and invoice creation behavior belongs in
`Specs/draft-03a-invoice-draft-core.md`.

## What the system should do

- Given an invoice file uploaded through WhatsApp, Telegram, or another
  Hermes-connected channel, Hermes should route the attachment to the shared
  invoice draft creation use case.
- Given an invoice received by BCC/forwarded email, the email adapter should
  extract attachments and message metadata, then route them to the shared
  invoice draft creation use case.
- Given sender identity and message metadata, the adapter should resolve the
  organization/user or reject the intake as ambiguous.
- Given duplicate channel message IDs or email IDs plus attachment hash, the
  adapter should behave idempotently.

## Data flow

```text
Hermes channel/email provider -> intake adapter -> invoice draft creation use case
```

Intake metadata:

- source channel: whatsapp, telegram, email, or other
- source message/email ID for idempotency
- sender identity and resolved organization/user if available
- original filename and content type
- email subject, from, to, cc/bcc metadata where available

## Acceptance criteria

- [ ] Hermes channel upload creates the same invoice draft type as web upload.
- [ ] BCC/forwarded email intake creates the same invoice draft type as web upload.
- [ ] Adapter tests use fake channel/email provider payloads.
- [ ] Ambiguous sender-to-organization mapping is rejected with a user-safe error.
- [ ] Intake is idempotent by source message/email ID plus attachment hash.
- [ ] Interface adapters do not duplicate invoice validation logic.

## Test plan

Expected test files:

- `tests/unit/interface/test_hermes_invoice_upload_adapter.py`
- `tests/unit/interface/test_email_invoice_intake_adapter.py`

Expected commands:

```bash
uv run pytest tests/unit/interface/test_hermes_invoice_upload_adapter.py -q
uv run pytest tests/unit/interface/test_email_invoice_intake_adapter.py -q
uv run ruff check src tests
```

## Constraints

- Chat-channel and email-provider specifics belong in interface adapters.
- No live email, WhatsApp, Telegram, or Hermes provider credentials in unit tests.
- The invoice draft core must exist before this adapter spec is implemented.

## Open questions

- What inbound email provider should handle BCC/forwarded invoice intake?
- How should the service map BCC sender/recipient identity to organization when
  the sender has multiple organizations?
- Which Hermes channels are in MVA?

## Spike vs Feature

**Feature** after channel/provider assumptions are decided.
