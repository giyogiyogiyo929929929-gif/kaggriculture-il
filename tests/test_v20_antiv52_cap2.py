# -*- coding: utf-8 -*-
"""v20の発火上限と原本保持を確認する。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V20 = ROOT / "submissions" / "v20_antiv52_cap2" / "main.py"
V52 = ROOT / "opponents" / "v52" / "main.py"


def _namespace():
    namespace = {}
    exec(compile(V20.read_text(encoding="utf-8"), str(V20), "exec"), namespace)
    return namespace


def test_v52_prefix_and_cap_state():
    assert V20.read_bytes().startswith(V52.read_bytes())
    ns = _namespace()
    assert ns["_KIL_V52_COMMIT"] == 300
    assert ns["_kil_v52_new_state"]()["fires"] == 0


def test_cap_returns_original_action():
    ns = _namespace()
    action = {"farmer": ["PASS"], "hands": [], "market": []}
    observation = {"step": 500}
    assert ns["_kil_v52_preempt"](observation, action, {"copy": True, "fires": 2}) is action


def test_broken_observation_is_safe():
    ns = _namespace()
    assert ns["_kil_v52_safe_agent"]({}) == {"farmer": ["PASS"], "hands": [], "market": []}
