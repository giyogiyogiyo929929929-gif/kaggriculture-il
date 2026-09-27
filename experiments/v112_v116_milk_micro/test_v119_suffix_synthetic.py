from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUFFIX = (ROOT / "v119_suffix.pyfrag").read_text()
compile(SUFFIX, "v119_suffix.pyfrag", "exec")

def make_ns(parent_action):
    def _get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)
    def parent(obs, config=None):
        return {"market": [list(o) for o in parent_action.get("market", [])]}
    parent.telemetry = {}
    ns = {"_get": _get, "agent": parent}
    exec(SUFFIX, ns)
    return ns

def run_case(market, inventory, prices, step=300):
    ns = make_ns({"market": market})
    obs = {"step": step, "market": {"inventory": inventory, "prices": prices}}
    return ns["agent"](obs), ns["_V119_REPORT"]

def main():
    a, r = run_case(
        [["SELL","WHEAT",5],["SELL","MILK",3],["SELL","WOOL",2]],
        {"WHEAT":10020,"MILK":9960,"WOOL":9900},
        {"WHEAT":24,"MILK":180,"WOOL":250},
    )
    assert a["market"] == [["SELL","WOOL",2],["SELL","WHEAT",5],["SELL","MILK",3]]
    assert r["reorders"] == 1 and r["wool"] == 1 and r["multi_premium_seen"] == 1

    a, r = run_case(
        [["SELL","MILK",3],["SELL","WOOL",2]],
        {"MILK":9950,"WOOL":9940},
        {"MILK":184,"WOOL":232},
    )
    assert a["market"][0][1] == "MILK"
    assert r["reorders"] == 0 and r["dominance_blocks"] == 1

    a, r = run_case(
        [["SELL","WOOL",2],["SELL","MILK",3]],
        {"MILK":9950,"WOOL":9900},
        {"MILK":176,"WOOL":250},
    )
    assert a["market"][0][1] == "WOOL"
    assert r["reorders"] == 0 and r["already_front_blocks"] == 1

    a, r = run_case(
        [["BUY_PRODUCT","WHEAT",1],["SELL","MILK",3],["SELL","WOOL",2]],
        {"MILK":9950,"WOOL":9900},
        {"MILK":176,"WOOL":250},
    )
    assert r["non_sell_blocks"] == 1

    a, r = run_case(
        [["SELL","WHEAT",5],["SELL","MILK",3],["SELL","WOOL",2]],
        {"WHEAT":9900,"MILK":9960,"WOOL":9900},
        {"WHEAT":28,"MILK":180,"WOOL":250},
    )
    assert r["front_race_blocks"] == 1

    a, r = run_case(
        [["SELL","MILK",3],["SELL","WOOL",2]],
        {"MILK":10010,"WOOL":10020},
        {"MILK":160,"WOOL":200},
    )
    assert r["scarcity_blocks"] == 1

    a, r = run_case(
        [["SELL","WHEAT",5],["SELL","WOOL",2]],
        {"WHEAT":10020,"WOOL":9900},
        {"WHEAT":24,"WOOL":250},
    )
    assert r["single_premium_blocks"] == 1

    print("v119 synthetic checks: PASS")

if __name__ == "__main__":
    main()
