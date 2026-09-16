# Issue 10: Real-runtime integration tests

**Plan phase:** 4 — real-runtime tests
**Depends on:** #06 command, #07 deactivation, #08 injection, #09 shortcuts
**Size:** L

## Context

Unit tests from earlier issues cover pure logic. This issue hardens the
extension against the **real Tau extension runtime**: actual `setup(tau)`
registration, command dispatch, hook composition, ephemeral context, reload
lifecycle, and print-mode operation — using deterministic fakes (fake bound
session, fake provider) rather than network calls, per the project's testing
rules.

The provider smoke test named in the plan validates design decision 1: the
injected instructions are present **exactly once per provider request** and
**never enter durable history**.

## Tasks

- Build a test harness that:
  - loads the extension through Tau's `ExtensionRuntime` with hermetic
    `TauResourcePaths` (temp dirs; never the developer's `~/.tau` or real
    config);
  - provides a fake bound session/provider that records provider requests,
    queued messages, notifications, and persisted session entries;
  - controls environment (`PONYTAIL_DEFAULT_MODE`, `XDG_CONFIG_HOME`) per test.
- Cover, end to end:
  - registration: `/ponytail` plus all five shortcut commands exist after
    load;
  - command behavior: mode set, `status`, `default` persistence with env
    precedence on reload;
  - hook chaining: this extension's `context` contribution coexists with a
    second fake `context` subscriber;
  - ephemeral injection: with a fake provider, assert exactly one injected
    message per request — initial prompt and a tool-follow-up turn — with the
    active mode's content marker; assert the text is absent from durable
    messages, events, and session persistence; `off` produces zero injected
    messages;
  - lifecycle: reload / `session_start` resets the active mode to the
    resolved default; a retired generation's captured APIs are not reused;
  - print mode: command + deactivation + injection paths work without a UI
    bridge (no Textual imports exercised);
  - shortcuts: idle and mid-run delivery via `follow_up`;
  - resilience: poisoned config file and simulated write failure during a
    session never break ordinary requests.
- Keep fakes deterministic; no sleeps, no network.

## Acceptance criteria

- [ ] All bullets above have at least one test in `tests/test_extension.py`
      (or a focused sibling).
- [ ] The suite runs green under `uv run pytest` in a clean checkout with no
      developer-local Tau state.
- [ ] Tests assert exact-once injection and durable-absence explicitly (these
      map to plan acceptance criteria 5 and 6).

## Out of scope

- Documentation (#11) and packaging validation in a real install (#12).
