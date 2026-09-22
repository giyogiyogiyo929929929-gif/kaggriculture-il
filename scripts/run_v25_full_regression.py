# -*- coding: utf-8 -*-
"""v25をv22保存結果と同一seedの18相手へ順次回帰する。"""
import json
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = Path("submissions/v25_e402_e410/main.py")
OUT = ROOT / "data/eval/v25_full_regression"
STATUS = ROOT / "data/eval/v25_full_regression.monitor.json"

TASKS = []
for name in ("smaller_market_shock", "v47", "master_v3", "wonderful_life", "pipe16", "dz_more_wheat"):
    TASKS.append((name, Path(f"opponents/{name}/main.py"),
                  Path(f"data/eval/v22_top_public_round8/vs_{name}_smoke.json")))
for name in ("v49", "v50", "metav4_v13", "k256_h2_q_v1", "market_rhythm",
             "story_of_seasons", "thomas_router_93", "tetsutani_dpts_b", "jaxa_2802", "ready_stock"):
    TASKS.append((name, Path(f"opponents/{name}/main.py"),
                  Path(f"data/eval/v22_antiv52_brunchguard_regression/vs_{name}.json")))
TASKS += [
    ("more_wheat_latest", Path("data/public_round9_extracted/kaggriculture-more-wheat-smarter-sales.py"),
     Path("data/eval/v22_user_two_latest/vs_more_wheat_latest_smoke.json")),
    ("v56", Path("data/public_round9_extracted/kaggriculture-v56-smarter-seeds-and-fertilizer.py"),
     Path("data/eval/v22_user_two_latest/vs_v56_smoke.json")),
]


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def first_five(result: dict) -> dict:
    differences = []
    for index in range(0, 10, 2):
        pair = result["matches_detail"][index:index + 2]
        differences.append(sum(float(match["money"][0]) - float(match["money"][1]) for match in pair) / 2)
    return {
        "wins": sum(value > 0 for value in differences),
        "losses": sum(value < 0 for value in differences),
        "draws": sum(value == 0 for value in differences),
        "pair_diff_mean": statistics.mean(differences),
        "pair_diff_stderr": statistics.stdev(differences) / len(differences) ** 0.5,
    }


def main() -> int:
    rows = []
    status("running", total=len(TASKS), completed=0, current=None, results=[])
    for index, (name, opponent, baseline_path) in enumerate(TASKS, 1):
        baseline_raw = json.loads((ROOT / baseline_path).read_text(encoding="utf-8-sig"))
        baseline = first_five(baseline_raw) if baseline_raw["pairs"] > 5 else {
            key: baseline_raw[key] for key in
            ("wins", "losses", "draws", "pair_diff_mean", "pair_diff_stderr")
        }
        seed = int(baseline_raw["matches_detail"][0]["seed"])
        status("running", total=len(TASKS), completed=index - 1, current=name, results=rows)
        target = OUT / f"vs_{name}.json"
        subprocess.run(
            [sys.executable, "scripts/eval.py", str(CANDIDATE), str(opponent),
             "-n", "5", "-j", "4", "--seed-start", str(seed), "--json", str(target)],
            cwd=ROOT, check=True,
        )
        result = json.loads(target.read_text(encoding="utf-8-sig"))
        candidate = {key: result[key] for key in
                     ("wins", "losses", "draws", "pair_diff_mean", "pair_diff_stderr")}
        rows.append({"name": name, "v25": candidate, "v22": baseline,
                     "win_delta": candidate["wins"] - baseline["wins"],
                     "mean_delta": candidate["pair_diff_mean"] - baseline["pair_diff_mean"],
                     "exceptions_a": result["exceptions"]["a"],
                     "exceptions_b": result["exceptions"]["b"],
                     "animals_lost": result["health"]["a"]["animals_lost"]})
        status("running", total=len(TASKS), completed=index, current=None, results=rows)
    passed = not any(row["win_delta"] < 0 or row["exceptions_a"] or row["animals_lost"] for row in rows)
    write(OUT / "summary.json", {"passed": passed, "results": rows})
    status("complete", total=len(TASKS), completed=len(TASKS), current=None,
           passed=passed, results=rows, summary=str(OUT / "summary.json"))
    return 0 if passed else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
