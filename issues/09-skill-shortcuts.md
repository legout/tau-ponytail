# Issue 09: Skill shortcut commands

**Plan phase:** 3 — Tau extension behavior (design decision 4)
**Depends on:** #05 extension core
**Size:** S

## Context

Upstream Ponytail ships review/audit/debt/gain/help skills. This extension
does **not** reimplement or bundle those skill bodies in v1 — they are
portable resources users install separately under Tau's `.tau/skills` or
`.agents/skills` directories. The extension only registers thin aliases that
queue the corresponding skill command:

- `/ponytail-review` → queue `/skill:ponytail-review`
- `/ponytail-audit`  → queue `/skill:ponytail-audit`
- `/ponytail-debt`   → queue `/skill:ponytail-debt`
- `/ponytail-gain`   → queue `/skill:ponytail-gain`
- `/ponytail-help`   → queue `/skill:ponytail-help`

Aliases must work both while idle and **while an agent run is active**, using
`tau.send_user_message(..., deliver_as="follow_up")` so the queued command is
delivered after the current run rather than dropped. If the skill is not
installed, the extension ships a short help response instead of an opaque
failure.

## Tasks

- Implement the five alias handlers in `src/tau_ponytail/commands.py` as one
  parameterized factory (no five copies of the same handler).
- Register all five in `setup(tau)`.
- Queue via `send_user_message` with `deliver_as="follow_up"`.
- Skill-unavailable fallback: decide how detection works on the current Tau
  API (e.g. the `/skill` command's own error, or a capability check if one
  exists). If detection is not reliably available in v1, fall back to
  notifying "queued; install the Ponytail skills under .tau/skills" — record
  the chosen mechanism.
- `review` is not a mode: ensure no shortcut ever changes the active mode.

## Acceptance criteria

- [ ] Each alias queues the corresponding `/skill:...` message with
      `follow_up` delivery; test asserts the queued payload for all five.
- [ ] Shortcut works while a (fake) run is active — the message is queued,
      not rejected.
- [ ] No shortcut touches mode state.
- [ ] A missing skill produces the short help response; no stack trace.

## Out of scope

- Copying or rewriting Ponytail skill bodies (explicit non-goal).
