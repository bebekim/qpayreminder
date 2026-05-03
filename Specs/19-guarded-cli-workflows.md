# Guarded CLI Workflows

Priority: high
State: ready

## Problem

QPayReminder intentionally uses composable CLI programs as a shared execution
surface for Hermes chat skills, web actions, and operator workflows. That is
powerful, but it also means agent-generated plans can operate on customer data,
invoices, payment records, reminders, provider webhooks, and eventually live
bank/payment state.

The CLI layer therefore needs a guardrail model before broad data-mutating
skills are exposed. The useful idea from Guardians is code/data separation:
generate a structured plan with symbolic references first, verify it against a
policy, and only then execute tools against concrete data.

## External Reference

- Guardians: <https://github.com/metareflection/guardians>
- Guardians design: <https://github.com/metareflection/guardians/blob/main/DESIGN.md>

Adopt the architecture, not necessarily the library wholesale at first. Start
with a small in-repo policy/verifier for PayCall CLI workflows, then evaluate
depending on Guardians directly once its APIs and packaging fit the project.

## Desired Behavior

- Hermes and web UI do not directly call data-mutating CLI programs.
- A caller submits an intent that becomes a structured workflow plan.
- The workflow plan uses symbolic references for data produced by prior steps
  instead of embedding live customer/provider records in subsequent commands.
- The plan is verified before any CLI program executes.
- Verification rejects unknown tools, forbidden tool sequences, invalid symbolic
  references, unsafe data flows, missing actor context, and missing confirmation
  for side effects.
- Read-only CLI tools and mutating CLI tools are tagged separately.
- Sensitive data sources are tagged, including invoices, bank transactions,
  payment allocations, contact data, reminder copy, and provider payloads.
- Side-effect sinks are tagged, including reminder send, invoice mutation,
  payment allocation, export, delete, provider write, and external message send.
- Runtime execution records a workflow trace, actor context, policy decision,
  command arguments with redaction, command result summary, and exit status.
- Operators can dry-run a verified workflow before approving side effects.

## Architecture

```text
Hermes/Web/Operator Intent
        |
        v
Structured Workflow Plan
        |
        v
Guarded Verifier
  - tool registry allowlist
  - symbolic reference scope check
  - taint/source/sink policy
  - security automata for command sequence
  - preconditions and frame conditions
  - confirmation/budget checks
        |
        v
Verified Workflow Executor
        |
        v
CLI Programs
```

The LLM may propose a plan, but it must not observe concrete sensitive data and
then decide new side-effecting commands based on unverified instructions hidden
inside that data.

## Workflow Shape

Minimum workflow schema:

```json
{
  "goal": "match new bank payments to open invoices",
  "actor_context": "@actor",
  "dry_run": true,
  "steps": [
    {
      "label": "Fetch open invoices",
      "tool": "invoice.list_open",
      "arguments": {"organization_id": "@actor.organization_id"},
      "result_binding": "open_invoices"
    },
    {
      "label": "Fetch new transactions",
      "tool": "bank.list_unmatched",
      "arguments": {"organization_id": "@actor.organization_id"},
      "result_binding": "transactions"
    },
    {
      "label": "Propose matches",
      "tool": "match.propose",
      "arguments": {
        "invoices": {"ref": "open_invoices"},
        "transactions": {"ref": "transactions"}
      },
      "result_binding": "match_proposals"
    }
  ]
}
```

For mutation:

```json
{
  "goal": "confirm a payment allocation",
  "actor_context": "@actor",
  "dry_run": false,
  "confirmation": {
    "confirmed_by": "@actor.actor_id",
    "confirmation_token": "operator-visible-token"
  },
  "steps": [
    {
      "label": "Confirm allocation",
      "tool": "payment.confirm_allocation",
      "arguments": {
        "proposal_id": "proposal_123",
        "organization_id": "@actor.organization_id"
      }
    }
  ]
}
```

## Initial Tool Registry

Read-only tools:

- `invoice.list_open`
- `invoice.get`
- `client.get`
- `bank.list_unmatched`
- `payment.list_proposals`
- `reminder.preview`

Pure transform tools:

- `invoice.parse_upload`
- `match.propose`
- `redact.sensitive_text`
- `format.operator_summary`

Mutating tools:

- `invoice.create_draft`
- `invoice.update_draft`
- `payment.confirm_allocation`
- `payment.reject_proposal`
- `payment.undo_allocation`
- `reminder.schedule`
- `reminder.cancel`
- `export.mark_sent`

External communication sinks:

- `reminder.send`
- `email.send`
- `sms.send`
- `whatsapp.send`
- `telegram.send`

## Policy Rules

- Only registered tools may run.
- Every workflow must include an `ActorContext`.
- Every tool call must be authorized against actor role/permissions.
- Every symbolic reference must be bound by an earlier step or input variable.
- Mutating tools require `dry_run=false` plus an explicit confirmation token.
- External communication sinks require confirmation and a preview generated in
  the same verified workflow.
- Provider payloads, invoice source documents, bank transactions, and reminder
  body text must not flow into external communication sinks unless passed
  through an approved redaction/formatting tool.
- Bank transaction data must not flow directly to `reminder.send`.
- Invoice upload OCR/extraction text must not become a tool name, command flag,
  shell argument, recipient address, or provider URL.
- `export.mark_sent` cannot run before the export artifact has been created and
  checksummed.
- Production workflows require production environment confirmation.
- Budget limits cap maximum tool count, loop count, records touched, external
  messages sent, and mutation count.

## CLI Contract

Every CLI should support:

- `--json` for structured output.
- `--dry-run` for non-mutating preview where applicable.
- `--actor-context` or `--actor-context-file`.
- `--request-id`.
- `--confirm <token>` for side effects.
- Exit code `0` for success.
- Exit code `2` for validation or policy rejection.
- Exit code `3` for authorization failure.
- Exit code `4` for dependency/provider failure.
- Redacted structured error envelopes.

Hermes skills and web actions call the guarded workflow executor, not raw
subprocess commands.

## Non-Goals

- Do not build arbitrary shell command execution.
- Do not let workflows contain raw shell strings, pipes, glob patterns, or
  environment-variable expansion.
- Do not permit LLM-generated tool names outside the registry.
- Do not expose production mutations before auth, org permissions, audit, and
  environment separation are implemented.
- Do not require Z3 on day one if a smaller verifier can enforce the first
  policy set deterministically.

## Likely Files

- `src/qpayreminder/guardians/workflow.py`
- `src/qpayreminder/guardians/registry.py`
- `src/qpayreminder/guardians/policy.py`
- `src/qpayreminder/guardians/verify.py`
- `src/qpayreminder/guardians/execute.py`
- `src/qpayreminder/cli/`
- `src/qpayreminder/hermes/skills/`
- `docs/guarded-cli-workflows.md`
- `tests/unit/guardians/test_workflow_scope.py`
- `tests/unit/guardians/test_policy_taint.py`
- `tests/unit/guardians/test_policy_automata.py`
- `tests/unit/guardians/test_executor_confirmations.py`
- `tests/integration/test_guarded_cli_workflow.py`

## Edge Cases

- Prompt-injection text appears inside invoice OCR output.
- Prompt-injection text appears inside a bank transaction memo.
- Prompt-injection text appears inside a client email or WhatsApp message.
- A workflow references a result binding that is only defined inside one branch.
- A workflow attempts to call an unregistered tool.
- A workflow attempts a mutation in dry-run mode.
- A workflow attempts a mutation without confirmation.
- A workflow attempts an external send without preview.
- A workflow uses production environment while actor intended testing.
- A workflow touches more records than the budget allows.
- A transform tool accidentally strips provenance labels.
- A redaction tool fails or returns unredacted sensitive content.
- A CLI exits non-zero after partially mutating state.

## Test Expectations

Expected tests:

```bash
uv run pytest tests/unit/guardians -q
uv run pytest tests/integration/test_guarded_cli_workflow.py -q
uv run ruff check src tests
```

Fixture workflows should include malicious text that attempts to instruct the
agent to send data externally, mutate production, bypass confirmation, or change
the tool sequence. Those workflows must be rejected before any CLI executes.

## Acceptance Criteria

- [ ] A workflow schema exists and rejects raw shell commands.
- [ ] Tool registry entries define read/mutate/external-send categories.
- [ ] Verification runs before execution by default.
- [ ] Unknown tools and out-of-scope symbolic references are rejected.
- [ ] Mutating tools require actor authorization and explicit confirmation.
- [ ] External sends require preview and explicit confirmation.
- [ ] Sensitive source data cannot flow to forbidden sink parameters.
- [ ] Workflow traces are audited with redacted arguments and results.
- [ ] Hermes and web actions call the guarded executor rather than raw CLIs.
- [ ] Tests demonstrate prompt-injection text in tool results cannot alter the
      verified plan.

## Known Risks

- **Risk**: The guard layer becomes paperwork around still-raw shell execution.
  **How we'd notice**: Workflows contain shell strings or arbitrary command
  arguments.
  **Mitigation**: Registry-only tools; no raw shell in workflow schema.

- **Risk**: The LLM still sees sensitive output before planning mutations.
  **How we'd notice**: Hermes skill flow alternates "run CLI, ask LLM what next"
  with live data.
  **Mitigation**: Require plan-before-data for any workflow that can mutate or
  send externally.

- **Risk**: Policies are too strict for useful operator workflows.
  **How we'd notice**: Operators need repeated manual bypasses.
  **Mitigation**: Add explicit policy exceptions with tests and audit, never
  invisible bypass flags.
