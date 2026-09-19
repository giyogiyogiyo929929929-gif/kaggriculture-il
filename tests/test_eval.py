"""評価スクリプトの受け入れ条件テスト。

仕様: docs/05_evaluation.md §1（方法）, §2（出力）, §5（受け入れ条件）
本番の720ターンは重いので、テストでは `--episode-steps` を小さくして回す。
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import eval as evaluation  # noqa: E402

SHORT = 48  # 2日ぶん


def test_resolve_builtin_agent():
    """組み込みエージェントはそのまま名前で渡す（doc 05 §1.1）。"""
    assert evaluation.resolve_agent("starter") == "starter"
    assert evaluation.resolve_agent("random") == "random"


def test_load_agent_from_file():
    """ファイル指定は最後に定義された callable を使う（doc 05 §1.1 / 06）。"""
    agent = evaluation.resolve_agent(str(ROOT / "main.py"))
    assert callable(agent)
    assert agent.__name__ == "agent"
    result = agent({}, None)  # 壊れた観測でもフォールバックする
    assert result["farmer"] == ["PASS"]


def test_load_agent_picks_last_callable(tmp_path):
    path = tmp_path / "dummy_agent.py"
    path.write_text(
        "def helper(obs):\n"
        "    return 1\n"
        "\n"
        "def my_agent(obs, config=None):\n"
        '    return {"farmer": ["PASS"], "hands": [], "market": []}\n',
        encoding="utf-8",
    )
    agent = evaluation.resolve_agent(str(path))
    assert agent.__name__ == "my_agent"


def test_build_matches_swaps_seats():
    """各 seed について席を入れ替えた2試合（doc 05 §1）。"""
    matches = evaluation.build_matches(pairs=2, seed_start=10)
    assert matches == [(10, False), (10, True), (11, False), (11, True)]


def test_play_match_metrics():
    """1試合の結果に必要な指標が揃う（doc 05 §2, §2.1）。"""
    result = evaluation.play_match("starter", "random", seed=3, swap=False, episode_steps=SHORT)
    assert result["seed"] == 3
    assert result["swap"] is False
    assert isinstance(result["money"], list) and len(result["money"]) == 2
    assert result["steps"] == SHORT
    for side in ("a", "b"):
        assert result["timings"][side]["max"] >= 0
        assert result["exceptions"][side] == 0
    health = result["health"]["a"]
    for key in ("planted", "harvested", "withered", "unharvested_lost", "lifespan_ended",
                "crop_losses", "weed_spawned", "animals_lost", "shed_final"):
        assert key in health
    assert health["crop_losses"] == health["withered"] + health["unharvested_lost"]


def test_classify_weed_separates_lifespan_from_loss():
    """PLANT→WEED の3分類（doc 05 §2.1、EXP-20260919-06）。

    ongoing 作物は最終収穫の翌日に必ず WEED になる。この寿命終了を損失に数えると
    枯死率が 25% に見えてしまう（実損失は 0.15%）。
    """
    harvested = {"kind": "PLANT", "crop": "STRAWBERRY", "max_lifespan_step": 100, "yield_units": 0}
    assert evaluation.classify_weed(harvested, step_index=101) == "lifespan_ended"

    left_on_the_vine = dict(harvested, yield_units=3)
    assert evaluation.classify_weed(left_on_the_vine, step_index=101) == "unharvested_lost"

    dried_out = {"kind": "PLANT", "crop": "WHEAT", "max_lifespan_step": -1,
                 "watered_today": False, "consecutive_unwatered": 1, "yield_units": 0}
    assert evaluation.classify_weed(dried_out, step_index=50) == "withered"

    # 寿命に達していなければ寿命終了とは数えない
    assert evaluation.classify_weed(dict(harvested, max_lifespan_step=200), step_index=101) == "withered"


def test_play_match_swap_reports_from_a_perspective():
    """swap=True でもエージェントAの結果が money[0] に来る（doc 05 §3：pass は 3000 のまま）。"""
    normal = evaluation.play_match("starter", "pass", seed=5, swap=False, episode_steps=SHORT)
    swapped = evaluation.play_match("starter", "pass", seed=5, swap=True, episode_steps=SHORT)
    assert normal["money"][1] == 3000.0  # B は pass なので所持金が動かない
    assert swapped["money"][1] == 3000.0
    assert normal["money"][0] != 3000.0  # A は starter なので種を買っている
    assert swapped["money"][0] != 3000.0


def test_evaluate_summary():
    summary = evaluation.evaluate("starter", "random", pairs=1, jobs=1, episode_steps=SHORT)
    assert summary["pairs"] == 1
    assert summary["matches"] == 2
    assert summary["wins"] + summary["losses"] + summary["draws"] == 1
    assert "pair_diff_mean" in summary and "pair_diff_stderr" in summary
    assert summary["timings"]["a"]["median"] >= 0
    text = evaluation.format_summary(summary)
    assert "ペア差" in text and "1ターン推論" in text and "健全性" in text


def test_parallel_matches_equal_serial():
    """-j 4 と -j 1 で結果が一致する（決定的なエージェント同士。doc 05 §1.2, §5）。"""
    serial = evaluation.evaluate("starter", "pass", pairs=2, jobs=1, episode_steps=SHORT)
    parallel = evaluation.evaluate("starter", "pass", pairs=2, jobs=4, episode_steps=SHORT)
    assert [m["money"] for m in serial["matches_detail"]] == [
        m["money"] for m in parallel["matches_detail"]
    ]
    assert serial["wins"] == parallel["wins"]


def test_agent_exception_is_counted(tmp_path):
    """例外を投げるエージェントでも評価が止まらない（doc 05 §5）。"""
    path = tmp_path / "broken_agent.py"
    path.write_text(
        "def agent(obs, config=None):\n"
        "    raise ValueError('壊れている')\n",
        encoding="utf-8",
    )
    result = evaluation.play_match(str(path), "starter", seed=1, swap=False, episode_steps=SHORT)
    assert result["exceptions"]["a"] > 0
    assert result["money"][1] > 0  # 相手は普通に試合を続けている


def test_single_argument_agent_is_called_like_kaggle(tmp_path):
    """`agent(obs)` だけのエージェントにも、Kaggle と同じく obs だけを渡す（doc 05 §1.1）。

    以前は常に (obs, config) を渡していたため、公開エージェント2本が毎ターン TypeError になり
    「一度も行動しない」と誤評価していた（EXP-20260919-10）。
    """
    path = tmp_path / "one_arg_agent.py"
    path.write_text(
        "def agent(obs):\n"
        "    return {'farmer': ['PASS'], 'hands': [], 'market': []}\n",
        encoding="utf-8",
    )
    result = evaluation.play_match(str(path), "starter", seed=1, swap=False, episode_steps=SHORT)
    assert result["exceptions"]["a"] == 0


def test_json_output(tmp_path):
    out = tmp_path / "result.json"
    code = evaluation.main([
        "starter", "random", "-n", "1", "-j", "1",
        "--episode-steps", str(SHORT), "--json", str(out),
    ])
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["agents"] == ["starter", "random"]
    assert data["pairs"] == 1


def test_cli_runs(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "eval.py"), "starter", "random",
         "-n", "1", "-j", "1", "--episode-steps", str(SHORT)],
        capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    assert "ペア差" in proc.stdout


@pytest.mark.slow
def test_baseline_beats_starter():
    """main.py が starter に全勝する（doc 05 §5、EXP-20260919-01 の再現）。"""
    summary = evaluation.evaluate(str(ROOT / "main.py"), "starter", pairs=5, jobs=4)
    assert summary["wins"] == 5
    assert summary["pair_diff_mean"] > 0
    assert summary["exceptions"]["a"] == 0


@pytest.mark.slow
def test_baseline_loses_no_animals():
    """提出の合格基準（doc 05 §4）：家畜の逃走ゼロ・作物の損失は植え付けの5%以下。

    逃走は EXP-20260919-05（cash_floor 800）で解消。
    損失は寿命終了を除いて数える（EXP-20260919-06。以前は 25% に見えていた）。
    """
    summary = evaluation.evaluate(str(ROOT / "main.py"), "starter", pairs=5, jobs=4)
    health = summary["health"]["a"]
    assert health["animals_lost"] == 0
    assert health["crop_losses"] <= health["planted"] * 0.05
