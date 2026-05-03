# Spec Preflight Report

Generated from `Specs/`, project docs, and Beads state.

## Summary

Preflight reviewed all Markdown files in `Specs/`. Beads (`bd`) is installed
and `.beads/` exists. The auth direction has changed from hosted-provider
selection to an in-house reusable auth platform contract:

- `Specs/10-auth-provider-selection.md` is superseded.
- `Specs/12-in-house-auth-platform-contract.md` is the current auth contract.
- Existing Beads auth-provider issue should be renamed or replaced with an
  in-house auth-contract issue.

Recommendation: keep Beads as the execution queue and dependency graph, but do
not put requirements only in Beads. Create one Beads issue per promoted spec
with the spec path in the issue description, then add hard dependencies with
`bd dep add <child-id> <parent-id>`.

## Specs Reviewed

| Spec | State | Notes |
| --- | --- | --- |
| `Specs/README.md` | done | Process documentation, not implementation work. |
| `Specs/draft-adopt-night-shift-harness.md` | done | Historical harness adoption record; should remain draft/done and ignored by Night Shift. |
| `Specs/00-feature-parity-inventory.md` | done | Completed in `docs/feature-parity.md`. Open questions were captured as follow-up planning inputs, not blockers. |
| `Specs/01-paycall-domain-core.md` | needs-clarification | Approved, but still contains blocking open questions around customer identity inference and tolerance values. Mark those non-blocking or answer them before Night Shift. |
| `Specs/02-hermes-command-contract.md` | needs-clarification | Approved, but still contains blocking open questions around command name, execution mode, and `bank.sync` was answered in body but remains in Open questions. |
| `Specs/10-auth-provider-selection.md` | superseded | Direction changed from provider selection to in-house reusable auth. Keep for history only. |
| `Specs/12-in-house-auth-platform-contract.md` | ready-for-splitting | Current auth contract. Split into smaller implementation specs before code work. |
| `Specs/13-auth-password-session-core.md` | ready | First implementation slice for reusable auth. Bounded to password, registration, sessions, actor context, and fake auth fixtures. |
| `Specs/14-auth-org-permission-core.md` | blocked | Depends on `Specs/13-auth-password-session-core.md`. |
| `Specs/15-auth-oauth-identity-linking.md` | blocked | Depends on `Specs/13-auth-password-session-core.md`. |
| `Specs/16-auth-api-tokens-cli-hermes.md` | blocked | Depends on `Specs/13-auth-password-session-core.md` and `Specs/14-auth-org-permission-core.md`. |
| `Specs/17-auth-audit-and-risk-events.md` | blocked | Depends on `Specs/13-auth-password-session-core.md`, `Specs/14-auth-org-permission-core.md`, and `Specs/16-auth-api-tokens-cli-hermes.md`. |
| `Specs/draft-03a-invoice-draft-core.md` | blocked | Defaults added for confidence/source retention/Excel scope; promote after domain core exists. |
| `Specs/draft-03b-channel-email-invoice-intake.md` | draft | Split from the original invoice intake spec; still blocked by channel and inbound email provider decisions. |
| `Specs/draft-04a-bank-ingestion-core.md` | blocked | Fake-provider and freshness defaults are set; promote after domain core exists. |
| `Specs/draft-04b-live-bank-provider-integration.md` | draft | Split from the original bank sync spec; blocked by Basiq/Wych/provider decision and sandbox/staging setup. |
| `Specs/draft-05-ai-match-proposals-and-allocations.md` | blocked | Fake-AI, deterministic governance, confidence bands, and template version defaults are set; depends on domain, invoice, and bank primitives. |
| `Specs/draft-06-dashboard-new-payments.md` | blocked | Mark-viewed, sync freshness, and confidence display defaults are set; depends on allocation proposals and sync state. |
| `Specs/draft-07-confirm-reject-undo-allocations.md` | blocked | Role, reason, and post-export undo defaults are set; depends on allocation proposal primitives. |
| `Specs/draft-08a-reminder-scheduling-core.md` | blocked | Fake-provider and single-reminder cadence defaults are set; depends on reliable confirmation/payment state. |
| `Specs/draft-08b-live-call-provider-integration.md` | draft | Split from the original reminders spec; blocked by provider, compliance, retry, and retention decisions. |
| `Specs/draft-09-billing-and-plan-limits.md` | deferred | Billing is deferred for private-beta MVA unless paid access is explicitly required. |
| `Specs/11-preflight-beads-readiness-workflow.md` | ready | Approved and currently being executed by this report. Move to done after review if desired. |

## Readiness Table

| Ready for Night Shift? | Spec |
| --- | --- |
| Done | `Specs/00-feature-parity-inventory.md` |
| Yes, for spec splitting only | `Specs/12-in-house-auth-platform-contract.md` |
| Yes | `Specs/13-auth-password-session-core.md` |
| Not yet | `Specs/14-auth-org-permission-core.md` |
| Not yet | `Specs/15-auth-oauth-identity-linking.md` |
| Not yet | `Specs/16-auth-api-tokens-cli-hermes.md` |
| Not yet | `Specs/17-auth-audit-and-risk-events.md` |
| Not yet | `Specs/01-paycall-domain-core.md` |
| Not yet | `Specs/02-hermes-command-contract.md` |
| Not yet | `Specs/11-preflight-beads-readiness-workflow.md` after this report is reviewed/moved to done |

The approved domain and Hermes specs are good directionally, but preflight
should be stricter than approval: non-draft specs with unresolved blocking open
questions should not be used for autonomous implementation until those questions
are answered or explicitly marked non-blocking.

## Dependency Graph

Recommended hard-dependency graph:

```text
00-feature-parity-inventory
  -> 12-in-house-auth-platform-contract
      -> 13-auth-password-session-core
          -> 14-auth-org-permission-core
          -> 15-auth-oauth-identity-linking
              -> 16-auth-api-tokens-cli-hermes
                  -> 17-auth-audit-and-risk-events
  -> 01-paycall-domain-core
      -> 02-hermes-command-contract
      -> 03a-invoice-draft-core
          -> 03b-channel-email-invoice-intake
      -> 04a-bank-ingestion-core
          -> 04b-live-bank-provider-integration
          -> 05-ai-match-proposals-and-allocations
              -> 06-dashboard-new-payments
              -> 07-confirm-reject-undo-allocations
                  -> 08a-reminder-scheduling-core
                      -> 08b-live-call-provider-integration
      -> 09-billing-and-plan-limits

11-preflight-beads-readiness-workflow
  -> all future Night Shift implementation work
```

Notes:

- `12-in-house-auth-platform-contract` should precede any production actor/auth
  integration and should inform Hermes actor context.
- `13-auth-password-session-core` is the first implementation-ready auth slice.
- `14`, `15`, `16`, and `17` should stay blocked until their listed auth
  predecessors are implemented and tested.
- `03a` and `04a` can proceed independently after the domain core if scoped to
  fake/local providers.
- `03b`, `04b`, and `08b` are provider/channel integration follow-ups.
- `05` depends on both invoice and bank primitives.
- `06` and `07` depend on allocation proposals.
- `08` should not run before confirmation/payment state is reliable.
- `09` can be deferred if billing is not MVA.

## Beads Sync Notes

Beads is installed (`bd version 1.0.3`) and initialized. The prior promoted
auth-provider issue was closed after the in-house auth contract was split. The
current auth queue is:

```text
paymentreminder-3s0 -> closed, Specs/12-in-house-auth-platform-contract.md
paymentreminder-2zt -> ready, Specs/13-auth-password-session-core.md
paymentreminder-36b -> blocked by paymentreminder-2zt, Specs/14-auth-org-permission-core.md
paymentreminder-zrn -> blocked by paymentreminder-2zt, Specs/15-auth-oauth-identity-linking.md
paymentreminder-nwj -> blocked by paymentreminder-2zt and paymentreminder-36b, Specs/16-auth-api-tokens-cli-hermes.md
paymentreminder-lof -> blocked by paymentreminder-2zt, paymentreminder-36b, and paymentreminder-nwj, Specs/17-auth-audit-and-risk-events.md
```

Recommended future issue creation commands after finalizing which non-auth specs
should enter the queue:

```bash
bd create "PayCall domain core" -t feature -p 0 \
  --description "Spec: Specs/01-paycall-domain-core.md" --json

bd create "Hermes command contract" -t feature -p 0 \
  --description "Spec: Specs/02-hermes-command-contract.md" --json

bd create "Invoice draft core" -t feature -p 1 \
  --description "Spec: Specs/draft-03a-invoice-draft-core.md" --json

bd create "Channel and email invoice intake" -t feature -p 2 \
  --description "Spec: Specs/draft-03b-channel-email-invoice-intake.md" --json

bd create "Bank ingestion core" -t feature -p 1 \
  --description "Spec: Specs/draft-04a-bank-ingestion-core.md" --json

bd create "Live bank provider integration" -t feature -p 2 \
  --description "Spec: Specs/draft-04b-live-bank-provider-integration.md" --json

bd create "AI match proposals and allocations" -t feature -p 1 \
  --description "Spec: Specs/draft-05-ai-match-proposals-and-allocations.md" --json

bd create "Dashboard new payments" -t feature -p 1 \
  --description "Spec: Specs/draft-06-dashboard-new-payments.md" --json

bd create "Confirm reject undo allocations" -t feature -p 1 \
  --description "Spec: Specs/draft-07-confirm-reject-undo-allocations.md" --json

bd create "Reminder scheduling core" -t feature -p 2 \
  --description "Spec: Specs/draft-08a-reminder-scheduling-core.md" --json

bd create "Live call provider integration" -t feature -p 3 \
  --description "Spec: Specs/draft-08b-live-call-provider-integration.md" --json

bd create "Billing and plan limits" -t feature -p 2 \
  --description "Spec: Specs/draft-09-billing-and-plan-limits.md" --json
```

After creation, capture the returned IDs and add dependencies. Auth dependencies
for `paymentreminder-36b`, `paymentreminder-zrn`, `paymentreminder-nwj`, and
`paymentreminder-lof` have already been applied:

```bash
bd dep add <domain-core-id> <feature-parity-id>
bd dep add <hermes-command-id> <domain-core-id>
bd dep add <invoice-draft-core-id> <domain-core-id>
bd dep add <channel-email-intake-id> <invoice-draft-core-id>
bd dep add <bank-ingestion-core-id> <domain-core-id>
bd dep add <live-bank-provider-id> <bank-ingestion-core-id>
bd dep add <ai-match-id> <invoice-draft-core-id>
bd dep add <ai-match-id> <bank-ingestion-core-id>
bd dep add <dashboard-id> <ai-match-id>
bd dep add <confirm-reject-undo-id> <ai-match-id>
bd dep add <reminder-scheduling-core-id> <confirm-reject-undo-id>
bd dep add <live-call-provider-id> <reminder-scheduling-core-id>
bd dep add <billing-id> <domain-core-id>
```

For agent execution:

```bash
bd ready --json
bd update <id> --claim
bd show <id> --json
```

Use `discovered-from` or `related` for non-blocking findings:

```bash
bd create "Clarify BCC email provider" -t task -p 1 \
  --deps discovered-from:<channel-email-intake-id> \
  --description "Follow-up from Specs/draft-03b-channel-email-invoice-intake.md" --json
```

## Clarification Questions

## Draft Spec Review

This pass reviewed all `draft-*` specs for whether they should stay draft,
be split, or be promoted after dependency/clarification work.

| Spec | Recommendation | Reason |
| --- | --- | --- |
| `Specs/draft-03a-invoice-draft-core.md` | Promote after domain core | Defaults are now set for retention, review threshold, and Excel scope. |
| `Specs/draft-03b-channel-email-invoice-intake.md` | Keep draft | Split from the original invoice intake spec. Hermes upload and BCC/email intake require provider/channel decisions. |
| `Specs/draft-04a-bank-ingestion-core.md` | Promote after domain core | Fake/dev provider and sync freshness defaults are now set. |
| `Specs/draft-04b-live-bank-provider-integration.md` | Keep draft | Split from the original bank sync spec. Live Basiq/Wych behavior requires provider decision and sandbox/staging setup. |
| `Specs/draft-05-ai-match-proposals-and-allocations.md` | Promote after domain core, invoice intake, and bank ingestion | Fake-AI and confidence defaults are now set; remaining dependency is upstream primitives. |
| `Specs/draft-06-dashboard-new-payments.md` | Promote after allocation proposal spec | Mark-viewed and sync freshness defaults are now set; remaining dependency is allocation proposal state. |
| `Specs/draft-07-confirm-reject-undo-allocations.md` | Promote after allocation proposal spec | Role and undo defaults are now set; remaining dependency is allocation proposal state. |
| `Specs/draft-08a-reminder-scheduling-core.md` | Promote after confirmation/payment state | Fake call provider and cadence defaults are now set. |
| `Specs/draft-08b-live-call-provider-integration.md` | Keep draft | Split from the original reminders spec. Production calls require Australian calling-hour, retry, consent, privacy, and channel-scope decisions. |
| `Specs/draft-09-billing-and-plan-limits.md` | Deferred | Keep out of the first private-beta MVA unless paid access becomes a launch requirement. |
| `Specs/10-auth-provider-selection.md` | Superseded | Historical spike only. |
| `Specs/12-in-house-auth-platform-contract.md` | Ready for splitting | Current auth contract; split into implementation specs before coding. |
| `Specs/13-auth-password-session-core.md` | Ready | First implementation-ready auth slice. |
| `Specs/14-auth-org-permission-core.md` | Blocked | Depends on password/session primitives. |
| `Specs/15-auth-oauth-identity-linking.md` | Blocked | Depends on password/session primitives. |
| `Specs/16-auth-api-tokens-cli-hermes.md` | Blocked | Depends on password/session and permission primitives. |
| `Specs/17-auth-audit-and-risk-events.md` | Blocked | Depends on password/session, permissions, and API-token event sources. |
| `Specs/draft-adopt-night-shift-harness.md` | Leave draft/done | Historical adoption record only. Do not queue for Night Shift. |

### Suggested Promotion Order

```text
12-in-house-auth-platform-contract  (contract; split next)
13-auth-password-session-core       (first auth implementation slice)
14-auth-org-permission-core         (before product use-case authorization)
15-auth-oauth-identity-linking      (after 13)
16-auth-api-tokens-cli-hermes       (after 13 and 14)
17-auth-audit-and-risk-events       (after 13, 14, and 16)
01-paycall-domain-core              (after tolerance/customer-identity answers)
02-hermes-command-contract          (after command name/execution mode cleanup)
03a-invoice draft core              (after domain core)
04a-bank ingestion fake provider    (after domain core)
05-ai-match proposals fake AI       (after 03a and 04a)
06-dashboard new payments           (after 05)
07-confirm/reject/undo allocations  (after 05)
08a-reminder scheduling fake calls  (after 07)
03b-Hermes/email invoice intake adapters
04b-live bank provider integration
08b-live call provider integration
09-billing and plan limits          (deferred unless MVA includes billing)
```

### Draft Split Recommendations

- Split `draft-03` into:
  - `03a-invoice-draft-core`: web/manual upload, fake extractor, review, duplicate invoice handling.
  - `03b-channel-email-intake`: Hermes attachment adapters and BCC/forwarded email provider behavior.
- Split `draft-04` into:
  - `04a-bank-ingestion-core`: provider port, fake provider, immutable raw transaction persistence, sync runs.
  - `04b-bank-provider-integration`: Basiq/Wych selection, sandbox/staging validation, webhook details.
- Split `draft-08` into:
  - `08a-reminder-scheduling-core`: scheduling, fake call provider, `CALL` tier planning.
  - `08b-live-call-provider`: Vapi/Twilio integration, callbacks, recordings/transcripts, compliance windows.

### Defaults That Would Unblock Several Specs

If you want to keep momentum without deciding every future product detail now,
these defaults are sufficient for the next implementation wave:

- `draft-03a`: retain source documents through a storage port for MVA; manual review below confidence `0.85`; exclude Excel from first implementation unless customer data proves it is required.
- `draft-04a`: use a fake/dev bank provider first; define sync freshness as `OK <= 5 minutes`, `DELAYED > 5 minutes and <= 60 minutes`, `FAILED` after latest sync failure or no successful sync for more than 60 minutes.
- `draft-05`: deterministic exact matches may bypass live AI but must still create a governance envelope with `model=deterministic-rules`; confidence bands are `high >= 0.90`, `medium >= 0.70`, `review < 0.70`; first template is `paycall-match-v1`.
- `draft-06`: use explicit `dashboard.mark-viewed` after successful render; do not mark viewed merely by starting a request; show confidence as evidence-only label.
- `draft-07`: owner and bookkeeper may confirm/reject/undo; viewer may not. Use free-text reason plus optional enum later. Disallow undo after external accounting export until an export policy exists.
- `draft-08a`: use voice-only fake provider and one user-selected future scheduled reminder for MVA; email/SMS and live calling-provider compliance stay follow-up.
- `draft-09`: defer billing unless private beta requires paid plan enforcement.

### Blocking Before Domain Core Night Shift

- What exact fee/near-match tolerance should the domain core use for MVA?
- Is customer identity inferred on `BankTransaction`, only on `Allocation`, or
  both with different confidence semantics?

### Blocking Before Hermes Command Contract Night Shift

- Should the command module/binary be named `paycall`, `paycall-cli`, or another
  name?
- Is the first implementation in-process dispatcher plus CLI, or CLI only?
- Remove or resolve the stale `bank.sync` open question because the spec body now
  classifies it as `WRITE`.

### Blocking Before Draft Specs Become Ready

- Which bank provider is first: Basiq, Wych, or fake/dev only?
- Which inbound email provider handles BCC/forwarded invoice intake?
- Which AI provider and prompt/eval process is in scope for first live matching?
- Is billing in the MVA, and are Basic/Plus tiers still current?
- What are allowed calling hours and retry policies for Australian payment
  reminder calls?

## Recommended Doc Updates

- Keep `docs/feature-parity.md` aligned with auth direction.
- Keep `docs/auth-platform-direction.md` aligned with
  `Specs/12-in-house-auth-platform-contract.md`.
- Add `docs/migration-map.md` in the new repo when it exists.
- Add a short `docs/command-contract.md` after Hermes command contract details
  settle.

## Recommended Filename Changes

After clarifications:

- Keep `Specs/00-feature-parity-inventory.md` as ready.
- Keep `Specs/11-preflight-beads-readiness-workflow.md` ready until this report
  is accepted, then move it to `Specs/done/` in the new repo or leave it as a
  completed process spec here.
- Do not run `Specs/01-paycall-domain-core.md` or
  `Specs/02-hermes-command-contract.md` in Night Shift until blocking open
  questions are resolved or explicitly marked non-blocking.
- `Specs/10-auth-provider-selection.md` is superseded.
- `Specs/12-in-house-auth-platform-contract.md` has been split into
  `Specs/13-auth-password-session-core.md`,
  `Specs/14-auth-org-permission-core.md`,
  `Specs/15-auth-oauth-identity-linking.md`,
  `Specs/16-auth-api-tokens-cli-hermes.md`, and
  `Specs/17-auth-audit-and-risk-events.md`.
- Leave split provider/channel specs as drafts until their assumptions are
  clarified.

## Specs Safe for Night Shift

Safe now:

- `Specs/12-in-house-auth-platform-contract.md` for spec splitting only
- `Specs/13-auth-password-session-core.md`

Not safe yet:

- `Specs/01-paycall-domain-core.md`
- `Specs/02-hermes-command-contract.md`
- `Specs/14-auth-org-permission-core.md`
- `Specs/15-auth-oauth-identity-linking.md`
- `Specs/16-auth-api-tokens-cli-hermes.md`
- `Specs/17-auth-audit-and-risk-events.md`
- `Specs/draft-03a-invoice-draft-core.md`
- `Specs/draft-03b-channel-email-invoice-intake.md`
- `Specs/draft-04a-bank-ingestion-core.md`
- `Specs/draft-04b-live-bank-provider-integration.md`
- `Specs/draft-05-ai-match-proposals-and-allocations.md`
- `Specs/draft-06-dashboard-new-payments.md`
- `Specs/draft-07-confirm-reject-undo-allocations.md`
- `Specs/draft-08a-reminder-scheduling-core.md`
- `Specs/draft-08b-live-call-provider-integration.md`
- `Specs/draft-09-billing-and-plan-limits.md`

## Verification

Structural checks expected by `Specs/11-preflight-beads-readiness-workflow.md`:

```bash
test -f Specs/preflight-report.md
rg -n "Readiness|Dependency|Beads|Clarification|ready|blocked|needs-clarification" Specs/preflight-report.md
rg -n "bd create|bd dep add|bd unavailable|Beads unavailable" Specs/preflight-report.md
git diff -- app migrations src
```

No product application code, migrations, or provider integrations should be
changed by this preflight work.
