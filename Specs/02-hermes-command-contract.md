# Feature: Hermes command contract for PayCall

## Why

Hermes needs to parse user intent and call skills or CLIs without bypassing
business rules. The qnp-crm pattern shows the right shape: thin CLI adapters
over shared application use cases, a constrained command registry with schema,
validation, trust tiers, plan-before-write behavior, pipeable JSON envelopes,
and structured JSON results.

Without this contract, Telegram, WhatsApp, and Web Chat integrations will each
invent their own unsafe path into the application.

The command layer must not become a second implementation of business logic.
Web routes, chat/Hermes handlers, background jobs, and CLIs should all call the
same application use cases.

## What the system should do

- Given a natural-language user request, Hermes should map it to a structured
  command object, not directly to arbitrary code or SQL.
- Given a structured command object, the PayCall command layer should validate
  the command name, parameters, and trust tier before execution.
- Given a read command, the command layer should execute immediately and return
  a JSON result.
- Given a write command without confirmation, the command layer should return a
  plan and an exact confirmation command.
- Given a call or accounting-confirmation command, the command layer should
  require explicit confirmation according to the command tier.
- Given an executed command and expectations, the command layer should verify
  the result and report divergences.
- Given a web UI action and an equivalent chat/CLI action, both should execute
  the same application use case and differ only in input parsing, auth/session
  extraction, and response formatting.
- Given a CLI pipe, each command should read a JSON envelope from stdin when
  present, add its own result data, increment stage metadata, and emit a JSON
  envelope for the next stage.

Initial command domains:

- `account.current`
- `organizations.list`, `organizations.switch`
- `customers.search`, `customers.list`, `customers.add`, `customers.edit`
- `invoices.list`, `invoices.show`, `invoices.add`, `invoices.cancel`
- `invoice_drafts.create-from-upload`, `invoice_drafts.create-from-email`,
  `invoice_drafts.review`, `invoice_drafts.confirm`
- `payments.record`, `payments.list`
- `bank.status`, `bank.sync`, `bank.transactions`
- `allocations.propose`, `allocations.list`, `allocations.confirm`,
  `allocations.reject`, `allocations.undo`
- `dashboard.summary`, `dashboard.new-payments`, `dashboard.mark-viewed`
- `reminders.schedule`, `reminders.list`, `reminders.cancel`
- `calls.initiate`

Trust tiers:

- `READ`: execute immediately.
- `WRITE`: return plan unless `confirm=true`.
- `ACCOUNTING`: confirmation/rejection/undo of allocations; explicit user
  confirmation required.
- `CALL`: initiating an external voice call; explicit user confirmation required.

Initial tier decisions:

- `bank.sync` is `WRITE` because it imports raw transaction records and updates
  sync state, even though raw transactions are immutable after ingestion.

## Data flow

```
channel message -> Hermes intent -> command JSON -> validate -> plan/execute
    -> application use case -> result JSON -> channel response
```

Shared use-case flow:

```
Web route  -> application use case -> domain/repositories
CLI command -> application use case -> domain/repositories
Hermes skill -> CLI or dispatcher -> application use case -> domain/repositories
Worker job -> application use case -> domain/repositories
```

Pipe flow:

```
command A -> JSON envelope -> command B -> JSON envelope -> command C
```

Command input format:

```json
{
  "command": "invoices.list",
  "params": {
    "status": "overdue",
    "limit": 10
  }
}
```

Command execution context is separate from command params and includes the
authenticated actor:

```json
{
  "user_id": "user_123",
  "organization_id": "org_123",
  "membership_role": "owner",
  "channel": "whatsapp"
}
```

Invoice intake channels should all target the same invoice draft commands:

```
WhatsApp/Telegram upload -> Hermes -> invoice_drafts.create-from-upload
Web upload               -> Web adapter -> invoice_drafts.create-from-upload
BCC/email intake          -> Email adapter -> invoice_drafts.create-from-email
```

Command result format:

```json
{
  "ok": true,
  "data": {},
  "count": 0,
  "plan": null,
  "warnings": [],
  "hints": []
}
```

Pipe envelope format:

```json
{
  "v": 1,
  "ok": true,
  "pipe_id": "p-123",
  "stage": 1,
  "actor": {
    "user_id": "user_123",
    "organization_id": "org_123",
    "membership_role": "owner"
  },
  "data": {},
  "warnings": [],
  "error": null,
  "command": "bank.sync"
}
```

## Acceptance criteria

- [ ] The command registry exposes `schema`, `validate`, and `verify` commands.
- [ ] CLI commands are thin adapters and do not duplicate application use-case
      business logic.
- [ ] Web routes and equivalent CLI commands call the same application use
      cases.
- [ ] Commands can read and write a versioned JSON pipe envelope.
- [ ] Pipe stages preserve `pipe_id`, actor context, warnings, and prior data
      unless intentionally replacing fields.
- [ ] Unknown command names fail validation with a list of valid commands.
- [ ] Invalid parameters fail validation before any use case runs.
- [ ] Every command has exactly one trust tier.
- [ ] `WRITE`, `ACCOUNTING`, and `CALL` commands without confirmation return a
      plan and do not mutate state.
- [ ] Dispatch receives an authenticated actor context and enforces
      role/organization authorization before execution.
- [ ] `ACCOUNTING` and `CALL` commands require confirmation against a generated
      plan ID or confirmation token.
- [ ] `bank.sync` is a `WRITE` command.
- [ ] Confirmed write commands include an idempotency key or deterministic
      duplicate-protection behavior.
- [ ] Verification can assert `ok`, `count`, `hasPlan`, warning count, and
      selected fields.
- [ ] Unit tests cover validation success, validation failure, plan generation,
      confirmed execution, and verification divergence.
- [ ] The command layer does not import Flask request/session objects.

## Test plan

Expected test files:

- `tests/unit/commands/test_registry.py`
- `tests/unit/commands/test_validate.py`
- `tests/unit/commands/test_plan.py`
- `tests/unit/commands/test_verify.py`
- `tests/unit/commands/test_pipe_envelope.py`
- `tests/unit/commands/test_dispatch_tiers.py`
- `tests/unit/commands/test_clean_architecture.py`
- `tests/unit/interface/test_web_cli_use_same_use_case.py`

Expected commands:

```bash
uv run pytest tests/unit/commands -q
uv run pytest tests/unit/interface/test_web_cli_use_same_use_case.py -q
uv run python -m paycall schema
uv run python -m paycall validate '{"command":"invoices.list","params":{"status":"overdue","limit":10}}'
uv run ruff check src tests
```

The command-line examples may be adjusted if the final binary/module name is
not `paycall`, but the spec must retain equivalent executable checks.

## What could go wrong

- **Risk**: Hermes bypasses the command layer for "simple" actions.
  **How we'd notice**: Channel handlers call repositories or services directly.
  **Mitigation**: Make command dispatch the only allowed write path from agent
  channels.

- **Risk**: Plan text and execution command diverge.
  **How we'd notice**: User confirms one action but a different mutation runs.
  **Mitigation**: Generate plan and confirmation payload from the same validated
  command object.

- **Risk**: Trust tiers are inconsistently applied.
  **How we'd notice**: A call or accounting mutation executes without a plan.
  **Mitigation**: Enforce tier checks in the shared dispatcher, not handlers.

## Constraints

- Use qnp-crm as behavioral precedent, but implement in the new repo's stack.
- JSON is the primary machine interface.
- Human/channel phrasing is outside this spec except where it affects
  confirmation semantics.
- Do not implement LLM intent parsing in this spec; implement the command
  contract that intent parsing targets.
- Do not shell out from web routes to run the CLI; web routes should call shared
  use cases directly.
- Do not put business rules in CLI command handlers.

## Open questions

- Should the command binary be named `paycall`, `paycall-cli`, or something
  else?
- Should Hermes run commands in-process, as subprocess CLI calls, or through
  HTTP? The contract should support all three.
- Which command tier should `bank.sync` use if it only imports raw immutable
  transactions?

## Spike vs Feature

**Feature**. The qnp-crm command pattern is proven enough to implement a first
contract.
