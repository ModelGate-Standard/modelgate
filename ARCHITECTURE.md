# Architecture

`modelgate-core` is a single pipeline: **Reader → Manifest → Checker → Report**. This document describes each stage and the invariants that make cross-implementation conformance possible.

```
Dataset (ZIP | ImageFolder directory)
        │
        ▼
     Reader          only component that touches raw file formats
        │
        ▼
    Manifest         neutral representation: samples[], labels[], splits[]
        │
        ▼
   Checker ×4         MGS-0001..0004 — reads Manifest only, never the filesystem
        │
        ▼
     Report          verdict per Requirement + spec_version + dataset_hash
```

---

## Reader

A Reader is the only part of the library that knows about a specific dataset packaging format. Two ship today:

| Reader | Handles |
|---|---|
| `ZipReader` | `.zip` archives — single-root, flat-class, or split (`train/`, `test/`) layouts, auto-detected |
| `ImageFolderReader` | A plain directory in the same layouts |

Both share one structure-detection implementation (`_readers/_structure.py`) — there is exactly one place that decides whether a dataset is single-root, flat-class, or split, not one implementation per Reader. This is deliberate: a dataset's *logical* content must produce the same Manifest regardless of which Reader read it.

**Proven, not assumed:** `conformance/fixtures/imagefolder-equivalent/` and an equivalent `.zip` fixture with identical logical content produce byte-identical `dataset_hash` values. See [Conformance](#conformance) below.

Adding a new format (COCO, YOLO, HuggingFace datasets, ...) means writing one new Reader — zero changes to any Checker.

## Manifest

The neutral, format-agnostic representation every Checker reads:

```
Manifest
├── samples: [{ uri, content_hash, source_path, label, split, meta }, ...]
├── labels: [str, ...]
└── splits: [str, ...]   (empty if the dataset has no train/test/val structure)
```

- `uri` is the canonical identifier: `{split}/{label}/{filename}` or `{label}/{filename}` — order-independent, Reader-independent.
- `source_path` is implementation-internal (not part of the normative schema) — where Checkers actually read file bytes from. See `specs/mgs/MGS-1.0.md` §2 for the full, normative schema.
- `dataset_hash = sha256("\n".join(sorted(f"{uri}:{content_hash}" for each sample)))` — order-independent and Reader-independent by construction, which is what makes the equivalence proof above possible.

A Checker receiving a Manifest cannot tell whether it came from a ZIP or a directory, and does not need to.

## Checker

Four Checkers implement the four MGS-1.0 normative Requirements (`_checkers/{structure,integrity,duplicate,balance}.py`). Each:

- Takes `(manifest: Manifest, config: dict) -> RequirementResult`.
- Reads thresholds from `config`, falling back to the spec's documented defaults (`max_gini`, `hamming_threshold`, etc.) — never hardcoded, so a caller can override them and the Report records whether a default or an override was used.
- Returns `NOT_EVALUATED` when it cannot evaluate (e.g. zero samples) — **never** a default/neutral `PASS`. This is MGS-0000, the spec's fail-closed rule.

**Numeric determinism:** rounding uses `Decimal` + `ROUND_HALF_UP` (round-half-away-from-zero), not Python's built-in `round()` (which uses banker's rounding) — a different implementation using naive rounding would silently disagree with this one on tie-break cases. Duplicate detection uses a 64-bit perceptual hash with a documented Hamming-distance threshold. All of this is specified in prose in `specs/mgs/MGS-1.0.md`, not left to be reverse-engineered from this code — that's what makes an independent (e.g. Rust or Go) implementation possible in principle.

## Report

```
Report
├── spec_version        e.g. "1.0" — which MGS version this Report claims conformance to
├── tool_version         this package's version
├── dataset_hash         see above
├── requirements: [{ id, verdict, metrics, findings, config }, ...]
├── informative: {...}   e.g. resolution stats — never affects overall_verdict
└── overall_verdict       precedence: FAIL > NOT_EVALUATED/PARTIAL > PASS
```

Every value needed to reproduce a claim ("this dataset passes MGS-1.0") travels with the Report itself — see `CITATION.cff` and the README's Citing section.

## Stable API surface (D5.1)

Only `modelgate.__all__` is covered by any compatibility guarantee: `audit()`, `read_dataset()`, `Manifest`, `Report`, `RequirementResult`. Everything else lives under underscore-prefixed modules (`_readers`, `_checkers`, `_rounding`) and is enforced, not just documented by convention — internal modules are genuinely private, so `dir(modelgate)` reflects the same boundary `__all__` does.

## Conformance

```
conformance/
├── fixtures/       small synthetic datasets (.zip and plain directories)
├── expected/       frozen, byte-exact expected Report JSON per fixture
└── runner.py       drives modelgate via its CLI (subprocess), diffs against expected/
```

`runner.py` deliberately invokes `modelgate check <path> --json` as a subprocess rather than importing `modelgate-core` directly — the interop contract is defined at the process boundary, in JSON, so a conformant implementation in any language can be verified by the same corpus. This is what makes MGS 1.0 a specification with a test suite, not just a description of this one implementation's behavior. Any change to Reader/Checker/Report logic has to keep every fixture's output byte-identical, or CI (`.github/workflows/conformance.yml`) fails.
