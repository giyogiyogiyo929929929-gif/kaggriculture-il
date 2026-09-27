from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V147_SHA256 = "8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923"

APPEND = r'''

# v154: v153 dense leading-SELL self-impact reorder with a score-state safety gate.
# Relative to v153, the sole tactical change is: do not reorder while already
# ahead in current cash. Ties and trailing states remain eligible.
_V154_PARENT = agent
_V154_REPORT = {"eligible": 0, "changed": 0, "ahead_skips": 0, "errors": 0}
del agent


def _v154_self_exposure(observation, order, stock):
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
    action = _V154_PARENT(observation, configuration)
    try:
        step = int(observation.get("step", -1))
        orders = [list(o) for o in (action.get("market") or [])]
        if not (288 <= step < 694) or not orders or not orders[0] or orders[0][0] != "SELL":
            return action
        farms = observation.get("farms") or []
        player = int(observation.get("player", 0))
        if len(farms) >= 2:
            own_money = int(farms[player].get("money", 0))
            rival_money = int(farms[1 - player].get("money", 0))
            if own_money > rival_money:
                _V154_REPORT["ahead_skips"] += 1
                return action
        end = 0
        while end < len(orders) and orders[end] and orders[end][0] == "SELL":
            end += 1
        block = orders[:end]
        if len(block) < 5 or len({o[1] for o in block}) != len(block):
            return action
        _V154_REPORT["eligible"] += 1
        stock = projected_shed(action, FarmView(observation))
        scored = [(_v154_self_exposure(observation, o, stock), i, o) for i, o in enumerate(block)]
        reordered = [x[2] for x in sorted(scored, key=lambda x: (-x[0], x[1]))]
        if reordered != block:
            orders[:end] = reordered
            action = dict(action)
            action["market"] = orders
            _V154_REPORT["changed"] += 1
    except Exception:
        _V154_REPORT["errors"] += 1
    return action

agent.telemetry = _V154_REPORT
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
    print("v154_sha256=" + hashlib.sha256(dst.read_bytes()).hexdigest())
    print("change=v153 mechanism + do-not-reorder-while-ahead cash gate")


if __name__ == "__main__":
    main()
