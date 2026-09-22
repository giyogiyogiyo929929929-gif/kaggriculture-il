# -*- coding: utf-8 -*-
"""EXP-43の一時WHEAT周期とv22先頭保持を確認する。"""
import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V22 = ROOT / "submissions/v22_antiv52_brunchguard/main.py"
V23 = ROOT / "submissions/v23_productive_wheat/main.py"


def namespace():
    result = {}
    exec(compile(V23.read_text(encoding="utf-8"), str(V23), "exec"), result)
    return result


def test_v22_prefix_is_exact():
    assert V23.read_bytes().startswith(V22.read_bytes().rstrip())


def test_only_documented_route_commands_change():
    ns = namespace()
    original = copy.deepcopy(ns["_V23_RAW"])
    ns["_v23_install"]()
    tape = ns["_IMPL"].chassis.routes[0][:96]
    expected = copy.deepcopy(original)
    expected[0]["market"] = list(expected[0]["market"]) + [["BUY_SEED", "WHEAT", 1]]
    for step, command in {2: ["WEST"], 3: ["WEST"], 4: ["WEST"],
                          5: ["PLANT", "WHEAT"], 6: ["WATER"]}.items():
        expected[step]["hands"][1] = command
    expected[29]["hands"][2] = ["WATER"]
    commands = [["WEST"], ["WEST"], ["WEST"], ["WATER"], ["HARVEST"],
                ["BUILD_PASTURE"], ["EAST"], ["EAST"], ["DROP"]]
    for step, command in zip(range(49, 58), commands):
        expected[step]["hands"][0] = command
    assert tape == expected
    assert max(len(action.get("market", [])) for action in tape) <= 10


def test_reinstall_does_not_duplicate_seed_order():
    ns = namespace()
    ns["_v23_install"]()
    ns["_v23_install"]()
    orders = ns["_IMPL"].chassis.routes[0][0]["market"]
    assert orders.count(["BUY_SEED", "WHEAT", 1]) == 1


def test_extra_sale_respects_market_limit():
    ns = namespace()
    action = {"farmer": ["PASS"], "hands": [], "market": [["SELL", "MILK", 2]]}
    result = ns["_v23_sell_extra"](action, "WHEAT", 3)
    assert ["SELL", "WHEAT", 3] in result["market"]
    assert len(result["market"]) <= 10


def test_public_entry_is_safe_for_broken_observation():
    ns = namespace()
    assert ns["kaggle_submission_agent"]({}) == {
        "farmer": ["PASS"], "hands": [], "market": []}
