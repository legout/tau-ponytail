---
status: approved
approved: 2026-09-16
source-spec: ../specs/tau-ponytail-v1.md
source-spec-sha256: 0373d0e9f16b10b1013bd6a8de95c3c44f176a900210fe186a49dbb7358d2e2b
source-approved: 2026-09-16
planning-contract: 1
tracker: https://github.com/legout/tau-ponytail/issues
---

# Tau Ponytail v1 implementation plan

## Goal and authority

Implement the approved [Tau Ponytail v1 specification](../specs/tau-ponytail-v1.md) as a small, loadable Tau extension. The owner approved that specification and [ADRs 0001–0003](../adr/) on 2026-09-16. The specification owns behavior, the ADRs own architectural rationale, and the linked GitHub issues own the canonical task bodies.

The earlier root [PLAN.md](../../PLAN.md) is design evidence, not executable task authority.

## Capture checkpoint

- **Vocabulary:** [CONTEXT.md](../../CONTEXT.md) defines Tau extension, Ponytail instruction, shortcut command, Ponytail mode, active mode, configured default, and mode deactivation. No unresolved terminology remains.
- **Decisions:** accepted ADRs require a standalone public Tau extension, ephemeral context injection, and persistence of only the configured default.
- **Behavior:** the approved v1 specification defines scope, non-goals, and ten acceptance criteria.
- **Uncertainty:** resolved. Standalone deactivation input is consumed and accepts only trailing `.`, `!`, `?`, `,`, or `;` in addition to case and whitespace variants.

## Constraints and assumptions

- Python `>=3.12`; runtime dependencies are limited to the standard library.
- Use only Tau's public `ExtensionAPI` and real extension runtime; do not access private session or TUI internals.
- All mutable state is created inside `setup(tau)` and belongs to that runtime generation.
- Ponytail-derived text retains upstream MIT attribution.
- No JavaScript runtime, Tau-core change, branch-level active-mode persistence, custom status widget, or bundled companion skills.
- Security review: **n/a**. The extension handles process environment and user-owned local configuration, not an untrusted or remote boundary. Atomic configuration writes remain required to prevent local data loss.

## Requirement coverage

| Specification criterion | Canonical ticket(s) |
| --- | --- |
| 1. Clean checkout loads through Tau manifest | [#1](https://github.com/legout/tau-ponytail/issues/1), [#5](https://github.com/legout/tau-ponytail/issues/5) |
| 2. Mode, status, and default commands | [#2](https://github.com/legout/tau-ponytail/issues/2), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 3. Status reports active and configured modes | [#2](https://github.com/legout/tau-ponytail/issues/2), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 4. Default persistence, key preservation, precedence | [#2](https://github.com/legout/tau-ponytail/issues/2), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 5. Exact active instruction per request; `off` no-op | [#1](https://github.com/legout/tau-ponytail/issues/1), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 6. Injected guidance is never durable | [#1](https://github.com/legout/tau-ponytail/issues/1), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 7. Exact consumed natural-language deactivation | [#3](https://github.com/legout/tau-ponytail/issues/3), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 8. Five shortcuts work idle and active | [#3](https://github.com/legout/tau-ponytail/issues/3), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 9. Configuration/write failures remain non-fatal | [#1](https://github.com/legout/tau-ponytail/issues/1), [#2](https://github.com/legout/tau-ponytail/issues/2), [#4](https://github.com/legout/tau-ponytail/issues/4) |
| 10. No Textual/runtime dependencies; checks pass | [#1](https://github.com/legout/tau-ponytail/issues/1), [#4](https://github.com/legout/tau-ponytail/issues/4), [#5](https://github.com/legout/tau-ponytail/issues/5) |

## Execution order

The tickets are sequential because the first three share `extension.py` and runtime state. Ticket #4 validates their integrated public-runtime behavior; ticket #5 is the release-candidate gate.

| Order | Canonical ticket | Depends on | Owned surface | Validation |
| --- | --- | --- | --- | --- |
| 1 | [#1 Loadable default-guidance tracer bullet](https://github.com/legout/tau-ponytail/issues/1) | — | Package skeleton, mode/instruction/config foundations, extension lifecycle, focused tests | V1 `new-test`, normal risk |
| 2 | [#2 `/ponytail` commands and default persistence](https://github.com/legout/tau-ponytail/issues/2) | #1 | Config writes, command adapter/registration, focused tests | V2 `new-test`, normal risk |
| 3 | [#3 Exact deactivation and companion shortcuts](https://github.com/legout/tau-ponytail/issues/3) | #2 | Input hook, shortcut adapters, focused tests | V3 `new-test`, normal risk |
| 4 | [#4 Tau real-runtime proof](https://github.com/legout/tau-ponytail/issues/4) | #3 | Runtime integration tests and candidate review | V4 `new-test`, normal risk |
| 5 | [#5 Documentation and release-candidate validation](https://github.com/legout/tau-ponytail/issues/5) | #4 | README/metadata, full checks, clean Tau smoke | V5 `existing-check`, low risk |

Do not duplicate or edit task details here; update the owning ticket and reconcile this dependency/coverage overview only when its routing changes.

## Handoff and review

- Execution mode: supervised; one writer per worktree.
- Implementation profile: builtin `worker`; independent review profile: fresh read-only builtin `reviewer`. Confirm both are executable and record their resolved names in the run manifest before dispatch.
- Candidate review occurs once in ticket #4 after integrated runtime evidence exists. One authorized fix pass and one delta-only recheck are the limit; unresolved material findings return to the owner.
- A material behavior, interface, or scope change requires updating and reapproving the specification before affected tickets continue.
- Integration, push, PR merge, and release remain separately authorized actions.

## Residual risks

- The exact installed Tau public API may differ from the researched branch. If a named public type or hook is unavailable, stop and reconcile the specification/ADR rather than reaching into private internals.
- Provider interpretation of an ephemeral user-context message may differ from system-level guidance. The integration smoke proves delivery, not semantic equivalence; a future public system-prompt seam remains the documented migration path.

## Provenance

Planning Contract version: 1. Installed `planning-contract` catalog revision: unknown. Plan derived from approved specification SHA-256 `0373d0e9f16b10b1013bd6a8de95c3c44f176a900210fe186a49dbb7358d2e2b` and accepted ADRs 0001–0003. Canonical tickets were created in `legout/tau-ponytail` on 2026-09-16.
