"""Reader protocol.

A Reader is the only part of a conformant implementation permitted to
know anything about raw file layout or archive formats (spec §1). Every
Reader produces a Manifest via the same shared structure-detection logic
in _structure.py — one implementation, not one per Reader, is what
guarantees two Readers never disagree on a dataset's layout.
"""

from typing import Protocol

from modelgate.manifest import Manifest


class Reader(Protocol):
    def can_read(self, path: str) -> bool: ...

    def read(self, path: str) -> Manifest: ...
