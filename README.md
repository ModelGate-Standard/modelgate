# ModelGate — check a CV dataset with MGS before you train on it

[![PyPI](https://img.shields.io/pypi/v/modelgate-mgs.svg)](https://pypi.org/project/modelgate-mgs/)
[![Python versions](https://img.shields.io/pypi/pyversions/modelgate-mgs.svg)](https://pypi.org/project/modelgate-mgs/)
[![Conformance](https://github.com/ModelGate-Standard/modelgate/actions/workflows/conformance.yml/badge.svg)](https://github.com/ModelGate-Standard/modelgate/actions/workflows/conformance.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21630072.svg)](https://doi.org/10.5281/zenodo.21630072)

**Repository:** https://github.com/modelgate-standard/modelgate

`modelgate` is the reference implementation of **MGS** (Model Gate Standard) — an open spec for evaluating computer vision dataset
quality, designed so independent implementations produce identical,
reproducible verdicts for the same dataset.

**Primary use case:** you're about to train a model. Before you do, check
the dataset — in the same notebook or script, no server, no upload, no
infrastructure.

**Contents:** [Install](#install) · [What it checks](#what-it-actually-checks-mgs-10) · [How it works](#how-it-works-internally) · [Conformance](#conformance--the-proof-not-just-the-claim) · [Contributing](#contributing) · [Directory structure](#directory-structure)

```python
from modelgate import audit

report = audit("./my_dataset")  # a ZIP, or a plain folder-per-class directory

if report.overall_verdict != "PASS":
    raise RuntimeError(f"Dataset failed MGS: {report.overall_verdict}")

# proceed to training
```

See [`packages/modelgate-core/examples/quickstart.ipynb`](packages/modelgate-core/examples/quickstart.ipynb)
for a runnable version of this, end to end, generating its own tiny
example dataset so it works standalone.

---

## Install

```bash
pip install modelgate-mgs
```

The PyPI project is `modelgate-mgs` (`modelgate` was already taken by
an unrelated package), but the import and the CLI command are both
still just `modelgate` — same pattern as `beautifulsoup4` installing
as `bs4`.

Or from source, for development:

```bash
cd packages/modelgate-core
pip install -e .
```

CLI, same thing without Python:

```bash
modelgate check ./my_dataset --spec mgs-1.0 --json > report.json
```

Exits non-zero on anything but a clean `PASS` — usable directly as a
CI gate, not just interactively.

---

## What it actually checks (MGS 1.0)

| Requirement | What it evaluates |
|---|---|
| `MGS-0001` Structure | At least 2 classes, each with at least one valid sample |
| `MGS-0002` Integrity | No corrupted/unreadable image files |
| `MGS-0003` Duplicate | Near-duplicate images (perceptual hash), under 3% |
| `MGS-0004` Balance | Class imbalance (Gini coefficient), under 0.4 |

Each gets one of four verdicts: `PASS`, `FAIL`, `NOT_EVALUATED`, or
`PARTIAL`. A dataset that can't actually be evaluated (empty, unreadable)
reports `NOT_EVALUATED` — never a silent `PASS`. That's MGS-0000, the
spec's fail-closed rule: an empty or unreadable dataset must never be
reported as passing. See `specs/mgs/MGS-1.0.md` for the full spec.

A secondary "health score" (0–1) is also reported, for comparing dataset
versions over time — it's informative only, never a substitute for the
verdict above.

---

## How it works internally

```
Dataset → Reader → Manifest → Checker (×4) → Report
```

A **Reader** is the only part that knows about raw file formats (ZIP,
plain directory). It normalizes everything into a **Manifest** —
`{samples[], labels[], splits[]}` — that every **Checker** reads, never
touching the filesystem directly. This split is what lets `modelgate`
guarantee **the exact same Manifest produces the exact same verdict**,
regardless of whether the dataset arrived as a ZIP or an already-
extracted folder — proven in `conformance/`, not just claimed (a ZIP and
an equivalent directory fixture hash identically; see
`conformance/fixtures/imagefolder-equivalent/`).

---

## Conformance — the proof, not just the claim

```bash
python3 conformance/runner.py
```

Runs a corpus of small synthetic datasets through `modelgate` and checks
the output against frozen `conformance/expected/*.json` byte-for-byte.
This is what makes MGS a specification rather than a description of one
implementation's behavior — any change to `modelgate-core` has to still
reproduce every one of these exactly, or CI fails
(`.github/workflows/conformance.yml`).

---

## Citing

If you use MGS or `modelgate` in a paper, cite the specific version you ran against — see [`CITATION.cff`](CITATION.cff) (GitHub renders a "Cite this repository" button from it), or use the DOI directly: [10.5281/zenodo.21630072](https://doi.org/10.5281/zenodo.21630072). Include the `spec_version` and `dataset_hash` from your `Report` too — that's what makes the claim checkable by someone else, not just the citation.

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) — the short version: all audit
logic lives in `packages/modelgate-core`, nowhere else, and any change
has to keep the conformance corpus green.

---

## Directory structure

This repo is library-only — no hosted server, no web UI, no CI-action wrapper. Just the library, the spec, and the proof that they match.

```
modelgate/
├── packages/
│   └── modelgate-core/       THE library. pip install this. Zero infra deps.
│       └── examples/          quickstart.ipynb — the primary documented use case
├── specs/
│   ├── mgs/                  MGS specification (MGS-1.0.md — frozen)
│   └── LICENSE                CC-BY-4.0, for the spec only
├── conformance/                Fixtures + runner proving conformance
├── .github/workflows/
│   └── conformance.yml         Gates modelgate-core + the quickstart notebook
├── LICENSE                     Apache-2.0, for the code
├── CITATION.cff                 Machine-readable citation metadata
└── ARCHITECTURE.md             Design of the Reader/Manifest/Checker/Report pipeline
```
