#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

V130_SHA256 = '7a8e337b5651ba3bf0f805b588ba871ba1ad629f515e47bc4c42494862eacfa8'
V133_SHA256 = 'ff7e198954f3d0b1198184966e4ae76a16e0d344ca93cfccb30f99253c54ba65'
V134_SHA256 = '693ca693378f8adae5d57642610ca682e43a03ad636be71141e1615a5e2d1edd'

V130_BLOCK = '''    if step>=577 and _ADV_LATE_DRAW_GATE.get(player,False):
        _shops=tuple((obs.get('town',{}) or {}).get('unlocked_shops',[]) or [])
        def _draw_before_due(item,due):
            for u in range(step,due):
                if u%24==0:
                    return True
                if u%4==0 and any(item in _RACE_SHOPS.get(s,()) for s in _shops):
                    return True
            return False
        plan=[x for x in plan if not _draw_before_due(x[1],x[0])]
'''

V133_BLOCK = '''    if step>=577 and _ADV_LATE_DRAW_GATE.get(player,False):
        def _draw_before_due(item,due):
            return any(u%24==0 for u in range(step,due))
        plan=[x for x in plan if not _draw_before_due(x[1],x[0])]
'''

V134_BLOCK = '''    if step>=577 and _ADV_LATE_DRAW_GATE.get(player,False):
        # v134: do not partially split a same-item sale across the Town Center tick.
        # If the parent action already sells this item now, keep v121's advance;
        # otherwise the v133 center-only hold remains active.
        _native_sell_items={o[1] for o in (action.get('market') or []) if o and len(o)>=3 and o[0]=='SELL'}
        def _draw_before_due(item,due):
            return item not in _native_sell_items and any(u%24==0 for u in range(step,due))
        plan=[x for x in plan if not _draw_before_due(x[1],x[0])]
'''

def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def replace_once(src: str, old: str, new: str, label: str) -> str:
    if src.count(old) != 1:
        raise SystemExit(f'{label}: expected exactly one source block, got {src.count(old)}')
    return src.replace(old, new, 1)

def build(v130: str) -> tuple[str, str]:
    if sha(v130) != V130_SHA256:
        raise SystemExit(f'v130 sha mismatch: {sha(v130)}')
    v133 = replace_once(v130, V130_BLOCK, V133_BLOCK, 'v133')
    if sha(v133) != V133_SHA256:
        raise SystemExit(f'v133 sha mismatch: {sha(v133)}')
    v134 = replace_once(v133, V133_BLOCK, V134_BLOCK, 'v134')
    if sha(v134) != V134_SHA256:
        raise SystemExit(f'v134 sha mismatch: {sha(v134)}')
    compile(v134, '<v134>', 'exec')
    return v133, v134

def synthetic() -> None:
    def blocks(step, due, item, native):
        return item not in native and any(u % 24 == 0 for u in range(step, due))
    assert blocks(600, 601, 'MILK', {'MILK'}) is False
    assert blocks(600, 601, 'MILK', set()) is True
    assert blocks(599, 601, 'MILK', set()) is True
    assert blocks(601, 604, 'MILK', set()) is False
    assert blocks(600, 601, 'EGG', {'MILK'}) is True

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--v130', default='eval_agents/v130/v130.py')
    ap.add_argument('--out', default='eval_agents/v130/v134_candidate_center_nonsplit.py')
    args=ap.parse_args()
    synthetic()
    src=Path(args.v130).read_text(encoding='utf-8')
    _, out=build(src)
    p=Path(args.out); p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(out.encode('utf-8'))
    print(f'v134={p} sha256={sha(out)} synthetic=ok syntax=ok')

if __name__ == '__main__':
    main()
