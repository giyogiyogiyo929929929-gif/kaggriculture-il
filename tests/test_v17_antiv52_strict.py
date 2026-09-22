# -*- coding: utf-8 -*-
"""v17の厳格な確定時刻と原本保存を確認する。"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V17 = ROOT / "submissions" / "v17_antiv52_strict" / "main.py"
V52 = ROOT / "opponents" / "v52" / "main.py"


def _namespace():
    namespace = {}
    exec(compile(V17.read_text(encoding="utf-8"), str(V17), "exec"), namespace)
    return namespace


def test_v52_prefix_is_unchanged():
    base = V52.read_bytes()
    assert hashlib.sha256(base).hexdigest() == "8c0f7d90db965a676bd0e211e0250aa9b9235d64d43ff0b4e3852a71d1ef7c24"
    assert V17.read_bytes().startswith(base)


def test_strict_commit_and_chain():
    ns = _namespace()
    assert ns["_KIL_V52_COMMIT"] == 300
    assert [value for value in ns.values() if callable(value)][-1].__name__ == "_kil_v52_safe_agent"


def test_broken_observation_is_safe():
    ns = _namespace()
    assert ns["_kil_v52_safe_agent"]({}) == {"farmer": ["PASS"], "hands": [], "market": []}
