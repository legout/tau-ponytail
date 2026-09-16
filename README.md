# tau-ponytail

A small Python extension that brings Ponytail's minimal-code mode to Tau.

This repository contains an approved v1 behavior specification, accepted
architectural decisions, and an approved implementation plan. It targets Tau's
public Python extension API and will not modify Tau core or require runtime
dependencies beyond Python's standard library.

## Planned usage

```text
/ponytail                 # enable the configured mode
/ponytail lite|full|ultra|off
/ponytail status
/ponytail default lite|full|ultra|off
/ponytail-review
/ponytail-audit
/ponytail-debt
/ponytail-gain
/ponytail-help
```

The extension will be loadable with either:

```bash
tau -e /path/to/tau-ponytail
```

or, once the repository has an implementation and release ref:

```bash
tau install git:github.com/<owner>/tau-ponytail
```

The approved behavioral contract is
[docs/specs/tau-ponytail-v1.md](docs/specs/tau-ponytail-v1.md), and the approved
execution map is [docs/plans/tau-ponytail-v1.md](docs/plans/tau-ponytail-v1.md).
Domain vocabulary is in [CONTEXT.md](CONTEXT.md), architectural rationale is in
[docs/adr/](docs/adr/), and [PLAN.md](PLAN.md) is retained as design evidence.
