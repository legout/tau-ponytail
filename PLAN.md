# Plan: Ponytail for Tau

## Status

Superseded for execution by the approved
[behavioral specification](docs/specs/tau-ponytail-v1.md) and approved
[implementation plan](docs/plans/tau-ponytail-v1.md). This document is retained
as historical design evidence. Its `context`-hook and synchronous-command assumptions
were replaced by the public Tau prerequisites proposed and implemented in
[huggingface/tau#732](https://github.com/huggingface/tau/pull/732); do not execute
those obsolete sections.

## Goal

Port Ponytail's minimal-code discipline to Tau as a small, self-contained
Python extension. The first release should provide the useful behavior of the
Pi integration without adding a Tau-core dependency, a JavaScript runtime, or a
new persistence subsystem.

The extension will:

- inject the active Ponytail instructions into every provider request;
- support `off`, `lite`, `full`, and `ultra` modes;
- provide `/ponytail` mode and status commands;
- provide shortcuts for Ponytail's review/audit/debt/gain/help skills;
- resolve a default mode from an environment variable, a config file, or
  `full`;
- remain usable in both TUI and print mode.

## Evidence and constraints

The design is based on:

- upstream Ponytail: `https://github.com/DietrichGebert/ponytail`;
- the upstream Pi extension's mode/config/command behavior;
- Tau's public extension guide and examples;
- Tau's `context` hook, which is already available on the current
  `feat/pi-extension-ports` branch.

Tau extensions are synchronous `setup(tau)` Python modules. Commands are
synchronous; event handlers may be async. Tau's extension installer accepts a
repository containing `extension.py` or a `[tool.tau].extensions` manifest and
does not install Python dependencies.

## Smallest viable architecture

```text
Tau ExtensionAPI
  setup()
    ├─ register `/ponytail` and shortcut commands
    ├─ subscribe to `session_start`
    ├─ subscribe to `input`
    └─ subscribe to `context`
          └─ append the active Ponytail instructions ephemerally
```

Proposed files:

```text
pyproject.toml
README.md
LICENSE
AGENTS.md
src/tau_ponytail/
  __init__.py
  extension.py
  config.py
  instructions.py
  commands.py
tests/
  test_config.py
  test_instructions.py
  test_extension.py
```

The `[tool.tau]` manifest will point at
`src/tau_ponytail/extension.py`. The package may also be a normal Python
package for editor/type-checker support, but Tau will load the declared entry
file directly and will not pip-install it.

## Design decisions

### 1. Use Tau's `context` hook, not a Tau-core change

Ponytail's Pi adapter changes the system prompt before each agent run. Tau's
public extension API does not currently expose a dynamic system-prompt hook,
and adding one would make this small port a Tau-core feature.

The extension will instead return one ephemeral `UserMessage` from the
`context` hook containing the active Ponytail instructions. This runs for each
provider request, including tool-follow-up requests, and is not persisted or
shown in the transcript. It uses the existing append-only context seam and
keeps all implementation in `tau_coding` extension space.

The instructions must clearly identify themselves as behavioral guidance, not
as a user task. A focused provider smoke test will validate that the message is
present exactly once per request and never enters durable history. If a future
Tau API provides a provider-neutral dynamic system-prompt seam, migrating to it
will be a follow-up rather than a reason to expand this first release.

### 2. Keep mode state process-local; persist only the default

- `PONYTAIL_DEFAULT_MODE` has highest precedence.
- Otherwise read `XDG_CONFIG_HOME/ponytail/config.json`, or
  `~/.config/ponytail/config.json` on POSIX and the normal `%APPDATA%` location
  on Windows.
- Invalid, missing, or unsupported configuration falls back to `full`.
- `/ponytail default <mode>` writes only `defaultMode` and preserves unrelated
  JSON keys.
- The active mode belongs to the extension runtime generation and resets to the
  resolved default on `session_start`.

This intentionally does not reproduce Pi's branch-level custom session entry.
Tau command handlers are synchronous while `append_entry` is async; starting an
unowned background persistence task would be less safe than omitting it. Add
session-level persistence only when Tau exposes a synchronous or explicitly
scheduled extension persistence contract.

### 3. Match Ponytail's four runtime levels

- `off`: no instruction injection.
- `lite`: build the requested change and name a simpler alternative briefly.
- `full`: enforce the YAGNI/stdlib/native/minimum ladder; this is the default.
- `ultra`: aggressively prefer deletion and the smallest working change.

Instruction bodies will be kept in a readable, versioned Python module (or
packaged Markdown resource if that makes synchronization with upstream less
error-prone). Mode-specific text should be selected without stringly-typed
partial mutations. Upstream-derived text will retain its MIT attribution.

`review` is not a runtime mode. The review command invokes the dedicated
`ponytail-review` skill instead of changing the persistent mode.

### 4. Commands should be thin adapters

`/ponytail` behavior:

- no argument: enable the resolved default, except that a default of `off`
  enables `full`, matching upstream;
- `lite`, `full`, `ultra`, `off`: set the active mode;
- `status`: report current and configured default;
- `default <mode>`: write the default config;
- invalid input: return a short usage/error message without changing state.

Register these aliases:

- `/ponytail-review` → queue `/skill:ponytail-review`;
- `/ponytail-audit` → queue `/skill:ponytail-audit`;
- `/ponytail-debt` → queue `/skill:ponytail-debt`;
- `/ponytail-gain` → queue `/skill:ponytail-gain`;
- `/ponytail-help` → queue `/skill:ponytail-help`.

Use `context.api.send_user_message(..., deliver_as="follow_up")` for shortcut
commands so an alias works while a run is active. The extension will not
reimplement the skill picker or copy all skill files in the first release;
those are portable resources that users can install separately under Tau's
`.tau/skills` or `.agents/skills` directories. The bundled extension will ship
a short help response if a shortcut skill is unavailable.

### 5. Deactivation must be exact

The `input` hook will recognize only a whole input equal to `stop ponytail` or
`normal mode`, ignoring case and trailing punctuation/whitespace. It will set
`off` and leave ordinary prompts containing those words untouched.

Because Tau may handle slash commands before the normal prompt path, `/ponytail`
state changes are handled by the registered command, not by the input hook.

### 6. Avoid UI coupling

The first version will use `tau.notify` for mode changes and will not add a
status-bar/sidebar indicator. That keeps it functional in print mode and avoids
requiring Textual. A sidebar status can be added later using the documented
feature-detected `context.ui.sidebar` API if it proves useful.

## Implementation phases

### Phase 1 — package and configuration

- Add `pyproject.toml` with Python `>=3.12`, project metadata, and the Tau
  extension manifest.
- Add the package skeleton and MIT attribution.
- Implement mode normalization, default resolution, platform config paths,
  tolerant JSON loading, and safe default-mode writes.
- Test precedence, invalid values, BOM handling, missing files, unrelated-key
  preservation, and environment isolation.

### Phase 2 — instruction provider

- Add the four mode instruction bodies, derived from upstream Ponytail.
- Add an `instructions_for_mode(mode)` function with a deterministic fallback.
- Keep `off` allocation-free/no-op at the extension boundary.
- Test mode-specific output and that no unsupported mode leaks into the prompt.

### Phase 3 — Tau extension behavior

- Implement `setup(tau)` and runtime state.
- Register `/ponytail`, `status`, `default`, and mode parsing.
- Register the five skill shortcut commands.
- Add `session_start` default initialization.
- Add exact natural-language deactivation through `input`.
- Add `context` injection using `ContextHookResult` and `UserMessage`.
- Contain malformed configuration and command-write failures with diagnostics or
  concise notifications; never make ordinary agent requests fail.

### Phase 4 — real-runtime tests and documentation

- Load the extension through `ExtensionRuntime` with hermetic `TauResourcePaths`.
- Use a fake bound session/provider to prove registration, command behavior,
  hook chaining, ephemeral context, reload/session-start reset, print-mode
  operation, and shortcut delivery.
- Document installation with `tau -e` and `tau install` after the manifest is
  present, plus the separate optional skill installation.
- Document the deliberate difference from the Pi adapter: active mode is
  generation/session-lived, while the configured default is file-persisted.

### Phase 5 — release gate

Run:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

Then validate the packaged shape in a clean temporary Tau install:

```bash
tau -e /path/to/tau-ponytail -p "Use the simplest safe implementation"
```

Do not publish until the repository is loadable from a clean checkout and the
extension does not require dependencies outside Tau's environment.

## Acceptance criteria

1. A clean checkout loads through `tau -e` and the `[tool.tau]` manifest.
2. `/ponytail`, `/ponytail lite`, `/ponytail full`, `/ponytail ultra`, and
   `/ponytail off` produce the expected active mode.
3. `status` reports current and configured default modes.
4. `default <mode>` persists only the configured default and honors environment
   precedence on the next startup.
5. Every provider request receives exactly the active mode's instructions when
   mode is not `off`; `off` adds nothing.
6. Injected instructions are absent from Tau's durable messages, events, and
   session persistence.
7. `stop ponytail` and `normal mode` deactivate only when supplied as standalone
   commands, including trailing punctuation/case variants.
8. Shortcut commands work while idle and while an agent run is active.
9. Missing/invalid configuration and write errors are actionable but do not
   crash normal Tau operation.
10. The extension works without Textual-specific code or third-party runtime
    dependencies, and all documented checks pass.

## Explicit non-goals

- no JavaScript runtime or direct reuse of Ponytail's Pi extension;
- no Context Mode/MCP integration;
- no Tau core changes in this repository;
- no branch-level active-mode persistence in v1;
- no custom sidebar/status widget in v1;
- no reimplementation of Ponytail's review/audit/debt/gain/help skill bodies;
- no automatic modification of a user's existing `AGENTS.md` or global config;
- no remote GitHub repository creation as part of local project setup.

## Open follow-up

If users expect Ponytail instructions to be treated as system-level guidance
rather than an ephemeral user-context message, propose a separate generic Tau
API for dynamic per-request system-prompt additions and migrate the extension
without changing its mode/config/command surface.
