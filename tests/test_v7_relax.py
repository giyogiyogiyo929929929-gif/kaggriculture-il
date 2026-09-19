"""v7_relax（v6 のコピー判定を「96〜167 ステップで、雑草と所持金を除いた農場が一致し、所持金の差が一定」に変えた版）のテスト。

仕様: docs/07_v4_improvement.md §3 候補A3
"""
import hashlib
from pathlib import Path

import pytest

from scripts import preflight

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "submissions" / "thomas_v94" / "main.py"
V7 = ROOT / "submissions" / "v7_relax" / "main.py"
NORMAL, DEEP = (40, 48), (52, 52)


@pytest.fixture(scope="module")
def ns():
    namespace: dict = {}
    exec(compile(V7.read_text(encoding="utf-8"), str(V7), "exec"), namespace)
    return namespace


def _farm(money=100.0, weed_at=None, crop_at=(5, 5)):
    tiles = [[None] * 10 for _ in range(10)]
    x, y = crop_at
    tiles[y][x] = {"kind": "PLANT", "crop": "WHEAT"}
    if weed_at is not None:
        wx, wy = weed_at
        tiles[wy][wx] = {"kind": "WEED"}
    return {"tiles": tiles, "money": money, "farmer": [0, 0], "hands": []}


def _obs(step, own=None, rival=None, player=0):
    farms = [None, None]
    farms[player] = own if own is not None else _farm()
    farms[1 - player] = rival if rival is not None else _farm()
    return {"step": step, "player": player, "farms": farms}


@pytest.fixture
def probe(ns, monkeypatch):
    """中の v9/4 を、呼ばれたときの先読み幅を記録するだけの関数に差し替える。"""
    seen = []

    def fake_inner(observation, configuration=None):
        seen.append((ns["V9_RACE_DEFAULT"], ns["V9_RACE_MAX"]))
        return {"farmer": ["PASS"], "hands": [], "market": []}

    monkeypatch.setitem(ns, "_KIL_V5_INNER", fake_inner)
    ns["_KIL_V5_STATE"].clear()
    return seen


def _play(ns, observations):
    for obs in observations:
        ns["_kil_v5_agent"](obs)


def test_original_prefix_is_byte_identical():
    original = ORIGINAL.read_bytes()
    assert hashlib.sha256(original).hexdigest().startswith("bfee70e9daaebeae")
    assert V7.read_bytes().startswith(original)


def test_chain_is_safe_preempt_v5():
    agent = preflight.load_like_kaggle(V7)
    assert agent.__name__ == "_kil_safe_agent"
    assert agent.__globals__["_KIL_INNER_AGENT"].__name__ == "_kil_pe_agent"
    assert agent.__globals__["_KIL_PE_INNER"].__name__ == "_kil_v5_agent"


def test_safe_wrapper_returns_pass_on_bad_observation():
    assert preflight.load_like_kaggle(V7)({}) == {"farmer": ["PASS"], "hands": [], "market": []}


def test_constants(ns):
    assert ns["_KIL_V5_START_STEP"] == 96
    assert ns["_KIL_V5_COMMIT_STEP"] == 167
    assert ns["_KIL_V5_HORIZON"] == 52
    assert ns["_KIL_PE_LEAD"] == 1


def test_key_ignores_weeds_and_money(ns):
    key = ns["_kil_v5_key"]
    assert key(_farm()) == key(_farm(weed_at=(1, 1)))
    assert key(_farm()) == key(_farm(money=150.0))
    assert key(_farm()) != key(_farm(crop_at=(6, 6)))


def test_exact_copy_still_detected(ns, probe):
    _play(ns, [_obs(s) for s in range(0, 170)])
    assert probe[:167] == [NORMAL] * 167
    assert probe[167:] == [DEEP] * 3


def test_differences_before_window_are_ignored(ns, probe):
    observations = [_obs(s, rival=_farm(money=90.0, crop_at=(6, 6))) for s in range(0, 96)]
    observations += [_obs(s, rival=_farm(money=50.0)) for s in range(96, 170)]
    _play(ns, observations)
    assert probe[-1] == DEEP


def test_constant_money_gap_is_copy(ns, probe):
    _play(ns, [_obs(s, own=_farm(money=1000.0 + s), rival=_farm(money=1050.0 + s)) for s in range(0, 170)])
    assert probe[-1] == DEEP


def test_changing_money_gap_is_not_copy(ns, probe):
    observations = [_obs(s, rival=_farm(money=150.0)) for s in range(0, 170)]
    observations[120] = _obs(120, rival=_farm(money=151.0))
    _play(ns, observations)
    assert set(probe) == {NORMAL}


def test_tile_difference_in_window_is_not_copy(ns, probe):
    observations = [_obs(s) for s in range(0, 200)]
    observations[130] = _obs(130, rival=_farm(crop_at=(6, 6)))
    _play(ns, observations)
    assert set(probe) == {NORMAL}


def test_weed_difference_does_not_disable(ns, probe):
    observations = [_obs(s) for s in range(0, 170)]
    observations[150] = _obs(150, rival=_farm(weed_at=(2, 3)))
    _play(ns, observations)
    assert probe[-1] == DEEP


def test_after_commit_divergence_keeps_copy_mode(ns, probe):
    observations = [_obs(s) for s in range(0, 168)]
    observations += [_obs(s, rival=_farm(money=5.0, crop_at=(1, 1))) for s in range(168, 175)]
    _play(ns, observations)
    assert probe[-1] == DEEP


def test_new_game_resets_gap(ns, probe):
    _play(ns, [_obs(s, rival=_farm(money=150.0)) for s in range(0, 170)])
    assert probe[-1] == DEEP
    # 次の試合（step が戻る）では、前の試合の差（−50）を引き継がない
    _play(ns, [_obs(s, rival=_farm(money=80.0)) for s in range(0, 170)])
    assert probe[-1] == DEEP
