# -*- coding: utf-8 -*-
"""v25へOrder Book Layer Dだけを追加してv27を生成する。

仕様: docs/experiments/EXP-20260922-52-v25-orderbook-layer-d.md
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "submissions/v25_e402_e410/main.py"
TARGET = ROOT / "submissions/v27_orderbook_layer_d/main.py"

LAYER = r'''

# ---- kaggriculture-il追加（2026-09-22、EXP-52）：Order Book Layer D ----
# Ported from shiiin9/your-market-list-is-an-order-book (Apache-2.0).
import itertools as _v27_it
_V27_PARENT = kaggle_submission_agent
_V27_FIXED = ("HIRE", "BUY_SEED", "BUY_ANIMAL", "BUY_LAND")
_V27_BUDGET = 800
_V27_REPORT = dict(reordered_turns=0, estimated_gain=0.0, evaluations=0,
                   budget_hits=0, errors=0)


def _v27_candidates(orders, slots, sells, fixed):
    for positions in _v27_it.permutations(slots, len(sells)):
        result = list(orders)
        remaining = [index for index in slots if index not in positions]
        for index, order in zip(positions, sells):
            result[index] = order
        for index, order in zip(remaining, fixed):
            result[index] = order
        yield result


def _v27_reorder(observation, action):
    market = action.get("market") or []
    if len(market) < 2:
        return action
    orders = [list(order) if isinstance(order, (list, tuple)) else order
              for order in market]
    bought = {order[1] for order in orders
              if order and len(order) > 1 and order[0] == "BUY_PRODUCT"}
    slots, sells, fixed = [], [], []
    for index, order in enumerate(orders):
        if not order:
            continue
        if order[0] in _V27_FIXED:
            slots.append(index)
            fixed.append(order)
        elif order[0] == "SELL" and len(order) > 1 and order[1] not in bought:
            slots.append(index)
            sells.append(order)
    if not sells or len(slots) < 2:
        return action
    params = _v44y_params(observation)
    stock = {key: max(0, int(value)) for key, value in
             projected_shed(action, FarmView(observation)).items()}
    inventory = {key: int(value) for key, value in
                 observation["market"]["inventory"].items()}
    factor = _v44y_factor_margin(orders, inventory, stock, params)
    base = best = factor(orders)
    best_orders = None
    evaluations = 0
    for candidate in _v27_candidates(orders, slots, sells, fixed):
        if candidate == orders:
            continue
        evaluations += 1
        if evaluations > _V27_BUDGET:
            _V27_REPORT["budget_hits"] += 1
            break
        value = factor(candidate)
        if value > best + 0.5:
            best, best_orders = value, candidate
    _V27_REPORT["evaluations"] += evaluations
    if best_orders is None:
        return action
    _V27_REPORT["reordered_turns"] += 1
    _V27_REPORT["estimated_gain"] += best - base
    return dict(action, market=best_orders)


globals().pop("agent", None)


def agent(observation, configuration=None):
    try:
        if int(observation["step"]) == 0:
            _V27_REPORT.update(reordered_turns=0, estimated_gain=0.0,
                               evaluations=0, budget_hits=0, errors=0)
        action = _V27_PARENT(observation, configuration)
        return _v27_reorder(observation, action)
    except Exception:
        _V27_REPORT["errors"] += 1
        try:
            return _V27_PARENT(observation, configuration)
        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}


agent.telemetry = _V27_REPORT
'''


if __name__ == "__main__":
    base = BASE.read_text(encoding="utf-8")
    body = (base.rstrip() + LAYER + "\n").encode("utf-8")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(body)
    print(f"{TARGET}: {len(body):,} bytes")
    print(f"  main SHA-256: {hashlib.sha256(body).hexdigest()}")
