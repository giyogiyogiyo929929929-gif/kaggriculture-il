# -*- coding: utf-8 -*-
"""v23の上位代表ゲート後、合格時だけ重要10相手回帰へ進む。

仕様: docs/experiments/EXP-20260922-43-v23-productive-wheat.md
"""
import json
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = Path("submissions/v23_productive_wheat/main.py")
OUT = ROOT / "data/eval/v23_productive_wheat"
STATUS = ROOT / "data/eval/v23_productive_wheat.monitor.json"
TOP = ("smaller_market_shock", "v47", "master_v3", "wonderful_life", "pipe16", "dz_more_wheat")
REG = ("v49", "v50", "metav4_v13", "k256_h2_q_v1", "market_rhythm",
       "story_of_seasons", "thomas_router_93", "tetsutani_dpts_b", "jaxa_2802", "ready_stock")


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


def run(name: str, seed: int, stage: str) -> dict:
    opponent = Path(f"opponents/{name}/main.py")
    target = OUT / f"{stage}_vs_{name}.json"
    subprocess.run([sys.executable, "scripts/eval.py", str(CANDIDATE), str(opponent),
                    "-n", "5", "-j", "4", "--seed-start", str(seed),
                    "--json", str(target)], cwd=ROOT, check=True)
    return json.loads(target.read_text(encoding="utf-8-sig"))


def row(name: str, result: dict, baseline: dict) -> dict:
    return {"name": name,
            "v23": {key: result[key] for key in
                    ("wins", "losses", "draws", "pair_diff_mean", "pair_diff_stderr")},
            "v22": baseline,
            "exceptions_a": result["exceptions"]["a"],
            "exceptions_b": result["exceptions"]["b"],
            "animals_lost": result["health"]["a"]["animals_lost"]}


def main() -> int:
    top_rows = []
    total = len(TOP) + len(REG)
    status("running", stage="top", total=total, completed=0, current=None, results=[])
    for index, name in enumerate(TOP, 1):
        status("running", stage="top", total=total, completed=index - 1,
               current=name, results=top_rows)
        result = run(name, 601, "top")
        baseline_raw = json.loads((ROOT / f"data/eval/v22_top_public_round8/vs_{name}_smoke.json").read_text(encoding="utf-8-sig"))
        top_rows.append(row(name, result, {key: baseline_raw[key] for key in
                                          ("wins", "losses", "draws", "pair_diff_mean", "pair_diff_stderr")}))
    top_pass = (sum(r["v23"]["wins"] for r in top_rows) > sum(r["v22"]["wins"] for r in top_rows)
                and not any(r["exceptions_a"] or r["animals_lost"] for r in top_rows))
    write(OUT / "top_gate.json", {"passed": top_pass, "results": top_rows})
    if not top_pass:
        status("complete", stage="top_rejected", total=total, completed=len(TOP),
               current=None, top_passed=False, results=top_rows)
        return 2

    reg_rows = []
    for offset, name in enumerate(REG, 1):
        completed = len(TOP) + offset - 1
        status("running", stage="regression", total=total, completed=completed,
               current=name, top_results=top_rows, results=reg_rows)
        baseline_raw = json.loads((ROOT / f"data/eval/v22_antiv52_brunchguard_regression/vs_{name}.json").read_text(encoding="utf-8-sig"))
        seed = int(baseline_raw["matches_detail"][0]["seed"])
        result = run(name, seed, "regression")
        reg_rows.append(row(name, result, first_five(baseline_raw)))
    regression_pass = not any(
        r["v23"]["wins"] < r["v22"]["wins"] or r["v23"]["losses"] > r["v22"]["losses"]
        or r["exceptions_a"] or r["animals_lost"] for r in reg_rows)
    summary = {"top_passed": top_pass, "regression_passed": regression_pass,
               "top_results": top_rows, "regression_results": reg_rows}
    write(OUT / "summary.json", summary)
    status("complete", stage="done", total=total, completed=total, current=None,
           top_passed=top_pass, regression_passed=regression_pass,
           top_results=top_rows, results=reg_rows, summary=str(OUT / "summary.json"))
    return 0 if regression_pass else 3


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
