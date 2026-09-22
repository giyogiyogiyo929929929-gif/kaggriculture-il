# -*- coding: utf-8 -*-
"""EXP-51のR148単独移植とv25先頭保持を確認する。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V25 = ROOT / "submissions/v25_e402_e410/main.py"
V26 = ROOT / "submissions/v26_r148_overflow/main.py"


def namespace():
    result = {}
    exec(compile(V26.read_text(encoding="utf-8"), str(V26), "exec"), result)
    return result


def observation(step=23):
    empty = {"kind": "EMPTY"}
    tiles = [[dict(empty) for _ in range(10)] for _ in range(10)]
    farm = {
        "money": 100_000,
        "hires_today": 0,
        "farmer": [5, 5],
        "hands": [],
        "tiles": tiles,
        "unlocked_quadrants": [0, 1, 2, 3],
    }
    private = {
        "shed": {"CARROT": 99, "WHEAT": 1},
        "seeds": {},
        "inventories": [{"WHEAT": 2}],
    }
    market = {
        "prices": {"WHEAT": 100, "CARROT": 100},
        "inventory": {"WHEAT": 10_000, "FERTILIZER": 10_000},
    }
    return {"player": 0, "step": step, "farms": [farm, dict(farm)],
            "private": private, "market": market}


def test_v25_prefix_is_exact():
    assert V26.read_bytes().startswith(V25.read_bytes().rstrip())


def test_overflow_sale_preserves_post_dawn_stock():
    ns = namespace()
    action = {"farmer": ["PASS"], "hands": [], "market": []}
    result = ns["_v26_apply"](observation(), action)
    assert result["market"] == [["SELL", "WHEAT", 1]]
    assert ns["_V26_REPORT"]["overflow_turns"] == 1
    assert ns["_V26_REPORT"]["overflow_units"] == 1


def test_non_dawn_turn_is_identity():
    ns = namespace()
    action = {"farmer": ["PASS"], "hands": [], "market": []}
    assert ns["_v26_apply"](observation(step=22), action) is action


def test_full_market_is_identity():
    ns = namespace()
    action = {"farmer": ["PASS"], "hands": [],
              "market": [["SELL", "CARROT", 1] for _ in range(10)]}
    assert ns["_v26_apply"](observation(), action) is action


def test_public_entry_is_safe_for_broken_observation():
    ns = namespace()
    assert ns["agent"]({}) == {"farmer": ["PASS"], "hands": [], "market": []}
