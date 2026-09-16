# Issue 07: Natural-language deactivation via `input` hook

**Plan phase:** 3 — Tau extension behavior (design decision 5)
**Depends on:** #05 extension core
**Size:** S

## Context

Upstream Ponytail deactivates on plain-language commands. Tau's `input`
lifecycle hook sees ordinary prompt input before it becomes a user message.
Deactivation must be **exact**: only a whole input equal to `stop ponytail`
or `normal mode`, ignoring case and trailing punctuation/whitespace, may set
the active mode to `off`. Ordinary prompts that merely *contain* those words
(e.g. "how do I stop ponytail from injecting?") must pass through untouched.

Because Tau may handle slash commands before the normal prompt path, this hook
must not try to interpret `/ponytail ...` — that is #06's job.

## Tasks

- Subscribe to the `input` event in `setup(tau)` (may be async).
- Normalize for matching only: case-fold and strip trailing whitespace and a
  small, explicit trailing-punctuation set (e.g. `.!?,;`); do not strip
  interior punctuation or split on whitespace generally.
- On exact match of either phrase: set the active mode to `off` and notify.
  Decide and test whether the input is consumed (not sent to the model) or
  passed through — upstream behavior is that the command is the whole intent,
  so consuming it is the default choice; record the decision.
- Non-matching input must be forwarded unchanged (whatever the hook's
  pass-through contract is — do not mutate it).

## Acceptance criteria

- [ ] `stop ponytail`, `STOP PONYTAIL`, `Normal Mode.`, `stop ponytail!`
      deactivate (active mode becomes `off`, notification shown).
- [ ] "how do I stop ponytail", "normal mode is what I want to discuss",
      empty input, and `/ponytail off` do **not** deactivate through this
      hook (`/ponytail off` is handled by #06).
- [ ] Matching input never reaches the model as a prompt (or passes through
      unchanged, per the recorded decision) — the test asserts whichever
      contract was chosen.
- [ ] The handler cannot raise into Tau for any input.

## Out of scope

- Persistence: deactivation changes only the generation-local active mode
  (#05); the configured default is untouched.
