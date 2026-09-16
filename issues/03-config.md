# Issue 03: Configuration resolution and persistence

**Plan phase:** 1 — package and configuration (design decision 2)
**Depends on:** #01 scaffolding, #02 mode model
**Size:** M

## Context

The extension resolves one persisted setting — the default mode — and never
persists the active mode (that is session-lived, see #05). Resolution
precedence, highest first:

1. `PONYTAIL_DEFAULT_MODE` environment variable;
2. `defaultMode` in `config.json` under:
   - `$XDG_CONFIG_HOME/ponytail/config.json` when `XDG_CONFIG_HOME` is set,
   - otherwise `~/.config/ponytail/config.json` on POSIX,
   - otherwise the normal `%APPDATA%`\ponytail\config.json location on Windows;
3. fallback `full`.

Invalid, missing, or unsupported configuration at any layer falls back to
`full` without raising. `/ponytail default <mode>` (implemented in #06) will
write `defaultMode` only, preserving unrelated JSON keys in the file.

## Tasks

- Implement in `src/tau_ponytail/config.py`:
  - `config_path(env: Mapping[str, str] | None = None) -> Path` implementing
    the platform resolution above (env injectable for tests);
  - `resolve_default_mode(env: Mapping[str, str] | None = None,
    path: Path | None = None) -> Mode`: env var → file → `full`; tolerant of
    missing files, invalid JSON, BOM-prefixed JSON, non-string/wrong-typed
    `defaultMode`, and unwritable-adjacent errors (never raise for reads);
  - `write_default_mode(mode: Mode, path: Path | None = None,
    env: Mapping[str, str] | None = None) -> None`: reads any existing JSON,
    sets `defaultMode`, preserves unrelated keys, creates parent directories,
    writes atomically (temp file + replace) so a crash cannot truncate the
    config.
- Pure-stdlib implementation; all environment and filesystem access injectable
  for deterministic tests.

## Acceptance criteria

- [ ] Env var wins over file; file wins over `full`; nothing set → `full`.
- [ ] Invalid env value (`PONYTAIL_DEFAULT_MODE=banana`) → `full`, not the
      file value — an explicitly *invalid* higher-precedence value must not
      silently fall through to a lower layer unless tests record that choice
      deliberately; pick one behavior and test it (plan: fall back to `full`).
- [ ] Missing file, malformed JSON, BOM-prefixed JSON, and
      `{"defaultMode": 3}` all resolve to `full` without raising.
- [ ] Writing `lite` into
      `{"defaultMode": "ultra", "theme": {"accent": "red"}}` yields
      `{"defaultMode": "lite", "theme": {"accent": "red"}}` with key order and
      unrelated data preserved.
- [ ] Write creates parent directories; tests use `tmp_path` and monkeypatched
      env, never the developer's real config.

## Out of scope

- Any Tau API usage — this module is pure Python and has no imports from Tau.
