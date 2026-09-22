# -*- coding: utf-8 -*-
"""ADR-0007: 旧v52コピー検出と売却先回りのテスト。"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
V16 = ROOT / "submissions" / "v16_antiv52" / "main.py"
V52 = ROOT / "opponents" / "v52" / "main.py"


@pytest.fixture(scope="module")
def ns():
    namespace: dict = {}
    sys.path.append(str(V16.parent))
    try:
        exec(compile(V16.read_text(encoding="utf-8"), str(V16), "exec"), namespace)
    finally:
        sys.path.pop()
    return namespace


def _farm(money=3000, crop=(5, 5), weed=None):
    tiles = [[None] * 10 for _ in range(10)]
    tiles[crop[1]][crop[0]] = {"kind": "PLANT", "crop": "WHEAT"}
    if weed:
        tiles[weed[1]][weed[0]] = {"kind": "WEED"}
    return {"tiles": tiles, "money": money, "farmer": [4, 4], "hands": [], "unlocked_quadrants": [0]}


def _obs(ns, step, rival_farm=None, rival_quantity=3):
    items = ns["_V92_P_ITEMS"]
    inventory = {item: 100 for item in items}
    inventory[items[0]] = 100 + 3 + rival_quantity
    return {
        "step": step,
        "player": 0,
        "farms": [_farm(), rival_farm or _farm(money=9999, weed=(1, 1))],
        "market": {"inventory": inventory},
    }


def _previous(ns, step, quantity=3):
    items = ns["_V92_P_ITEMS"]
    return {
        "step": step - 1,
        "shops": [],
        "inventory": {item: 100 for item in items},
        "prices": {item: 10 for item in items},
        "own": {items[0]: quantity},
    }


@pytest.fixture
def detector(ns, monkeypatch):
    ns["_KIL_V52_STATE"].clear()
    ns["_KIL_V52_REPORT"].update(copy_games=0, copy_turns=0, evidence=0, mismatches=0,
                                  preempt_fires=0, preempt_units=0, errors=0)
    monkeypatch.setitem(ns, "_v9_town_draw", lambda shops, step: {})
    return ns["_kil_v52_update_detector"]


def test_v52_prefix_is_byte_identical():
    base, candidate = V52.read_bytes(), V16.read_bytes()
    assert hashlib.sha256(base).hexdigest() == "8c0f7d90db965a676bd0e211e0250aa9b9235d64d43ff0b4e3852a71d1ef7c24"
    assert candidate[: len(base)] == base


def test_callable_chain(ns):
    callables = [value for value in ns.values() if callable(value)]
    assert callables[-1].__name__ == "_kil_v52_safe_agent"
    assert ns["_KIL_V52_SAFE_INNER"].__name__ == "_kil_v52_counter_agent"
    assert ns["_KIL_V52_PARENT"].__name__ == "_e350_agent"


def test_key_ignores_money_and_weeds(ns):
    key = ns["_kil_v52_farm_key"]
    assert key(_farm()) == key(_farm(money=1, weed=(1, 1)))
    assert key(_farm()) != key(_farm(crop=(6, 5)))


def test_exact_farm_and_sales_commit(ns, detector):
    for step in range(168):
        previous = _previous(ns, step) if step >= 96 else None
        state = detector(_obs(ns, step), previous)
    assert state["copy"] is True
    assert state["evidence"] >= ns["_KIL_V52_MIN_EVIDENCE"]


def test_sale_mismatch_rejects(ns, detector):
    for step in range(168):
        previous = _previous(ns, step) if step >= 96 else None
        rival_quantity = 4 if step == 120 else 3
        state = detector(_obs(ns, step, rival_quantity=rival_quantity), previous)
    assert state["copy"] is False
    assert state["same_sales"] is False


def test_farm_mismatch_rejects(ns, detector):
    for step in range(168):
        previous = _previous(ns, step) if step >= 96 else None
        rival = _farm(crop=(6, 5)) if step == 130 else None
        state = detector(_obs(ns, step, rival_farm=rival), previous)
    assert state["copy"] is False
    assert state["same_farm"] is False


def test_no_sale_evidence_does_not_commit(ns, detector):
    for step in range(168):
        state = detector(_obs(ns, step, rival_quantity=0), None)
    assert state["copy"] is False
    assert state["evidence"] == 0


def test_new_game_resets(ns, detector):
    for step in range(168):
        state = detector(_obs(ns, step), _previous(ns, step) if step >= 96 else None)
    assert state["copy"] is True
    state = detector(_obs(ns, 0), None)
    assert state["copy"] is False
    assert state["evidence"] == 0


def test_broken_observation_returns_pass(ns):
    assert ns["_kil_v52_safe_agent"]({}) == {"farmer": ["PASS"], "hands": [], "market": []}
