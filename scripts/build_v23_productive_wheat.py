# -*- coding: utf-8 -*-
"""v22へv54の一時WHEAT周期だけを追加してv23を生成する。

仕様: docs/experiments/EXP-20260922-43-v23-productive-wheat.md
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "submissions/v22_antiv52_brunchguard/main.py"
TARGET = ROOT / "submissions/v23_productive_wheat/main.py"

LAYER = r'''

# ---- kaggriculture-il追加（2026-09-22、EXP-43）：一時WHEAT周期 ----
_V23_PARENT = _kil_v52_safe_agent
_V23_RAW = copy.deepcopy(_IMPL.chassis.routes[0][:96])
_V23_STATE = {}
_V23_REPORT = dict(temporary_crop_seen=0, temporary_crop_harvested=0,
                   restored_pasture_seen=0, delivered_extra_wheat=0, errors=0)


def _v23_install():
    tape = _IMPL.chassis.routes[0]
    tape[:96] = copy.deepcopy(_V23_RAW)
    tape[0]["market"] = list(tape[0]["market"]) + [["BUY_SEED", "WHEAT", 1]]
    for step, command in {2: ["WEST"], 3: ["WEST"], 4: ["WEST"],
                          5: ["PLANT", "WHEAT"], 6: ["WATER"]}.items():
        tape[step]["hands"][1] = command
    tape[29]["hands"][2] = ["WATER"]
    commands = [["WEST"], ["WEST"], ["WEST"], ["WATER"], ["HARVEST"],
                ["BUILD_PASTURE"], ["EAST"], ["EAST"], ["DROP"]]
    for step, command in zip(range(49, 58), commands):
        tape[step]["hands"][0] = command


def _v23_sell_extra(action, item, quantity):
    if quantity <= 0:
        return action
    orders = [list(order) for order in action.get("market", [])]
    sell = next((order for order in orders
                 if len(order) >= 3 and order[:2] == ["SELL", item]), None)
    if sell is not None:
        sell[2] += quantity
    elif len(orders) < MAX_ORDERS:
        orders.append(["SELL", item, quantity])
    else:
        return action
    return dict(action, market=orders)


def _v23_agent(observation, configuration=None):
    player, step = int(observation["player"]), int(observation["step"])
    state = _V23_STATE.get(player)
    if state is None or step <= state["step"]:
        _v23_install()
        state = _V23_STATE[player] = {"step": -1}
        for key in _V23_REPORT:
            _V23_REPORT[key] = 0
    action = _V23_PARENT(observation, configuration)
    try:
        farm, private = observation["farms"][player], observation["private"]
        site = farm["tiles"][4][2]
        if step == 6:
            _V23_REPORT["temporary_crop_seen"] = int(
                isinstance(site, dict) and site.get("crop") == "WHEAT")
        if step == 54:
            _V23_REPORT["temporary_crop_harvested"] = int(
                private["inventories"][1].get("WHEAT", 0))
        if step == 55:
            _V23_REPORT["restored_pasture_seen"] = int(
                isinstance(site, dict) and site.get("kind") == "PASTURE")
        if (step == 57 and farm["hands"] and tuple(farm["hands"][0]) == (4, 4)
                and action.get("hands", [[]])[0] == ["DROP"]):
            quantity = int(private["inventories"][1].get("WHEAT", 0))
            action = _v23_sell_extra(action, "WHEAT", quantity)
            _V23_REPORT["delivered_extra_wheat"] = quantity
    except Exception:
        _V23_REPORT["errors"] += 1
    state["step"] = step
    return action


_v23_agent.telemetry = _V23_REPORT


def kaggle_submission_agent(observation, configuration=None):
    try:
        return _v23_agent(observation, configuration)
    except Exception:
        _V23_REPORT["errors"] += 1
        return {"farmer": ["PASS"], "hands": [], "market": []}


kaggle_submission_agent.telemetry = _V23_REPORT
'''


if __name__ == "__main__":
    base = BASE.read_text(encoding="utf-8")
    body = (base.rstrip() + LAYER + "\n").encode("utf-8")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(body)
    print(f"{TARGET}: {len(body):,} bytes")
    print(f"  main SHA-256: {hashlib.sha256(body).hexdigest()}")
