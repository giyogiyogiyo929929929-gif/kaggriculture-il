# -*- coding: utf-8 -*-
"""v20の発火上限を1回へ下げたv21を生成する。"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "opponents" / "v52" / "main.py"
V20 = ROOT / "submissions" / "v20_antiv52_cap2" / "main.py"

if __name__ == "__main__":
    base = BASE.read_bytes()
    body = V20.read_bytes()
    assert body.startswith(base)
    old = b'state.get("fires", 0) >= 2'
    new = b'state.get("fires", 0) >= 1'
    assert body.count(old) == 2
    body = body.replace(old, new)
    out_dir = ROOT / "submissions" / "v21_antiv52_cap1"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "main.py"
    target.write_bytes(body)
    print(f"{target}: {len(body):,} bytes")
    print(f"  main SHA-256: {hashlib.sha256(body).hexdigest()}")
