# MGS ↔ modelgate version support matrix

MGS (the spec) and `modelgate` (the tool) version independently — see
`MGS-1.0.md` §8. This document is the living record of which tool
versions implement which spec versions. **Update this file in the same
PR that ships a new tool release or a new spec version** — a tool
release without a corresponding row here is not something a Report
consumer can trust to be reproducible.

| `modelgate` version | PyPI package / index | Implements MGS | Notes |
|---|---|---|---|
| `1.0.0` | `modelgate-mgs` (production PyPI) | `1.0` | Current production release. |
| `0.1.0` | `modelgate` (TestPyPI only) | `1.0` | Development release, not installable via plain `pip install`. |

## How this is enforced, not just documented

`modelgate check --spec <version>` (CLI) refuses to run — exit code 2,
not a silent evaluation — if the requested spec version isn't the one
this build implements (see `packages/modelgate-core/src/modelgate/cli.py`,
`_normalize_spec_arg` / the `--spec` check in `main()`). This is what
makes the matrix above load-bearing rather than aspirational: a user
who pins `--spec mgs-1.0` gets either a Report genuinely evaluated
against MGS 1.0, or a clear refusal — never a Report silently evaluated
against a spec version they didn't ask for.

## When MGS 1.1 (or later) exists

This table gains a row per tool release, and the CLI's accepted
`--spec` values grow to match whichever spec versions that release
actually implements. A tool release that drops support for an older
spec version (rare, but possible for a major version bump) must say so
explicitly in this table's Notes column — silently dropping support
would break anyone who cited a specific `modelgate`+MGS version pair in
a paper's Methods section.
