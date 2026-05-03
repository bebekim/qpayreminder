# Specs

Specs are the source of truth for Night Shift implementation work.

- `draft-*` files are ignored by Night Shift.
- Non-draft Markdown specs are eligible only when their state is `ready`.
- Keep specs bounded enough for one reviewable commit.
- Prefer one to three ready specs per Night Shift run.
- Put implementation details, acceptance criteria, and test expectations in the spec.

Use the root template at `../.night-shift/templates/spec-template.md` when
drafting a new spec from this repository group, or copy the structure manually
if this repository is used outside the parent workspace.

## Beads

Beads is used lightly as the queue and dependency graph when initialized.

- Link each Beads issue to a spec path such as `Specs/fix-reminder-scheduling.md`.
- Use `bd ready` to identify unblocked work.
- Use `bd update <id> --claim` before implementation.
- Use `bd dep add <child> <parent>` for task ordering.
- Keep the spec as the implementation contract; keep Beads as status, blockers, and links.
