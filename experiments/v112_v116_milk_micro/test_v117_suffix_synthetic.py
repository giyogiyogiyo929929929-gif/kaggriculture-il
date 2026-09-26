from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUFFIX = (ROOT / "v117_suffix.pyfrag").read_text()
compile(SUFFIX, "v117_suffix.pyfrag", "exec")

def make_ns(actions, shops, parent_actions, parent_state=None):
    def _get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def _seat(obs):
        return obs.get("seat", 0)

    def _wcount(obs):
        unlocked = _get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or []
        return sum(1 for shop in unlocked if "WHEAT" in shops.get(shop, ()))

    def _wdemand(obs, step):
        if step % 24 == 0:
            return True
        if step % 4 != 0:
            return False
        unlocked = _get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or []
        return any("WHEAT" in shops.get(shop, ()) for shop in unlocked)

    def parent(obs, config=None):
        a = parent_actions.get(obs["step"], {"market": []})
        return {"market": [list(o) for o in a.get("market", [])]}

    parent.telemetry = {}
    ns = {
        "_ACTIONS": actions,
        "_SHOP_PRODUCTS": shops,
        "_get": _get,
        "_seat": _seat,
        "_v110_wheat_demand_shop_count": _wcount,
        "_v110_wheat_demand_now": _wdemand,
        "_V110_STATE": parent_state or {
            0: {"due_step": -1, "due": 0},
            1: {"due_step": -1, "due": 0},
        },
        "agent": parent,
    }
    exec(SUFFIX, ns)
    return ns

def run_case(
    *,
    shopn=4,
    inv=10,
    current_market=None,
    next_native=None,
    next_parent=None,
    future_wheat=False,
    parent_state=None,
):
    step = 300
    actions = [{"market": []} for _ in range(310)]
    current_market = current_market if current_market is not None else [["SELL", "WHEAT", 5]]
    next_native = next_native if next_native is not None else []
    next_parent = next_parent if next_parent is not None else next_native
    actions[step] = {"market": [list(o) for o in current_market]}
    actions[step + 1] = {"market": [list(o) for o in next_native]}
    if future_wheat:
        actions[step + 3] = {"market": [["SELL", "WHEAT", 4]]}
    parents = {
        step: {"market": [list(o) for o in current_market]},
        step + 1: {"market": [list(o) for o in next_parent]},
    }
    shops = {f"s{i}": ("WHEAT",) for i in range(shopn)}
    ns = make_ns(actions, shops, parents, parent_state)
    obs0 = {
        "step": step,
        "seat": 0,
        "market": {"inventory": {"WHEAT": inv}},
        "town": {"unlocked_shops": list(shops)},
    }
    obs1 = {
        "step": step + 1,
        "seat": 0,
        "market": {"inventory": {"WHEAT": max(0, inv - 1)}},
        "town": {"unlocked_shops": list(shops)},
    }
    return ns["agent"](obs0), ns["agent"](obs1), ns["_V117_REPORT"]

def main():
    a0, a1, r = run_case()
    assert a0["market"] == []
    assert a1["market"] == [["SELL", "WHEAT", 5]]
    assert r["shifts"] == 1 and r["repay_inserts"] == 1 and r["errors"] == 0

    _, _, r = run_case(next_native=[["SELL", "WHEAT", 2]], next_parent=[["SELL", "WHEAT", 2]])
    assert r["shifts"] == 1 and r["repay_merges"] == 1 and r["repay_shortfalls"] == 0

    _, _, r = run_case(shopn=3)
    assert r["shifts"] == 0 and r["low_demand_blocks"] == 1

    _, _, r = run_case(inv=0)
    assert r["shifts"] == 0 and r["market_empty_blocks"] == 1

    _, _, r = run_case(current_market=[["SELL", "WHEAT", 5], ["BUY_PRODUCT", "MILK", 1]])
    assert r["shifts"] == 0 and r["cash_blocks"] == 1

    _, _, r = run_case(next_native=[["SELL", "CARROT", 1]] * 8)
    assert r["shifts"] == 0 and r["next_slot_blocks"] == 1

    _, _, r = run_case(parent_state={0: {"due_step": 302, "due": 4}, 1: {"due_step": -1, "due": 0}})
    assert r["shifts"] == 0 and r["parent_shift_blocks"] == 1

    _, _, r = run_case(future_wheat=True)
    assert r["shifts"] == 0 and r["future_wheat_blocks"] == 1

    print("v117 synthetic checks: PASS")

if __name__ == "__main__":
    main()
