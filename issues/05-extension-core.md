# Issue 05: Extension core — setup, runtime state, session reset

**Plan phase:** 3 — Tau extension behavior (design decision 2)
**Depends on:** #01 scaffolding, #02 mode model, #03 config
**Size:** M

## Context

Tau extensions are synchronous `setup(tau)` Python modules using the public
`ExtensionAPI`; event handlers may be async. Every runtime generation (reload,
resume, new session, cwd replacement) calls `setup` fresh, and retiring a
generation invalidates captured APIs — so all extension state must be created
inside `setup` and owned by that generation.

State model (deliberately different from Ponytail's Pi adapter):

- The **default mode** is file/env persisted (#03).
- The **active mode** is process-local, owned by the runtime generation, and
  resets to the resolved default on every `session_start`.

There is intentionally no branch-level persistence of the active mode: Tau
command handlers are synchronous while session `append_entry` is async, and
starting an unowned background persistence task would be less safe than
omitting it.

## Tasks

- Implement `setup(tau)` in `src/tau_ponytail/extension.py`:
  - resolve the default mode via `config.resolve_default_mode()` once;
  - create a per-generation state object (e.g. dataclass with
    `default_mode`, `active_mode`) — never module-level mutable globals;
  - subscribe a `session_start` handler that resets `active_mode` to the
    (re-resolved or cached) default.
- Contain malformed configuration: any exception from config resolution during
  `setup` or `session_start` must degrade to `full` with a diagnostic
  (`tau.notify(..., level="warning")`), never fail extension load.
- Keep `commands.py` ready to receive the state object (registration of
  commands happens in #06–#09).
- Do not capture the `tau` API object in long-lived structures beyond the
  generation's lifetime.

## Acceptance criteria

- [ ] Loading the extension through Tau's real `ExtensionRuntime` (or the
      closest test harness available) runs `setup` without error.
- [ ] `session_start` resets the active mode to the resolved default,
      including after a mode change within the previous session.
- [ ] With a poisoned config file (invalid JSON), setup still succeeds and
      the default resolves to `full` with one warning notification.
- [ ] No module-level mutable state; two simulated generations do not share
      state.

## Out of scope

- Command registration (#06, #09), deactivation (#07), injection (#08).
