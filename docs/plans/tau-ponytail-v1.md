---
status: approved
approved: 2026-09-17
source-spec: ../specs/tau-ponytail-v1.md
source-spec-sha256: 90c42fbd4eb6f52354dbca017da05bd42ab01918a278867b83c7bb9a930831f4
source-approved: 2026-09-17
planning-contract: 1
tracker: https://github.com/legout/tau-ponytail/issues
prerequisite-pr: https://github.com/huggingface/tau/pull/732
---

# Tau Ponytail v1 implementation plan

## Goal and authority

Implement the owner-approved revision 2 of [Tau Ponytail v1](../specs/tau-ponytail-v1.md) as a small, loadable Tau extension. The specification owns behavior, accepted ADRs own architectural rationale, and GitHub issues #1–#5 own canonical task bodies after reconciliation to this revision.

The earlier root [PLAN.md](../../PLAN.md) remains historical design evidence. Its ephemeral `context`-message and synchronous-command assumptions are superseded by Tau's implemented prerequisite design and [huggingface/tau#732](https://github.com/huggingface/tau/pull/732).

## Capture checkpoint

- **Vocabulary:** [CONTEXT.md](../../CONTEXT.md) defines Tau extension, Ponytail instruction, shortcut command, Ponytail mode, active mode, configured default, and mode deactivation.
- **Decisions:** ADR 0001 keeps a standalone public extension; accepted ADR 0004 uses run-scoped system-prompt transformation; accepted ADR 0005 keeps active state generation-local until public custom-entry readback exists.
- **Behavior:** specification revision 2 corrects deactivation forwarding/punctuation, adds quiet-startup parity, and pins development to the implemented Tau seams.
- **Upstream prerequisite:** Tau PR #732 is open at head `bad16acf984dbe921ecbe18e57b75b362c04ff55`. Local implementation may test against that exact public API; release remains blocked until an official Tau version contains it.
- **Tracker:** issue bodies are reconciled to specification revision 2 in this approval checkpoint before implementation begins.

## Constraints and assumptions

- Python `>=3.12`; runtime dependencies are limited to the standard library.
- Use only Tau's public `ExtensionAPI` and real extension runtime; do not access private session or TUI internals.
- All mutable state is created inside `setup(tau)` and belongs to that runtime generation.
- Ponytail-derived text retains the complete upstream MIT notice and identifies the 4.10.0 source snapshot.
- No JavaScript runtime, provider wrapper, monkey patch, durable prompt message, custom status widget, or bundled companion skills.
- `before_agent_start` returns the whole prompt, appending one instruction to the event prompt; it does not mutate durable session state.
- Natural-language deactivation changes state but returns no consuming/transformation result, so the original prompt continues unchanged.
- Security review: **n/a**. Runtime input is process environment plus user-owned local configuration, not an untrusted remote boundary. Atomic configuration replacement remains required to avoid local data loss.

## Requirement coverage

| Specification criterion | Canonical ticket(s) |
| --- | --- |
| 1. Clean checkout loads on prerequisite Tau | [#1](https://github.com/legout/tau-ponytail/issues/1), [#4](https://github.com/legout/tau-ponytail/issues/4), [#5](https://github.com/legout/tau-ponytail/issues/5) |
| 2. Mode, status, and default commands | [#2](https://github.com/legout/tau-ponytail/issues/2), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 3. Status plus quiet-startup precedence | [#1](https://github.com/legout/tau-ponytail/issues/1), [#2](https://github.com/legout/tau-ponytail/issues/2), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 4. Atomic default persistence and key preservation | [#2](https://github.com/legout/tau-ponytail/issues/2), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 5. Exact active instruction per run; `off` no-op | [#1](https://github.com/legout/tau-ponytail/issues/1), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 6. Prompt restoration and no durable guidance | [#1](https://github.com/legout/tau-ponytail/issues/1), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 7. Exact non-consuming natural-language deactivation | [#3](https://github.com/legout/tau-ponytail/issues/3), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 8. Five shortcuts work idle and active | [#3](https://github.com/legout/tau-ponytail/issues/3), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 9. Configuration/write/hook failures remain non-fatal | [#1](https://github.com/legout/tau-ponytail/issues/1), [#2](https://github.com/legout/tau-ponytail/issues/2), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 10. Public API, stdlib runtime, attribution, checks | [#1](https://github.com/legout/tau-ponytail/issues/1), [#4](https://github.com/legout/tau-ponytail/issues/4), [#5](https://github.com/legout/tau-ponytail/issues/5) |

## Execution order

The first three tickets remain sequential because they share the extension adapter and generation-local state. Ticket #4 proves the integrated behavior against Tau's real public runtime. Ticket #5 is the release-candidate gate and cannot complete until Tau publishes a release containing PR #732.

| Order | Canonical ticket | Depends on | Owned surface | Validation |
| --- | --- | --- | --- | --- |
| 1 | [#1 Loadable run-guidance tracer bullet](https://github.com/legout/tau-ponytail/issues/1) | approved revision 2; Tau PR #732 API | Package skeleton, modes/instructions/config reads, lifecycle, `before_agent_start`, focused tests | V1 `new-test`, normal risk |
| 2 | [#2 `/ponytail` commands and default persistence](https://github.com/legout/tau-ponytail/issues/2) | #1 | Atomic config writes, command adapter/registration, focused tests | V2 `new-test`, normal risk |
| 3 | [#3 Exact deactivation and companion shortcuts](https://github.com/legout/tau-ponytail/issues/3) | #2 | Input hook, shortcut adapters, focused tests | V3 `new-test`, normal risk |
| 4 | [#4 Tau real-runtime proof](https://github.com/legout/tau-ponytail/issues/4) | #3 | Runtime integration tests and candidate review | V4 `new-test`, normal risk |
| 5 | [#5 Documentation and release-candidate validation](https://github.com/legout/tau-ponytail/issues/5) | #4; released Tau version containing #732 | README/metadata, full checks, clean released-Tau smoke | V5 `existing-check`, low risk |

Do not duplicate full task bodies here. Each issue's authority SHA and revision-sensitive requirements must match specification revision 2 before dispatch.

## Test strategy

### Unit seams

- mode normalization and complete instruction selection for `lite`, `full`, `ultra`, and `off`;
- config-path resolution, BOM/invalid JSON handling, default precedence, quiet-startup truthiness, and atomic unrelated-key-preserving writes;
- command parser/state transitions and exact deactivation truth table;
- shortcut message and `deliver_as` selection.

### Real Tau runtime

Use Tau's actual `ExtensionRuntime`, public event/result classes, and deterministic fake bound session/UI/provider objects from a Tau build containing PR #732. Prove:

- `[tool.tau]` discovery and setup generation isolation;
- session-start reset and quiet notification behavior;
- full-replacement `before_agent_start` output, one appended instruction, `off` no-op, empty-base handling, and fail-open malformed/error handling;
- transformed prompt use through multi-call tool runs and unconditional base-prompt restoration after success, error, and cancellation;
- no instruction in durable messages/events/custom entries/session files;
- command dispatch, exact non-consuming input deactivation, and idle/active shortcut delivery;
- print-mode paths need no Textual objects.

Do not duplicate Tau core's exhaustive hook/command composition tests. Tau Ponytail tests own its handler outputs and one integration proof per public boundary.

## Handoff and review

- Execution mode: supervised; one writer owns the sequential #1–#5 lane.
- Implementation profile: builtin `worker`; independent review profile: fresh read-only builtin `reviewer`. Confirm executable agents and record resolved identities in the run manifest before dispatch.
- Commit each ticket atomically after its scoped validation passes. Do not close or publicly edit an issue until the parent verifies the corresponding commit and evidence.
- Run one fresh candidate review after ticket #4. One authorized in-scope fix pass and one delta-only recheck are the limit.
- A material behavior/interface/scope change requires specification reconciliation and owner reapproval before affected work continues.
- Local candidate integration, push, PR creation/merge, upstream Tau merge, version assignment, and release remain separate authority gates.

## Release gates

Run from the Tau Ponytail repository:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

Then use a clean environment with an official Tau release containing PR #732:

```bash
tau -e /path/to/tau-ponytail -p "Use the simplest safe implementation"
```

Before that release exists, the same smoke may be run against contributor commit `bad16acf984dbe921ecbe18e57b75b362c04ff55` as development evidence, but it does not satisfy ticket #5's publication gate.

## Residual risks

- Tau PR #732 is open and may change during review; rebase API-level tests to the merged public contract before release.
- Tau does not expose public custom-entry readback, so active mode intentionally resets on `session_start` rather than matching Pi's persisted session mode.
- Tau does not expose a status-bar contribution API, so the Pi indicator and `hideStatus` have no v1 equivalent.
- Active-run shortcut messages rely on Tau's public follow-up delivery; integration tests must establish the observable queued request without private queue inspection.

## Provenance

Planning Contract version: 1. Revision 2 was approved on 2026-09-17 with SHA-256 `90c42fbd4eb6f52354dbca017da05bd42ab01918a278867b83c7bb9a930831f4`. It is derived from upstream Ponytail 4.10.0, Tau PR #732 at `bad16acf984dbe921ecbe18e57b75b362c04ff55`, accepted ADRs 0004–0005, and the superseded revision 1 SHA-256 `0373d0e9f16b10b1013bd6a8de95c3c44f176a900210fe186a49dbb7358d2e2b`.
