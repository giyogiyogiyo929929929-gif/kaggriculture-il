# -*- coding: utf-8 -*-
"""ユーザー指定2本の異系統安全性と直接比較を監視付きで評価する。

仕様: docs/experiments/EXP-20260922-44-user-two-public-notebooks.md
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/eval/two_latest_safety"
STATUS = ROOT / "data/eval/two_latest_safety.monitor.json"
MORE = Path("data/public_round9_extracted/kaggriculture-more-wheat-smarter-sales.py")
V56 = Path("data/public_round9_extracted/kaggriculture-v56-smarter-seeds-and-fertilizer.py")
TASKS = [
    ("more_vs_jaxa", MORE, Path("opponents/jaxa_2802/main.py"), 5, 241),
    ("more_vs_v49", MORE, Path("opponents/v49/main.py"), 5, 241),
    ("more_vs_story", MORE, Path("opponents/story_of_seasons/main.py"), 5, 301),
    ("v56_vs_jaxa", V56, Path("opponents/jaxa_2802/main.py"), 5, 241),
    ("v56_vs_v49", V56, Path("opponents/v49/main.py"), 5, 241),
    ("v56_vs_story", V56, Path("opponents/story_of_seasons/main.py"), 5, 301),
    ("v56_vs_more", V56, MORE, 10, 901),
]


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def main() -> int:
    rows = []
    status("running", total=len(TASKS), completed=0, current=None, results=[])
    for index, (name, candidate, opponent, pairs, seed) in enumerate(TASKS, 1):
        status("running", total=len(TASKS), completed=index - 1, current=name, results=rows)
        target = OUT / f"{name}.json"
        subprocess.run([sys.executable, "scripts/eval.py", str(candidate), str(opponent),
                        "-n", str(pairs), "-j", "4", "--seed-start", str(seed),
                        "--json", str(target)], cwd=ROOT, check=True)
        result = json.loads(target.read_text(encoding="utf-8-sig"))
        rows.append({"name": name, **{key: result[key] for key in
                    ("pairs", "wins", "losses", "draws", "pair_diff_mean", "pair_diff_stderr")},
                    "exceptions_a": result["exceptions"]["a"],
                    "exceptions_b": result["exceptions"]["b"],
                    "animals_lost": result["health"]["a"]["animals_lost"]})
        status("running", total=len(TASKS), completed=index, current=None, results=rows)
    summary = {"results": rows}
    write(OUT / "summary.json", summary)
    status("complete", total=len(TASKS), completed=len(TASKS), current=None,
           results=rows, summary=str(OUT / "summary.json"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
