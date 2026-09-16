# Issue 08: Per-request instruction injection via `context` hook

**Plan phase:** 3 — Tau extension behavior (design decision 1)
**Depends on:** #04 instruction provider, #05 extension core
**Size:** M

## Preconditions

- Requires a Tau build exposing the `context` hook (available on the
  `feat/pi-extension-ports` branch). **Verify the installed Tau exposes it
  before starting**; if the seam is missing or shaped differently, this issue
  blocks on the Tau branch, not on a workaround in this repository.

## Context

Ponytail's Pi adapter edits the system prompt before each run. Tau's public
API has no dynamic system-prompt hook, and adding one would make this port a
Tau-core feature. Instead the extension returns **one ephemeral `UserMessage`**
from the `context` hook containing the active mode's instructions:

- the hook runs for each provider request, including tool-follow-up requests;
- the appended context is ephemeral: not persisted, not shown in the
  transcript, never entering durable history;
- when the active mode is `off`, the hook returns nothing (allocation-free,
  per #04);
- the message must identify itself as behavioral guidance, not a user task.

If a future Tau API provides a provider-neutral dynamic system-prompt seam,
migrating to it is a follow-up, not part of this issue.

## Tasks

- Subscribe to the `context` event in `setup(tau)` and return a
  `ContextHookResult` carrying one `UserMessage` built from
  `instructions_for_mode(state.active_mode)`.
- Wrap the message body with a short framing sentence identifying it as
  behavioral guidance from the Ponytail extension (kept constant across
  modes so #10 can assert presence and count).
- `off` → return the empty/no-op result without building any message.
- Contain failures: any exception in the hook must be caught and degraded to
  a no-op (optionally one diagnostic); ordinary agent requests must never
  fail because of injection.
- Verify against the real hook contract on the branch: result type, message
  type, whether handlers may be async, and how multiple subscribers compose
  (chaining must not drop or duplicate other extensions' context).

## Acceptance criteria

- [ ] With active mode `full`, each provider request (initial and
      tool-follow-up) receives exactly one injected message containing the
      `full` body's content marker.
- [ ] Switching to `lite`/`ultra` changes the injected body; `off` injects
      nothing.
- [ ] Injected text is absent from durable session messages and events in
      the test harness.
- [ ] Hook chaining: injection composes with another (fake) `context`
      subscriber without dropping either contribution.
- [ ] A forced internal error (e.g. poisoned state) does not fail the
      provider request.

## Out of scope

- Migrating to a future system-prompt seam (tracked in PLAN.md "Open
  follow-up").
- Exact once-per-request and durability assertions at the provider level —
  #10 hardens these into the integration suite.
