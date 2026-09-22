# -*- coding: utf-8 -*-
"""v17の検知器で、基準販売量と実際の販売量を分離したv19を生成する。"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "opponents" / "v52" / "main.py"
V17 = ROOT / "submissions" / "v17_antiv52_strict" / "main.py"


if __name__ == "__main__":
    base = BASE.read_text(encoding="utf-8")
    body = V17.read_text(encoding="utf-8")
    assert body.startswith(base)

    old_state = '''def _kil_v52_new_state(step=-1):
    return {"step": step, "same_farm": True, "same_sales": True, "copy": False,
            "evidence": 0, "seen": {}, "best": {}}
'''
    new_state = '''def _kil_v52_new_state(step=-1):
    return {"step": step, "same_farm": True, "same_sales": True, "copy": False,
            "abandoned": False, "actual_prev": None,
            "evidence": 0, "seen": {}, "best": {}}
'''

    new_detector = '''def _kil_v52_update_detector(observation, previous, actual_previous=None):
    player, step = int(observation["player"]), int(observation["step"])
    state = _KIL_V52_STATE.get(player)
    if state is None or step <= state["step"]:
        state = _KIL_V52_STATE[player] = _kil_v52_new_state()
    state["step"] = step

    if previous and previous.get("step") == step - 1:
        accounting = actual_previous
        if not accounting or accounting.get("step") != step - 1:
            accounting = previous
        draw = _v9_town_draw(accounting.get("shops", []), accounting["step"])
        inventory = observation["market"]["inventory"]
        for index, item in enumerate(_V92_P_ITEMS):
            baseline = int(previous.get("own", {}).get(item, 0))
            executed = int(accounting.get("own", {}).get(item, 0))
            rival = (int(inventory[item]) - int(accounting["inventory"][item])
                     + int(draw.get(item, 0)) - executed)
            if previous.get("prices", {}).get(item, 0) > 3 and baseline >= 2:
                state["seen"][(step - 1, index)] = baseline
            if step >= _KIL_V52_START and (baseline >= 2 or rival >= 2):
                state["evidence"] += 1
                _KIL_V52_REPORT["evidence"] += 1
                if baseline != rival:
                    state["same_sales"] = False
                    _KIL_V52_REPORT["mismatches"] += 1
                    if state["copy"]:
                        state["copy"] = False
                        state["abandoned"] = True

    if (_KIL_V52_START <= step <= _KIL_V52_COMMIT and not state["copy"]
            and not state["abandoned"]):
        farms = observation["farms"]
        if _kil_v52_farm_key(farms[player]) != _kil_v52_farm_key(farms[1 - player]):
            state["same_farm"] = False
        if (step == _KIL_V52_COMMIT and state["same_farm"] and state["same_sales"]
                and state["evidence"] >= _KIL_V52_MIN_EVIDENCE):
            state["copy"] = True
            _KIL_V52_REPORT["copy_games"] += 1
    return state
'''

    counter_start = body.index("def _kil_v52_counter_agent(")
    counter_end = body.index("\n\n_KIL_V52_SAFE_INNER", counter_start)
    old_counter = body[counter_start:counter_end]
    new_counter = '''def _kil_v52_actual_snapshot(observation, action):
    stock = dict(projected_shed(action, FarmView(observation)))
    own = {}
    for order in action.get("market") or []:
        if len(order) < 3 or order[0] != "SELL":
            continue
        item = order[1]
        quantity = min(100, max(0, int(order[2])), int(stock.get(item, 0)))
        if quantity:
            own[item] = own.get(item, 0) + quantity
            stock[item] = int(stock.get(item, 0)) - quantity
    market = observation["market"]
    return {"step": int(observation["step"]),
            "shops": list((observation.get("town") or {}).get("unlocked_shops", [])),
            "inventory": dict(market["inventory"]), "prices": dict(market["prices"]),
            "own": own}


def _kil_v52_counter_agent(observation, configuration=None):
    try:
        player = int(observation["player"])
        previous = (_V9_RACE.get(player) or {}).get("prev")
        prior_state = _KIL_V52_STATE.get(player) or {}
        state = _kil_v52_update_detector(observation, previous, prior_state.get("actual_prev"))
    except Exception:
        _KIL_V52_REPORT["errors"] += 1
        state = {"copy": False}
    action = _KIL_V52_PARENT(observation, configuration)
    try:
        result = _kil_v52_preempt(observation, action, state)
        state["actual_prev"] = _kil_v52_actual_snapshot(observation, result)
        return result
    except Exception:
        _KIL_V52_REPORT["errors"] += 1
        return action
'''

    assert body.count(old_state) == 1
    body = body.replace(old_state, new_state)
    start = body.index("def _kil_v52_update_detector(")
    end = body.index("\n\ndef _kil_v52_best", start)
    body = body[:start] + new_detector + body[end:]
    counter_start = body.index("def _kil_v52_counter_agent(")
    counter_end = body.index("\n\n_KIL_V52_SAFE_INNER", counter_start)
    body = body[:counter_start] + new_counter + body[counter_end:]

    out_dir = ROOT / "submissions" / "v19_antiv52_actualsales"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "main.py"
    encoded = body.encode("utf-8")
    target.write_bytes(encoded)
    print(f"{target}: {len(encoded):,} bytes")
    print(f"  main SHA-256: {hashlib.sha256(encoded).hexdigest()}")
