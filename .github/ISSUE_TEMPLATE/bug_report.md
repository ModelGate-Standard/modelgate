---
name: Bug report
about: Something in modelgate-core or its CLI behaves incorrectly
labels: bug
---

**Component** (check one):
- [ ] `modelgate-core` (Reader / Checker / Report)
- [ ] CLI (`modelgate check`)
- [ ] `specs/mgs/` (spec text itself, not an implementation)

**What happened**

**What you expected**

**Minimal reproduction**

If possible, attach (or describe) a small dataset that reproduces the
issue — this can become a conformance fixture (`conformance/fixtures/`)
if it reveals a real bug, per `CONTRIBUTING.md`.

```
modelgate check ./your-dataset --json
```

**Environment**
- `modelgate-mgs` version (`pip show modelgate-mgs` or `modelgate --version`):
- MGS spec version targeted (`--spec` flag, if used):
- OS / Python version:
