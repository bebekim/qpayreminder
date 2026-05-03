# PayCall Feature Parity Inventory

Source spec: `Specs/00-feature-parity-inventory.md`

This inventory captures observable behavior in the current PaymentReminder repo
so a new PayCall repo can migrate the right behavior without copying accidental
implementation details.

Status labels:

- `implemented`: present in code and covered by at least one route, service,
  domain object, or test.
- `partial`: present, but incomplete, inconsistent with the target PRD, or not
  fully wired through the product flow.
- `target-only`: specified in docs/specs, but not implemented as user-facing
  behavior.
- `legacy-review`: inherited ToodlelooMe/payment-reminder behavior that may be
  useful but should not be ported blindly.
- `drop`: should not be ported to the new PayCall repo unless explicitly
  re-approved.

Verification modes:

- `mocked`: unit tests or fake adapters are enough for migration parity.
- `sandbox`: provider sandbox access is needed.
- `staging`: deployed staging plus webhook/redirect URLs are needed.
- `live`: real provider access or real-world transactions/calls are needed.
- `n/a`: no external service dependency.

## Authentication and Onboarding

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Email/password signup and login. | implemented | mocked | `app/interfaces/web/auth.py`, `app/services/user_service.py`, `tests/unit/test_auth_service.py` | `Specs/12-in-house-auth-platform-contract.md` |
| Google OAuth login and account creation. | implemented | sandbox | `app/interfaces/web/auth.py`, `app/infrastructure/google_oauth.py`, `tests/unit/test_google_oauth.py` | `Specs/12-in-house-auth-platform-contract.md` |
| Safe redirect handling after login. | implemented | mocked | `app/interfaces/web/auth.py`, `app/services/security_service.py` | `Specs/12-in-house-auth-platform-contract.md` |
| Business onboarding captures business name and ABN. | implemented | mocked | `app/interfaces/web/onboarding.py`, `app/infrastructure/database/models.py`, `tests/unit/test_onboarding.py` | `Specs/12-in-house-auth-platform-contract.md` |
| Bank-details onboarding captures BSB/account metadata. | implemented | mocked | `app/interfaces/web/onboarding.py`, `app/infrastructure/database/models.py`, `tests/unit/test_onboarding.py` | `Specs/draft-04a-bank-ingestion-core.md` |
| Reusable in-house auth platform contract. | target-only | n/a | `Specs/12-in-house-auth-platform-contract.md`, `docs/auth-platform-direction.md` | `Specs/12-in-house-auth-platform-contract.md` |

## Organization, Users, Roles, and Permissions

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| User model has an `org_role` field with owner/bookkeeper/viewer intent. | partial | mocked | `app/infrastructure/database/models.py`, `docs/PRD_PayCall.md` | `Specs/01-paycall-domain-core.md` |
| Multi-user organizations with membership roles. | target-only | n/a | `docs/PRD_PayCall.md`, `Specs/01-paycall-domain-core.md` | `Specs/01-paycall-domain-core.md` |
| Authorization checks on invoice/client ownership. | partial | mocked | `app/interfaces/web/invoices.py`, `tests/unit/test_invoices_routes.py` | `Specs/01-paycall-domain-core.md` |
| Role-based confirmation and rejection permissions. | target-only | n/a | `docs/PRD_PayCall.md`, `Specs/draft-07-confirm-reject-undo-allocations.md` | `Specs/draft-07-confirm-reject-undo-allocations.md` |

## Client and Customer Management

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Create, list, view, edit, and soft-delete clients. | implemented | mocked | `app/interfaces/web/invoices.py`, `app/services/invoice_management/client_service.py`, `app/domain/client.py`, `tests/unit/test_client_model.py` | `Specs/01-paycall-domain-core.md` |
| Client phone and email validation. | implemented | mocked | `app/domain/client.py`, `tests/unit/test_client_model.py` | `Specs/01-paycall-domain-core.md` |
| Do-not-call flag blocks reminder scheduling. | implemented | mocked | `app/domain/client.py`, `app/services/invoice_management/reminder_service.py`, `tests/unit/test_reminder_task_model.py` | `Specs/draft-08a-reminder-scheduling-core.md` |
| Customer identity as organization-level accounting entity. | partial | mocked | `app/domain/client.py`, `app/infrastructure/database/models.py`, `Specs/01-paycall-domain-core.md` | `Specs/01-paycall-domain-core.md` |

## Invoice Creation, Upload, Extraction, and Review

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Manual invoice creation with client, invoice number, amount, due date, and currency. | implemented | mocked | `app/interfaces/web/invoices.py`, `app/services/invoice_management/invoice_service.py`, `app/domain/invoice.py`, `tests/unit/test_invoice_model.py` | `Specs/01-paycall-domain-core.md` |
| Invoice listing, detail view, and due-date editing. | implemented | mocked | `app/interfaces/web/invoices.py`, `tests/unit/test_invoices_routes.py` | `Specs/01-paycall-domain-core.md` |
| Invoice cancellation before payment. | implemented | mocked | `app/services/invoice_management/invoice_service.py`, `app/domain/invoice.py` | `Specs/01-paycall-domain-core.md` |
| Upload invoice file through web UI. | implemented | mocked | `app/interfaces/web/invoice_upload.py`, `tests/unit/test_invoice_upload_routes.py` | `Specs/draft-03a-invoice-draft-core.md` |
| OCR/extraction from PDF/image/Excel through preprocess and vision ports. | partial | mocked/sandbox | `app/application/use_cases/parse_invoice_document.py`, `app/application/ports/vision_extraction.py`, `app/infrastructure/adapters/vision_extraction.py`, `tests/unit/application/test_parse_invoice_document.py` | `Specs/draft-03a-invoice-draft-core.md` |
| Review extracted upload and confirm into an invoice. | implemented | mocked | `app/interfaces/web/invoice_upload.py`, `app/domain/uploaded_invoice.py`, `tests/unit/test_uploaded_invoice_entity.py` | `Specs/draft-03a-invoice-draft-core.md` |
| Upload invoice via Hermes channels such as WhatsApp or Telegram. | target-only | n/a | `Specs/draft-03b-channel-email-invoice-intake.md`, `Specs/02-hermes-command-contract.md` | `Specs/draft-03b-channel-email-invoice-intake.md` |
| BCC or forward invoice email intake. | target-only | n/a | `Specs/draft-03b-channel-email-invoice-intake.md` | `Specs/draft-03b-channel-email-invoice-intake.md` |

## Payment Recording and Invoice Status

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Manual payment recording against an invoice. | implemented | mocked | `app/interfaces/web/invoices.py`, `app/services/invoice_management/payment_service.py`, `app/domain/payment.py`, `tests/unit/test_payment_service.py` | `Specs/01-paycall-domain-core.md` |
| Invoice status changes from pending to partial or paid from payments. | implemented | mocked | `app/domain/invoice.py`, `app/services/invoice_management/payment_service.py`, `tests/unit/test_invoice_model.py` | `Specs/01-paycall-domain-core.md` |
| Payment deletion recalculates invoice paid state. | implemented | mocked | `app/services/invoice_management/payment_service.py` | `needs-spec` |
| Overpayment is allowed, but preserved credit/unapplied balance is not explicit. | partial | mocked | `app/services/invoice_management/payment_service.py`, `docs/PRD_PayCall.md`, `Specs/01-paycall-domain-core.md` | `Specs/01-paycall-domain-core.md` |
| Payment state derived only from confirmed allocations/manual payments. | partial | mocked | `app/services/accounts_receivable/invoice_matcher.py`, `Specs/01-paycall-domain-core.md` | `Specs/01-paycall-domain-core.md` |

## Bank Connection, Transaction Ingestion, and Reconciliation

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Basiq user creation and consent URL flow. | implemented | sandbox | `app/services/accounts_receivable/basiq_service.py`, `app/interfaces/web/basiq.py`, `tests/unit/test_basiq_service.py` | `Specs/draft-04b-live-bank-provider-integration.md` |
| Basiq connection callback syncs connections and accounts. | implemented | sandbox/staging | `app/interfaces/web/basiq.py`, `app/services/accounts_receivable/basiq_service.py` | `Specs/draft-04b-live-bank-provider-integration.md` |
| Bank account listing and primary-account selection. | implemented | mocked | `app/interfaces/web/basiq.py`, `app/infrastructure/database/models.py` | `Specs/draft-04a-bank-ingestion-core.md` |
| Manual transaction sync. | implemented | sandbox | `app/interfaces/web/basiq.py`, `app/services/accounts_receivable/basiq_service.py`, `tests/unit/test_basiq_service.py` | `Specs/draft-04a-bank-ingestion-core.md` |
| Basiq webhook verification and event processing. | implemented | staging | `app/interfaces/web/basiq.py`, `app/services/accounts_receivable/basiq_service.py`, `tests/integration/test_basiq_integration.py` | `Specs/draft-04b-live-bank-provider-integration.md` |
| Raw bank transaction persistence with provider IDs and payload details. | implemented | mocked | `app/infrastructure/database/models.py`, `tests/unit/test_basiq_service.py` | `Specs/01-paycall-domain-core.md` |
| Sync freshness target of five minutes and delayed/failed UX. | target-only | staging | `docs/PRD_PayCall.md`, `Specs/draft-06-dashboard-new-payments.md` | `Specs/draft-06-dashboard-new-payments.md` |
| Wych production connector abstraction. | target-only | n/a | User architecture notes in conversation, `Specs/draft-04b-live-bank-provider-integration.md` | `Specs/draft-04b-live-bank-provider-integration.md` |

## AI Match Proposal, Allocation, Confirmation, Rejection, and Undo

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Rule-based bank transaction to invoice matching by invoice number, client name, exact amount, and tolerance. | implemented | mocked | `app/services/accounts_receivable/invoice_matcher.py`, `tests/unit/test_basiq_service.py` | `Specs/draft-05-ai-match-proposals-and-allocations.md` |
| Manual transaction-to-invoice matching. | implemented | mocked | `app/services/accounts_receivable/invoice_matcher.py`, `app/interfaces/web/basiq.py` | `Specs/draft-07-confirm-reject-undo-allocations.md` |
| Domain allocation object and allocation event audit models. | partial | mocked | `app/domain/allocation.py`, `app/domain/allocation_event.py`, `tests/unit/test_paycall_phase2_models.py` | `Specs/01-paycall-domain-core.md` |
| AI decision governance envelope. | partial | mocked | `app/domain/decision_envelope.py`, `docs/PRD_PayCall.md`, `Specs/01-paycall-domain-core.md` | `Specs/01-paycall-domain-core.md` |
| Allocation proposal separate from accounting truth. | partial | mocked | `app/infrastructure/database/models.py`, `tests/unit/test_paycall_phase2_models.py`, `Specs/01-paycall-domain-core.md` | `Specs/draft-05-ai-match-proposals-and-allocations.md` |
| User confirmation and rejection workflow for proposed allocations. | partial | mocked | `app/infrastructure/database/models.py`, `tests/unit/test_paycall_phase2_models.py`, `Specs/draft-07-confirm-reject-undo-allocations.md` | `Specs/draft-07-confirm-reject-undo-allocations.md` |
| Undo creates compensating event rather than deleting history. | target-only | n/a | `docs/PRD_PayCall.md`, `Specs/01-paycall-domain-core.md`, `Specs/draft-07-confirm-reject-undo-allocations.md` | `Specs/draft-07-confirm-reject-undo-allocations.md` |
| AI is the final decision-maker for matching. | target-only | sandbox | `docs/PRD_PayCall.md`, `docs/ARCHITECTURE_SUMMARY_PayCall.md` | `Specs/draft-05-ai-match-proposals-and-allocations.md` |

## Dashboard Freshness and New Payments

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Main dashboard exists for authenticated users. | implemented | mocked | `app/interfaces/web/main.py`, `app/templates/dashboard.html`, `tests/e2e/playwright/test_dashboard.py` | `Specs/draft-06-dashboard-new-payments.md` |
| Invoice dashboard shows summary, overdue invoices, pending invoices, and outstanding AUD. | implemented | mocked | `app/interfaces/web/invoices.py`, `app/services/invoice_management/invoice_service.py`, `app/templates/invoices/dashboard.html` | `Specs/draft-06-dashboard-new-payments.md` |
| User `last_viewed_dashboard_at` field exists. | partial | mocked | `app/infrastructure/database/models.py`, `docs/PRD_PayCall.md` | `Specs/draft-06-dashboard-new-payments.md` |
| "New payments" equals proposed allocations after last dashboard view. | target-only | mocked | `docs/PRD_PayCall.md`, `Specs/draft-06-dashboard-new-payments.md` | `Specs/draft-06-dashboard-new-payments.md` |
| Sync status badge and last-synced header. | target-only | staging | `docs/PRD_PayCall.md`, `Specs/draft-06-dashboard-new-payments.md` | `Specs/draft-06-dashboard-new-payments.md` |
| Catch-up mode and high-volume banner. | target-only | mocked | `docs/PRD_PayCall.md`, `Specs/draft-06-dashboard-new-payments.md` | `Specs/draft-06-dashboard-new-payments.md` |

## Reminder Scheduling, Voice Calls, SMS/Email, and Outcomes

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Reminder domain tracks scheduled, calling, completed, failed, and cancelled states. | implemented | mocked | `app/domain/reminder.py`, `tests/unit/test_reminder_task_model.py` | `Specs/draft-08a-reminder-scheduling-core.md` |
| Reminder service schedules future calls and validates do-not-call clients. | implemented | mocked | `app/services/invoice_management/reminder_service.py`, `tests/unit/test_reminder_task_model.py` | `Specs/draft-08a-reminder-scheduling-core.md` |
| Vapi service can create assistants, assign phone numbers, and inspect phone/assistant state. | implemented | sandbox/staging | `app/services/vapi_service.py`, `tests/unit/test_vapi_service.py`, `tests/unit/test_vapi_assistant_webhooks.py` | `Specs/draft-08b-live-call-provider-integration.md` |
| Twilio phone provisioning and pool administration. | legacy-review | sandbox/staging | `app/services/phone_provisioning_service.py`, `app/interfaces/web/admin.py`, `tests/unit/test_phone_provisioning_service.py` | `Specs/draft-08b-live-call-provider-integration.md` |
| SMS consent, opt-out, and call consent tracking. | legacy-review | mocked | `app/infrastructure/database/models.py`, `tests/unit/test_user_model_datetime_migration.py` | `Specs/draft-08b-live-call-provider-integration.md` |
| Email reminder delivery. | target-only | sandbox | `docs/IMPLEMENTATION_PLAN_PayCall.md`, `Specs/draft-08b-live-call-provider-integration.md` | `Specs/draft-08b-live-call-provider-integration.md` |
| Allowed calling hours and retry policy for Australia. | target-only | n/a | `Specs/draft-08b-live-call-provider-integration.md` | `Specs/draft-08b-live-call-provider-integration.md` |

## Subscription Billing and Plan Limits

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Public pricing and Stripe checkout for subscriptions. | implemented | sandbox | `app/interfaces/web/payments.py`, `app/interfaces/web/subscriptions.py`, `app/infrastructure/adapters/stripe_checkout_adapter.py`, `tests/unit/test_stripe_payments.py` | `Specs/draft-09-billing-and-plan-limits.md` |
| Stripe webhook handling. | implemented | staging | `app/interfaces/web/payments.py`, `tests/unit/test_stripe_payments.py` | `Specs/draft-09-billing-and-plan-limits.md` |
| Subscription domain supports basic, plus, pro, and commission model. | partial | mocked | `app/domain/subscription.py`, `app/domain/billing_config.py`, `tests/unit/test_subscription_use_cases.py` | `Specs/draft-09-billing-and-plan-limits.md` |
| Invoice upload quota checking and recording. | implemented | mocked | `app/application/use_cases/subscription/check_invoice_quota.py`, `app/application/use_cases/subscription/record_invoice_upload.py`, `tests/unit/test_subscription_use_cases.py` | `Specs/draft-09-billing-and-plan-limits.md` |
| README Basic/Plus plan table. | partial | n/a | `README.md`, `app/domain/billing_config.py` | `Specs/draft-09-billing-and-plan-limits.md` |
| Billing in first MVA. | target-only | n/a | `Specs/draft-09-billing-and-plan-limits.md`, `Specs/preflight-report.md` | `Specs/draft-09-billing-and-plan-limits.md` |

## Admin and Operator Workflows

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Admin dashboard and statistics routes. | legacy-review | mocked | `app/interfaces/web/admin.py`, `tests/unit/test_admin_dashboard_design.py`, `tests/unit/test_admin_realtime_metrics.py` | `needs-spec` |
| Phone number pool, Vapi number, and assistant administration. | legacy-review | sandbox/staging | `app/interfaces/web/admin.py`, `tests/unit/test_admin_phone_routes.py`, `tests/unit/test_admin_twilio_numbers.py` | `needs-spec` |
| Waitlist and referral administration. | legacy-review | mocked | `app/interfaces/web/admin.py`, `app/infrastructure/database/models.py` | `drop` |
| Production assistant health checks. | legacy-review | sandbox/staging | `app/services/prod_assistant_health.py`, `tests/unit/test_prod_assistant_health.py` | `needs-spec` |

## Webhooks and Background Jobs

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Basiq webhook endpoint with signature verification. | implemented | staging | `app/interfaces/web/basiq.py`, `app/services/accounts_receivable/basiq_service.py` | `Specs/draft-04b-live-bank-provider-integration.md` |
| Stripe webhook endpoint. | implemented | staging | `app/interfaces/web/payments.py`, `tests/unit/test_stripe_payments.py` | `Specs/draft-09-billing-and-plan-limits.md` |
| Vapi webhook-oriented assistant/call handling. | partial | staging | `app/services/vapi_service.py`, `tests/unit/test_vapi_assistant_webhooks.py` | `Specs/draft-08b-live-call-provider-integration.md` |
| Background bank ingestion every five minutes. | target-only | staging | `docs/PRD_PayCall.md`, `Specs/draft-04a-bank-ingestion-core.md` | `Specs/draft-04a-bank-ingestion-core.md` |
| Celery/Redis queue operations. | target-only | staging | `README.md`, `docker/`, `docs/PRD_PayCall.md` | `needs-spec` |

## Hermes and Command Surface

| Behavior | Status | Verification | Sources | New-repo target |
| --- | --- | --- | --- | --- |
| Hermes intent parser and skill dispatcher. | target-only | n/a | User architecture notes in conversation, `Specs/02-hermes-command-contract.md` | `Specs/02-hermes-command-contract.md` |
| Pipeable command JSON envelope and shared CLI/application use cases. | target-only | mocked | `Specs/02-hermes-command-contract.md` | `Specs/02-hermes-command-contract.md` |
| Web UI, CLI, and chat adapters call the same use cases. | target-only | mocked | `Specs/02-hermes-command-contract.md` | `Specs/02-hermes-command-contract.md` |
| qnp-crm style CLI pipeline compatibility. | target-only | mocked | `Specs/02-hermes-command-contract.md` | `Specs/02-hermes-command-contract.md` |
| PaymentReminder Apple Shortcut API surface. | legacy-review | mocked | `APPLE_SHORTCUT_TEMPLATE.md`, `app/interfaces/web/main.py` | `drop` |

## Minimum MVA Parity Set

The new repo should not attempt full feature parity first. The minimum MVA set
is:

1. In-house auth package integrated enough for an authenticated actor context.
2. Organization, membership role, customer, invoice, money, bank transaction,
   allocation, payment, and audit event domain core.
3. Manual client and invoice creation.
4. Web invoice upload and reviewed invoice draft confirmation.
5. Fake/dev bank transaction ingestion plus raw transaction persistence.
6. Match proposal creation that never mutates accounting truth until confirmed.
7. Confirmation, rejection, and undo with audit events.
8. Dashboard new-payments query based on proposed allocations since the user's
   last dashboard view.
9. Manual transaction sync and mocked/sandbox verification path.
10. Hermes command contract over shared application use cases, after the domain
    core is settled.

## Do Not Port Without Re-approval

- Referral rewards, referral fraud checks, waitlist management, and social-exit
  growth mechanics.
- Apple Shortcut download/API-token flows unless a PayCall channel explicitly
  requires them.
- US-centric TCPA/A2P/VoIP prevention behavior unless the reminder-calling spec
  keeps it for Australian compliance.
- ToodlelooMe assistant pool administration as-is; only port the smaller subset
  required for PayCall reminder calls.
- Multi-currency behavior. PayCall MVA is AUD only.

## Follow-up Specs Needed

- Auth implementation specs:
  `Specs/13-auth-password-session-core.md`,
  `Specs/14-auth-org-permission-core.md`,
  `Specs/15-auth-oauth-identity-linking.md`,
  `Specs/16-auth-api-tokens-cli-hermes.md`, and
  `Specs/17-auth-audit-and-risk-events.md`.
- A provider-neutral bank connector spec that decides fake/dev, Basiq, Wych, or
  another provider for first implementation.
- A Hermes channel intake spec for upload sources: chat upload, direct web
  upload, and BCC/forwarded email.
- A reminder-calling compliance spec for Australian calling hours, retries,
  consent, opt-out, and channel scope.
- An operator workflow spec that decides which admin/Vapi/Twilio tooling is
  required for PayCall production support.
