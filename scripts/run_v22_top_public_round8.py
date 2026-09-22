# -*- coding: utf-8 -*-
"""Public Score上位10本との対戦を監視付きで実行する。

仕様: docs/experiments/EXP-20260922-39-top-public-round8.md
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = Path("submissions/v22_antiv52_brunchguard/main.py")
OUT = ROOT / "data" / "eval" / "v22_top_public_round8"
STATUS = ROOT / "data" / "eval" / "v22_top_public_round8.monitor.json"
OPPONENTS = [
    ("smaller_market_shock", Path("opponents/smaller_market_shock/main.py")),
    ("v47", Path("opponents/v47/main.py")),
    ("farmer_john_idle", Path("data/public_round8_extracted/farmer-john-and-the-idle-seller.py")),
    ("v54", Path("data/public_round8_extracted/kaggriculture-v54-productive-wheat-and-patient.py")),
    ("master_v3", Path("opponents/master_v3/main.py")),
    ("farmer_john_wheat", Path("data/public_round8_extracted/farmer-john-and-the-wheat-seller.py")),
    ("autonomous_ai", Path("data/public_round8_extracted/kaggriculture-autonomous-ai-farming-agent.py")),
    ("wonderful_life", Path("opponents/wonderful_life/main.py")),
    ("pipe16", Path("opponents/pipe16/main.py")),
    ("dz_more_wheat", Path("opponents/dz_more_wheat/main.py")),
]


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def write_status(state: str, **extra) -> None:
    write_json(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def evaluate(name: str, opponent: Path, pairs: int, seed: int, suffix: str) -> dict:
    target = OUT / f"vs_{name}_{suffix}.json"
    command = [sys.executable, "scripts/eval.py", str(CANDIDATE), str(opponent),
               "-n", str(pairs), "-j", "4", "--seed-start", str(seed),
               "--json", str(target)]
    print(f"\n=== {name}: {pairs} pairs, seed {seed}- ===", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)
    return json.loads(target.read_text(encoding="utf-8-sig"))


def compact(name: str, stage: str, result: dict) -> dict:
    return {
        "name": name,
        "stage": stage,
        "pairs": result["pairs"],
        "wins": result["wins"],
        "losses": result["losses"],
        "draws": result["draws"],
        "pair_diff_mean": result["pair_diff_mean"],
        "pair_diff_stderr": result["pair_diff_stderr"],
        "exceptions_a": result["exceptions"]["a"],
        "exceptions_b": result["exceptions"]["b"],
        "animals_lost": result["health"]["a"]["animals_lost"],
    }


def main() -> int:
    missing = [str(path) for _, path in OPPONENTS if not (ROOT / path).is_file()]
    if missing:
        raise FileNotFoundError("missing opponents: " + ", ".join(missing))
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    write_status("running", total=len(OPPONENTS), completed=0, current=None, results=[])
    for index, (name, opponent) in enumerate(OPPONENTS, 1):
        write_status("running", total=len(OPPONENTS), completed=index - 1,
                     current=name, results=rows)
        smoke = evaluate(name, opponent, 5, 601, "smoke")
        row = compact(name, "smoke", smoke)
        uncertain = (smoke["wins"] <= smoke["losses"] or
                     abs(smoke["pair_diff_mean"]) <= 2 * smoke["pair_diff_stderr"])
        if uncertain:
            confirm = evaluate(name, opponent, 10, 701, "confirm")
            row = compact(name, "confirm", confirm)
            row["smoke"] = compact(name, "smoke", smoke)
        rows.append(row)
        write_status("running", total=len(OPPONENTS), completed=index,
                     current=None, results=rows)
    summary = {
        "candidate": str(CANDIDATE),
        "ranking_observed": "2026-09-22 Kaggle API scoreDescending",
        "results": rows,
        "exceptions_total": sum(r["exceptions_a"] + r["exceptions_b"] for r in rows),
        "animals_lost_total": sum(r["animals_lost"] for r in rows),
    }
    write_json(OUT / "summary.json", summary)
    write_status("complete", total=len(OPPONENTS), completed=len(OPPONENTS),
                 current=None, results=rows, summary=str(OUT / "summary.json"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        write_status("failed", error=repr(error))
        raise
