"""inspect_replay の受け入れ条件テスト。

仕様: docs/03_replay_schema.md §6, §7
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import inspect_replay  # noqa: E402


def _agent_buyer(obs):
    """step 0 で種を買い、step 1 で植える。行動と観測の対応を見るため。"""
    step = obs.get("day", 0) * 24 + obs.get("hour", 0)
    if step == 0:
        return {"farmer": ["PASS"], "market": [["BUY_SEED", "WHEAT", 2]]}
    if step == 1:
        return {"farmer": ["PLANT", "WHEAT"], "market": [["HIRE"]]}
    return {"farmer": ["WATER"], "market": []}


def _agent_idle(obs):
    return {"farmer": ["PASS"], "market": []}


@pytest.fixture(scope="session")
def local_replay(tmp_path_factory):
    """ローカル対戦を1本走らせたリプレイ（30ステップ）。"""
    from kaggle_environments import make

    env = make("kaggriculture", configuration={"episodeSteps": 30, "seed": 42})
    env.run([_agent_buyer, _agent_idle])
    rep = env.toJSON()
    path = tmp_path_factory.mktemp("replay") / "local_replay.json"
    path.write_text(json.dumps(rep), encoding="utf-8")
    return path


def test_load_replay(local_replay):
    rep, wrapper = inspect_replay.load_replay(local_replay)
    assert wrapper is None
    assert rep["name"] == "kaggriculture"
    assert len(rep["steps"]) == 30


def test_report_has_all_sections(local_replay):
    """§6 の1〜8をすべて出力する。"""
    rep, _ = inspect_replay.load_replay(local_replay)
    report = inspect_replay.describe(rep, path=local_replay)
    for n in range(1, 9):
        assert f"[{n}]" in report, f"section {n} missing"
    assert "kaggriculture" in report
    assert "episodeSteps" in report  # [2] configuration
    assert "BUY_SEED" in report  # [6] market が空でない行動例


def test_observation_keys_per_seat(local_replay):
    """席1の観測に step キーが無いこと（doc 03 §3.2）。"""
    rep, _ = inspect_replay.load_replay(local_replay)
    keys = inspect_replay.observation_keys(rep)
    assert "step" in keys[0]
    assert "step" not in keys[1]
    for seat in (0, 1):
        assert {"day", "hour", "farms", "market", "town", "private"} <= keys[seat]


def test_action_alignment(local_replay):
    """steps[t].action は steps[t-1].observation に対する行動（doc 03 §3.1）。"""
    rep, _ = inspect_replay.load_replay(local_replay)
    result = inspect_replay.check_action_alignment(rep, seat=0)
    assert result["aligned"] is True
    # BUY_SEED WHEAT 2 は steps[1] に記録され、その結果は steps[1] の観測に出る
    assert result["first_market_step"] == 1
    assert result["money_before"] > result["money_after"]
    assert rep["steps"][0][0]["observation"]["private"]["seeds"]["WHEAT"] == 0
    assert rep["steps"][1][0]["observation"]["private"]["seeds"]["WHEAT"] == 2


def test_final_rewards(local_replay):
    rep, _ = inspect_replay.load_replay(local_replay)
    outcome = inspect_replay.final_outcome(rep)
    assert outcome["rewards"] == [
        rep["steps"][-1][0]["observation"]["farms"][0]["money"],
        rep["steps"][-1][0]["observation"]["farms"][1]["money"],
    ]
    assert outcome["statuses"] == ["DONE", "DONE"]
    assert outcome["winner"] in (0, 1, None)


def test_cli_runs(local_replay):
    """CLI が終了コード0で1〜8を標準出力に出す。"""
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "inspect_replay.py"), str(local_replay)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    for n in range(1, 9):
        assert f"[{n}]" in proc.stdout
