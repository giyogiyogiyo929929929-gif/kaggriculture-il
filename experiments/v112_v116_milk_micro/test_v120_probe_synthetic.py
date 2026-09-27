from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUFFIX = (ROOT / "v120_suffix.pyfrag").read_text(encoding="utf-8")
compile(SUFFIX, "v120_suffix.pyfrag", "exec")

def make_ns():
    returned = []
    def _get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)
    def parent(obs, config=None):
        step = int(_get(obs, "step", 0) or 0)
        action = {"market": [["SELL", "MILK", 2]] if step == 0 else [["SELL", "WHEAT", 1]]}
        returned.append(action)
        return action
    parent.telemetry = {"parent": {"ok": 1}}
    ns = {"_get": _get, "agent": parent}
    exec(SUFFIX, ns)
    return ns, returned

def obs(step, strawberry=10000, melon=10000, milk=10000, wool=10000,
        sp=120, mp=250, mip=160, wp=200):
    return {
        "step": step,
        "market": {
            "inventory": {
                "STRAWBERRY": strawberry, "MELON": melon,
                "MILK": milk, "WOOL": wool,
            },
            "prices": {
                "STRAWBERRY": sp, "MELON": mp,
                "MILK": mip, "WOOL": wp,
            },
        },
    }

def main():
    ns, returned = make_ns()
    agent = ns["agent"]

    a0 = agent(obs(0))
    assert a0 is returned[-1]
    assert a0 == {"market": [["SELL", "MILK", 2]]}

    a1 = agent(obs(1, strawberry=10004, milk=10005, sp=118, mip=150))
    assert a1 is returned[-1]
    assert a1 == {"market": [["SELL", "WHEAT", 1]]}

    r = ns["_V120_REPORT"]
    assert r["transitions"] == 1
    assert r["excess_events"]["STRAWBERRY"] == 1
    assert r["excess_units"]["STRAWBERRY"] == 4
    assert r["clean_positive_events"]["STRAWBERRY"] == 1
    assert r["clean_positive_units"]["STRAWBERRY"] == 4
    assert r["excess_events"]["MILK"] == 1
    assert r["excess_units"]["MILK"] == 3
    assert r["clean_positive_events"]["MILK"] == 0
    assert r["joint_excess_price_drop"]["MILK"] == 1
    assert r["errors"] == 0

    before = r["transitions"]
    a_reset = agent(obs(0))
    assert a_reset is returned[-1]
    assert r["transitions"] == before

    assert agent.telemetry["parent"]["ok"] == 1
    assert agent.telemetry["public_market_race_probe"] is r
    print("v120 synthetic checks: PASS")

if __name__ == "__main__":
    main()
