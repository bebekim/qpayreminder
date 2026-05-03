# Adopt Night Shift Harness

State: done
Priority: P2

## Summary

Add the shared Sandcastle, preflight, Night Shift, harness-engineering, and
lightweight Beads scaffolding to this repository.

## Acceptance Criteria

- `AGENTS.md` routes agents to the harness docs and repo-specific commands.
- `AGENT_LOOP.md` exists.
- `.sandcastle/implement-night-shift.md`, `.sandcastle/preflight-specs.md`, `.sandcastle/doctor.md`, and `.sandcastle/sandbox.json` exist.
- `Specs/` exists with readiness rules.
- `docs/` contains the expected harness context files.
- `TODO.md` and `CHANGELOG.md` exist.
- Beads usage is documented and initialized in stealth mode when available.

## Notes

This spec documents the harness adoption work itself and should stay as a
draft/done record, not a ready Night Shift task.
