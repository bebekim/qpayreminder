# Spike: Preflight and Beads readiness workflow

## Why

The migration specs need a repeatable readiness gate before implementation.
Specs describe behavior, but Beads is useful for queue state, claims,
dependencies, and blockers. Preflight should connect the two without replacing
the specs as the implementation contract.

Without this workflow, Night Shift or another implementation agent may start
work before dependencies, test plans, provider assumptions, or human approvals
are clear.

## What the system should do

- Given draft and ready specs in `Specs/`, preflight should review all specs and
  classify each one as `draft`, `needs-clarification`, `blocked`, `ready`, or
  `done`.
- Given approved non-draft specs, preflight should verify they are ready for
  implementation and have concrete acceptance criteria and test plans.
- Given dependencies between specs, preflight should write a dependency graph in
  `Specs/preflight-report.md`.
- Given Beads is available, preflight should compare ready specs with `bd`
  issues and recommend missing issue creation, status updates, claims, and
  dependency links.
- Given Beads is unavailable, preflight should still produce the report from
  specs alone and note the fallback.
- Given missing tests, fixtures, provider assumptions, environment variables, or
  human decisions, preflight should mark the spec not ready and list exact edits
  or questions.
- Given a spec has no `## Test plan`, preflight should mark it
  `needs-clarification`; it should not silently invent implementation checks.
- Given a non-draft spec has unresolved blocking open questions, preflight
  should mark it `needs-clarification` or `blocked` unless the questions are
  explicitly marked non-blocking.

## Data flow

```
Specs/*.md + docs/*.md + AGENTS.md + AGENT_LOOP.md + bd state
    -> preflight review
    -> Specs/preflight-report.md
    -> recommended spec edits / bd commands / ready queue
```

Beads role:

```
Spec = behavior and test contract
Bead = queue item, dependency node, claim, blocker, status
```

Beads operating model:

- Use `bd ready --json` for agent-readable unblocked work.
- Use `bd blocked` or `bd dep tree <id>` to inspect blocked work.
- Use `bd update <id> --claim` to atomically claim one task.
- Use `bd dep add <child-id> <parent-id>` for hard dependencies, where the
  child is blocked until the parent is complete.
- Use `discovered-from` or `related` links for non-blocking follow-up context.
- Use `bd create ... --json`, `bd show <id> --json`, and `bd list --json` when
  automation needs to parse output.
- Use `bd init --stealth` for local planning state that should not be committed
  during this migration planning phase.

Recommended dependency chain for current migration specs:

```
00-feature-parity-inventory
  -> 01-paycall-domain-core
      -> 02-hermes-command-contract
      -> draft-03a-invoice-draft-core
      -> draft-03b-channel-email-invoice-intake
      -> draft-04a-bank-ingestion-core
          -> draft-04b-live-bank-provider-integration
          -> draft-05-ai-match-proposals-and-allocations
              -> draft-06-dashboard-new-payments
              -> draft-07-confirm-reject-undo-allocations
                  -> draft-08a-reminder-scheduling-core
                      -> draft-08b-live-call-provider-integration
      -> draft-09-billing-and-plan-limits
      -> 10-auth-provider-selection
```

## Acceptance criteria

- [ ] `Specs/preflight-report.md` is created or updated.
- [ ] The report lists every Markdown spec under `Specs/`.
- [ ] The report classifies each spec as `draft`, `needs-clarification`,
      `blocked`, `ready`, or `done`.
- [ ] The report includes a dependency graph for the migration specs.
- [ ] The report identifies specs with missing or insufficient test plans.
- [ ] The report identifies unresolved external-service assumptions, including
      auth provider, bank provider, email intake provider, AI provider, billing
      provider, and call provider.
- [ ] Non-draft specs with unresolved blocking open questions are marked
      `needs-clarification` or `blocked`.
- [ ] If `bd` is available, the report includes recommended `bd create`,
      `bd update`, and `bd dep add` commands.
- [ ] If `bd` is unavailable, the report says so and continues from specs.
- [ ] No production application code, migrations, or provider integrations are
      changed.

## Test plan

This is a workflow/documentation spike. Validation is structural.

Expected checks:

```bash
test -f Specs/preflight-report.md
rg -n "Readiness|Dependency|Beads|Clarification|ready|blocked|needs-clarification" Specs/preflight-report.md
rg -n "bd create|bd dep add|bd unavailable|Beads unavailable" Specs/preflight-report.md
git diff -- app migrations src
```

Optional if Beads is initialized:

```bash
bd ready --json
```

Expected result:

- Preflight report exists.
- Report names all specs.
- Report includes dependency graph and Beads sync notes.
- Product code and migrations are unchanged.

## What could go wrong

- **Risk**: Beads becomes the source of requirements.
  **How we'd notice**: A bead contains acceptance criteria not present in the
  linked spec.
  **Mitigation**: Keep behavior and tests in specs; use Beads only for status,
  claims, blockers, and dependencies.

- **Risk**: Preflight approves specs with unresolved provider decisions.
  **How we'd notice**: Implementation needs live credentials or provider choice
  mid-task.
  **Mitigation**: Mark provider-dependent specs blocked or
  needs-clarification until provider assumptions are explicit.

- **Risk**: Preflight writes broad spec changes instead of reporting gaps.
  **How we'd notice**: Large spec rewrites appear without human review.
  **Mitigation**: Preflight may make small metadata/doc-routing edits, but
  substantive behavior changes should be recommendations or separate patches.

## Constraints

- Do not implement product code.
- Do not run live provider scripts.
- Do not initialize committed Beads state unless explicitly requested.
- Use stealth/local Beads mode if initialization is needed for local planning.
- Preflight should recommend exact Beads commands; it should not create or
  mutate Beads issues unless explicitly requested.
- Specs remain the implementation contract.
- Ready specs should not have `draft-` filenames.

## Open questions

- Should `.beads/` stay local-only in stealth mode for this planning phase, or
  should Beads state be committed in the new repo?
- Should preflight create Beads issues automatically, or only recommend exact
  commands for a human/agent to run?
- Should approved specs include `State: ready` metadata in addition to non-draft
  filenames?

## Spike vs Feature

**Spike**. The output is a preflight report and Beads synchronization plan. No
product implementation should be written.
