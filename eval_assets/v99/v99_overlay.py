# v99 candidate overlay: preserve main-farmer weedlag state across day boundaries.
# Parent: v96_champion_lead11_milkshops2.py
# One mechanism only: at step % 24 == 0, clear farmhand lag state but keep actor 0.

_V99_WL_REPORT = {"main_boundary_preserved": 0, "errors": 0}

def _e343_weedlag(obs, action):
    step = int(obs["step"])
    player = int(obs["player"])
    st = _E343_WL_STATE.setdefault(player, {"step": -1, "active": {}})
    if step <= st["step"]:
        st["active"] = {}
    st["step"] = step

    # v96 cleared every actor here because farmhands are re-hired daily.
    # Actor 0 is the persistent main farmer, so retain only its lag state.
    if step % 24 == 0:
        main = st["active"].get(0)
        st["active"] = ({0: main} if main is not None else {})
        if main is not None:
            _V99_WL_REPORT["main_boundary_preserved"] += 1

    farm = obs["farms"][player]
    positions = [tuple(farm["farmer"]), *map(tuple, farm["hands"])]
    tiles = farm["tiles"]
    units = [
        list(action.get("farmer") or ["PASS"]),
        *[list(h) if isinstance(h, list) else ["PASS"] for h in (action.get("hands") or [])],
    ]
    tape_now = _e343_tape_units(player, step)
    tape_prev = _e343_tape_units(player, step - 1)
    changed = False

    # Identical to v96 below this point.
    for k, tx in list(st["active"].items()):
        if k >= len(units) or k >= len(positions):
            st["active"].pop(k, None)
            continue
        age = step - tx["start"]
        if age == 1:
            units[k] = list(tx["intended"])
            changed = True
            _E343_WL_REPORT["replays"] += 1
        elif 2 <= age <= 1 + _E343_WL_STEPS:
            prev = tape_prev[k] if k < len(tape_prev) else ["PASS"]
            units[k] = list(prev) if isinstance(prev, list) and prev else ["PASS"]
            changed = True
            _E343_WL_REPORT["replays"] += 1
        else:
            st["active"].pop(k, None)

    for k in range(min(len(units), len(positions), len(tape_now))):
        if k in st["active"]:
            continue
        intent = tape_now[k]
        if not (isinstance(intent, list) and intent and intent[0] in _E343_WL_OPS):
            continue
        x, y = positions[k]
        tile = tiles[y][x]
        if not (isinstance(tile, dict) and tile.get("kind") == "WEED"):
            continue
        if units[k] != ["DIG"]:
            units[k] = ["DIG"]
            changed = True
        st["active"][k] = {"start": step, "intended": list(intent)}
        _E343_WL_REPORT["events"] += 1

    if not changed:
        return action
    return dict(action, farmer=units[0], hands=units[1:])
