# -*- coding: utf-8 -*-
"""v18の店舗組ガードと原本保存を確認する。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V18 = ROOT / "submissions" / "v18_antiv52_pairguard" / "main.py"
V52 = ROOT / "opponents" / "v52" / "main.py"


def _namespace():
    namespace = {}
    exec(compile(V18.read_text(encoding="utf-8"), str(V18), "exec"), namespace)
    return namespace


def test_v52_prefix_and_strict_commit():
    assert V18.read_bytes().startswith(V52.read_bytes())
    ns = _namespace()
    assert ns["_KIL_V52_COMMIT"] == 300


def test_ice_cream_pair_keeps_parent_action():
    ns = _namespace()
    action = {"farmer": ["PASS"], "hands": [], "market": [["SELL", "MILK", 2]]}
    observation = {"step": 500, "town": {"unlocked_shops": ["ICE_CREAM_SHOP", "ICE_CREAM_SHOP"]}}
    assert ns["_kil_v52_preempt"](observation, action, {"copy": True}) is action


def test_broken_observation_is_safe():
    ns = _namespace()
    assert ns["_kil_v52_safe_agent"]({}) == {"farmer": ["PASS"], "hands": [], "market": []}
