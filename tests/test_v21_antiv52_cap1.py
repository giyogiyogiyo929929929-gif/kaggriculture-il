# -*- coding: utf-8 -*-
"""v21の1発火上限と原本保持を確認する。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V21 = ROOT / "submissions" / "v21_antiv52_cap1" / "main.py"
V52 = ROOT / "opponents" / "v52" / "main.py"


def _namespace():
    namespace = {}
    exec(compile(V21.read_text(encoding="utf-8"), str(V21), "exec"), namespace)
    return namespace


def test_v52_prefix_and_cap_state():
    assert V21.read_bytes().startswith(V52.read_bytes())
    assert _namespace()["_kil_v52_new_state"]()["fires"] == 0


def test_cap_returns_original_action_after_one_fire():
    ns = _namespace()
    action = {"farmer": ["PASS"], "hands": [], "market": []}
    assert ns["_kil_v52_preempt"]({"step": 500}, action,
                                  {"copy": True, "fires": 1}) is action


def test_broken_observation_is_safe():
    ns = _namespace()
    assert ns["_kil_v52_safe_agent"]({}) == {"farmer": ["PASS"], "hands": [], "market": []}
