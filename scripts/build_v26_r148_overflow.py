# -*- coding: utf-8 -*-
"""v25へPipe19のR148 overflow回収だけを追加してv26を生成する。

仕様: docs/experiments/EXP-20260922-51-v25-r148-overflow.md
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "submissions/v25_e402_e410/main.py"
TARGET = ROOT / "submissions/v26_r148_overflow/main.py"

LAYER = r'''

# ---- kaggriculture-il追加（2026-09-22、EXP-51）：R148 overflow回収 ----
# Ported from Ahmed Berat Ozer's public V43 R148 via Pipe19 (Apache-2.0).
# At hour 23, sell only shed stock which would otherwise be replaced by
# destroyed worker cargo, while preserving the complete post-dawn stock vector.
_V26_PARENT = kaggle_submission_agent
_V26_REPORT = dict(overflow_turns=0, overflow_units=0, errors=0)


def _v26_fields(observation, action):
    player = int(observation["player"])
    farm, private = _PLANNER_NS["_clone_state"](
        observation["farms"][player], observation["private"])
    commands = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
    demand = {}
    for command in commands:
        if len(command) > 1 and command[0] == "PLANT":
            demand[command[1]] = demand.get(command[1], 0) + 1
    blocked = {product for product, count in demand.items()
               if count > private["seeds"].get(product, 0)}
    for actor, command in enumerate(commands[:len(private["inventories"])]):
        if len(command) > 1 and command[0] == "PLANT" and command[1] in blocked:
            continue
        _PLANNER_NS["_apply_unit_action"](
            farm, private, actor, command, 10,
            int(observation["step"]) // 24, 24, 100)
    return farm, private


def _v26_same(left, right):
    return all(int(left.get(product, 0)) == int(right.get(product, 0))
               for product in set(left) | set(right))


def _v26_apply(observation, action):
    if int(observation["step"]) % 24 != 23:
        return action
    orders = action.get("market") or []
    if len(orders) >= MAX_ORDERS or not _r97_budget(observation, orders):
        return action
    _, private = _v26_fields(observation, action)
    stock, _, _ = _r97_market_stock(private["shed"], orders)
    original, loss = _r97_delivery(stock, private, True)
    if not loss:
        return action
    remaining = max(0, 100 - sum(stock.values()))
    tail = []
    for inventory in private["inventories"]:
        for item, count in inventory.items():
            count = max(0, int(count))
            take = min(count, remaining)
            remaining -= take
            if count > take:
                tail.extend([item] * (count - take))
    released = {}
    best = None
    for item in tail:
        released[item] = released.get(item, 0) + 1
        if (item not in observation["market"]["prices"]
                or released[item] > stock.get(item, 0)):
            break
        if len(orders) + len(released) > MAX_ORDERS:
            break
        proposed = list(orders) + [
            ["SELL", product, count] for product, count in released.items()]
        after, _, _ = _r97_market_stock(private["shed"], proposed)
        final, _ = _r97_delivery(after, private, True)
        if _v26_same(original, final):
            best = proposed, dict(released)
    if best is None:
        return action
    _V26_REPORT["overflow_turns"] += 1
    _V26_REPORT["overflow_units"] += sum(best[1].values())
    return dict(action, market=best[0])


# The parent source may retain an older ``agent`` key. Remove it so this
# definition is inserted at the end of the namespace for Kaggle's loader.
globals().pop("agent", None)


def agent(observation, configuration=None):
    try:
        if int(observation["step"]) == 0:
            for key in _V26_REPORT:
                _V26_REPORT[key] = 0
        action = _V26_PARENT(observation, configuration)
        return _v26_apply(observation, action)
    except Exception:
        _V26_REPORT["errors"] += 1
        try:
            return _V26_PARENT(observation, configuration)
        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}


agent.telemetry = _V26_REPORT
'''


if __name__ == "__main__":
    base = BASE.read_text(encoding="utf-8")
    body = (base.rstrip() + LAYER + "\n").encode("utf-8")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(body)
    print(f"{TARGET}: {len(body):,} bytes")
    print(f"  main SHA-256: {hashlib.sha256(body).hexdigest()}")
