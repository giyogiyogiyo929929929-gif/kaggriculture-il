"""v5_race（v9/4 ＋ コピー相手のときだけ売りの先読みを深くする層 ＋ 安全包み）のテスト。

仕様: docs/07_v4_improvement.md §3 候補A, §4
"""
import copy
import hashlib
from pathlib import Path

import pytest

from scripts import preflight

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "submissions" / "thomas_v94" / "main.py"
V5 = ROOT / "submissions" / "v5_race" / "main.py"
ORIGINAL_SHA256 = "bfee70e9daaebeae"  # 先頭16桁（submissions\thomas_v94\SOURCE.md）


@pytest.fixture(scope="module")
def ns():
    namespace: dict = {}
    exec(compile(V5.read_text(encoding="utf-8"), str(V5), "exec"), namespace)
    return namespace


def _farm(money=100.0, weed_at=None):
    tiles = [[None] * 10 for _ in range(10)]
    tiles[5][5] = {"kind": "PLANT", "crop": "WHEAT"}
    if weed_at is not None:
        x, y = weed_at
        tiles[y][x] = {"kind": "WEED"}
    return {"tiles": tiles, "money": money, "farmer": [0, 0], "hands": []}


def _obs(step, player=0, own=None, rival=None):
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
    assert hashlib.sha256(original).hexdigest().startswith(ORIGINAL_SHA256)
    assert V5.read_bytes().startswith(original)


def test_last_callable_is_safe_wrapper():
    agent = preflight.load_like_kaggle(V5)
    assert agent.__name__ == "_kil_safe_agent"


def test_safe_wrapper_returns_pass_on_bad_observation():
    agent = preflight.load_like_kaggle(V5)
    assert agent({}) == {"farmer": ["PASS"], "hands": [], "market": []}


def test_constants(ns):
    assert ns["_KIL_V5_COMMIT_STEP"] == 167
    assert ns["_KIL_V5_HORIZON"] == 52
    assert (ns["V9_RACE_DEFAULT"], ns["V9_RACE_MAX"]) == (40, 48)


def test_key_ignores_weeds(ns):
    key = ns["_kil_v5_key"]
    assert key(_farm()) == key(_farm(weed_at=(1, 1)))
    assert key(_farm()) != key(_farm(money=101.0))


def test_identical_until_commit_turns_on_copy_mode(ns, probe):
    _play(ns, [_obs(s) for s in range(0, 170)])
    normal = (40, 48)
    assert probe[:167] == [normal] * 167  # step 0..166 は元のまま
    assert probe[167:] == [(52, 52)] * 3  # 167 で確定し、その呼び出しから深くする
    # 呼び出し後は元に戻っている
    assert (ns["V9_RACE_DEFAULT"], ns["V9_RACE_MAX"]) == normal


def test_commit_step_itself_uses_deep_horizon(ns, probe):
    _play(ns, [_obs(s) for s in range(0, 168)])
    assert probe[-1] == (52, 52)
    assert probe[-2] == (40, 48)


def test_one_mismatch_disables_for_the_game(ns, probe):
    observations = [_obs(s) for s in range(0, 200)]
    observations[5] = _obs(5, rival=_farm(money=99.0))
    _play(ns, observations)
    assert set(probe) == {(40, 48)}


def test_weed_difference_does_not_disable(ns, probe):
    observations = [_obs(s) for s in range(0, 170)]
    observations[100] = _obs(100, rival=_farm(weed_at=(2, 3)))
    _play(ns, observations)
    assert probe[-1] == (52, 52)


def test_after_commit_divergence_keeps_copy_mode(ns, probe):
    observations = [_obs(s) for s in range(0, 168)]
    observations += [_obs(s, rival=_farm(money=5.0)) for s in range(168, 175)]
    _play(ns, observations)
    assert probe[-1] == (52, 52)


def test_state_is_per_player_and_resets_on_new_game(ns, probe):
    _play(ns, [_obs(s, player=1) for s in range(0, 170)])
    assert probe[-1] == (52, 52)
    # 新しい試合（step が戻る）で状態を作り直す。step 0 で食い違えば、以後は元のまま
    _play(ns, [_obs(0, player=1, rival=_farm(money=1.0))] + [_obs(s, player=1) for s in range(1, 200)])
    assert probe[-1] == (40, 48)


def test_restores_constants_when_inner_raises(ns, probe, monkeypatch):
    _play(ns, [_obs(s) for s in range(0, 167)])

    def boom(observation, configuration=None):
        raise RuntimeError("x")

    monkeypatch.setitem(ns, "_KIL_V5_INNER", boom)
    with pytest.raises(RuntimeError):
        ns["_kil_v5_agent"](_obs(167))
    assert (ns["V9_RACE_DEFAULT"], ns["V9_RACE_MAX"]) == (40, 48)


def test_does_not_mutate_observation(ns, probe):
    obs = _obs(3, rival=_farm(weed_at=(4, 4)))
    before = copy.deepcopy(obs)
    ns["_kil_v5_agent"](obs)
    assert obs == before
