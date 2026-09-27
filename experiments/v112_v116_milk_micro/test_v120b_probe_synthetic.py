from pathlib import Path


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


_ACTIONS = [{"market": []} for _ in range(20)]
_ACTIONS[12] = {"market": [["SELL", "STRAWBERRY", 3]]}
_ACTIONS[13] = {"market": [["SELL", "MELON", 4]]}

_actions = {}

def parent(obs, config=None):
    return _actions[int(obs["step"])]

parent.telemetry = {"parent": {"ok": 1}}
agent = parent
exec((Path(__file__).resolve().parent / "v120b_suffix.pyfrag").read_text(encoding="utf-8"), globals())


def obs(step, s_inv, m_inv, s_price=150, m_price=260, s_shed=0, m_shed=0):
    return {
        "step": step,
        "market": {
            "inventory": {"STRAWBERRY": s_inv, "MELON": m_inv, "MILK": 10000, "WOOL": 10000},
            "prices": {"STRAWBERRY": s_price, "MELON": m_price, "MILK": 160, "WOOL": 200},
        },
        "private": {"shed": {"STRAWBERRY": s_shed, "MELON": m_shed}},
    }


a10 = {"market": []}
a11 = {"market": [["SELL", "STRAWBERRY", 2], ["BUY", "WHEAT", 1]]}
_actions[10] = a10
_actions[11] = a11

r0 = agent(obs(10, 100, 200), None)
assert r0 is a10
r1 = agent(obs(11, 105, 206, s_price=140, m_price=250, s_shed=7, m_shed=5), None)
assert r1 is a11

rep = _V120B_REPORT
assert rep["errors"] == 0
assert rep["clean_events"]["STRAWBERRY"] == 1
assert rep["clean_events"]["MELON"] == 1
assert rep["shed_positive"]["STRAWBERRY"] == 1
assert rep["shed_positive"]["MELON"] == 1
assert rep["same_sell_now"]["STRAWBERRY"] == 1
assert rep["same_sell_now"]["MELON"] == 0
assert rep["future_sell_h1"]["STRAWBERRY"] == 1
assert rep["future_sell_h2"]["MELON"] == 1
assert rep["any_sell_h0_3"]["STRAWBERRY"] == 1
assert rep["any_sell_h0_3"]["MELON"] == 1
assert rep["buy_free_now"]["STRAWBERRY"] == 0
assert rep["buy_free_now"]["MELON"] == 0
assert rep["shed_sell_buyfree"]["STRAWBERRY"] == 0
assert rep["price_above_base"]["STRAWBERRY"] == 1
assert rep["price_above_base"]["MELON"] == 1
assert len(rep["events"]) == 2
assert agent.telemetry["parent"]["ok"] == 1
print("v120b synthetic checks: PASS")
