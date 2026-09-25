#!/usr/bin/env python3
from pathlib import Path

src = Path("champion/v94_adaptive_h14_yarn2_nomilk/main.py")
out = Path("candidates/v96_generic_sell_lead1/main.py")
s = src.read_text(encoding="utf-8")

s = s.replace(
    '__version__ = "v90-classified-sell-lead"',
    '__version__ = "v96-generic-sell-lead1"',
    1,
)

anchor = '_V52_LEAD_STATE = {0: {"mode": "fallback", "probe_step": -1, "probe_ceiling": 0}, 1: {"mode": "fallback", "probe_step": -1, "probe_ceiling": 0}}\n'
insert = '''_GENERIC_LEAD_STATE = {\n    0: {"last_step": -1, "due_step": -1, "due": {}},\n    1: {"last_step": -1, "due_step": -1, "due": {}},\n}\n'''
assert anchor in s
s = s.replace(anchor, anchor + insert, 1)

func = '''def _generic_lead_state(obs, step):\n    seat = _seat(obs)\n    state = _GENERIC_LEAD_STATE[seat]\n    if step == 0 or step < int(state.get("last_step", -1)):\n        state = {"last_step": step, "due_step": -1, "due": {}}\n        _GENERIC_LEAD_STATE[seat] = state\n    state["last_step"] = step\n    return state\n\n\ndef _repay_generic_lead(obs, action, step):\n    state = _generic_lead_state(obs, step)\n    if int(state.get("due_step", -1)) != step:\n        if int(state.get("due_step", -1)) < step:\n            state["due_step"], state["due"] = -1, {}\n        return action\n    due = {item: max(0, int(q)) for item, q in dict(state.get("due") or {}).items()}\n    market = []\n    for raw in action.get("market", []) or []:\n        order = list(raw)\n        if len(order) >= 3 and order[0] == "SELL" and due.get(order[1], 0) > 0:\n            item = order[1]\n            q = max(0, int(order[2]))\n            cut = min(q, due[item])\n            q -= cut\n            due[item] -= cut\n            if q <= 0:\n                continue\n            order[2] = q\n        market.append(order)\n    action["market"] = market\n    state["due_step"], state["due"] = -1, {}\n    return action\n\n\ndef _town_consumes_after_current_sale(obs, step, item):\n    # Market orders execute before town consumption on the same step.\n    # A one-step advance from step+1 to step would cross this consumption tick.\n    town = _get(obs, "town", {}) or {}\n    shops = list(_get(town, "unlocked_shops", []) or [])\n    if step % 4 == 0:\n        for shop in shops:\n            products = _SHOP_PRODUCTS.get(shop, ())\n            if item in products:\n                return True\n    if item != "FERTILIZER" and step % 24 == 0:\n        return True\n    return False\n\n\ndef _generic_sell_lead1(obs, action, step):\n    if step + 1 >= len(_ACTIONS):\n        return action\n    state = _generic_lead_state(obs, step)\n    if state.get("due"):\n        return action\n    market = list(action.get("market") or [])\n    if len(market) >= 10:\n        return action\n    next_sells = {}\n    for raw in (_ACTIONS[step + 1].get("market") or []):\n        if _is_sell(raw):\n            item = str(raw[1])\n            next_sells[item] = next_sells.get(item, 0) + max(0, int(raw[2]))\n    if not next_sells:\n        return action\n    projected = _projected_shed(obs, action)\n    for raw in market:\n        if _is_sell(raw):\n            item = str(raw[1])\n            projected[item] = max(0, int(projected.get(item, 0) or 0) - max(0, int(raw[2])))\n    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}\n    shifted = {}\n    for item, planned in next_sells.items():\n        if len(market) >= 10:\n            break\n        if planned <= 0 or _town_consumes_after_current_sale(obs, step, item):\n            continue\n        if float(_get(prices, item, 0) or 0) <= _PRICE_FLOOR:\n            continue\n        q = min(planned, max(0, int(projected.get(item, 0) or 0)))\n        if q <= 0:\n            continue\n        market.append(["SELL", item, q])\n        projected[item] = max(0, int(projected.get(item, 0) or 0) - q)\n        shifted[item] = q\n    if shifted:\n        action["market"] = market[:10]\n        state["due_step"] = step + 1\n        state["due"] = shifted\n    return action\n\n\n'''
assert "def agent(obs):\n" in s
s = s.replace("def agent(obs):\n", func + "def agent(obs):\n", 1)

old = '''        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)\n        action = _repay_shift(obs, action, step)\n        action = _rank_sell_slots(obs, action, None)\n        action = _preempt_shift(obs, action, step)\n'''
new = '''        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)\n        action = _repay_generic_lead(obs, action, step)\n        action = _repay_shift(obs, action, step)\n        action = _rank_sell_slots(obs, action, None)\n        action = _generic_sell_lead1(obs, action, step)\n        action = _preempt_shift(obs, action, step)\n'''
assert old in s
s = s.replace(old, new, 1)

out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(s, encoding="utf-8")
print(out)
