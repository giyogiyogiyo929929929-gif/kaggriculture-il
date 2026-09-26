from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V147_SHA256 = "8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923"

APPEND = r'''

# v153: v152 dense leading-SELL self-impact exposure reorder + bugfix only.
# Tactical mechanism is unchanged from v152. The sole additional change is an
# empty-order guard before indexing orders[0][0], because v147 can emit [] as
# the first market entry on some turns.
_V153_PARENT = agent
_V153_REPORT = {"eligible": 0, "changed": 0, "errors": 0}
del agent


def _v153_self_exposure(observation, order, stock):
    if len(order) < 3 or order[0] != "SELL":
        return 0.0
    item = order[1]
    quantity = min(max(0, int(order[2])), max(0, int(stock.get(item, 0))))
    if quantity <= 0 or item not in _R37_MARKET_PARAMS:
        return 0.0
    inventory = int(observation["market"]["inventory"].get(item, 0))
    params = {k: dict(v) for k, v in _R37_MARKET_PARAMS.items()}
    for k, patch in observation["market"].get("params", {}).items():
        if k in params:
            params[k].update(patch)
    now = sum(_r37_market_price(item, inventory + j, params) for j in range(quantity))
    later = sum(_r37_market_price(item, inventory + quantity + j, params) for j in range(quantity))
    return float(now - later)


def agent(observation, configuration=None):
    action = _V153_PARENT(observation, configuration)
    try:
        step = int(observation.get("step", -1))
        orders = [list(o) for o in (action.get("market") or [])]
        if not (288 <= step < 694) or not orders or not orders[0] or orders[0][0] != "SELL":
            return action
        end = 0
        while end < len(orders) and orders[end] and orders[end][0] == "SELL":
            end += 1
        block = orders[:end]
        if len(block) < 5 or len({o[1] for o in block}) != len(block):
            return action
        _V153_REPORT["eligible"] += 1
        stock = projected_shed(action, FarmView(observation))
        scored = [(_v153_self_exposure(observation, o, stock), i, o) for i, o in enumerate(block)]
        reordered = [x[2] for x in sorted(scored, key=lambda x: (-x[0], x[1]))]
        if reordered != block:
            orders[:end] = reordered
            action = dict(action)
            action["market"] = orders
            _V153_REPORT["changed"] += 1
    except Exception:
        _V153_REPORT["errors"] += 1
    return action

agent.telemetry = _V153_REPORT
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    args = ap.parse_args()
    src = Path(args.source)
    dst = Path(args.output)
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    if got != V147_SHA256:
        raise SystemExit(f"v147 sha mismatch: {got}")
    text = src.read_text(encoding="utf-8")
    for symbol in ("def _r37_market_price", "_R37_MARKET_PARAMS", "def projected_shed", "class FarmView"):
        if symbol not in text:
            raise SystemExit(f"required symbol missing: {symbol}")
    dst.write_text(text + APPEND, encoding="utf-8")
    print("v153_sha256=" + hashlib.sha256(dst.read_bytes()).hexdigest())
    print("change=v152 dense leading SELL self-impact reorder + empty-first-order guard only")
    print("barriers=preserved; quantities=preserved; opening/terminal=unchanged")


if __name__ == "__main__":
    main()
