from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUFFIX = (ROOT / "v122_suffix.pyfrag").read_text(encoding="utf-8")

def fresh():
    ns = {}
    def _get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)
    def _seat(obs):
        return int(obs.get("seat", 0))
    def parent(obs, config=None):
        a = obs.get("parent_action", {})
        out = dict(a)
        out["market"] = [list(o) for o in (a.get("market") or [])]
        return out
    parent.telemetry = {}
    ns.update({"_get": _get, "_seat": _seat, "agent": parent})
    exec(compile(SUFFIX, "v122_suffix.pyfrag", "exec"), ns)
    return ns

def obs(step, inv, price=214, shed=8, market=None, seat=0):
    return {
        "step": step,
        "seat": seat,
        "market": {"inventory": {"WOOL": inv}, "prices": {"WOOL": price}},
        "private": {"shed": {"WOOL": shed}},
        "parent_action": {"market": list(market or [])},
    }

BASE = [
    ["SELL", "STRAWBERRY", 14],
    ["SELL", "WHEAT", 4],
    ["SELL", "WOOL", 8],
    ["HIRE"],
]

# Canonical step-456 shape: keep STRAWBERRY first, move WOOL across WHEAT only.
ns = fresh(); agent = ns["agent"]
agent(obs(455, 9993, market=[]))
a = agent(obs(456, 9996, market=BASE))
assert a["market"][:3] == [
    ["SELL", "STRAWBERRY", 14],
    ["SELL", "WOOL", 8],
    ["SELL", "WHEAT", 4],
], a
r = agent.telemetry["wool_lowrisk_front1"]
assert r["reorders"] == 1 and r["units"] == 8 and r["moved_slots"] == 1, r

# No clean increase.
ns = fresh(); agent = ns["agent"]
agent(obs(455, 9993, market=[]))
a = agent(obs(456, 9995, market=BASE))
assert a["market"] == BASE
assert agent.telemetry["wool_lowrisk_front1"]["signal_blocks"] == 1

# Price gate.
ns = fresh(); agent = ns["agent"]
agent(obs(455, 9990, market=[]))
a = agent(obs(456, 9994, price=209, market=BASE))
assert a["market"] == BASE

# Inventory gate.
ns = fresh(); agent = ns["agent"]
agent(obs(455, 9998, market=[]))
a = agent(obs(456, 10002, price=220, market=BASE))
assert a["market"] == BASE

# Entire-shed gate.
ns = fresh(); agent = ns["agent"]
agent(obs(455, 9990, market=[]))
a = agent(obs(456, 9994, price=220, shed=12, market=BASE))
assert a["market"] == BASE

# Never cross premium: WOOL immediately behind STRAWBERRY is unchanged.
PREMIUM = [["SELL", "MILK", 3], ["SELL", "WOOL", 8], ["SELL", "WHEAT", 4]]
ns = fresh(); agent = ns["agent"]
agent(obs(455, 9990, market=[]))
a = agent(obs(456, 9994, price=220, market=PREMIUM))
assert a["market"] == PREMIUM

# Never cross more than one low-risk order.
TWO_LOW = [["SELL", "STRAWBERRY", 14], ["SELL", "FERTILIZER", 3], ["SELL", "WHEAT", 4], ["SELL", "WOOL", 8]]
ns = fresh(); agent = ns["agent"]
agent(obs(455, 9990, market=[]))
a = agent(obs(456, 9994, price=220, market=TWO_LOW))
assert a["market"] == TWO_LOW

# Any BUY dependency blocks.
BUY = BASE + [["BUY_PRODUCT", "WHEAT", 1]]
ns = fresh(); agent = ns["agent"]
agent(obs(455, 9990, market=[]))
a = agent(obs(456, 9994, price=220, market=BUY))
assert a["market"] == BUY

# Own prior WOOL sale means the observed increase is not a clean opponent-only signal.
ns = fresh(); agent = ns["agent"]
agent(obs(455, 9990, shed=1, market=[["SELL", "WOOL", 1]]))
a = agent(obs(456, 9994, price=220, market=BASE))
assert a["market"] == BASE

# Seat state is independent.
ns = fresh(); agent = ns["agent"]
agent(obs(455, 9990, market=[], seat=0))
agent(obs(455, 9990, market=[["SELL", "WOOL", 1]], seat=1))
a0 = agent(obs(456, 9994, price=220, market=BASE, seat=0))
a1 = agent(obs(456, 9994, price=220, market=BASE, seat=1))
assert a0["market"][1][1] == "WOOL"
assert a1["market"] == BASE

print("v122 synthetic checks: PASS")
