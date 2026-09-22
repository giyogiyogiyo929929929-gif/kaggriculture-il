# -*- coding: utf-8 -*-
"""v17にICE_CREAM_SHOP同型ペアの先回り抑制を追加する。"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "opponents" / "v52" / "main.py"
V17 = ROOT / "submissions" / "v17_antiv52_strict" / "main.py"

if __name__ == "__main__":
    base = BASE.read_bytes()
    body = V17.read_bytes()
    assert body.startswith(base)
    old = b'''def _kil_v52_preempt(observation, action, state):
    step = int(observation["step"])
    if not state["copy"] or step < _KIL_V52_COMMIT or step >= 700 - _KIL_V52_LEAD:
'''
    new = b'''def _kil_v52_preempt(observation, action, state):
    step = int(observation["step"])
    shops = tuple((observation.get("town") or {}).get("unlocked_shops", [])[:2])
    if shops == ("ICE_CREAM_SHOP", "ICE_CREAM_SHOP"):
        return action
    if not state["copy"] or step < _KIL_V52_COMMIT or step >= 700 - _KIL_V52_LEAD:
'''
    assert body.count(old) == 1
    body = body.replace(old, new)
    out_dir = ROOT / "submissions" / "v18_antiv52_pairguard"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "main.py"
    target.write_bytes(body)
    print(f"{target}: {len(body):,} bytes")
    print(f"  main SHA-256: {hashlib.sha256(body).hexdigest()}")
