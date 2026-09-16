# Issue 12: Release gate

**Plan phase:** 5 — release gate
**Depends on:** all previous issues
**Size:** S

## Context

Final validation before the repository is publishable. The gate has two
parts: the four check commands, and a real clean-install smoke test proving
the packaged shape loads and behaves through Tau itself (plan acceptance
criteria 1, 8, 10).

## Tasks

1. Run and require green:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

2. Validate in a clean temporary environment (not the developer's
   `~/.tau/extensions`):

```bash
tau -e /path/to/tau-ponytail -p "Use the simplest safe implementation"
```

   Confirm the extension loads via the `[tool.tau]` manifest, injects the
   active mode's instructions into the request, and produces no load
   diagnostics.

3. Also exercise, in the same clean environment:

   - `/ponytail status`, `/ponytail lite`, `/ponytail off`;
   - `stop ponytail` as a standalone prompt;
   - one shortcut command (`/ponytail-review`) with and without the skills
     installed;
   - a `PONYTAIL_DEFAULT_MODE` override.

4. Fix anything found; do not waive failures.

## Acceptance criteria

- [ ] All four check commands pass with zero fixes pending.
- [ ] The clean `tau -e` smoke test loads the extension and shows injected
      behavior; no third-party dependencies required in Tau's environment.
- [ ] All ten plan acceptance criteria in PLAN.md are met; tick them off in
      the plan's status section or note exceptions explicitly.
- [ ] The repository is loadable from a clean checkout (fresh clone,
      `uv sync`, checks, `tau -e`).

## Out of scope

- Publishing to a remote repository (explicit non-goal of local setup);
  publishing happens only after this gate passes.
