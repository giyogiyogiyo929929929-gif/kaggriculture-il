"""提出前チェックのテスト。

仕様: docs/06_submission.md（チェックリスト）
"""
import sys
import tarfile
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import preflight  # noqa: E402

SHORT = 48


def test_last_callable_is_agent():
    check = preflight.check_last_callable(ROOT / "main.py")
    assert check.ok, check.detail


def test_last_callable_detects_wrong_order(tmp_path):
    path = tmp_path / "bad.py"
    path.write_text(
        "def agent(obs, config=None):\n"
        "    return {}\n"
        "\n"
        "def helper(x):\n"
        "    return x\n",
        encoding="utf-8",
    )
    assert not preflight.check_last_callable(path).ok


def test_imports_are_stdlib_only():
    files = [ROOT / "main.py"] + sorted((ROOT / "agent").glob("*.py"))
    check = preflight.check_imports(files)
    assert check.ok, check.detail


def test_imports_detects_third_party(tmp_path):
    path = tmp_path / "uses_numpy.py"
    path.write_text("import numpy as np\n\ndef agent(obs):\n    return {}\n", encoding="utf-8")
    check = preflight.check_imports([path])
    assert not check.ok
    assert "numpy" in check.detail


def test_kaggle_loader_check_passes():
    """本番と同じ exec 読み込みで動く（doc 06）。"""
    assert preflight.check_kaggle_loader(ROOT / "main.py").ok


def test_kaggle_loader_detects_file_dunder(tmp_path):
    """`__file__` を使うと本番で NameError になる（submission 56333731 の再現）。"""
    path = tmp_path / "uses_file.py"
    path.write_text(
        textwrap.dedent(
            """
            import os
            import sys

            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


            def agent(obs, config=None):
                return {"farmer": ["PASS"], "hands": [], "market": []}
            """
        ),
        encoding="utf-8",
    )
    check = preflight.check_kaggle_loader(path)
    assert not check.ok
    assert "NameError" in check.detail


def test_action_shape_and_fallback():
    agent = preflight.load_agent(ROOT / "main.py")
    assert preflight.check_action_shape(agent).ok
    assert preflight.check_fallback(agent).ok


def test_fallback_detects_raising_agent(tmp_path):
    path = tmp_path / "broken.py"
    path.write_text("def agent(obs, config=None):\n    raise ValueError('x')\n", encoding="utf-8")
    agent = preflight.load_agent(path)
    assert not preflight.check_action_shape(agent).ok
    assert not preflight.check_fallback(agent).ok


def test_build_archive_puts_main_at_root(tmp_path):
    output = tmp_path / "submission.tar.gz"
    preflight.build_archive(output, [ROOT / "main.py", ROOT / "agent"])
    with tarfile.open(output) as archive:
        names = archive.getnames()
    assert "main.py" in names
    assert "agent/macro.py" in names
    assert all(not name.startswith("/") for name in names)


def test_model_is_included_only_when_main_uses_it(tmp_path):
    """モデルは main.py が使うときだけ提出物に入れる（ADR-0002, doc 06）。"""
    assert not preflight.uses_model(ROOT / "main.py")        # 現在は v2（ルール表）
    assert preflight.submission_paths(ROOT) == ["main.py", "agent"]
    (tmp_path / "main.py").write_text(
        "from agent import macro, plan\n"
        "def agent(obs, config=None):\n"
        "    return macro.decide_market(obs, plan=plan.plan_for_turn(obs))\n",
        encoding="utf-8",
    )
    assert preflight.uses_model(tmp_path / "main.py")
    assert "models/macro.json" in preflight.submission_paths(tmp_path)


def test_build_archive_keeps_relative_paths(tmp_path):
    """ファイルもリポジトリからの相対パスで入れる。直下に潰すと本番でモデルが見つからない（doc 06）。"""
    output = tmp_path / "submission.tar.gz"
    preflight.build_archive(output, [ROOT / "main.py", ROOT / "agent", ROOT / "models" / "macro.json"])
    with tarfile.open(output) as archive:
        names = archive.getnames()
    assert "models/macro.json" in names
    assert "macro.json" not in names
    assert "main.py" in names and "agent/plan.py" in names


def test_model_check_passes_on_built_archive(tmp_path):
    """アーカイブを展開し、Kaggle と同じ読み込み方でモデルが読める（doc 06 チェックリスト7）。"""
    output = tmp_path / "submission.tar.gz"
    items = preflight.SUBMISSION_PATHS + preflight.MODEL_PATHS
    preflight.build_archive(output, [ROOT / item for item in items])
    check = preflight.check_model_in_archive(output)
    assert check.ok, check.detail


def test_model_check_fails_when_archive_lacks_model(tmp_path):
    """モデルが入っていないと落とす。黙ってルール表で提出してしまうのを防ぐ（doc 06）。"""
    output = tmp_path / "submission.tar.gz"
    preflight.build_archive(output, [ROOT / "main.py", ROOT / "agent"])
    check = preflight.check_model_in_archive(output)
    assert not check.ok
    assert "ルール表" in check.detail


def test_call_like_kaggle_trims_arguments():
    """Kaggle と同じく引数の数に合わせて (obs, config) を切り詰めて呼ぶ（doc 06, ADR-0003）。"""
    def one(obs):
        return ("one", obs)

    def two(obs, config=None):
        return ("two", obs, config)

    assert preflight.call_like_kaggle(one, {"a": 1}, {"c": 2}) == ("one", {"a": 1})
    assert preflight.call_like_kaggle(two, {"a": 1}, {"c": 2}) == ("two", {"a": 1}, {"c": 2})


def test_entry_name_can_be_specified():
    """rayk_c54 の最後の callable は c94_submission_agent（doc 06 公開エージェントの提出）。"""
    main_path = ROOT / "submissions" / "rayk_c54" / "main.py"
    assert not preflight.check_last_callable(main_path).ok
    assert preflight.check_last_callable(main_path, entry="c94_submission_agent").ok


def test_single_file_archive_has_only_main(tmp_path):
    """agent\\ が無いディレクトリなら main.py だけの tar になる（doc 06）。"""
    root = ROOT / "submissions" / "v16rc5"
    output = tmp_path / "submission.tar.gz"
    preflight.build_archive(output, [root / item for item in preflight.submission_paths(root)], root=root)
    with tarfile.open(output) as archive:
        assert archive.getnames() == ["main.py"]


def test_v16rc5_passes_preflight():
    """第1候補の公開エージェントが短い試合で preflight を通る（ADR-0003）。"""
    main_path = ROOT / "submissions" / "v16rc5" / "main.py"
    checks = preflight.run_checks(main_path=main_path, entry="agent", episode_steps=SHORT)
    failed = [f"{c.name}: {c.detail}" for c in checks if not c.ok]
    assert not failed, failed


def test_rayk_c54_fails_only_on_none_observation():
    """rayk_c54 は観測 None で AttributeError になる。そこだけが落ちることを記録する（doc 06）。"""
    main_path = ROOT / "submissions" / "rayk_c54" / "main.py"
    checks = preflight.run_checks(main_path=main_path, entry="c94_submission_agent", episode_steps=SHORT)
    failed = [c for c in checks if not c.ok]
    assert [c.name for c in failed] == ["壊れた観測でも落ちない"]
    assert "None" in failed[0].detail and "AttributeError" in failed[0].detail


def test_turn_time_criterion_is_worst_200ms_and_p99_50ms():
    """NFR-1（2026-09-19 改訂）：最悪 < 200ms かつ 99%点 < 50ms。"""
    base = [0.001] * 999
    assert preflight.turn_time_stats(base + [0.055])["ok"]        # v9/4 相当：最悪 55ms が1回だけ → 通す
    assert not preflight.turn_time_stats(base + [0.25])["ok"]     # 最悪 250ms → 落とす
    many_slow = [0.001] * 980 + [0.06] * 20                        # 2% のターンが 60ms → 99%点が 50ms を超える
    assert not preflight.turn_time_stats(many_slow)["ok"]


def test_fallback_check_accepts_non_pass_actions(tmp_path):
    """壊れた観測で PASS 以外を返しても、例外が無く形が正しければ通す（NFR-2）。"""
    def agent(obs):
        return {"farmer": ["PASS"], "hands": [], "market": [["HIRE"]]}

    assert preflight.check_fallback(agent).ok


def test_fallback_check_rejects_wrong_shape():
    def agent(obs, config=None):
        return {"farmer": "PASS"}

    assert not preflight.check_fallback(agent).ok


def test_run_checks_passes(tmp_path):
    """短い試合で一通り通ることを確認（時間計測以外は本番と同じ）。"""
    checks = preflight.run_checks(episode_steps=SHORT)
    failed = [check.name for check in checks if not check.ok]
    assert not failed, failed


def test_main_returns_zero_and_writes_json(tmp_path):
    out = tmp_path / "preflight.json"
    code = preflight.main(["--episode-steps", str(SHORT), "--json", str(out)])
    assert code == 0
    assert out.exists()


@pytest.mark.slow
def test_full_length_preflight():
    """本番と同じ720ターンでチェックを通す（doc 06）。"""
    checks = preflight.run_checks()
    failed = [f"{check.name}: {check.detail}" for check in checks if not check.ok]
    assert not failed, failed
