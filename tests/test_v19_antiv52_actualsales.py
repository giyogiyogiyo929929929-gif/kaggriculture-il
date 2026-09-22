# -*- coding: utf-8 -*-
"""v19の実販売量補正と、確定後の誤検知解除を確認する。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V19 = ROOT / "submissions" / "v19_antiv52_actualsales" / "main.py"
V52 = ROOT / "opponents" / "v52" / "main.py"


def _namespace():
    namespace = {}
    exec(compile(V19.read_text(encoding="utf-8"), str(V19), "exec"), namespace)
    return namespace


def _observation(step, inventory):
    farm = {"tiles": [[None]], "money": 0}
    return {"player": 0, "step": step, "farms": [farm, dict(farm)],
            "market": {"inventory": inventory, "prices": {"MILK": 4}},
            "town": {"unlocked_shops": []}}


def test_v52_prefix_and_strict_commit():
    assert V19.read_bytes().startswith(V52.read_bytes())
    ns = _namespace()
    assert ns["_KIL_V52_COMMIT"] == 300


def test_actual_sale_is_used_for_accounting_but_baseline_for_comparison():
    ns = _namespace()
    items = ns["_V92_P_ITEMS"]
    before = {item: 100 for item in items}
    after = dict(before)
    after["MILK"] = 108  # candidate 5 + rival/base-v52 3
    previous = {"step": 300, "shops": [], "inventory": before,
                "prices": {item: 4 for item in items}, "own": {"MILK": 3}}
    actual = dict(previous, own={"MILK": 5})
    state = ns["_kil_v52_new_state"](300)
    state.update(copy=True, evidence=3)
    ns["_KIL_V52_STATE"][0] = state
    result = ns["_kil_v52_update_detector"](_observation(301, after), previous, actual)
    assert result["copy"] is True
    assert result["same_sales"] is True


def test_post_commit_real_mismatch_abandons_counter():
    ns = _namespace()
    items = ns["_V92_P_ITEMS"]
    before = {item: 100 for item in items}
    after = dict(before)
    after["MILK"] = 109  # candidate 5 + rival 4; base-v52 expected 3
    previous = {"step": 300, "shops": [], "inventory": before,
                "prices": {item: 4 for item in items}, "own": {"MILK": 3}}
    actual = dict(previous, own={"MILK": 5})
    state = ns["_kil_v52_new_state"](300)
    state.update(copy=True, evidence=3)
    ns["_KIL_V52_STATE"][0] = state
    result = ns["_kil_v52_update_detector"](_observation(301, after), previous, actual)
    assert result["copy"] is False
    assert result["abandoned"] is True


def test_broken_observation_is_safe():
    ns = _namespace()
    assert ns["_kil_v52_safe_agent"]({}) == {"farmer": ["PASS"], "hands": [], "market": []}
