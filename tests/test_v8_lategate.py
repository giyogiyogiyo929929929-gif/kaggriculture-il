# -*- coding: utf-8 -*-
"""v8_lategate（候補D）のテスト。

仕様: docs/07_v4_improvement.md §3 候補D（探索：EXP-20260920-21）
    .venv\\Scripts\\python.exe -m pytest tests\\test_v8_lategate.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import preflight  # noqa: E402

V8 = ROOT / "submissions" / "v8_lategate" / "main.py"
V7 = ROOT / "submissions" / "v7_relax" / "main.py"
ORIGINAL = ROOT / "submissions" / "thomas_v94" / "main.py"


@pytest.fixture(scope="module")
def module():
    """v8 を Kaggle と同じ方法で読み込み、名前空間を返す。"""
    namespace: dict = {}
    code = compile(V8.read_text(encoding="utf-8"), str(V8), "exec")
    sys.path.append(str(V8.parent))
    try:
        exec(code, namespace)
    finally:
        sys.path.pop()
    return namespace


def test_v7_part_is_byte_identical():
    """先頭は v7 と、そのまた先頭は v9/4 原本と1バイトも違わない（doc 07 §4）。"""
    v8, v7, original = V8.read_bytes(), V7.read_bytes(), ORIGINAL.read_bytes()
    assert v8[: len(v7)] == v7
    assert v8[: len(original)] == original
    assert hashlib.sha256(v7).hexdigest().startswith("07be7bea")


def test_entry_is_the_d_layer(module):
    """Kaggle が使う「最後の callable」が候補D の層（doc 06「仕様」）。"""
    agent = [value for value in module.values() if callable(value)][-1]
    assert agent.__name__ == "_kil_d_agent"


def test_constants_match_the_doc(module):
    """doc 07 §3 候補D の値（終盤 day 20 から、牛乳といちご、下限30）。"""
    assert module["_KIL_D_ITEMS"] == ("MILK", "STRAWBERRY")
    assert module["_KIL_D_START"] == 480
    assert module["_KIL_D_MINPRICE"] == 30


def _observation(step, price_milk=60, price_straw=40, copy=False, player=0):
    return {
        "step": step,
        "player": player,
        "market": {"prices": {"MILK": price_milk, "STRAWBERRY": price_straw}},
        "_copy": copy,
    }


def _install_probe(module, observed):
    """内側の agent を差し替えて、呼ばれた瞬間の基準価格を記録する。"""
    def probe(observation, configuration=None):
        observed.append(dict(module["V9_RACEGATE_BASE"]))
        return {"farmer": ["PASS"], "hands": [], "market": []}
    module["_KIL_D_INNER"] = probe
    return module["_kil_d_agent"]


def test_gate_opens_late_for_milk_and_strawberry(module):
    """終盤・非コピー・値が付いているときは、その呼び出しの間だけ基準価格が 0 になる。"""
    observed: list[dict] = []
    agent = _install_probe(module, observed)
    module["_KIL_V5_STATE"].clear()
    agent(_observation(step=600))
    assert observed[-1]["MILK"] == 0
    assert observed[-1]["STRAWBERRY"] == 0
    # 呼び出しの後は必ず元に戻っている
    assert module["V9_RACEGATE_BASE"]["MILK"] == 160
    assert module["V9_RACEGATE_BASE"]["STRAWBERRY"] == 120


def test_nothing_before_the_late_game(module):
    """day 20 より前は何もしない。"""
    observed: list[dict] = []
    agent = _install_probe(module, observed)
    module["_KIL_V5_STATE"].clear()
    agent(_observation(step=479))
    assert observed[-1]["MILK"] == 160


def test_nothing_in_copy_games(module):
    """コピーと確定した試合では何もしない（候補A・A2 を乱さない。EXP-20260920-21 結果2）。"""
    observed: list[dict] = []
    agent = _install_probe(module, observed)
    module["_KIL_V5_STATE"].clear()
    module["_KIL_V5_STATE"][0] = {"step": 600, "same": True, "copy": True}
    agent(_observation(step=600))
    assert observed[-1]["MILK"] == 160
    assert observed[-1]["STRAWBERRY"] == 120


def test_nothing_below_the_price_floor(module):
    """値が下限（30）未満の品目には触らない。"""
    observed: list[dict] = []
    agent = _install_probe(module, observed)
    module["_KIL_V5_STATE"].clear()
    agent(_observation(step=600, price_milk=29, price_straw=45))
    assert observed[-1]["MILK"] == 160
    assert observed[-1]["STRAWBERRY"] == 0


def test_nothing_above_the_base_price(module):
    """基準価格より高い（値崩れしていない）品目は、元の RACEGATE のままにする。"""
    observed: list[dict] = []
    agent = _install_probe(module, observed)
    module["_KIL_V5_STATE"].clear()
    agent(_observation(step=600, price_milk=200, price_straw=40))
    assert observed[-1]["MILK"] == 160
    assert observed[-1]["STRAWBERRY"] == 0


def test_base_price_restored_after_an_exception(module):
    """内側が例外を出しても基準価格は元に戻り、行動を返す（doc 01 NFR-2）。"""
    def boom(observation, configuration=None):
        raise RuntimeError("内側が落ちた")
    calls = {"n": 0}

    def inner(observation, configuration=None):
        calls["n"] += 1
        if calls["n"] == 1:
            boom(observation, configuration)
        return {"farmer": ["PASS"], "hands": [], "market": []}

    module["_KIL_D_INNER"] = inner
    module["_KIL_V5_STATE"].clear()
    action = module["_kil_d_agent"](_observation(step=600))
    assert action == {"farmer": ["PASS"], "hands": [], "market": []}
    assert module["V9_RACEGATE_BASE"]["MILK"] == 160
    assert module["V9_RACEGATE_BASE"]["STRAWBERRY"] == 120


def test_broken_observation_returns_a_valid_action():
    """壊れた観測でも例外を出さず、形の正しい行動を返す（doc 01 NFR-2、doc 06 チェック4）。"""
    agent = preflight.load_like_kaggle(V8)
    for observation in ({}, None, {"step": 600}, {"step": "x", "player": 0}):
        action = agent(observation, None)
        assert isinstance(action, dict)
        assert "farmer" in action and "market" in action
