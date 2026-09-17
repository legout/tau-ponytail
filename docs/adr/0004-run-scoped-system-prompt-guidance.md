---
status: accepted
approved: 2026-09-17
supersedes: 0002-ephemeral-context-injection.md
source: ../specs/tau-ponytail-v1.md
---

# Transform the run-scoped system prompt

Tau Ponytail will apply the active instruction through Tau's public `before_agent_start` hook by returning the complete replacement system prompt. The handler appends one mode-specific Ponytail instruction to the prompt supplied by Tau and returns nothing when the active mode is `off`.

This matches the upstream Pi adapter's role semantics: Ponytail text is behavioral guidance, not a user task. Tau invokes the hook once after prompt expansion and pre-run compaction, uses the transformed prompt for every provider call in that run, and restores the base prompt on every exit path. Hook failures are contained by Tau and therefore fail open.

An ephemeral user-context message was rejected because it changes the instruction's role and relies on a different, unpublished hook. Static prompt sections were rejected because the active mode changes at runtime. Private session access, provider wrappers, monkey patches, and durable prompt messages remain forbidden.

Implementation and release validation require a Tau build containing [huggingface/tau#732](https://github.com/huggingface/tau/pull/732); the minimum released Tau version will be recorded after that change ships.
