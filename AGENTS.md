# Project Instructions

- Target Python >=3.12, matching Tau's extension contract.
- Keep runtime dependencies to the Python standard library.
- Use Tau's public `ExtensionAPI`; do not reach into private Tau session or TUI internals.
- Keep the extension small: prompt behavior, slash commands, and mode configuration only.
- Use `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy` for checks once implementation exists.
- Test through Tau's real extension runtime with deterministic fakes.
- Keep Ponytail-derived instruction text and mode behavior attributable to the upstream MIT-licensed project.
