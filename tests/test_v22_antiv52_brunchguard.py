# -*- coding: utf-8 -*-
"""v22のBRUNCH同店舗ガードと原本保持を確認する。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V22 = ROOT / "submissions" / "v22_antiv52_brunchguard" / "main.py"
V52 = ROOT / "opponents" / "v52" / "main.py"


def _namespace():
    namespace = {}
    exec(compile(V22.read_text(encoding="utf-8"), str(V22), "exec"), namespace)
    return namespace


def test_v52_prefix_and_strict_commit():
    assert V22.read_bytes().startswith(V52.read_bytes())
    assert _namespace()["_KIL_V52_COMMIT"] == 300


def test_brunch_pair_keeps_parent_action():
    ns = _namespace()
    action = {"farmer": ["PASS"], "hands": [], "market": [["SELL", "MILK", 2]]}
    observation = {"step": 500, "town": {"unlocked_shops": ["BRUNCH_SPOT", "BRUNCH_SPOT"]}}
    assert ns["_kil_v52_preempt"](observation, action, {"copy": True}) is action


def test_broken_observation_is_safe():
    ns = _namespace()
    assert ns["_kil_v52_safe_agent"]({}) == {"farmer": ["PASS"], "hands": [], "market": []}
