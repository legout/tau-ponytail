---
status: approved
approved: 2026-09-16
source: ../../PLAN.md
planning-contract: 1
---

# Tau Ponytail v1 behavior

## Status and authority

This behavioral specification was approved by the owner on 2026-09-16. It was derived from [PLAN.md](../../PLAN.md), which remains design evidence; this document owns the observable behavior and acceptance criteria.

The vocabulary is defined in [CONTEXT.md](../../CONTEXT.md). The architectural rationale is recorded in [ADR 0001](../adr/0001-standalone-public-tau-extension.md), [ADR 0002](../adr/0002-ephemeral-context-injection.md), and [ADR 0003](../adr/0003-persist-default-not-active-mode.md).

## Scope

The v1 extension adds Ponytail guidance to Tau while remaining usable in both TUI and print mode. It provides:

- four runtime modes;
- default-mode resolution and persistence;
- `/ponytail` mode and status commands;
- five shortcut commands for companion Ponytail skills;
- exact natural-language deactivation;
- per-provider-request guidance that is ephemeral rather than durable; and
- diagnostics that do not make ordinary Tau requests fail.

## Runtime modes

The extension recognizes exactly these modes:

| Mode | Required behavior |
| --- | --- |
| `off` | Add no Ponytail guidance to a provider request. |
| `lite` | Build the requested change and briefly name a simpler alternative. |
| `full` | Apply the YAGNI, standard-library/native, and smallest-safe-change ladder. This is the normal default. |
| `ultra` | Prefer deletion and the smallest working change aggressively. |

`review` is not a mode. Review is exposed through the dedicated shortcut command.

## Default resolution and active state

1. `PONYTAIL_DEFAULT_MODE` has highest precedence.
2. If the environment variable is absent, read `XDG_CONFIG_HOME/ponytail/config.json` on POSIX, or the normal `%APPDATA%` location on Windows.
3. A missing, invalid, or unsupported value resolves to `full`.
4. The active mode starts at the resolved default on `session_start`.
5. Mode commands change the active mode for the current runtime/session only.
6. Persisting a default changes only `defaultMode` and preserves unrelated JSON keys.
7. Invalid configuration and configuration write failures produce an actionable diagnostic but do not crash normal Tau operation.

## Commands

The registered command surface is:

- `/ponytail` enables the resolved default; if that default is `off`, it enables `full`, matching upstream behavior.
- `/ponytail lite`, `/ponytail full`, `/ponytail ultra`, and `/ponytail off` set the active mode.
- `/ponytail status` reports the active mode and configured default.
- `/ponytail default <mode>` persists one of the four modes as the configured default without changing unrelated configuration keys.
- Invalid `/ponytail` input returns a short usage/error response and does not change state.

Mode changes notify the user without requiring a Textual-specific status widget.

## Companion shortcuts

These commands queue the corresponding skill request:

- `/ponytail-review` → `ponytail-review`;
- `/ponytail-audit` → `ponytail-audit`;
- `/ponytail-debt` → `ponytail-debt`;
- `/ponytail-gain` → `ponytail-gain`; and
- `/ponytail-help` → `ponytail-help`.

Shortcuts work while idle and while an agent run is active. If a shortcut skill is unavailable, the extension returns a short help response rather than failing the request.

## Request guidance

For every provider request, the extension evaluates the active mode:

- non-`off` modes contribute exactly one active Ponytail instruction message;
- `off` contributes nothing; and
- injected guidance is ephemeral and must not appear in durable messages, events, or session persistence.

The extension does not make provider requests fail because configuration or command diagnostics are malformed. The injected text is behavioral guidance, not a user task, and retains the upstream Ponytail MIT attribution.

## Natural-language deactivation

The input hook recognizes only a whole input equal to `stop ponytail` or `normal mode`, ignoring case and trailing whitespace. It also accepts trailing `.`, `!`, `?`, `,`, or `;` after whitespace is trimmed. A matching input sets the active mode to `off`, notifies the user, and is consumed rather than sent to the model.

Ordinary prompts that merely contain those words are forwarded unchanged. Slash-command state changes are handled by the registered `/ponytail` command and are not inferred from the input hook.

## Packaging and compatibility

- A clean checkout loads through `tau -e /path/to/tau-ponytail` and the `[tool.tau]` manifest.
- The extension uses Tau's public Python extension API and no Tau-core changes.
- Runtime dependencies remain Python standard library only; no JavaScript runtime or Textual-specific code is required.
- The extension does not reimplement or bundle the companion skill bodies; users install those portable skills separately.

## Non-goals

- JavaScript runtime or direct reuse of the Pi extension;
- Context Mode/MCP integration;
- Tau core changes;
- branch-level active-mode persistence in v1;
- a custom sidebar or status widget;
- reimplementation of review/audit/debt/gain/help skill bodies;
- automatic modification of an existing `AGENTS.md` or global configuration; and
- remote GitHub repository creation during local setup.

## Acceptance criteria

1. A clean checkout loads through `tau -e` and the `[tool.tau]` manifest.
2. `/ponytail`, the four explicit mode commands, `status`, and `default <mode>` produce the specified state and output.
3. `status` reports current and configured default modes.
4. `default <mode>` persists only the configured default, preserves unrelated keys, and honors environment precedence on the next startup.
5. Every provider request receives exactly the active mode's instructions when the mode is not `off`; `off` adds nothing.
6. Injected instructions are absent from Tau's durable messages, events, and session persistence.
7. `stop ponytail` and `normal mode` deactivate only as standalone inputs, accept case/whitespace variants plus trailing `.`, `!`, `?`, `,`, or `;`, and are consumed.
8. All five shortcut commands work while idle and while an agent run is active.
9. Missing/invalid configuration and write errors are actionable but do not crash ordinary Tau operation.
10. The extension works without Textual-specific code or third-party runtime dependencies, and the documented repository checks pass.

## Source traceability

| Behavioral area | PLAN source |
| --- | --- |
| Modes, defaults, and persistence | Design decisions 2–3; phases 1–2 |
| Commands and shortcuts | Design decision 4; phase 3 |
| Deactivation | Design decision 5; phase 3 |
| Per-request guidance | Design decision 1; phase 3 |
| Runtime loading, tests, and release validation | Evidence and constraints; phases 1, 3–5 |
