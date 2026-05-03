# Feature: Invoice draft core, extraction, review, and creation

State: draft

## Why

PayCall starts from invoice records. Users need a low-friction way to register
invoices, then use those invoices as the basis for matching incoming payments
and scheduling reminders.

This split spec covers the provider-independent invoice draft core: web/manual
entry, fake extraction, review, duplicate detection, and invoice creation. Chat
uploads and BCC/forwarded email intake are covered separately in
`Specs/draft-03b-channel-email-invoice-intake.md`.

## What the system should do

- Given a supported invoice file uploaded through the web service, the system
  should store upload metadata and parse the file into structured invoice data.
- Given manual invoice entry, the system should use the same domain validation
  and invoice creation use case as uploaded invoices.
- Given extracted invoice data with required fields and sufficient confidence,
  the system should present a reviewable draft.
- Given extracted data that is incomplete or low confidence, the system should
  require user review and correction before creating an invoice.
- Given a confirmed invoice draft, the system should create or link a customer
  and create an invoice transactionally.
- Given a duplicate invoice number for the same customer/organization, the
  system should reject creation or surface the existing invoice.

Supported MVA formats:

- PDF
- PNG
- JPG/JPEG
- XLS/XLSX only if explicitly retained after review

## Data flow

```text
web/manual intake -> invoice draft creation -> document preprocessor
    -> fake extractor/provider port -> extracted invoice draft
    -> user review -> customer + invoice
```

Required extracted fields:

- invoice number
- total amount
- currency, fixed to AUD for MVA
- due date
- issuer or customer name sufficient for review

## Acceptance criteria

- [ ] Unsupported file types are rejected before parsing.
- [ ] Missing file, empty file, and unreadable file cases return user-safe errors.
- [ ] Web upload and manual invoice entry use the same invoice creation validation.
- [ ] Intake is idempotent by source upload ID plus attachment hash.
- [ ] Extracted draft stores source filename, extracted fields, confidence, and warnings.
- [ ] Missing invoice number, total amount, or due date prevents automatic invoice creation.
- [ ] Low confidence extraction creates a review-required draft.
- [ ] Confirming a valid draft creates exactly one customer if needed and one invoice.
- [ ] Duplicate invoice number for the same customer is rejected.
- [ ] Created invoice amount is immutable after creation.
- [ ] Unit tests mock the extractor and cover success, incomplete extraction,
      duplicate invoice, unsupported format, and manual entry.
- [ ] No live Anthropic/OpenAI call is required for unit tests.

## Defaults

- Retain source documents in local/dev storage for MVA with a storage port so
  production retention can be changed later.
- Require manual review when extractor confidence is below `0.85`.
- Exclude XLS/XLSX from first implementation unless current customer data proves
  Excel invoices are required.

## Test plan

Expected test files:

- `tests/unit/application/test_parse_invoice_document.py`
- `tests/unit/application/test_create_invoice_from_draft.py`
- `tests/unit/application/test_invoice_intake.py`
- `tests/unit/application/test_manual_invoice_entry.py`
- `tests/unit/infrastructure/test_document_preprocessor.py`

Expected commands:

```bash
uv run pytest tests/unit/application/test_parse_invoice_document.py -q
uv run pytest tests/unit/application/test_create_invoice_from_draft.py -q
uv run pytest tests/unit/application/test_invoice_intake.py -q
uv run pytest tests/unit/application/test_manual_invoice_entry.py -q
uv run pytest tests/unit/infrastructure/test_document_preprocessor.py -q
uv run ruff check src tests
```

Tests must use fake extractor/preprocessor fixtures. No provider credentials
should be required.

## What could go wrong

- **Risk**: AI extraction silently creates incorrect invoices.
  **How we'd notice**: Wrong amount or due date enters accounting flow.
  **Mitigation**: Use review-required drafts for low confidence and persist
  extractor warnings.

- **Risk**: Upload flow duplicates manual invoice logic.
  **How we'd notice**: Different validation behavior for manual vs uploaded
  invoices.
  **Mitigation**: Both flows call the same create-invoice use case.

## Constraints

- Domain and application use cases must not depend on Flask request objects.
- Provider-specific extraction belongs behind an extraction port.
- Unit tests must run without live AI credentials.
- Raw document retention policy must be explicit before production deployment.

## Open questions

- Should production retain source documents long-term, or only extracted
  metadata and audit traces?
- Is Excel invoice support required after the PDF/image MVA?

## Spike vs Feature

**Feature** once the domain core exists and the open questions above are
answered or explicitly defaulted.
