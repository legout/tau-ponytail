# tau-ponytail

Ponytail's minimal-code discipline as a standalone [Tau](https://github.com/huggingface/tau)
extension. Four intensity modes (`off`, `lite`, `full`, `ultra`) inject Ponytail's
run-scoped guidance into the system prompt of each agent run through Tau's public
extension API — no Tau-core changes, no third-party runtime dependencies.

The behavioral contract is the approved
[specification](docs/specs/tau-ponytail-v1.md); rationale lives in
[docs/adr/](docs/adr/), the execution map in
[docs/plans/tau-ponytail-v1.md](docs/plans/tau-ponytail-v1.md), and domain
vocabulary in [CONTEXT.md](CONTEXT.md).

## Requirements

- Python >= 3.12
- A Tau build containing the two public extension seams from
  [huggingface/tau#732](https://github.com/huggingface/tau/pull/732): the
  run-scoped `before_agent_start` system-prompt hook and awaitable
  slash-command handlers.

**Minimum released Tau version:** none yet. No official Tau release contains
the required seams (Tau 0.4.4 predates them), and huggingface/tau#732 is still
open. Until a release including it ships, run Tau from the pinned development
commit `bad16acf984dbe921ecbe18e57b75b362c04ff55` or any local checkout
containing that change. This section will name the minimum version as soon as
that release exists.

## Installation

Load directly from a checkout:

```bash
tau -e /path/to/tau-ponytail
```

or install it as a trusted extension:

```bash
tau install git:github.com/legout/tau-ponytail
```

The extension declares itself through the `[tool.tau]` manifest in
`pyproject.toml` and installs no Python dependencies.

For development, the repository pins a Tau build with the required seams as a
dev dependency (see `[dependency-groups]` in `pyproject.toml`):

```bash
uv sync
uv run pytest
```

## Usage

```text
/ponytail                     # enable the resolved default (a default of off enables full)
/ponytail lite|full|ultra|off # set the active mode
/ponytail status              # current and default modes, e.g. "Ponytail: current full • default lite"
/ponytail default lite|full|ultra|off   # persist the configured default
```

Natural-language deactivation: sending `stop ponytail` or `normal mode` as a
whole input (case/whitespace tolerant, optional trailing `.`, `!`, or `?`)
switches the mode to `off`; the prompt still reaches the model unchanged.
Phrases embedded in longer requests never match.

Companion shortcuts queue the corresponding Ponytail skill and work both while
idle and as a follow-up during an active run:

```text
/ponytail-review
/ponytail-audit
/ponytail-debt
/ponytail-gain
/ponytail-help
```

These send `/skill:ponytail-*` requests; the skills themselves are optional
portable resources you can install separately under Tau's skill directories.
Print mode (`tau -e ... -p "..."`) is fully supported.

## Configuration

Default-mode precedence: `PONYTAIL_DEFAULT_MODE` environment variable, then
`config.json`, then `full`. Invalid or missing values fall back with an
actionable warning instead of crashing.

- Environment values are lowercased but not trimmed (upstream parity).
- `quietStartup`: set `PONYTAIL_QUIET_STARTUP` (any value except `0`, `false`,
  `no`, or empty means true) or `"quietStartup": true` in `config.json`; the
  environment variable wins. Quiet startup suppresses only the
  `Ponytail loaded: <mode>` notification.
- `/ponytail default <mode>` writes only `defaultMode`, preserves unrelated
  keys, and replaces the file atomically. An environment override still wins
  over the persisted value.

Config file location: `$XDG_CONFIG_HOME/ponytail/config.json`, else
`~/.config/ponytail/config.json` on POSIX and `%APPDATA%/ponytail/config.json`
on Windows:

```json
{
  "defaultMode": "lite",
  "quietStartup": false
}
```

## Differences from the Pi adapter

- **Active mode is session-local.** The active mode resets to the resolved
  default on every `session_start` and is not restored across sessions. Pi
  persists the active mode as a custom session entry; Tau exposes no public
  custom-entry readback yet, so only the configured default is persisted
  (ADR 0005).
- **No status indicator.** Upstream's sidebar widget and `hideStatus` option
  are omitted because Tau has no public status seam. Use `/ponytail status`
  instead, and `quietStartup` to silence the startup notification.

## Development checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

## License

MIT — see [LICENSE](LICENSE). Derived from upstream
[Ponytail](https://github.com/DietrichGebert/ponytail) 4.10.0 (MIT, Copyright
(c) 2026 DietrichGebert); its complete notice is preserved in `LICENSE` and the
instruction bodies in `src/tau_ponytail/instructions.py`.
