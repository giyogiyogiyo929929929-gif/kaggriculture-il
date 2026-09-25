"""Exact loader for Kaggriculture v95 KEEP TESTING candidate.

v95 is reconstructed from the canonical v94 source with exactly four audited
text substitutions. The final SHA-256 must match the locally validated v95
candidate before execution.
"""
import base64
import hashlib
import zlib
from pathlib import Path

_ROOT = Path(__file__).parents[2]
_SOURCE_DIR = _ROOT / "lineages" / "v94_exact_source"
_BLOB = "".join((_SOURCE_DIR / f"part{i:02d}.b85").read_text(encoding="utf-8") for i in range(3))
_SOURCE = zlib.decompress(base64.b85decode(_BLOB.encode("ascii"))).decode("utf-8")
_REPLACEMENTS = [
    (
        'min(14 if _adaptive_h14_allowed(obs) else 13, previous + 1)',
        'min(15 if _adaptive_h14_allowed(obs) else 13, previous + 1)',
    ),
    (
        'min(14 if _adaptive_h14_allowed(obs) else 13, max(6, int(lead.get("ceiling", 7) or 7)))',
        'min(15 if _adaptive_h14_allowed(obs) else 13, max(6, int(lead.get("ceiling", 7) or 7)))',
    ),
    (
        'if horizon == 14 and item == "MILK":',
        'if horizon >= 14 and item == "MILK":',
    ),
    (
        'agent.__version__ = "v94-adaptive-h14-yarn2-nomilk"',
        'agent.__version__ = "v95-adaptive-h15-yarn2-nomilk"',
    ),
]
for _old, _new in _REPLACEMENTS:
    if _SOURCE.count(_old) != 1:
        raise RuntimeError(f"v95 reconstruction pattern count != 1: {_old}")
    _SOURCE = _SOURCE.replace(_old, _new)
_EXPECTED_SHA256 = "ba21fe1dcf78113bb5c2531d015f318dbc0af290c608ea5925578b2485ee62cd"
_ACTUAL_SHA256 = hashlib.sha256(_SOURCE.encode("utf-8")).hexdigest()
if _ACTUAL_SHA256 != _EXPECTED_SHA256:
    raise RuntimeError(f"v95 source hash mismatch: {_ACTUAL_SHA256}")
_NS = {"__name__": "_v95_exact", "__file__": str(_SOURCE_DIR / "reconstructed_v95.py")}
exec(compile(_SOURCE, _NS["__file__"], "exec"), _NS, _NS)
agent = _NS["agent"]
