# -*- coding: utf-8 -*-
"""v10_de（候補D ＋ 候補E）のテスト。

仕様: docs/07_v4_improvement.md §9（提出版 v10）、§3 候補D・候補E
    .venv\\Scripts\\python.exe -m pytest tests\\test_v10_de.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

V10 = ROOT / "submissions" / "v10_de" / "main.py"
V8 = ROOT / "submissions" / "v8_lategate" / "main.py"
V7 = ROOT / "submissions" / "v7_relax" / "main.py"
ORIGINAL = ROOT / "submissions" / "thomas_v94" / "main.py"


@pytest.fixture(scope="module")
def module():
    namespace: dict = {}
    code = compile(V10.read_text(encoding="utf-8"), str(V10), "exec")
    sys.path.append(str(V10.parent))
    try:
        exec(code, namespace)
    finally:
        sys.path.pop()
    return namespace


def test_layers_are_stacked_on_untouched_bases():
    """v10 の先頭は v8、その先頭は v7、その先頭は v9/4 原本と1バイトも違わない（doc 07 §4）。"""
    v10, v8, v7, original = V10.read_bytes(), V8.read_bytes(), V7.read_bytes(), ORIGINAL.read_bytes()
    assert v10[: len(v8)] == v8
    assert v8[: len(v7)] == v7
    assert v7[: len(original)] == original
    assert hashlib.sha256(original).hexdigest().startswith("bfee70e9")


def test_entry_is_the_e_layer(module):
    """Kaggle が使う「最後の callable」は候補E の層（D の上に E を積んでいる）。"""
    agent = [value for value in module.values() if callable(value)][-1]
    assert agent.__name__ == "_kil_e_agent"


def test_both_layers_are_present(module):
    """候補D と候補E の両方が載っていて、E が D を包んでいる。"""
    assert module["_KIL_D_ITEMS"] == ("MILK", "STRAWBERRY")
    assert module["_KIL_E_START"] == 216
    assert module["_KIL_E_INNER"].__name__ == "_kil_d_agent"


def test_reports_start_empty(module):
    """両方の層が telemetry を持っている（発火回数を測れる。EXP-20260920-26 の教訓）。"""
    assert set(module["_KIL_D_REPORT"]) == {"d_turns", "d_items", "d_errors"}
    assert "e_turns" in module["_KIL_E_REPORT"] and "e_gain" in module["_KIL_E_REPORT"]


def _observation(step, shed=None, player=0):
    items = ("MILK", "WHEAT", "STRAWBERRY", "MELON", "WOOL", "EGG", "CARROT", "TOMATO", "FERTILIZER")
    return {
        "step": step,
        "player": player,
        "day": step // 24,
        "hour": step % 24,
        "farms": [{"money": 1000.0, "tiles": [[None] * 10 for _ in range(10)],
                   "farmer": [0, 0], "hands": [], "unlocked_quadrants": [0], "hires_today": 0}] * 2,
        "private": {"shed": dict(shed or {}), "seeds": {}, "inventories": [{}]},
        "market": {"inventory": {item: 10_000 for item in items},
                   "prices": {item: 100 for item in items}},
    }


def test_d_layer_stops_in_copy_games(module):
    """コピーと確定した試合では候補D が何もしない（doc 07 D.2）。E は動いてよい。"""
    observed: list[dict] = []

    def probe(observation, configuration=None):
        observed.append(dict(module["V9_RACEGATE_BASE"]))
        return {"farmer": ["PASS"], "hands": [], "market": []}

    module["_KIL_D_INNER"] = probe
    module["_KIL_V5_STATE"].clear()
    module["_KIL_V5_STATE"][0] = {"step": 600, "same": True, "copy": True}
    module["_kil_e_agent"](_observation(600))
    assert observed[-1]["MILK"] == 160          # 基準価格が下げられていない＝D は止まっている
    assert observed[-1]["STRAWBERRY"] == 120


def test_d_layer_opens_the_gate_late_otherwise(module):
    """コピーでない終盤では候補D が基準価格を一時的に 0 にする。"""
    observed: list[dict] = []

    def probe(observation, configuration=None):
        observed.append(dict(module["V9_RACEGATE_BASE"]))
        return {"farmer": ["PASS"], "hands": [], "market": []}

    module["_KIL_D_INNER"] = probe
    module["_KIL_V5_STATE"].clear()
    observation = _observation(600)
    observation["market"]["prices"].update({"MILK": 60, "STRAWBERRY": 40})
    module["_kil_e_agent"](observation)
    assert observed[-1]["MILK"] == 0
    assert observed[-1]["STRAWBERRY"] == 0
    assert module["V9_RACEGATE_BASE"]["MILK"] == 160      # 呼び出しの後は元に戻る


def test_e_layer_only_reorders(module):
    """候補E は売る品目と数量を変えない（順序だけ）。"""
    action = {"farmer": ["PASS"], "hands": [],
              "market": [["SELL", "MILK", 9], ["SELL", "WHEAT", 11], ["SELL", "MELON", 3]]}
    module["_KIL_E_INNER"] = lambda observation, configuration=None: action
    out = module["_kil_e_agent"](_observation(600, shed={"MILK": 9, "WHEAT": 11, "MELON": 3}))
    assert sorted((o[1], o[2]) for o in out["market"]) == sorted((o[1], o[2]) for o in action["market"])


def test_returns_inner_action_on_error(module):
    """層の中で何かあっても内側の行動を返す（NFR-2）。"""
    action = {"farmer": ["PASS"], "hands": [], "market": [["SELL", "MILK", 9], ["SELL", "WHEAT", 11]]}
    module["_KIL_E_INNER"] = lambda observation, configuration=None: action
    broken = _observation(600, shed={"MILK": 9, "WHEAT": 11})
    del broken["market"]
    assert module["_kil_e_agent"](broken) is action
