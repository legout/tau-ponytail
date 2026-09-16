# Issue 11: Documentation

**Plan phase:** 4 — documentation
**Depends on:** #06–#09 (documented behavior must exist)
**Size:** S

## Context

The README currently describes planned usage. Finalize it so a user can
install, configure, drive, and reason about the extension without reading the
plan. Documentation must state the deliberate difference from Ponytail's Pi
adapter: the active mode is generation/session-lived, while the configured
default is file-persisted.

## Tasks

- Rewrite `README.md`:
  - what it does; MIT attribution to upstream Ponytail;
  - install: `tau -e /path/to/tau-ponytail` for local use, and
    `tau install git:github.com/<owner>/tau-ponytail` once a release ref
    exists (manifest ships with #01);
  - usage: `/ponytail` table (bare, modes, `status`, `default`), the five
    shortcuts, and `stop ponytail` / `normal mode`;
  - configuration: `PONYTAIL_DEFAULT_MODE` precedence, config file paths per
    platform, fallback to `full`, preservation of unrelated keys;
  - optional separate installation of the Ponytail skills under
    `.tau/skills` or `.agents/skills`, and the built-in help fallback when a
    skill is missing;
  - Pi-adapter differences: no branch-level mode persistence, ephemeral
    context message instead of system-prompt edit, session reset on
    `session_start`;
  - print-mode support statement; no status-bar widget in v1.
- Update `AGENTS.md` only if the check commands or layout changed from what
  it already documents.
- Remove or update any "plan only / proposed" status wording across README
  and PLAN.md status section.

## Acceptance criteria

- [ ] A new user can install and drive every documented feature using only
      the README.
- [ ] Every behavior in plan acceptance criteria 1–9 is either documented or
      deliberately omitted with rationale.
- [ ] Attribution and the Pi-adapter differences are stated.
- [ ] `uv run ruff format --check .` still passes (docs-only change).

## Out of scope

- Publishing (#12).
