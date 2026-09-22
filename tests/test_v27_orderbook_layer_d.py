# -*- coding: utf-8 -*-
"""EXP-52のLayer D単独移植とv25先頭保持を確認する。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V25 = ROOT / "submissions/v25_e402_e410/main.py"
V27 = ROOT / "submissions/v27_orderbook_layer_d/main.py"


def namespace():
    result = {}
    exec(compile(V27.read_text(encoding="utf-8"), str(V27), "exec"), result)
    return result


def test_v25_prefix_is_exact():
    assert V27.read_bytes().startswith(V25.read_bytes().rstrip())


def test_candidates_keep_fixed_relative_order():
    ns = namespace()
    sells = [["SELL", "WHEAT", 2], ["SELL", "CARROT", 3]]
    fixed = [["HIRE"], ["BUY_SEED", "WHEAT", 1]]
    orders = [*sells, *fixed]
    candidates = list(ns["_v27_candidates"](orders, list(range(4)), sells, fixed))
    assert len(candidates) == 12
    for candidate in candidates:
        kept = [order for order in candidate if order[0] != "SELL"]
        assert kept == fixed


def test_candidate_generation_does_not_touch_other_slots():
    ns = namespace()
    orders = [["BUY_PRODUCT", "WHEAT", 1], ["SELL", "CARROT", 2], ["HIRE"]]
    candidates = list(ns["_v27_candidates"](
        orders, [1, 2], [orders[1]], [orders[2]]))
    assert all(candidate[0] == orders[0] for candidate in candidates)


def test_public_entry_is_safe_for_broken_observation():
    ns = namespace()
    assert ns["agent"]({}) == {"farmer": ["PASS"], "hands": [], "market": []}
