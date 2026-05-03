# Guarded CLI Workflows

QPayReminder uses CLI programs as a shared execution surface for Hermes, web UI,
and operators. That requires a guard layer before CLIs can operate broadly on
customer, invoice, payment, bank, reminder, or provider data.

The design adopts the useful Guardians pattern:

1. Generate a structured workflow plan.
2. Use symbolic references for data produced by tools.
3. Verify the complete plan against a policy before any tool runs.
4. Execute only verified workflows.
5. Audit the trace with redaction.

The core rule: an LLM must not read concrete sensitive data and then decide new
side-effecting commands based on that data. Plans are verified before data is
bound.

## Guarded Executor Boundary

Hermes skills and web actions should call a guarded workflow executor. They
should not directly run raw subprocesses for data mutation or external sends.

Allowed flow:

```text
Intent -> Workflow Plan -> Verify -> Execute -> Audit
```

Disallowed flow:

```text
Run CLI -> Give concrete output to LLM -> LLM chooses next mutating CLI
```

## Initial Policy Shape

Policies should cover:

- tool allowlists
- actor permissions
- symbolic reference scope
- sensitive source labels
- forbidden sink parameters
- mutation confirmation
- external send preview
- environment confirmation for production
- command budgets

## External Reference

- Guardians: https://github.com/metareflection/guardians
- Design: https://github.com/metareflection/guardians/blob/main/DESIGN.md
