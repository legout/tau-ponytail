---
status: superseded
approved: 2026-09-16
superseded: 2026-09-17
superseded-by: 0004-run-scoped-system-prompt-guidance.md
source: ../../PLAN.md
---

# Inject Ponytail guidance through ephemeral request context

The extension will append the active Ponytail guidance through Tau's existing per-request `context` hook as one ephemeral `UserMessage`, rather than changing Tau core to add a dynamic system-prompt hook. This preserves the public API boundary, applies to provider follow-up requests, and keeps guidance out of durable messages and session history; a future provider-neutral system-prompt seam can replace this mechanism without changing the user-facing mode or command surface.

The behavior must be exactly once per provider request when the mode is not `off`, and absent when it is `off`.
