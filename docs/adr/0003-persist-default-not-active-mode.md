---
status: superseded
approved: 2026-09-16
superseded: 2026-09-17
superseded-by: 0005-persist-default-until-session-entry-readback.md
source: ../../PLAN.md
---

# Persist the configured default, not the active mode

The active Ponytail mode is process-local and resets to the resolved configured default at `session_start`; only the default is persisted in environment/configuration. This keeps command state deterministic and avoids starting an unowned background persistence task when Tau command handlers are synchronous but `append_entry` is asynchronous. Branch-level or session-level active-mode persistence is deferred until Tau exposes an explicit extension persistence contract.
