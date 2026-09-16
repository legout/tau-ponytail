# Implementation Issues

This directory splits [PLAN.md](../PLAN.md) into self-contained, PR-sized
issues. Each file restates the context needed to implement it without reading
the whole plan, but the plan remains the source of truth for design rationale.

## Conventions for every issue

- Python `>=3.12`; runtime dependencies limited to the standard library.
- Only Tau's public `ExtensionAPI`; no private session/TUI internals, no
  Tau-core changes in this repository.
- Upstream Ponytail-derived text keeps its MIT attribution.
- After implementation, all four checks must pass:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

## Dependency order

Issues can start once their dependencies are merged. `#05`–`#09` are
independent of each other once `#01`–`#05` are done.

| #  | Issue                                            | Depends on  |
|----|--------------------------------------------------|-------------|
| 01 | [Scaffolding and toolchain](01-scaffolding.md)   | —           |
| 02 | [Mode model and normalization](02-mode-model.md) | 01          |
| 03 | [Configuration resolution and persistence](03-config.md) | 01, 02 |
| 04 | [Instruction provider](04-instructions.md)       | 01, 02      |
| 05 | [Extension core: setup and runtime state](05-extension-core.md) | 01, 02, 03 |
| 06 | [`/ponytail` command](06-ponytail-command.md)    | 05          |
| 07 | [Natural-language deactivation](07-deactivation.md) | 05         |
| 08 | [Per-request instruction injection](08-context-injection.md) | 04, 05 |
| 09 | [Skill shortcut commands](09-skill-shortcuts.md) | 05          |
| 10 | [Real-runtime integration tests](10-integration-tests.md) | 06, 07, 08, 09 |
| 11 | [Documentation](11-documentation.md)             | 05–09       |
| 12 | [Release gate](12-release-gate.md)               | all         |
