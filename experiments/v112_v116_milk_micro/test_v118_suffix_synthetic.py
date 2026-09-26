from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUFFIX = (ROOT / "v118_suffix.pyfrag").read_text()
compile(SUFFIX, "v118_suffix.pyfrag", "exec")

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
    obs = {
        "step": step,
        "market": {"inventory": inventory, "prices": prices},
    }
    return ns["agent"](obs), ns["_V118_REPORT"]

def main():
    a, r = run_case(
        [["SELL","WHEAT",5],["SELL","MILK",3]],
        {"WHEAT":10020,"MILK":9950},
        {"WHEAT":24,"MILK":190},
    )
    assert a["market"] == [["SELL","MILK",3],["SELL","WHEAT",5]]
    assert r["reorders"] == 1 and r["milk"] == 1 and r["units"] == 3
    assert r["moved_positions"] == 1 and r["errors"] == 0

    a, r = run_case(
        [["SELL","MILK",3],["SELL","WHEAT",5]],
        {"WHEAT":10020,"MILK":9950},
        {"WHEAT":24,"MILK":190},
    )
    assert a["market"][0][1] == "MILK"
    assert r["reorders"] == 0 and r["already_front_blocks"] == 1

    a, r = run_case(
        [["SELL","WHEAT",5],["SELL","MILK",3]],
        {"WHEAT":10020,"MILK":10000},
        {"WHEAT":24,"MILK":160},
    )
    assert a["market"][0][1] == "WHEAT"
    assert r["reorders"] == 0 and r["scarcity_blocks"] == 1

    a, r = run_case(
        [["SELL","WHEAT",5],["SELL","MILK",3],["SELL","WOOL",2]],
        {"WHEAT":10020,"MILK":9950,"WOOL":9940},
        {"WHEAT":24,"MILK":190,"WOOL":230},
    )
    assert r["reorders"] == 0 and r["multi_premium_blocks"] == 1

    a, r = run_case(
        [["SELL","TOMATO",2],["SELL","MILK",3]],
        {"TOMATO":10020,"MILK":9950},
        {"TOMATO":55,"MILK":190},
    )
    assert r["reorders"] == 0 and r["unsafe_prefix_blocks"] == 1

    a, r = run_case(
        [["SELL","WHEAT",5],["SELL","MILK",3]],
        {"WHEAT":9900,"MILK":9950},
        {"WHEAT":30,"MILK":190},
    )
    assert r["reorders"] == 0 and r["front_race_blocks"] == 1

    a, r = run_case(
        [["SELL","WHEAT",5],["BUY_PRODUCT","MILK",1],["SELL","MILK",3]],
        {"WHEAT":10020,"MILK":9950},
        {"WHEAT":24,"MILK":190},
    )
    assert r["reorders"] == 0 and r["non_sell_blocks"] == 1

    a, r = run_case(
        [["SELL","EGG",2],["SELL","FERTILIZER",1],["SELL","STRAWBERRY",4]],
        {"EGG":10010,"FERTILIZER":10020,"STRAWBERRY":9960},
        {"EGG":49,"FERTILIZER":95,"STRAWBERRY":150},
    )
    assert a["market"] == [
        ["SELL","STRAWBERRY",4],
        ["SELL","EGG",2],
        ["SELL","FERTILIZER",1],
    ]
    assert r["reorders"] == 1 and r["strawberry"] == 1 and r["moved_positions"] == 2

    print("v118 synthetic checks: PASS")

if __name__ == "__main__":
    main()
