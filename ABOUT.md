# ModelGate — A Dataset Governance Framework for Computer Vision

## What is ModelGate?

ModelGate is the **reference implementation** of **MGS** (Model Gate Standard) — an open specification that defines what it means for
a computer vision image dataset to be "fit to evaluate," and what an
evaluating implementation must produce so that two independent
implementations — in any language — arrive at the same verdict for
the same dataset. The full specification is in `specs/mgs/`.

ModelGate isn't a model-training tool — it's a **gatekeeper** before a
dataset enters a training pipeline, and a reference implementation of
a specification larger than itself: anyone can build another MGS
implementation, and it's just as valid as long as it conforms to the
spec — see `specs/mgs/MGS-1.0.md` §7.

---

## Who is it for?

| User | Need |
|---|---|
| **Researchers & students** | Confirm a collected dataset is fit for purpose before experiments start, and cite the exact spec version used in the Methods section |
| **ML engineers** | Audit a dataset before it enters a production training pipeline — via CLI/CI, not just a UI |
| **Data curators** | Detect quality problems (duplicates, corrupted files, uneven distribution) automatically and reproducibly |
| **Other tool builders** | Implement MGS in another language/platform, using the spec as the contract — not ModelGate's code as the source of truth |

---

## Why is MGS/ModelGate needed?

Poor dataset quality is the leading cause of failed CV models — not model architecture.

**Common dataset problems that manual inspection usually misses:**

- Corrupted image files that the filesystem still reads as valid
- Duplicate images that cause a model to overfit on specific data
- Significant class imbalance (high Gini coefficient)
- Empty or near-empty class folders

Without an audit, these problems only surface once model accuracy stalls or evaluation fails — after hours to days of wasted training compute.

**The deeper problem MGS tries to answer:** "audited" without a clear specification easily becomes an unverifiable claim — two people run "an audit" on the same dataset and get different results, with undocumented thresholds, from a tool no one else can rerun. MGS explicitly defines thresholds, rounding semantics, and the Manifest format precisely so that the claim "this dataset passes MGS-1.0" can be reproduced by anyone, not just taken on faith.

---

## When should you use it?

Used **before** training starts, as a mandatory checkpoint in the ML pipeline:

```
Data Collection → [MGS CHECK] → Preprocessing → Training → Evaluation
```

Use it whenever:
- A new dataset has just been collected or scraped
- Merging multiple dataset sources into one
- Receiving an unverified dataset from a third party
- Adding new data to an existing dataset
- Preparing a dataset for publication/a paper, and you want to cite reproducible quality evidence

---

## Where does it sit in the ecosystem?

Sits at the **Data Quality** layer — after raw data collection, before preprocessing and training.

```
[Data Source]         raw images, scraping, labeling tools
      ↓
[MGS CHECK]           modelgate-core: automated audit, per-requirement verdict
      ↓
[Preprocessing]       augmentation, normalization, train/val/test split
      ↓
[Training]            PyTorch, TensorFlow, Keras, etc.
      ↓
[Evaluation & Deploy] inference, monitoring
```

Not tied to any ML framework. This repo is library/CLI only —
`packages/modelgate-core`, used directly in a notebook or CI, nothing
else. The realistic adoption path for a verification tool is
`pip install` plus one step in CI, not standing up a whole
microservice stack.

---

## How does it work?

### 1. A Reader reads the dataset as-is

A dataset in a supported format (ZIP, ImageFolder directory — more
formats planned) is read by a **Reader** and
normalized into a **Manifest** — a neutral representation that no
longer knows whether it originated from a ZIP or a folder. Every
Checker below only reads the Manifest, never touching the raw dataset
directly. Manifest schema details are in `specs/mgs/MGS-1.0.md` §2.

### 2. A Checker evaluates each MGS-1.0 Requirement

| Requirement | Checker | What it evaluates |
|---|---|---|
| MGS-0001 Structure | Structure | At least 2 classes, each with ≥1 valid sample |
| MGS-0002 Integrity | Corruption | Corrupted or unreadable image files |
| MGS-0003 Duplicate | Duplicate | Near-identical images (perceptual hash, threshold documented in the spec) |
| MGS-0004 Balance | Distribution | Class-count imbalance (Gini coefficient) |

Image resolution is still reported, but as an **informative** metric, not a Requirement with a PASS/FAIL verdict — see spec §5.5 for why.

### 3. A verdict, not just a number

Each Requirement produces one of four verdicts:

```
PASS            — evaluated, condition satisfied
FAIL            — evaluated, condition not satisfied
NOT_EVALUATED   — could not be evaluated (missing/empty data) — NEVER
                  silently treated as PASS (see MGS-0000, spec §3)
PARTIAL         — evaluated for only part of the Manifest
```

A summary number (the former "Health Score") is still computed and
displayed as a metric for comparing dataset versions over time, but
its status is **informative, not normative** — it must not be used to
claim MGS compliance. The per-Requirement verdicts above are what
determine compliance.

### 4. The report

Every report (`Report`, see spec §4) includes `spec_version`,
`tool_version`, and `dataset_hash` — so anyone reading the report knows
exactly which spec version was used, which tool version produced it,
and which exact dataset it was.

---

## Value delivered

**Saves training time.**
A problematic dataset that reaches the training pipeline wastes hours to days of compute. Problems are caught in minutes instead.

**Better model outcomes.**
A clean dataset produces a model that generalizes better and overfits less.

**A reproducible process — what distinguishes MGS from just "an audit tool."**
The same report, from the same dataset, evaluated against the same spec version, must produce the same verdict — in any implementation. That's not an aspiration, it's the definition of conformance (`specs/mgs/MGS-1.0.md` §7).

**Not locked to one tool.**
MGS is an open specification (CC BY 4.0, `specs/LICENSE`). ModelGate is one reference implementation of it, not the only valid one.
