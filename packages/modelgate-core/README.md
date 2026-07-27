# modelgate-core

Reference implementation of [MGS (Model Gate Standard)](../../specs/mgs/MGS-1.0.md) — pure-Python, zero infrastructure dependencies.

```bash
pip install modelgate-mgs
```

No FastAPI, no database, no message queue — this package is meant to be
usable from a plain Python script, a notebook, or a CI job with nothing
but `pip install modelgate-mgs`.

## Usage

```python
from modelgate import audit

report = audit("./my_dataset.zip")
print(report.overall_verdict)  # PASS / FAIL / NOT_EVALUATED
for r in report.requirements:
    print(r.id, r.verdict, r.metrics)
```

```bash
modelgate check ./my_dataset.zip --spec mgs-1.0 --json > report.json
```

## Stable API surface (D5.1)

Only what's listed in `modelgate.__all__` is covered by any stability
guarantee:

- `modelgate.audit(path, config=None) -> Report`
- `modelgate.read_dataset(path) -> Manifest` — structure-only parsing,
  no Requirement checks run. Useful if you want a Manifest without
  paying for a full audit.
- `modelgate.Report`, `modelgate.RequirementResult`, `modelgate.Manifest`

Anything under `modelgate._readers`, `modelgate._checkers`,
`modelgate._rounding` — the leading underscore is enforced, not just
documented — may change shape between minor versions without notice.
The `modelgate check` CLI's `--json` output shape (spec §4) is the other
thing meant to be stable; parse that, not Python internals, if you're
integrating from outside Python.
