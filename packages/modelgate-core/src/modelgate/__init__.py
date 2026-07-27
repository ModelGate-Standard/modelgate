"""modelgate — reference implementation of MGS (Model Gate Standard).

Public API surface (stable as of 1.0, see D5.1 in ARCHITECTURE.md):
    modelgate.audit, modelgate.read_dataset, modelgate.Manifest,
    modelgate.Report, modelgate.RequirementResult

`read_dataset` is exported on its own (not just reached into via
`modelgate._readers`) because structure-only validation — build a
Manifest, confirm it parses, without running the full Requirement
checks — is a legitimate standalone use case beyond `audit()`, e.g. for
a consumer that wants to validate a dataset's structure before
committing to a full audit.

Everything else — modelgate._readers, modelgate._checkers, modelgate._rounding
— is implementation detail and may change without notice between minor
versions until the stability guarantee above is declared.
"""

import importlib.metadata as _importlib_metadata

from modelgate._checkers import get_normative_checkers as _get_normative_checkers
from modelgate._checkers import resolution as _resolution
from modelgate.manifest import Manifest
from modelgate._readers import read_dataset
from modelgate.report import Report, RequirementResult, now_iso8601_utc as _now_iso8601_utc

try:
    __version__ = _importlib_metadata.version("modelgate-mgs")
except _importlib_metadata.PackageNotFoundError:
    __version__ = "0.0.0.dev0"  # editable/unbuilt checkout, no installed metadata

# D5.1: this is the entire stable public surface. Everything
# imported above with a leading underscore is deliberately kept out of
# `dir(modelgate)`'s non-underscore names, not just out of __all__ — a
# stray `import modelgate; modelgate._get_normative_checkers()` should not
# work by accident just because the function happened to get imported here.
__all__ = ["audit", "read_dataset", "Manifest", "Report", "RequirementResult"]


def audit(path: str, config: dict | None = None) -> Report:
    """Evaluate a Dataset at `path` against MGS-1.0.

    `path` may be a ZIP file or a plain directory (ImageFolder layout) —
    see modelgate._readers for what's supported. `config` overrides
    per-Requirement thresholds (e.g. {"hamming_threshold": 8}); whatever
    value ends up used (override or default) is always recorded in the
    Report (spec §4), never left implicit.
    """
    config = config or {}
    manifest = read_dataset(path)

    requirements: list[RequirementResult] = []
    for checker in _get_normative_checkers():
        requirements.append(checker.check(manifest, config))

    informative = {"resolution": _resolution.compute(manifest)}

    return Report(
        spec_version=manifest.spec_version,
        tool_version=__version__,
        dataset_hash=manifest.dataset_hash,
        generated_at=_now_iso8601_utc(),
        requirements=requirements,
        informative=informative,
    )
