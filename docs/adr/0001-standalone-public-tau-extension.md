---
status: accepted
approved: 2026-09-16
source: ../../PLAN.md
---

# Keep Ponytail as a standalone public Tau extension

Ponytail will be delivered as a small Python extension loaded through Tau's public `ExtensionAPI` and `[tool.tau]` manifest, with only Python standard-library runtime dependencies. This avoids a Tau-core change, a JavaScript runtime, and direct reuse of Pi internals; those alternatives would widen the integration boundary for a behavior that belongs in extension space.

The extension remains installable from a clean checkout without pip-installed application dependencies. Tau's documented extension contract and the upstream Ponytail MIT attribution are the compatibility boundaries.
