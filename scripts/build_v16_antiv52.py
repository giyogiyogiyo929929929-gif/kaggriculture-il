# -*- coding: utf-8 -*-
r"""v52原本＋旧v52コピー検出＋PREDICT 1ターン先回り＋安全包みを生成する。"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LAYER = r'''

# ---- kaggriculture-il 追加（2026-09-21、ADR-0007）：旧v52コピー専用のPREDICT先回り ----
_KIL_V52_PARENT = [value for value in list(globals().values()) if callable(value)][-1]
_KIL_V52_STATE = {}
_KIL_V52_START = 96
_KIL_V52_COMMIT = 167
_KIL_V52_MIN_EVIDENCE = 3
_KIL_V52_LEAD = 1
_KIL_V52_REPORT = dict(copy_games=0, copy_turns=0, evidence=0, mismatches=0,
                         preempt_fires=0, preempt_units=0, errors=0)


def _kil_v52_farm_key(farm):
    tiles = [[None if isinstance(tile, dict) and tile.get("kind") == "WEED" else tile
              for tile in row] for row in (farm.get("tiles") or [])]
    return tiles, {key: value for key, value in farm.items() if key not in ("tiles", "money")}


def _kil_v52_new_state(step=-1):
    return {"step": step, "same_farm": True, "same_sales": True, "copy": False,
            "evidence": 0, "seen": {}, "best": {}}


def _kil_v52_update_detector(observation, previous):
    player, step = int(observation["player"]), int(observation["step"])
    state = _KIL_V52_STATE.get(player)
    if state is None or step <= state["step"]:
        state = _KIL_V52_STATE[player] = _kil_v52_new_state()
    state["step"] = step

    if previous and previous.get("step") == step - 1:
        draw = _v9_town_draw(previous.get("shops", []), previous["step"])
        inventory = observation["market"]["inventory"]
        for index, item in enumerate(_V92_P_ITEMS):
            own = int(previous.get("own", {}).get(item, 0))
            rival = int(inventory[item]) - int(previous["inventory"][item]) + int(draw.get(item, 0)) - own
            if previous.get("prices", {}).get(item, 0) > 3 and own >= 2:
                state["seen"][(step - 1, index)] = own
            if step >= _KIL_V52_START and (own >= 2 or rival >= 2):
                state["evidence"] += 1
                _KIL_V52_REPORT["evidence"] += 1
                if own != rival:
                    state["same_sales"] = False
                    _KIL_V52_REPORT["mismatches"] += 1

    if _KIL_V52_START <= step <= _KIL_V52_COMMIT and not state["copy"]:
        farms = observation["farms"]
        if _kil_v52_farm_key(farms[player]) != _kil_v52_farm_key(farms[1 - player]):
            state["same_farm"] = False
        if (step == _KIL_V52_COMMIT and state["same_farm"] and state["same_sales"]
                and state["evidence"] >= _KIL_V52_MIN_EVIDENCE):
            state["copy"] = True
            _KIL_V52_REPORT["copy_games"] += 1
    return state


def _kil_v52_best(state, observation, step):
    if step not in state["best"]:
        previous = state["best"].get(step - 1)
        if step % _V92_P_EVERY == 0 or previous is None:
            state["best"][step] = _v92_p_forecast(
                {"step": step, "town": observation["town"]}, {"obs": state["seen"]})
        else:
            state["best"][step] = previous
    return state["best"][step]


def _kil_v52_preempt(observation, action, state):
    step = int(observation["step"])
    if not state["copy"] or step < _KIL_V52_COMMIT or step >= 700 - _KIL_V52_LEAD:
        return action
    _KIL_V52_REPORT["copy_turns"] += 1
    for target_step in range(max(state["best"], default=step - 1) + 1, step + _KIL_V52_LEAD + 1):
        _kil_v52_best(state, observation, target_step)
    target = step + _KIL_V52_LEAD
    best = state["best"].get(target) or []
    native = _IMPL.chassis.players.get(int(observation["player"]))
    if not best or not native or native.get("route") not in _IMPL.chassis.routes:
        return action
    tape = _IMPL.chassis.routes[native["route"]]
    market = [list(order) for order in action.get("market") or []]
    already = {order[1] for order in market if len(order) > 1 and order[0] in ("SELL", "BUY_PRODUCT")}
    stock = None
    changed = False
    for index, item in enumerate(_V92_P_ITEMS):
        if item not in _V92_P_USE or item in already or len(market) >= MAX_ORDERS:
            continue
        if not any(event.get((target + 1, index), 0) + event.get((target + 2, index), 0) >= _V92_P_K
                   for event in best):
            continue
        ours = 0
        for future in range(step + 1, min(len(tape), target + _V92_P_H + 1)):
            ours += sum(min(100, int(order[2])) for order in (tape[future] or {}).get("market") or []
                        if len(order) >= 3 and order[0] == "SELL" and order[1] == item)
        if stock is None:
            stock = projected_shed(action, FarmView(observation))
        quantity = min(int(stock.get(item, 0)), ours)
        if quantity > 0:
            market.insert(0, ["SELL", item, quantity])
            _KIL_V52_REPORT["preempt_fires"] += 1
            _KIL_V52_REPORT["preempt_units"] += quantity
            changed = True
    if not changed:
        return action
    result = dict(action)
    result["market"] = market[:MAX_ORDERS]
    return result


def _kil_v52_counter_agent(observation, configuration=None):
    try:
        player = int(observation["player"])
        previous = (_V9_RACE.get(player) or {}).get("prev")
        state = _kil_v52_update_detector(observation, previous)
    except Exception:
        _KIL_V52_REPORT["errors"] += 1
        state = {"copy": False}
    action = _KIL_V52_PARENT(observation, configuration)
    try:
        return _kil_v52_preempt(observation, action, state)
    except Exception:
        _KIL_V52_REPORT["errors"] += 1
        return action


_KIL_V52_SAFE_INNER = _kil_v52_counter_agent


def _kil_v52_safe_agent(observation, configuration=None):
    try:
        return _KIL_V52_SAFE_INNER(observation, configuration)
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
'''


if __name__ == "__main__":
    base = (ROOT / "opponents" / "v52" / "main.py").read_bytes()
    out_dir = ROOT / "submissions" / "v16_antiv52"
    out_dir.mkdir(parents=True, exist_ok=True)
    body = base + LAYER.encode("utf-8")
    target = out_dir / "main.py"
    target.write_bytes(body)
    assert body[: len(base)] == base
    print(f"{target}: {len(body):,} bytes")
    print(f"  v52 SHA-256: {hashlib.sha256(base).hexdigest()}")
    print(f"  main SHA-256: {hashlib.sha256(body).hexdigest()}")
