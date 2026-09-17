---
status: approved
approved: 2026-09-17
revision: 2
supersedes-approved-sha256: 0373d0e9f16b10b1013bd6a8de95c3c44f176a900210fe186a49dbb7358d2e2b
source: ../../PLAN.md
planning-contract: 1
prerequisite: https://github.com/huggingface/tau/pull/732
---

# Tau Ponytail v1 behavior

## Status and authority

The owner approved this revision on 2026-09-17. It reconciles the 2026-09-16 specification with upstream Ponytail 4.10.0 and Tau's implemented public prerequisite seams, and now owns the observable v1 behavior and acceptance criteria.

The vocabulary is defined in [CONTEXT.md](../../CONTEXT.md). Architectural rationale is recorded in [ADR 0001](../adr/0001-standalone-public-tau-extension.md), [ADR 0004](../adr/0004-run-scoped-system-prompt-guidance.md), and [ADR 0005](../adr/0005-persist-default-until-session-entry-readback.md). ADRs 0004 and 0005 supersede ADRs 0002 and 0003.

## Scope

The v1 extension adds Ponytail guidance to Tau while remaining usable in both TUI and print mode. It provides:

- four runtime modes;
- default-mode resolution and persistence;
- `/ponytail` mode, status, and default commands;
- five shortcut commands for companion Ponytail skills;
- exact natural-language deactivation without swallowing the user's prompt;
- run-scoped system-prompt guidance that is never durable; and
- diagnostics that do not make ordinary Tau requests fail.

## Runtime modes

The extension recognizes exactly these modes:

| Mode | Required behavior |
| --- | --- |
| `off` | Leave the run's system prompt unchanged. |
| `lite` | Build the requested change and briefly name a simpler alternative. |
| `full` | Apply the YAGNI, standard-library/native, and smallest-safe-change ladder. This is the normal default. |
| `ultra` | Prefer deletion and the smallest working change aggressively. |

`review` is not a mode. Review is exposed through the dedicated shortcut command.

Instruction text and composition are derived from upstream `@dietrichgebert/ponytail` 4.10.0 and retain its MIT attribution. Each active mode emits the complete common instruction body plus only that mode's intensity row and worked example.

## Default resolution and active state

1. `PONYTAIL_DEFAULT_MODE` has highest precedence.
2. If the environment variable is absent, read `XDG_CONFIG_HOME/ponytail/config.json` on any platform; otherwise use `~/.config/ponytail/config.json` on POSIX or the normal `%APPDATA%` location on Windows.
3. A missing, invalid, or unsupported value resolves to `full`.
4. The active mode starts at the resolved default on every `session_start`.
5. Mode commands change the active mode for the current bound session/generation only.
6. Persisting a default changes only `defaultMode` and preserves unrelated JSON keys.
7. `PONYTAIL_QUIET_STARTUP` overrides `quietStartup` in the same config file. Empty, `0`, `false`, and `no` mean false; any other non-empty value means true.
8. Unless startup is quiet, `session_start` reports `Ponytail loaded: <mode>` through Tau's public notification API.
9. Missing configuration is normal. Invalid configuration and configuration write failures produce an actionable diagnostic but do not crash ordinary Tau operation.

Tau currently has no public extension readback for custom session entries, so active-mode restoration across resume/reload is not part of v1. Tau also has no public status-bar contribution API, so upstream `hideStatus` and the live status indicator are not implemented.

## Commands

The registered command surface is:

- `/ponytail` enables the resolved default; if that default is `off`, it enables `full`, matching upstream behavior.
- `/ponytail lite`, `/ponytail full`, `/ponytail ultra`, and `/ponytail off` set the active mode.
- `/ponytail status` reports the active mode and configured default.
- `/ponytail default <mode>` persists one of the four modes as the configured default without changing unrelated configuration keys.
- Invalid `/ponytail` input returns a short usage/error response and does not change state.

Mode changes notify the user through public Tau APIs without requiring a Textual-specific status widget. Command handlers may be synchronous or asynchronous under Tau's public contract; Tau Ponytail must not spawn detached persistence tasks.

## Companion shortcuts

These commands queue the corresponding skill request:

- `/ponytail-review` → `/skill:ponytail-review`;
- `/ponytail-audit` → `/skill:ponytail-audit`;
- `/ponytail-debt` → `/skill:ponytail-debt`;
- `/ponytail-gain` → `/skill:ponytail-gain`; and
- `/ponytail-help` → `/skill:ponytail-help`.

Shortcuts start a turn while idle and queue a follow-up while an agent run is active. They use only Tau's public `send_user_message` contract and do not reimplement skill discovery, expansion, a picker, or the skill bodies. An unavailable skill follows Tau's normal handling and must not crash the extension.

## Run guidance

Immediately before a new idle agent run, the extension evaluates the active mode through Tau's public `before_agent_start` hook:

- a non-`off` mode appends exactly one complete active Ponytail instruction to the supplied system prompt and returns the whole replacement prompt;
- `off` returns no replacement and leaves the prompt unchanged;
- an empty supplied prompt produces the instruction without an `None`/`undefined` prefix; and
- the transformed prompt governs every provider call in that run, including tool follow-ups.

Tau restores the base system prompt after every run exit path. Ponytail guidance must not appear in durable messages, events, custom entries, transcript persistence, or later `off` runs. Configuration or hook diagnostics must not make the request fail. The text remains behavioral system guidance rather than a user task.

## Natural-language deactivation

The input hook recognizes only a whole input equal to `stop ponytail` or `normal mode`, ignoring case, surrounding whitespace, and trailing `.`, `!`, or `?`. A matching input sets the active mode to `off` and notifies the user, but the original input continues to the model unchanged, matching upstream behavior.

Comma and semicolon suffixes do not match. Ordinary prompts that contain the phrases are forwarded unchanged without changing mode. Slash-command state changes are handled by the registered `/ponytail` command and are not inferred from the input hook.

## Packaging and compatibility

- A clean checkout loads through `tau -e /path/to/tau-ponytail` and the `[tool.tau]` manifest.
- The extension uses only Tau's public Python `ExtensionAPI`; it does not modify Tau core or access private session/TUI structures.
- Runtime dependencies remain Python standard library only; no JavaScript runtime or Textual-specific code is required.
- Development and integration tests use a Tau build containing [huggingface/tau#732](https://github.com/huggingface/tau/pull/732), currently represented by commit `bad16acf984dbe921ecbe18e57b75b362c04ff55` on the contributor fork.
- Release is blocked until those public seams ship in Tau and a minimum released Tau version can be documented.
- The extension does not reimplement or bundle the companion skill bodies; users install those portable skills separately.

## Non-goals

- JavaScript runtime or direct reuse of the Pi extension;
- Context Mode/MCP integration;
- private Tau access or Ponytail-specific Tau-core code;
- branch/session active-mode persistence before public custom-entry readback exists;
- a custom sidebar/status widget or inert `hideStatus` option;
- reimplementation of review/audit/debt/gain/help skill bodies;
- automatic modification of an existing `AGENTS.md` or global configuration; and
- remote GitHub repository creation during local setup.

## Acceptance criteria

1. A clean checkout loads through `tau -e` and the `[tool.tau]` manifest on a Tau build containing the two prerequisite seams.
2. `/ponytail`, the four explicit mode commands, `status`, and `default <mode>` produce the specified state and output.
3. `status` reports current and configured default modes; startup notification obeys environment/config `quietStartup` precedence.
4. `default <mode>` atomically persists only the configured default, preserves unrelated keys, and honors environment precedence on the next startup.
5. Each new run receives exactly one active instruction in its system prompt when the mode is not `off`; `off` leaves the prompt unchanged, and all provider calls in that run use the same transformed prompt.
6. The base system prompt is restored after success, error, or cancellation, and injected instructions are absent from durable messages, events, custom entries, and session persistence.
7. `stop ponytail` and `normal mode` deactivate only as standalone inputs, accept case/whitespace variants plus trailing `.`, `!`, or `?`, reject comma/semicolon suffixes, and still reach the model unchanged.
8. All five shortcut commands use the corresponding `/skill:ponytail-*` request while idle and as an active-run follow-up.
9. Missing/invalid configuration, write errors, and hook/command diagnostics are actionable but do not crash ordinary Tau operation.
10. The extension uses no private Tau/Textual API or third-party runtime dependency, retains upstream MIT attribution, and passes the documented repository and clean-load checks.

## Source traceability

| Behavioral area | Source |
| --- | --- |
| Instruction text, modes, defaults, quiet startup | Upstream Ponytail 4.10.0 skill/config/Pi adapter |
| Run-scoped system guidance | Upstream Pi `before_agent_start`; Tau PR #732 |
| Commands and shortcuts | Upstream Pi adapter; Tau public command/message APIs |
| Deactivation | Upstream `isDeactivationCommand` and Pi input handler |
| Active-state limitation | Tau public lifecycle/custom-entry APIs; ADR 0005 |
| Packaging, tests, and release validation | Repository constraints and implementation plan |
