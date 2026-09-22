# -*- coding: utf-8 -*-
"""ユーザー指定の最新公開2本をv22と監視付きで評価する。

仕様: docs/experiments/EXP-20260922-44-user-two-public-notebooks.md
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = Path("submissions/v22_antiv52_brunchguard/main.py")
OUT = ROOT / "data/eval/v22_user_two_latest"
STATUS = ROOT / "data/eval/v22_user_two_latest.monitor.json"
OPPONENTS = [
    ("more_wheat_latest", Path("data/public_round9_extracted/kaggriculture-more-wheat-smarter-sales.py")),
    ("v56", Path("data/public_round9_extracted/kaggriculture-v56-smarter-seeds-and-fertilizer.py")),
]


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def status(state: str, **extra) -> None:
    write(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def evaluate(name: str, opponent: Path, pairs: int, seed: int, stage: str) -> dict:
    target = OUT / f"vs_{name}_{stage}.json"
    subprocess.run([sys.executable, "scripts/eval.py", str(CANDIDATE), str(opponent),
                    "-n", str(pairs), "-j", "4", "--seed-start", str(seed),
                    "--json", str(target)], cwd=ROOT, check=True)
    return json.loads(target.read_text(encoding="utf-8-sig"))


def compact(name: str, stage: str, result: dict) -> dict:
    return {"name": name, "stage": stage, **{key: result[key] for key in
            ("pairs", "wins", "losses", "draws", "pair_diff_mean", "pair_diff_stderr")},
            "exceptions_a": result["exceptions"]["a"],
            "exceptions_b": result["exceptions"]["b"],
            "animals_lost": result["health"]["a"]["animals_lost"]}


def main() -> int:
    rows = []
    status("running", total=2, completed=0, current=None, results=[])
    for index, (name, opponent) in enumerate(OPPONENTS, 1):
        status("running", total=2, completed=index - 1, current=name, results=rows)
        smoke = evaluate(name, opponent, 5, 801, "smoke")
        result = compact(name, "smoke", smoke)
        if smoke["wins"] <= smoke["losses"] or abs(smoke["pair_diff_mean"]) <= 2 * smoke["pair_diff_stderr"]:
            confirm = evaluate(name, opponent, 10, 851, "confirm")
            result = compact(name, "confirm", confirm)
            result["smoke"] = compact(name, "smoke", smoke)
        rows.append(result)
        status("running", total=2, completed=index, current=None, results=rows)
    summary = {"candidate": str(CANDIDATE), "results": rows}
    write(OUT / "summary.json", summary)
    status("complete", total=2, completed=2, current=None, results=rows,
           summary=str(OUT / "summary.json"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
