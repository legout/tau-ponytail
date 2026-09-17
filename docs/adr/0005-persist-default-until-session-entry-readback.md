---
status: accepted
approved: 2026-09-17
supersedes: 0003-persist-default-not-active-mode.md
source: ../specs/tau-ponytail-v1.md
---

# Persist only the configured default until public readback exists

The active Ponytail mode remains mutable state owned by one `setup(tau)` generation. Every `session_start` resets it to the resolved configured default; only `defaultMode` is persisted in environment or configuration.

Upstream Ponytail records mode changes as custom session entries and restores the latest entry when a session starts. Tau exposes public asynchronous custom-entry writes, but its extension lifecycle does not expose public custom-entry readback at `session_start`. Writing state that cannot be restored would add durable noise without delivering parity. Reading Tau's private session structures is outside the extension boundary.

Awaitable command handlers remove the old background-task concern but do not provide readback. Session-level active-mode persistence can supersede this decision when Tau exposes a public replay/read contract. Until then, deterministic reset is the closest complete behavior available through public APIs.
