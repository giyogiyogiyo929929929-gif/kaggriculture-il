"""エージェント凍結のテスト。

仕様: docs/05_evaluation.md §3（比較対象：直前の提出版）
凍結版が「現行コードの変更に影響されない」ことがこのツールの存在理由。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import eval as evaluation  # noqa: E402
from scripts import freeze_agent  # noqa: E402


def test_freeze_rewrites_package_imports(tmp_path):
    source = tmp_path / "agent"
    source.mkdir()
    (source / "__init__.py").write_text("", encoding="utf-8")
    (source / "features.py").write_text("VALUE = 1\n", encoding="utf-8")
    (source / "macro.py").write_text(
        "from agent import features\n"
        "\n"
        "def decide_market(obs, config=None, params=None):\n"
        "    return [features.VALUE]\n",
        encoding="utf-8",
    )
    (source / "execute.py").write_text(
        "from agent.macro import decide_market\n"
        "\n"
        "def assign(obs, config=None, params=None):\n"
        '    return {"farmer": ["PASS"], "hands": []}\n',
        encoding="utf-8",
    )

    original_baselines = freeze_agent.BASELINES
    freeze_agent.BASELINES = tmp_path / "baselines"
    try:
        entry = freeze_agent.freeze("t1", note="テスト", source=source)
    finally:
        freeze_agent.BASELINES = original_baselines

    assert entry.exists()
    package_dir = tmp_path / "baselines" / "t1_pkg"
    assert (package_dir / "macro.py").read_text(encoding="utf-8").startswith("from t1_pkg import")
    assert "from t1_pkg.macro import" in (package_dir / "execute.py").read_text(encoding="utf-8")
    assert "from t1_pkg import execute, macro" in entry.read_text(encoding="utf-8")


def test_frozen_agent_is_loadable_and_independent():
    """凍結済みの v1 / v2 が読み込めて、現行の agent パッケージとは別物であること。"""
    v1 = evaluation.resolve_agent(str(ROOT / "baselines" / "v1_agent.py"))
    v2 = evaluation.resolve_agent(str(ROOT / "baselines" / "v2_agent.py"))
    assert v1.__name__ == "agent" and v2.__name__ == "agent"
    assert v1({}, None)["farmer"] == ["PASS"]

    import v1_pkg.macro as v1_macro  # noqa: E402  凍結時の sys.path 追加で読める
    import v2_pkg.macro as v2_macro  # noqa: E402
    from agent import macro as current_macro  # noqa: E402

    # v1 は提出版（cash_floor 200）、v2 は改善版（800）。現行は v2 と同じ値
    assert v1_macro.PARAMS["cash_floor"] == 200
    assert v2_macro.PARAMS["cash_floor"] == 800
    assert current_macro.PARAMS["cash_floor"] == v2_macro.PARAMS["cash_floor"]
    assert v1_macro.PARAMS is not current_macro.PARAMS
