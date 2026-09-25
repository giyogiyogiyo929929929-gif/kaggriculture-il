#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V130_SHA256 = "7a8e337b5651ba3bf0f805b588ba871ba1ad629f515e47bc4c42494862eacfa8"
V133_SHA256 = "ff7e198954f3d0b1198184966e4ae76a16e0d344ca93cfccb30f99253c54ba65"

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

V135_BLOCK = '''    if step>=577 and _ADV_LATE_DRAW_GATE.get(player,False):
        # v135: keep v133's Town-Center hold except for the known dangerous
        # same-item MILK split shape.  If selling one extra MILK now crosses
        # an actual $1 quote boundary, retaining that unit can hand the rival
        # the higher quote (the v133/bl_v21/382002 failure mode).
        _native_sell_items={o[1] for o in (action.get('market') or []) if o and len(o)>=3 and o[0]=='SELL'}
        _mkt=obs.get('market',{}) or {}
        _inv_map=_mkt.get('inventory',{}) or {}
        _price_map=_mkt.get('prices',{}) or {}
        def _milk_quote_after_one_more_sale():
            try:
                inv=int(_inv_map.get('MILK',10000))
                nxt=inv+1
                if nxt<10000:
                    price=160.0+(0.60*160.0/(122.0**0.5))*((10000.0-nxt)**0.5)
                else:
                    price=160.0-(1.60*160.0/122.0)*(nxt-10000.0)
                return max(1,int(round(price)))
            except Exception:
                return None
        def _milk_quote_boundary_risk(item):
            if item!='MILK' or item not in _native_sell_items:
                return False
            try:
                now=int(_price_map.get('MILK'))
            except Exception:
                return False
            nxt=_milk_quote_after_one_more_sale()
            return nxt is not None and nxt<now
        def _draw_before_due(item,due):
            crosses_center=any(u%24==0 for u in range(step,due))
            return crosses_center and not _milk_quote_boundary_risk(item)
        plan=[x for x in plan if not _draw_before_due(x[1],x[0])]
'''


def sha(src: str) -> str:
    return hashlib.sha256(src.encode()).hexdigest()


def replace_once(src: str, old: str, new: str, label: str) -> str:
    count = src.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source block, got {count}")
    return src.replace(old, new, 1)


def build(v130: str) -> tuple[str, str]:
    if sha(v130) != V130_SHA256:
        raise SystemExit(f"v130 sha mismatch: {sha(v130)}")
    v133 = replace_once(v130, V130_BLOCK, V133_BLOCK, "v133")
    if sha(v133) != V133_SHA256:
        raise SystemExit(f"v133 sha mismatch: {sha(v133)}")
    v135 = replace_once(v133, V133_BLOCK, V135_BLOCK, "v135")
    compile(v135, "<v135>", "exec")
    return v133, v135


def _milk_quote(inv: int) -> int:
    if inv < 10000:
        price = 160.0 + (0.60 * 160.0 / (122.0**0.5)) * ((10000.0 - inv) ** 0.5)
    else:
        price = 160.0 - (1.60 * 160.0 / 122.0) * (inv - 10000.0)
    return max(1, int(round(price)))


def synthetic() -> None:
    # Negative-control price boundary from the v133 regression shape:
    # one extra MILK can move the quote 218 -> 217.
    assert _milk_quote(9956) == 218
    assert _milk_quote(9957) == 217

    def boundary_risk(item: str, native: set[str], inv: int, now: int) -> bool:
        return item == "MILK" and item in native and _milk_quote(inv + 1) < now

    def blocks(step: int, due: int, item: str, native: set[str], inv: int, now: int) -> bool:
        crosses = any(u % 24 == 0 for u in range(step, due))
        return crosses and not boundary_risk(item, native, inv, now)

    # Known-dangerous same-item MILK split: release hold.
    assert blocks(600, 601, "MILK", {"MILK"}, 9956, 218) is False
    # Same item but no quote boundary: preserve v133 hold.
    assert blocks(600, 601, "MILK", {"MILK"}, 9955, 218) is True
    # No native MILK sale: preserve v133 hold even at a boundary.
    assert blocks(600, 601, "MILK", set(), 9956, 218) is True
    # Do not generalize the guard to other items.
    assert blocks(600, 601, "EGG", {"EGG"}, 9956, 218) is True
    # No center crossing: no hold.
    assert blocks(601, 604, "MILK", {"MILK"}, 9956, 218) is False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v130", default="eval_agents/v130/v130.py")
    ap.add_argument("--out", default="eval_agents/v130/v135_candidate_milk_quote_boundary.py")
    args = ap.parse_args()

    synthetic()
    src = Path(args.v130).read_text(encoding="utf-8")
    _, out = build(src)
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(out.encode("utf-8"))
    print(f"v135={p} sha256={sha(out)} synthetic=ok syntax=ok")


if __name__ == "__main__":
    main()
