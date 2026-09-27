from pathlib import Path
import hashlib
import sys

V151_SHA256 = "54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31"

OVERLAY = r'''
# ---- v154 tactic: port v153 dense self-exposure SELL ordering onto exact v151 ----
_V154_PARENT = agent
_V154_REPORT = {"eligible": 0, "changed": 0, "errors": 0}

del agent

def _v154_self_exposure(observation, order, stock):
    if len(order) < 3 or order[0] != "SELL":
        return 0
    item = order[1]
    quantity = min(max(0, int(order[2])), max(0, int(stock.get(item, 0))))
    if quantity <= 0 or item not in _R37_MARKET_PARAMS:
        return 0
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
    # Preserve v151 None-observation safety exactly; this is not a new tactic/safety behavior.
    if observation is None:
        return action
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
kaggle_submission_agent_v154 = agent
'''

if __name__ == "__main__":
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    if got != V151_SHA256:
        raise SystemExit(f"expected exact v151 {V151_SHA256}, got {got}")
    dst.write_bytes(src.read_bytes() + b"\n" + OVERLAY.lstrip("\n").encode("utf-8"))
    print("v151_sha256=" + got)
    print("v154_sha256=" + hashlib.sha256(dst.read_bytes()).hexdigest())
    print("change=v153 dense leading SELL self-impact ordering ported onto exact v151")
