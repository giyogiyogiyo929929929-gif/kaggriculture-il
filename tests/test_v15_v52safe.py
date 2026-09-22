# -*- coding: utf-8 -*-
"""v15_v52safe（v52原本＋例外フォールバック）のテスト。"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
V15 = ROOT / "submissions" / "v15_v52safe" / "main.py"
V52 = ROOT / "opponents" / "v52" / "main.py"


@pytest.fixture(scope="module")
def module():
    namespace: dict = {}
    code = compile(V15.read_text(encoding="utf-8"), str(V15), "exec")
    sys.path.append(str(V15.parent))
    try:
        exec(code, namespace)
    finally:
        sys.path.pop()
    return namespace


def test_base_is_byte_identical():
    candidate, base = V15.read_bytes(), V52.read_bytes()
    assert candidate[: len(base)] == base
    assert hashlib.sha256(base).hexdigest() == "8c0f7d90db965a676bd0e211e0250aa9b9235d64d43ff0b4e3852a71d1ef7c24"


def test_entry_is_safe_wrapper(module):
    agent = [value for value in module.values() if callable(value)][-1]
    assert agent.__name__ == "_kil_v52_safe_agent"


def test_inner_is_v52_entry(module):
    assert module["_KIL_V52_INNER_AGENT"].__name__ == "_e350_agent"


def test_broken_observation_returns_pass(module):
    agent = module["_kil_v52_safe_agent"]
    for broken in ({}, None, {"step": 0}, {"step": "x", "player": 0}, []):
        assert agent(broken) == {"farmer": ["PASS"], "hands": [], "market": []}


def test_normal_action_passes_through(module):
    sentinel = {"farmer": ["NORTH"], "hands": [], "market": [["SELL", "MILK", 3]]}
    module["_KIL_V52_INNER_AGENT"] = lambda observation, configuration=None: sentinel
    assert module["_kil_v52_safe_agent"]({"step": 5, "player": 0}) is sentinel
