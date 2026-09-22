# -*- coding: utf-8 -*-
"""v54を重要10相手へ5ペアで当て、v22既存結果と比較する。

仕様: docs/experiments/EXP-20260922-42-v54-targeted-regression.md
"""
import json
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = Path("data/public_round8_extracted/kaggriculture-v54-productive-wheat-and-patient.py")
BASE = ROOT / "data/eval/v22_antiv52_brunchguard_regression"
OUT = ROOT / "data/eval/v54_targeted_regression"
STATUS = ROOT / "data/eval/v54_targeted_regression.monitor.json"
NAMES = ("v49", "v50", "metav4_v13", "k256_h2_q_v1", "market_rhythm",
         "story_of_seasons", "thomas_router_93", "tetsutani_dpts_b", "jaxa_2802",
         "ready_stock")


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def first_five(result: dict) -> dict:
    diffs = []
    for index in range(0, 10, 2):
        pair = result["matches_detail"][index:index + 2]
        diffs.append(sum(float(m["money"][0]) - float(m["money"][1]) for m in pair) / 2)
    return {"wins": sum(x > 0 for x in diffs), "losses": sum(x < 0 for x in diffs),
            "draws": sum(x == 0 for x in diffs), "pair_diff_mean": statistics.mean(diffs),
            "pair_diff_stderr": statistics.stdev(diffs) / len(diffs) ** 0.5 if len(diffs) > 1 else 0.0}


def main() -> int:
    rows = []
    status("running", total=len(NAMES), completed=0, current=None, results=[])
    for index, name in enumerate(NAMES, 1):
        status("running", total=len(NAMES), completed=index - 1, current=name, results=rows)
        baseline_raw = json.loads((BASE / f"vs_{name}.json").read_text(encoding="utf-8-sig"))
        seed = int(baseline_raw["matches_detail"][0]["seed"])
        opponent = Path(f"opponents/{name}/main.py")
        target = OUT / f"vs_{name}.json"
        subprocess.run([sys.executable, "scripts/eval.py", str(CANDIDATE), str(opponent),
                        "-n", "5", "-j", "4", "--seed-start", str(seed),
                        "--json", str(target)], cwd=ROOT, check=True)
        result = json.loads(target.read_text(encoding="utf-8-sig"))
        rows.append({"name": name, "seed_start": seed,
                     "v54": {key: result[key] for key in
                             ("wins", "losses", "draws", "pair_diff_mean", "pair_diff_stderr")},
                     "v22": first_five(baseline_raw),
                     "exceptions_a": result["exceptions"]["a"],
                     "exceptions_b": result["exceptions"]["b"],
                     "animals_lost": result["health"]["a"]["animals_lost"]})
        status("running", total=len(NAMES), completed=index, current=None, results=rows)
    summary = {"candidate": str(CANDIDATE), "pairs_each": 5, "results": rows}
    write(OUT / "summary.json", summary)
    status("complete", total=len(NAMES), completed=len(NAMES), current=None,
           results=rows, summary=str(OUT / "summary.json"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
