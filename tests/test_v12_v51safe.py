# -*- coding: utf-8 -*-
"""v12_v51safe（ADR-0004 第1段：v51 ＋ 例外時フォールバックの包み）のテスト。

仕様: docs/adr/0004-switch-base-to-v51.md（第1段）, docs/01_requirements.md NFR-2
    .venv\\Scripts\\python.exe -m pytest tests\\test_v12_v51safe.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

V12 = ROOT / "submissions" / "v12_v51safe" / "main.py"
V51 = ROOT / "opponents" / "v51" / "main.py"


@pytest.fixture(scope="module")
def module():
    namespace: dict = {}
    code = compile(V12.read_text(encoding="utf-8"), str(V12), "exec")
    sys.path.append(str(V12.parent))
    try:
        exec(code, namespace)
    finally:
        sys.path.pop()
    return namespace


def test_base_is_byte_identical():
    """先頭は取り込んだ v51 の原本と1バイトも違わない（ADR-0004：原本は改変しない）。"""
    v12, v51 = V12.read_bytes(), V51.read_bytes()
    assert v12[: len(v51)] == v51
    assert hashlib.sha256(v51).hexdigest().startswith("c1e3590d")


def test_entry_is_the_safe_wrapper(module):
    """Kaggle が使う「最後の callable」が包み（doc 06「仕様」）。"""
    agent = [value for value in module.values() if callable(value)][-1]
    assert agent.__name__ == "_kil_safe_agent"


def test_inner_is_the_v51_entry(module):
    """包んでいるのは v51 の最後の callable。"""
    assert module["_KIL_INNER_AGENT"].__name__ == "_e350_agent"


def test_broken_observation_returns_pass(module):
    """壊れた観測でも例外を出さず、形の正しい行動を返す（NFR-2）。"""
    agent = module["_kil_safe_agent"]
    for broken in ({}, None, {"step": 0}, {"step": "x", "player": 0}, []):
        action = agent(broken)
        assert action == {"farmer": ["PASS"], "hands": [], "market": []}


def test_normal_action_passes_through(module):
    """内側が返した行動はそのまま通す（包みは中身を変えない）。"""
    sentinel = {"farmer": ["NORTH"], "hands": [], "market": [["SELL", "MILK", 3]]}
    module["_KIL_INNER_AGENT"] = lambda observation, configuration=None: sentinel
    assert module["_kil_safe_agent"]({"step": 5, "player": 0}) is sentinel
