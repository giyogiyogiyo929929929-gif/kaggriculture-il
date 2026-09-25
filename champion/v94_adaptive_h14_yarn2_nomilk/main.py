"""Exact loader for formal Kaggriculture champion v94.

The canonical source is stored compressed under lineages/v94_exact_source to keep
this isolated Actions branch auditable. The reconstructed source SHA-256 must
match the locally validated v94 source before it is executed.
"""
import base64
import hashlib
import zlib
from pathlib import Path

_ROOT = Path(__file__).parents[2]
_SOURCE_DIR = _ROOT / "lineages" / "v94_exact_source"
_BLOB = "".join((_SOURCE_DIR / f"part{i:02d}.b85").read_text(encoding="utf-8") for i in range(3))
_SOURCE = zlib.decompress(base64.b85decode(_BLOB.encode("ascii"))).decode("utf-8")
_EXPECTED_SHA256 = "869b7e9fe727694ca52710716921856fea6511ccae71b0613be26f4e9236baa3"
_ACTUAL_SHA256 = hashlib.sha256(_SOURCE.encode("utf-8")).hexdigest()
if _ACTUAL_SHA256 != _EXPECTED_SHA256:
    raise RuntimeError(f"v94 source hash mismatch: {_ACTUAL_SHA256}")
_NS = {"__name__": "_v94_exact", "__file__": str(_SOURCE_DIR / "reconstructed_v94.py")}
exec(compile(_SOURCE, _NS["__file__"], "exec"), _NS, _NS)
agent = _NS["agent"]
