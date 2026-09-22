# -*- coding: utf-8 -*-
"""v14_queueclosure（v12 + final effective-queue closure）のテスト。

仕様: docs/adr/0005-selective-public-base-adoption.md
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

V12 = ROOT / "submissions" / "v12_v51safe" / "main.py"
V14 = ROOT / "submissions" / "v14_queueclosure" / "main.py"


@pytest.fixture(scope="module")
def module():
    namespace: dict = {}
    code = compile(V14.read_text(encoding="utf-8"), str(V14), "exec")
    sys.path.append(str(V14.parent))
    try:
        exec(code, namespace)
    finally:
        sys.path.pop()
    return namespace


@pytest.fixture()
def stock_projection(module, monkeypatch):
    """市場直前の在庫だけを指定してキュー変換を単体検証する。"""
    stock = {}
    monkeypatch.setitem(module, "FarmView", lambda observation: observation)
    monkeypatch.setitem(module, "projected_shed", lambda action, view: dict(stock))
    return stock


def _action(market):
    return {"farmer": ["PASS"], "hands": [], "market": market}


def test_base_is_byte_identical():
    v12, v14 = V12.read_bytes(), V14.read_bytes()
    assert hashlib.sha256(v12).hexdigest() == "fd3231bd638414cbcdd9246be88f544f5367e365388e5debb24fee18834ab652"
    assert v14[: len(v12)] == v12


def test_entry_wraps_v12_safe_agent(module):
    callables = [value for value in module.values() if callable(value)]
    assert callables[-1].__name__ == "_kil_queue_agent"
    assert module["_KIL_QUEUE_PARENT"].__name__ == "_kil_safe_agent"


def test_zero_effective_sale_becomes_hole_and_later_sale_moves(module, stock_projection):
    stock_projection.update(EGG=4, MILK=3)
    original = _action([
        ["SELL", "EGG", 4],
        ["SELL", "EGG", 6],
        ["HIRE", "HAND", 1],
        ["SELL", "MILK", 3],
    ])
    result = module["_kil_q_close"]({}, original)
    assert result["market"] == [
        ["SELL", "EGG", 4],
        ["SELL", "MILK", 3],
        ["HIRE", "HAND", 1],
        [],
    ]
    assert original["market"][1] == ["SELL", "EGG", 6]


def test_all_executable_sales_are_unchanged(module, stock_projection):
    stock_projection.update(EGG=4, MILK=3)
    original = _action([["SELL", "EGG", 4], ["SELL", "MILK", 3]])
    assert module["_kil_q_close"]({}, original) is original


def test_partial_sale_stays_and_only_zero_remainder_is_hole(module, stock_projection):
    stock_projection.update(CARROT=5, MILK=2)
    original = _action([
        ["SELL", "CARROT", 8],
        ["SELL", "CARROT", 1],
        ["SELL", "MILK", 2],
    ])
    result = module["_kil_q_close"]({}, original)
    assert result["market"] == [
        ["SELL", "CARROT", 8],
        ["SELL", "MILK", 2],
        [],
    ]


def test_fixed_orders_and_excluded_products_keep_their_slots(module, stock_projection):
    stock_projection.update(EGG=1, MILK=1, WHEAT=0, FERTILIZER=0)
    original = _action([
        ["SELL", "EGG", 1],
        ["SELL", "EGG", 2],
        ["BUY_SEED", "CARROT", 3],
        ["SELL", "WHEAT", 9],
        ["SELL", "FERTILIZER", 7],
        ["SELL", "MILK", 1],
    ])
    result = module["_kil_q_close"]({}, original)
    assert len(result["market"]) == len(original["market"])
    assert result["market"][1] == ["SELL", "MILK", 1]
    assert result["market"][2:5] == original["market"][2:5]
    assert result["market"][5] == []


def test_transform_is_idempotent(module, stock_projection):
    stock_projection.update(EGG=1, MILK=1)
    original = _action([
        ["SELL", "EGG", 1],
        ["SELL", "EGG", 2],
        ["SELL", "MILK", 1],
    ])
    once = module["_kil_q_close"]({}, original)
    twice = module["_kil_q_close"]({}, once)
    assert twice == once


def test_nonstandard_or_malformed_input_falls_back(module, monkeypatch):
    assert not module["_kil_q_standard"]({"boardSize": 11})
    assert not module["_kil_q_standard"](object())
    malformed = _action([["SELL", "EGG", "not-an-int"], ["SELL", "MILK", 1]])
    parent = lambda observation, configuration=None: malformed
    monkeypatch.setitem(module, "_KIL_QUEUE_PARENT", parent)
    result = module["_kil_queue_agent"]({}, None)
    assert result is malformed

