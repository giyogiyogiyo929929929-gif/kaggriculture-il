# -*- coding: utf-8 -*-
"""v16の旧v52確定窓をstep 300まで延長した厳格版を生成する。"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "opponents" / "v52" / "main.py"
V16 = ROOT / "submissions" / "v16_antiv52" / "main.py"

if __name__ == "__main__":
    base = BASE.read_bytes()
    body = V16.read_bytes()
    assert body.startswith(base)
    old = b"_KIL_V52_COMMIT = 167"
    new = b"_KIL_V52_COMMIT = 300"
    assert body.count(old) == 1
    body = body.replace(old, new)
    out_dir = ROOT / "submissions" / "v17_antiv52_strict"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "main.py"
    target.write_bytes(body)
    print(f"{target}: {len(body):,} bytes")
    print(f"  main SHA-256: {hashlib.sha256(body).hexdigest()}")
