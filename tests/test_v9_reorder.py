# -*- coding: utf-8 -*-
"""v9_reorder（候補E：同じターンに出す SELL の並べ替え）のテスト。

仕様: docs/07_v4_improvement.md §3 候補E（約定ルールは E.1b）
    .venv\\Scripts\\python.exe -m pytest tests\\test_v9_reorder.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

V9 = ROOT / "submissions" / "v9_reorder" / "main.py"
V7 = ROOT / "submissions" / "v7_relax" / "main.py"
ORIGINAL = ROOT / "submissions" / "thomas_v94" / "main.py"


@pytest.fixture(scope="module")
def module():
    """v9 を Kaggle と同じ方法で読み込み、名前空間を返す。"""
    namespace: dict = {}
    code = compile(V9.read_text(encoding="utf-8"), str(V9), "exec")
    sys.path.append(str(V9.parent))
    try:
        exec(code, namespace)
    finally:
        sys.path.pop()
    return namespace


def test_v7_part_is_byte_identical():
    """先頭は v7 と、そのまた先頭は v9/4 原本と1バイトも違わない（doc 07 §4）。"""
    v9, v7, original = V9.read_bytes(), V7.read_bytes(), ORIGINAL.read_bytes()
    assert v9[: len(v7)] == v7
    assert v9[: len(original)] == original
    assert hashlib.sha256(v7).hexdigest().startswith("07be7bea")


def test_entry_is_the_e_layer(module):
    """Kaggle が使う「最後の callable」が候補E の層（doc 06「仕様」）。"""
    agent = [value for value in module.values() if callable(value)][-1]
    assert agent.__name__ == "_kil_e_agent"


def test_constants_match_the_doc(module):
    """doc 07 §3 候補E の値。"""
    assert module["_KIL_E_START"] == 216
    assert module["_KIL_E_MAXBLOCK"] == 6


def test_inner_is_the_v7_agent(module):
    """層が包んでいるのは v7 の安全包み（import した関数を掴んでいない）。

    層の中で先に `from time import perf_counter` をすると、それが「最後の callable」になり、
    内側として掴まれてしまう（2026-09-20 に実際に起きた。preflight が捕まえた）。
    """
    assert module["_KIL_E_INNER"].__name__ == "_kil_safe_agent"


# ---------------------------------------------------------------- 約定の再現

def test_price_model_matches_the_engine(module):
    """層が使う価格が、環境の market_price と全品目・広い在庫で一致する（doc 07 §3 E.1b）。"""
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine

    price = module["_r37_market_price"]
    for item in engine.PRODUCTS:
        for inventory in (0, 500, 9_000, 9_900, 10_000, 10_100, 10_500, 12_000):
            assert price(item, inventory) == engine.market_price(item, inventory), (item, inventory)


def test_revenue_matches_the_engine_lockstep(module):
    """1品目の約定の再現が、環境の市場処理そのものと一致する（E.1b の 2〜5）。"""
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine

    params = {item: dict(value) for item, value in engine.MARKET_PARAMS.items()}
    item, inventory, stock = "MILK", 10_000, 12

    # 自分は スロット0 に 5個、相手は スロット0 に 4個。
    mine, theirs = {0: 5}, {0: 4}
    got_me, got_them = module["_kil_e_revenue"](item, mine, theirs, inventory, stock, params)

    # 環境の約定をそのまま動かす。
    market = {"inventory": {item: inventory}, "prices": {}, "params": params}
    farms = [{"money": 0.0}, {"money": 0.0}]
    privates = [{"shed": {item: stock}}, {"shed": {item: stock}}]
    remaining = [5, 4]
    while True:
        quoted = [None, None]
        for side in (0, 1):
            if remaining[side] > 0:
                quoted[side] = engine.market_price(item, market["inventory"][item], params)
        if all(q is None for q in quoted):
            break
        committed = False
        for side in (0, 1):
            if quoted[side] is None:
                continue
            if engine._commit_unit("SELL", item, quoted[side], farms[side], privates[side], market, 100):
                remaining[side] -= 1
                committed = True
            else:
                remaining[side] = 0
        if not committed:
            break

    assert got_me == pytest.approx(farms[0]["money"])
    assert got_them == pytest.approx(farms[1]["money"])


def test_later_slot_earns_less(module):
    """同じ品を相手より後のスロットに置くと手取りが減る（並べ替えが効く理由）。"""
    params = {item: dict(value) for item, value in module["_R37_MARKET_PARAMS"].items()}
    same = module["_kil_e_revenue"]("MILK", {0: 6}, {0: 6}, 10_000, 20, params)
    later = module["_kil_e_revenue"]("MILK", {1: 6}, {0: 6}, 10_000, 20, params)
    assert same[0] == same[1]          # 同じスロットなら同じ価格で売れる
    assert later[0] < same[0]          # 後のスロットだと、相手が売った後の安い値になる


# ---------------------------------------------------------------- 層のふるまい

def _observation(step, inventory=None, shed=None, player=0):
    """並べ替えだけを見る最小の観測（FarmView / projected_shed が読む形）。"""
    items = ("MILK", "WHEAT", "STRAWBERRY", "MELON", "WOOL", "EGG", "CARROT", "TOMATO", "FERTILIZER")
    return {
        "step": step,
        "player": player,
        "day": step // 24,
        "hour": step % 24,
        "farms": [{"money": 1000.0, "tiles": [[None] * 10 for _ in range(10)],
                   "farmer": [0, 0], "hands": [], "unlocked_quadrants": [0], "hires_today": 0}] * 2,
        "private": {"shed": dict(shed or {}), "seeds": {}, "inventories": [{}]},
        "market": {"inventory": {item: (inventory or {}).get(item, 10_000) for item in items},
                   "prices": {item: 100 for item in items}},
    }


def _install(module, action):
    """内側の agent を、決まった action を返すものに差し替える。"""
    module["_KIL_E_INNER"] = lambda observation, configuration=None: action
    for key in module["_KIL_E_REPORT"]:
        module["_KIL_E_REPORT"][key] = 0
    return module["_kil_e_agent"]


def _sells(action):
    return sorted((order[1], int(order[2])) for order in action["market"] if order[0] == "SELL")


def test_orders_are_only_reordered_never_changed(module):
    """並べ替えても、売る品目と数量の集合は変わらない。"""
    action = {"farmer": ["PASS"], "hands": [],
              "market": [["SELL", "MILK", 9], ["SELL", "WHEAT", 11], ["SELL", "MELON", 3]]}
    agent = _install(module, action)
    out = agent(_observation(600, shed={"MILK": 9, "WHEAT": 11, "MELON": 3}))
    assert _sells(out) == _sells(action)
    assert out["farmer"] == ["PASS"] and out["hands"] == []


def test_nothing_before_the_start_step(module):
    """step 216 より前は何もしない。"""
    action = {"farmer": ["PASS"], "hands": [],
              "market": [["SELL", "MILK", 9], ["SELL", "WHEAT", 11]]}
    agent = _install(module, action)
    out = agent(_observation(215, shed={"MILK": 9, "WHEAT": 11}))
    assert out["market"] == action["market"]
    assert module["_KIL_E_REPORT"]["e_turns"] == 0


def test_single_order_is_untouched(module):
    """SELL が1件だけなら並べ替えようがない。"""
    action = {"farmer": ["PASS"], "hands": [], "market": [["SELL", "MILK", 9]]}
    agent = _install(module, action)
    out = agent(_observation(600, shed={"MILK": 9}))
    assert out["market"] == action["market"]


def test_non_sell_orders_are_kept_in_place(module):
    """SELL 以外の注文（BUY_SEED など）は動かさない。"""
    action = {"farmer": ["PASS"], "hands": [],
              "market": [["BUY_SEED", "WHEAT", 1], ["SELL", "MILK", 9], ["SELL", "WHEAT", 11]]}
    agent = _install(module, action)
    out = agent(_observation(600, shed={"MILK": 9, "WHEAT": 11}))
    assert out["market"][0] == ["BUY_SEED", "WHEAT", 1]
    assert _sells(out) == _sells(action)


def test_returns_inner_action_on_error(module):
    """層の中で何かあっても、内側の行動をそのまま返す（NFR-2）。"""
    action = {"farmer": ["PASS"], "hands": [],
              "market": [["SELL", "MILK", 9], ["SELL", "WHEAT", 11]]}
    agent = _install(module, action)
    broken = _observation(600, shed={"MILK": 9, "WHEAT": 11})
    del broken["market"]         # 価格も在庫も読めなくなる
    out = agent(broken)
    assert out is action
    assert module["_KIL_E_REPORT"]["e_errors"] == 1


def test_inner_exception_is_not_swallowed_by_this_layer(module):
    """内側（v7 の安全包み）が返した行動をそのまま通す。層は例外を足さない。"""
    sentinel = {"farmer": ["PASS"], "hands": [], "market": []}
    agent = _install(module, sentinel)
    assert agent(_observation(600)) is sentinel
