# tau-ponytail

A small Python extension that brings Ponytail's minimal-code mode to Tau.

This repository currently contains the implementation plan only. It will target
Tau's public Python extension API and will not modify Tau core or require
runtime dependencies beyond Python's standard library.

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

See [PLAN.md](PLAN.md) for scope, design decisions, test strategy, and
acceptance criteria.
