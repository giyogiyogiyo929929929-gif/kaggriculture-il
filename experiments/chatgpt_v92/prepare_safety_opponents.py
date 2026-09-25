from __future__ import annotations

import base64
import gzip
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPECS = {
    "uploaded_main": {
        "pattern": "uploaded_main.py.gz.b64.part*",
        "sha256": "997e6bfc5234534e246e945bc61c87858ebf997ab85b0a5c9427dd4ed710f1b6",
        "output": "uploaded_main.py",
    },
    "h4": {
        "pattern": "h4.py.gz.b64.part*",
        "sha256": "f01c0791ef5e131fa6e56b1a3cd84df9c8422a4f4f8b0f1cf6e15efede53951e",
        "output": "h4.py",
    },
}

for name, spec in SPECS.items():
    parts = sorted(ROOT.glob(spec["pattern"]))
    if not parts:
        raise SystemExit(f"missing {name} payload")
    payload = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    source = gzip.decompress(base64.b64decode(payload))
    sha = hashlib.sha256(source).hexdigest()
    if sha != spec["sha256"]:
        raise SystemExit(f"{name} sha256 mismatch: {sha} != {spec['sha256']}")
    (ROOT / spec["output"]).write_bytes(source)
    print(f"{name}_sha256={sha}")
    print(f"{name}_bytes={len(source)}")
