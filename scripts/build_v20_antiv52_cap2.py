# -*- coding: utf-8 -*-
"""v17の先回り発火を1試合2回までに制限したv20を生成する。"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "opponents" / "v52" / "main.py"
V17 = ROOT / "submissions" / "v17_antiv52_strict" / "main.py"

if __name__ == "__main__":
    base = BASE.read_bytes()
    body = V17.read_bytes()
    assert body.startswith(base)
    replacements = (
        (b'"evidence": 0, "seen": {}, "best": {}}',
         b'"evidence": 0, "fires": 0, "seen": {}, "best": {}}'),
        (b'if not state["copy"] or step < _KIL_V52_COMMIT or step >= 700 - _KIL_V52_LEAD:',
         b'if (not state["copy"] or state.get("fires", 0) >= 2\n            or step < _KIL_V52_COMMIT or step >= 700 - _KIL_V52_LEAD):'),
        (b'    for index, item in enumerate(_V92_P_ITEMS):\n        if item not in _V92_P_USE',
         b'    for index, item in enumerate(_V92_P_ITEMS):\n        if state.get("fires", 0) >= 2:\n            break\n        if item not in _V92_P_USE'),
        (b'            _KIL_V52_REPORT["preempt_fires"] += 1\n            _KIL_V52_REPORT["preempt_units"] += quantity',
         b'            _KIL_V52_REPORT["preempt_fires"] += 1\n            state["fires"] = state.get("fires", 0) + 1\n            _KIL_V52_REPORT["preempt_units"] += quantity'),
    )
    for old, new in replacements:
        assert body.count(old) == 1, old
        body = body.replace(old, new)
    out_dir = ROOT / "submissions" / "v20_antiv52_cap2"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "main.py"
    target.write_bytes(body)
    print(f"{target}: {len(body):,} bytes")
    print(f"  main SHA-256: {hashlib.sha256(body).hexdigest()}")
