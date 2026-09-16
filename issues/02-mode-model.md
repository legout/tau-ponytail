# Issue 02: Mode model and normalization

**Plan phase:** 1 — package and configuration (design decision 3)
**Depends on:** #01 scaffolding
**Size:** S

## Context

Ponytail has exactly four runtime levels, and every later feature (config,
instructions, commands, hooks) speaks in terms of them:

- `off` — no instruction injection;
- `lite` — build the requested change and name a simpler alternative briefly;
- `full` — enforce the YAGNI/stdlib/native/minimum ladder; the default;
- `ultra` — aggressively prefer deletion and the smallest working change.

`review` is **not** a mode; the review shortcut invokes a skill instead.

All string inputs to the extension (environment variables, config JSON,
`/ponytail` arguments) must go through one tolerant parser so that invalid,
missing, or unsupported values never crash or half-apply. Parsing must be pure
— no I/O — so config and command layers can reuse it.

## Tasks

- In `src/tau_ponytail/` (new `modes.py` or inside `config.py` — pick one and
  record the choice), define:
  - a `Mode` type (e.g. `Literal` or `StrEnum`) covering exactly
    `off | lite | full | ultra`;
  - `DEFAULT_MODE: Mode = "full"`;
  - `parse_mode(value: str | None) -> Mode | None`: trims whitespace, folds
    case, returns `None` for anything unsupported (including empty/`None`).
- No stringly-typed partial mutations anywhere: callers receive a `Mode` or
  `None`, never a "maybe fixed up" string.

## Acceptance criteria

- [ ] `parse_mode` accepts case/whitespace variants of all four modes.
- [ ] `parse_mode` returns `None` for `None`, empty strings, `"review"`,
      `"medium"`, and arbitrary garbage.
- [ ] Unit tests cover the table above; no I/O in the module.

## Out of scope

- Deciding *which* fallback applies when parsing fails — that belongs to the
  config layer (#03) and the command layer (#06), which differ on purpose.
