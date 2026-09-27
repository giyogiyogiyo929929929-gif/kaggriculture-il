from pathlib import Path
import hashlib
import sys

V151_SHA256 = "54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31"

OVERLAY = r'''
# ---- v155 tactic: v154 dense self-exposure SELL ordering, only while not ahead in cash ----
_V155_PARENT = agent
_V155_REPORT = {"eligible": 0, "changed": 0, "ahead_skips": 0, "errors": 0}

del agent

def _v155_self_exposure(observation, order, stock):
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
    action = _V155_PARENT(observation, configuration)
    if observation is None:
        return action
    try:
        step = int(observation.get("step", -1))
        orders = [list(o) for o in (action.get("market") or [])]
        if not (288 <= step < 694) or not orders or not orders[0] or orders[0][0] != "SELL":
            return action

        farms = observation.get("farms") or []
        player = int(observation.get("player", 0))
        if len(farms) >= 2 and player in (0, 1):
            own_money = int(farms[player].get("money", 0))
            rival_money = int(farms[1 - player].get("money", 0))
            if own_money > rival_money:
                _V155_REPORT["ahead_skips"] += 1
                return action

        end = 0
        while end < len(orders) and orders[end] and orders[end][0] == "SELL":
            end += 1
        block = orders[:end]
        if len(block) < 5 or len({o[1] for o in block}) != len(block):
            return action
        _V155_REPORT["eligible"] += 1
        stock = projected_shed(action, FarmView(observation))
        scored = [(_v155_self_exposure(observation, o, stock), i, o) for i, o in enumerate(block)]
        reordered = [x[2] for x in sorted(scored, key=lambda x: (-x[0], x[1]))]
        if reordered != block:
            orders[:end] = reordered
            action = dict(action)
            action["market"] = orders
            _V155_REPORT["changed"] += 1
    except Exception:
        _V155_REPORT["errors"] += 1
    return action

agent.telemetry = _V155_REPORT
kaggle_submission_agent_v155 = agent
'''

if __name__ == "__main__":
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    if got != V151_SHA256:
        raise SystemExit(f"expected exact v151 {V151_SHA256}, got {got}")
    dst.write_bytes(src.read_bytes() + b"\n" + OVERLAY.lstrip("\n").encode("utf-8"))
    print("v151_sha256=" + got)
    print("v155_sha256=" + hashlib.sha256(dst.read_bytes()).hexdigest())
    print("change=v154 dense leading SELL self-impact ordering + do-not-reorder-while-ahead cash guard")
