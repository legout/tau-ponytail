# Issue 01: Scaffolding and toolchain

**Plan phase:** 1 — package and configuration
**Depends on:** none
**Size:** S

## Context

The repository currently contains only `README.md`, `PLAN.md`, and `AGENTS.md`;
no implementation exists. This issue creates the package skeleton, build
metadata, Tau extension manifest, licensing, and development tooling so every
later issue has a place to land and a working check loop.

Tau's extension installer accepts a repository containing `extension.py` or a
`[tool.tau].extensions` manifest. This project keeps its implementation in a
normal package (`src/tau_ponytail/`) and points the manifest at
`src/tau_ponytail/extension.py`. Tau loads the declared entry file directly and
does not pip-install the package, so the layout must work both as a loaded
entry file (relative imports are unreliable — import siblings through the
package) and for editor/type-checker support.

## Tasks

- Add `pyproject.toml`:
  - `requires-python = ">=3.12"`, project metadata for `tau-ponytail`;
  - `[tool.tau]` manifest declaring `src/tau_ponytail/extension.py` as the
    extension entry;
  - dev dependency group for `pytest`, `ruff`, and `mypy` (dev-only; runtime
    stays stdlib);
  - tool configuration for ruff and mypy.
- Add the package skeleton under `src/tau_ponytail/`:
  - `__init__.py` (public exports, package docstring);
  - empty stub modules `extension.py`, `config.py`, `instructions.py`,
    `commands.py` with module docstrings describing their future role.
- Add `LICENSE` (MIT, copyright per upstream Ponytail and this project) and an
  attribution note in the README crediting
  `https://github.com/DietrichGebert/ponytail` (MIT).
- Add a minimal `tests/` package with one placeholder test that imports the
  package, so the check loop is real from the start.
- Update `README.md` status wording if it still says "plan only".

## Acceptance criteria

- [ ] `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`,
      and `uv run mypy` all pass on the skeleton.
- [ ] `python -c "import tau_ponytail"` works from the project root via the
      uv environment (src layout configured).
- [ ] The `[tool.tau]` manifest names the entry file; no code outside
      `src/tau_ponytail/` and `tests/`.
- [ ] No runtime dependencies declared beyond the standard library.

## Out of scope

- Any behavior: no config parsing, instructions, commands, or hooks.
