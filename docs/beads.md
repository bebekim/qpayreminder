# Beads

Beads is adopted lightly in this repository as a queue and dependency graph for
agent work. It does not replace Markdown specs.

## Role

- `Specs/` holds implementation contracts: behavior, acceptance criteria,
  constraints, and test plans.
- Beads holds task status, claims, dependencies, blockers, and follow-up links.
- Preflight checks consistency between ready specs and Beads when available.
- Night Shift may use `bd ready --json` to choose unblocked work before opening
  the linked spec.

## Local Setup

Initialize local-only Beads state with:

```sh
bd init --stealth
```

Stealth mode keeps Beads useful for local coordination without requiring the
database to be committed immediately.

## Issue Convention

Create one issue per ready spec and link the spec path in the description:

```sh
bd create "Fix reminder scheduling drift" -t task -p 1   --description "Spec: Specs/fix-reminder-scheduling-drift.md" --json
```

Before implementation:

```sh
bd ready --json
bd update <id> --claim
bd show <id> --json
```

From the repository group root, preview parallel Night Shift execution with:

```sh
./beads-night-shift paymentreminder --max 2
```

Launch selected ready Beads issues with:

```sh
./beads-night-shift paymentreminder --max 2 --run
```

The parallel runner claims each selected issue, creates one Git worktree per
issue, and launches the existing Sandcastle Night Shift flow against each
worktree.

For hard dependencies, use:

```sh
bd dep add <child-id> <parent-id>
```

This means the child is blocked until the parent is complete.

For non-blocking follow-up context, use `discovered-from` or `related` links:

```sh
bd create "Clarify provider fixture" -t task -p 2   --deps discovered-from:<parent-id>   --description "Follow-up discovered while implementing <spec>" --json
```

Close Beads issues after implementation and checks are complete:

```sh
bd close <id> --reason "Implemented and tested"
```

## Fallback

If `bd` is unavailable or `.beads/` is absent, agents should continue from
ready specs in `Specs/`.
