from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUFFIX = (ROOT / "v121_suffix.pyfrag").read_text(encoding="utf-8")


def fresh(actions=None):
    actions = actions or [{} for _ in range(720)]
    ns = {"_ACTIONS": actions}

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
    exec(compile(SUFFIX, "v121_suffix.pyfrag", "exec"), ns)
    return ns


def obs(step, inv, price=153, shed=32, market=None, seat=0):
    return {
        "step": step,
        "seat": seat,
        "market": {"inventory": {"STRAWBERRY": inv}, "prices": {"STRAWBERRY": price}},
        "private": {"shed": {"STRAWBERRY": shed}},
        "parent_action": {"market": list(market or [])},
    }


def strawberry_sell(action):
    return sum(int(o[2]) for o in action.get("market", []) if len(o) >= 3 and o[0] == "SELL" and o[1] == "STRAWBERRY")


# Canonical hotspot shape: +5 external inventory, high price, shed32,
# parent sells8, later static sell22. Shift 4 now, repay 4 later.
actions = [{} for _ in range(720)]
actions[599] = {"market": [["SELL", "STRAWBERRY", 22]]}
ns = fresh(actions)
agent = ns["agent"]
agent(obs(576, 9980, market=[]))
a = agent(obs(577, 9985, market=[["SELL", "STRAWBERRY", 8]]))
assert strawberry_sell(a) == 12, a
rep = agent.telemetry["strawberry_race_shift4"]
assert rep["activations"] == 1 and rep["units_shifted"] == 4, rep
assert rep["activation_steps"][0]["repay_step"] == 599, rep
b = agent(obs(599, 9990, price=130, shed=22, market=[["SELL", "STRAWBERRY", 22], ["SELL", "WHEAT", 3]]))
assert strawberry_sell(b) == 18, b
assert b["market"][1] == ["SELL", "WHEAT", 3], b
assert rep["repayments"] == 1 and rep["units_repaid"] == 4 and rep["repay_shortfalls"] == 0, rep

# No external inventory increase -> no activation.
ns = fresh(actions); agent = ns["agent"]
agent(obs(576, 9980, market=[]))
a = agent(obs(577, 9980, market=[["SELL", "STRAWBERRY", 8]]))
assert strawberry_sell(a) == 8
assert agent.telemetry["strawberry_race_shift4"]["activations"] == 0

# Low price blocks.
ns = fresh(actions); agent = ns["agent"]
agent(obs(576, 9980, market=[]))
a = agent(obs(577, 9985, price=140, market=[["SELL", "STRAWBERRY", 8]]))
assert strawberry_sell(a) == 8
assert agent.telemetry["strawberry_race_shift4"]["price_blocks"] == 1

# Insufficient shed blocks.
ns = fresh(actions); agent = ns["agent"]
agent(obs(576, 9980, market=[]))
a = agent(obs(577, 9985, shed=11, market=[["SELL", "STRAWBERRY", 8]]))
assert strawberry_sell(a) == 8
assert agent.telemetry["strawberry_race_shift4"]["shed_blocks"] == 1

# BUY dependency blocks and order stays unchanged.
ns = fresh(actions); agent = ns["agent"]
agent(obs(576, 9980, market=[]))
m = [["SELL", "STRAWBERRY", 8], ["BUY", "WHEAT", 1]]
a = agent(obs(577, 9985, market=m))
assert a["market"] == m
assert agent.telemetry["strawberry_race_shift4"]["buy_blocks"] == 1

# No sufficiently large future static repayment SELL -> no activation.
small = [{} for _ in range(720)]
small[599] = {"market": [["SELL", "STRAWBERRY", 4]]}
ns = fresh(small); agent = ns["agent"]
agent(obs(576, 9980, market=[]))
a = agent(obs(577, 9985, market=[["SELL", "STRAWBERRY", 8]]))
assert strawberry_sell(a) == 8
assert agent.telemetry["strawberry_race_shift4"]["repay_window_blocks"] == 1

# If target parent's actual sale is unexpectedly too small, defer debt to the
# next static sale rather than silently changing lifetime quantity.
defer = [{} for _ in range(720)]
defer[599] = {"market": [["SELL", "STRAWBERRY", 22]]}
defer[615] = {"market": [["SELL", "STRAWBERRY", 10]]}
ns = fresh(defer); agent = ns["agent"]
agent(obs(576, 9980, market=[]))
a = agent(obs(577, 9985, market=[["SELL", "STRAWBERRY", 8]]))
assert strawberry_sell(a) == 12
b = agent(obs(599, 9990, price=120, shed=2, market=[["SELL", "STRAWBERRY", 2]]))
assert strawberry_sell(b) == 2
rep = agent.telemetry["strawberry_race_shift4"]
assert rep["repay_deferrals"] == 1 and rep["repay_shortfalls"] == 0, rep
c = agent(obs(615, 9990, price=100, shed=10, market=[["SELL", "STRAWBERRY", 10]]))
assert strawberry_sell(c) == 6
assert rep["repayments"] == 1 and rep["units_repaid"] == 4 and rep["repay_shortfalls"] == 0, rep

# Seat state is independent.
ns = fresh(actions); agent = ns["agent"]
agent(obs(576, 9980, market=[], seat=0))
agent(obs(576, 9980, market=[], seat=1))
a0 = agent(obs(577, 9985, market=[["SELL", "STRAWBERRY", 8]], seat=0))
a1 = agent(obs(577, 9980, market=[["SELL", "STRAWBERRY", 8]], seat=1))
assert strawberry_sell(a0) == 12 and strawberry_sell(a1) == 8

print("v121 synthetic checks: PASS")
