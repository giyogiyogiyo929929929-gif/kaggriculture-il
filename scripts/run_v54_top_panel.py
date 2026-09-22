# -*- coding: utf-8 -*-
"""最終v54を上位代表6本へ当て、終了状態を記録する。

仕様: docs/experiments/EXP-20260922-41-v54-top-panel.md
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = Path("data/public_round8_extracted/kaggriculture-v54-productive-wheat-and-patient.py")
OUT = ROOT / "data/eval/v54_top_panel"
STATUS = ROOT / "data/eval/v54_top_panel.monitor.json"
OPPONENTS = [
    ("smaller_market_shock", Path("opponents/smaller_market_shock/main.py")),
    ("v47", Path("opponents/v47/main.py")),
    ("master_v3", Path("opponents/master_v3/main.py")),
    ("wonderful_life", Path("opponents/wonderful_life/main.py")),
    ("pipe16", Path("opponents/pipe16/main.py")),
    ("dz_more_wheat", Path("opponents/dz_more_wheat/main.py")),
]


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def compact(name: str, stage: str, result: dict) -> dict:
    return {"name": name, "stage": stage, **{key: result[key] for key in
            ("pairs", "wins", "losses", "draws", "pair_diff_mean", "pair_diff_stderr")},
            "exceptions_a": result["exceptions"]["a"],
            "exceptions_b": result["exceptions"]["b"],
            "animals_lost": result["health"]["a"]["animals_lost"]}


def evaluate(name: str, opponent: Path, pairs: int, seed: int, stage: str) -> dict:
    target = OUT / f"vs_{name}_{stage}.json"
    subprocess.run([sys.executable, "scripts/eval.py", str(CANDIDATE), str(opponent),
                    "-n", str(pairs), "-j", "4", "--seed-start", str(seed),
                    "--json", str(target)], cwd=ROOT, check=True)
    return json.loads(target.read_text(encoding="utf-8-sig"))


def main() -> int:
    rows = []
    status("running", total=len(OPPONENTS), completed=0, current=None, results=[])
    for index, (name, opponent) in enumerate(OPPONENTS, 1):
        status("running", total=len(OPPONENTS), completed=index - 1, current=name, results=rows)
        smoke = evaluate(name, opponent, 5, 601, "smoke")
        row = compact(name, "smoke", smoke)
        if smoke["wins"] <= smoke["losses"] or abs(smoke["pair_diff_mean"]) <= 2 * smoke["pair_diff_stderr"]:
            confirm = evaluate(name, opponent, 10, 701, "confirm")
            row = compact(name, "confirm", confirm)
            row["smoke"] = compact(name, "smoke", smoke)
        rows.append(row)
        status("running", total=len(OPPONENTS), completed=index, current=None, results=rows)
    summary = {"candidate": str(CANDIDATE), "results": rows}
    write(OUT / "summary.json", summary)
    status("complete", total=len(OPPONENTS), completed=len(OPPONENTS), current=None,
           results=rows, summary=str(OUT / "summary.json"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
