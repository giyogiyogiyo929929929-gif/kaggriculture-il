from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V138_SHA256 = "33d495561774c1379a0f66c6a863b344ae0249fe64e196fc208a15c53188438f"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("champion")
    parser.add_argument("out")
    args = parser.parse_args()

    source = Path(args.champion).read_text(encoding="utf-8")
    got = sha256_text(source)
    if got != V115_SHA256:
        raise SystemExit(f"v115 source sha256 mismatch: {got} != {V115_SHA256}")

    old = '''    market = [list(o) for o in action.get("market") or []]\n    already = {o[1] for o in market if len(o) > 1 and o[0] in ("SELL", "BUY_PRODUCT")}\n    stock = projected_shed(action, FarmView(obs))\n    changed = False\n    for i, item in enumerate(_V92_P_ITEMS):\n        if item not in _V92_P_USE or item in already or len(market) >= MAX_ORDERS:\n            continue\n        if item == "STRAWBERRY" and float(st.get("top_score", -999.0)) < 25:\n            continue\n        votes = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= _V92_P_K)\n        if votes < 1:\n            continue\n        ours = 0\n        for t in range(step + 1, min(len(tape), step + _V92_P_H + 1)):\n            ours += sum(min(100, int(o[2])) for o in (tape[t] or {}).get("market") or []\n                        if len(o) >= 3 and o[0] == "SELL" and o[1] == item)\n        qty = min(int(stock.get(item, 0)), ours)\n        if qty > 0:\n            market.insert(0, ["SELL", item, qty])\n            _V92_P_REPORT["pred_units"] += qty\n            _V92_P_REPORT["pred_fires"] += 1\n            changed = True\n    if not changed:\n        return action\n    result = dict(action)\n    result["market"] = market[:MAX_ORDERS]\n    return result\n'''
    new = '''    market = [list(o) for o in action.get("market") or []]\n    already = {o[1] for o in market if len(o) > 1 and o[0] in ("SELL", "BUY_PRODUCT")}\n    stock = projected_shed(action, FarmView(obs))\n    pending = []\n    changed = False\n    for i, item in enumerate(_V92_P_ITEMS):\n        if item not in _V92_P_USE or item in already or len(market) + len(pending) >= MAX_ORDERS:\n            continue\n        if item == "STRAWBERRY" and float(st.get("top_score", -999.0)) < 25:\n            continue\n        votes = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= _V92_P_K)\n        if votes < 1:\n            continue\n        ours = 0\n        for t in range(step + 1, min(len(tape), step + _V92_P_H + 1)):\n            ours += sum(min(100, int(o[2])) for o in (tape[t] or {}).get("market") or []\n                        if len(o) >= 3 and o[0] == "SELL" and o[1] == item)\n        qty = min(int(stock.get(item, 0)), ours)\n        if qty > 0:\n            pending.append(["SELL", item, qty])\n            _V92_P_REPORT["pred_units"] += qty\n            _V92_P_REPORT["pred_fires"] += 1\n            changed = True\n    if not changed:\n        return action\n    # v138: preserve the selected items and quantities; only order the V92\n    # preempt SELL block by v115's existing public quote-exposure model.\n    if len(pending) > 1:\n        pending.sort(key=lambda o: _r37_quote_priority(obs, o, stock), reverse=True)\n    result = dict(action)\n    result["market"] = (pending + market)[:MAX_ORDERS]\n    return result\n'''
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"V92 preempt block: expected one target, found {count}")
    source = source.replace(old, new)

    got = sha256_text(source)
    if got != V138_SHA256:
        raise SystemExit(f"v138 sha256 mismatch: {got} != {V138_SHA256}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"v138_sha256={got}")
    print(f"v138_bytes={len(source.encode('utf-8'))}")


if __name__ == "__main__":
    main()
