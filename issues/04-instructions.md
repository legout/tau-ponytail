# Issue 04: Instruction provider

**Plan phase:** 2 — instruction provider (design decisions 1 and 3)
**Depends on:** #01 scaffolding, #02 mode model
**Size:** M

## Context

Each mode injects a distinct instruction body into the provider request. The
bodies derive from upstream Ponytail (`https://github.com/DietrichGebert`,
MIT) and must:

- clearly identify themselves as behavioral guidance, not a user task
  (they will be delivered as an ephemeral context message by #08);
- be kept in a readable, versioned Python module (a packaged Markdown
  resource is acceptable if it makes upstream synchronization less
  error-prone — pick one and record why);
- be selected as whole per-mode bodies — no stringly-typed partial mutations
  or common-prefix editing;
- retain MIT attribution for upstream-derived text.

Mode semantics from upstream: `lite` builds the requested change and names a
simpler alternative briefly; `full` enforces the YAGNI / stdlib-first /
native / minimum-change ladder; `ultra` aggressively prefers deletion and the
smallest working change.

`off` is allocation-free at this module's boundary: asking for `off`
instructions is a no-op returning nothing, not an empty string.

## Tasks

- Add the four instruction bodies in `src/tau_ponytail/instructions.py`,
  derived from upstream Ponytail's mode text, with an attribution comment.
- Implement `instructions_for_mode(mode: Mode) -> str | None`:
  - returns the whole body for `lite` / `full` / `ultra`;
  - returns `None` for `off`;
  - deterministic fallback: any unexpected internal value never produces a
    crash or a partial prompt — define and test the fallback (e.g. fall back
    to `full`'s body) so no unsupported mode can leak into the prompt.
- Keep bodies as module-level constants or a frozen mapping keyed by `Mode`.

## Acceptance criteria

- [ ] Each of `lite`, `full`, `ultra` returns a non-empty, distinct body that
      names its behavioral level (so #10 can assert injection identity).
- [ ] `instructions_for_mode("off") is None`.
- [ ] No code path returns a partial/templated mutation of another mode.
- [ ] Unit tests assert mode-specific content markers and the fallback
      behavior; MIT attribution present in the module.

## Out of scope

- Delivery mechanism (hook, message type, ephemeral-ness) — that is #08.
