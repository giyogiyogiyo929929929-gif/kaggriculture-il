"""現在のエージェントを比較用に丸ごと凍結する。

仕様: docs/05_evaluation.md §3（比較対象：直前の提出版）

`baselines\\<name>_agent.py` と `baselines\\<name>_pkg\\` を作る。
パッケージ名を変えて写すので、`agent/` 側のコードを変えても凍結版は変わらない。

    .venv\\Scripts\\python.exe scripts\\freeze_agent.py v2

注意：パラメータだけを写した凍結版では**コードの変更を比較できない**
（両方が同じ `agent/` を import してしまう）。必ずこのスクリプトで凍結すること。
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINES = ROOT / "baselines"

ENTRY_TEMPLATE = '''"""比較用に凍結したエージェント（{name}）。{note}

`scripts\\\\freeze_agent.py` が生成。手で編集しない。
"""
import os
import sys

if "__file__" in globals():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from {package} import execute, macro  # noqa: E402


def agent(obs, config=None):
    try:
        market = macro.decide_market(obs, config=config)
        units = execute.assign(obs, config=config)
        return {{"farmer": units["farmer"], "hands": units["hands"], "market": market}}
    except Exception:
        return {{"farmer": ["PASS"], "hands": [], "market": []}}
'''


def freeze(name: str, note: str = "", source: Path = ROOT / "agent") -> Path:
    """`agent/` を `baselines/<name>_pkg/` に写し、入口の `<name>_agent.py` を作る。"""
    package = f"{name}_pkg"
    target = BASELINES / package
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for path in sorted(source.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        # 自分のパッケージ名への参照を書き換える（agent.macro → <name>_pkg.macro）
        text = re.sub(r"\bfrom agent\b", f"from {package}", text)
        text = re.sub(r"\bfrom agent\.", f"from {package}.", text)
        text = re.sub(r"\bimport agent\b", f"import {package}", text)
        (target / path.name).write_text(text, encoding="utf-8")
    entry = BASELINES / f"{name}_agent.py"
    entry.write_text(
        ENTRY_TEMPLATE.format(name=name, package=package, note=f" {note}" if note else ""),
        encoding="utf-8",
    )
    return entry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="エージェントを凍結する（docs/05_evaluation.md §3）")
    parser.add_argument("name", help="凍結名（例：v2）")
    parser.add_argument("--note", default="", help="説明（提出IDなど）")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except (AttributeError, ValueError):
        pass
    entry = freeze(args.name, args.note)
    print(f"凍結: {entry}")
    print(f"      {BASELINES / (args.name + '_pkg')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
