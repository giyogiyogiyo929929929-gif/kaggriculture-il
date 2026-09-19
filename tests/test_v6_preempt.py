"""v6_preempt（v5 ＋ コピーの PREDICT を1ターン先回りする層 ＋ 安全包み）のテスト。

仕様: docs/07_v4_improvement.md §3 候補A2
"""
import hashlib
from pathlib import Path

import pytest

from scripts import preflight

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "submissions" / "thomas_v94" / "main.py"
V5 = ROOT / "submissions" / "v5_race" / "main.py"
V6 = ROOT / "submissions" / "v6_preempt" / "main.py"
PASS = {"farmer": ["PASS"], "hands": [], "market": []}


@pytest.fixture(scope="module")
def ns():
    namespace: dict = {}
    exec(compile(V6.read_text(encoding="utf-8"), str(V6), "exec"), namespace)
    return namespace


def _obs(step, player=0):
    return {"step": step, "player": player, "farms": [{}, {}], "town": {"unlocked_shops": []},
            "market": {"prices": {}, "inventory": {}}}


def test_original_prefix_is_byte_identical():
    original = ORIGINAL.read_bytes()
    assert hashlib.sha256(original).hexdigest().startswith("bfee70e9daaebeae")
    assert V6.read_bytes().startswith(original)


def test_contains_v5_layer_unchanged():
    v5 = V5.read_text(encoding="utf-8")
    layer = v5[v5.index("# ---- kaggriculture-il 追加：候補A"):v5.index("\n# ---- kaggriculture-il による追加")]
    assert layer in V6.read_text(encoding="utf-8")


def test_last_callable_is_safe_wrapper_around_preempt():
    agent = preflight.load_like_kaggle(V6)
    assert agent.__name__ == "_kil_safe_agent"
    assert agent.__globals__["_KIL_INNER_AGENT"].__name__ == "_kil_pe_agent"
    assert agent.__globals__["_KIL_PE_INNER"].__name__ == "_kil_v5_agent"


def test_safe_wrapper_returns_pass_on_bad_observation():
    assert preflight.load_like_kaggle(V6)({}) == PASS


def test_constants(ns):
    assert ns["_KIL_PE_LEAD"] == 1


def test_does_nothing_without_copy_mode(ns, monkeypatch):
    action = {"farmer": ["PASS"], "hands": [], "market": [["SELL", "WHEAT", 3]]}
    monkeypatch.setitem(ns, "_KIL_PE_INNER", lambda o, c=None: action)
    ns["_KIL_V5_STATE"].clear()
    ns["_KIL_PE_STATE"].clear()
    ns["_KIL_V5_STATE"][0] = {"step": 300, "same": False, "copy": False}
    forecast_calls = []
    monkeypatch.setitem(ns, "_v92_p_forecast", lambda *a: forecast_calls.append(a) or [])
    assert ns["_kil_pe_agent"](_obs(300)) is action
    assert forecast_calls == []


def test_returns_inner_action_when_layer_raises(ns, monkeypatch):
    action = {"farmer": ["PASS"], "hands": [], "market": []}
    monkeypatch.setitem(ns, "_KIL_PE_INNER", lambda o, c=None: action)
    ns["_KIL_V5_STATE"][0] = {"step": 300, "same": True, "copy": True}
    ns["_KIL_PE_STATE"].clear()

    def boom(*args):
        raise RuntimeError("x")

    monkeypatch.setitem(ns, "_v92_p_forecast", boom)
    before = ns["_KIL_PE_REPORT"]["errors"]
    assert ns["_kil_pe_agent"](_obs(300)) is action
    assert ns["_KIL_PE_REPORT"]["errors"] == before + 1


def test_best_follows_copy_refresh_cycle(ns, monkeypatch):
    calls = []
    monkeypatch.setitem(ns, "_v92_p_forecast", lambda obs, st: calls.append(obs["step"]) or [obs["step"]])
    st = {"seen": {}, "best": {}}
    for step in (299, 300, 301, 302, 303):
        ns["_kil_pe_best"](st, _obs(step), step)
    # 最初（前が無い 299）と、3の倍数（300・303）だけ作り直し、間は前の結果を使う
    assert calls == [299, 300, 303]
    assert st["best"][301] == [300] and st["best"][302] == [300]
