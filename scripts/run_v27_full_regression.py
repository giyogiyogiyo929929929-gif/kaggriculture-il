# -*- coding: utf-8 -*-
"""既存v25の18相手結果を再利用し、v27側だけを同一seedで順次回帰する。"""
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

import run_v26_r148_panel as panel

ROOT = panel.ROOT
OUT = ROOT / "data/eval/v27_full_regression"
STATUS = ROOT / "data/eval/v27_full_regression.monitor.json"
CANDIDATE = "submissions/v27_orderbook_layer_d/main.py"

TASKS = []
for name in ("smaller_market_shock", "v47", "master_v3", "wonderful_life", "pipe16", "dz_more_wheat"):
    TASKS.append((name, f"opponents/{name}/main.py",
                  f"data/eval/v25_full_regression/vs_{name}.json"))
for name in ("v49", "v50", "metav4_v13", "k256_h2_q_v1", "market_rhythm",
             "story_of_seasons", "thomas_router_93", "tetsutani_dpts_b", "jaxa_2802", "ready_stock"):
    TASKS.append((name, f"opponents/{name}/main.py",
                  f"data/eval/v25_full_regression/vs_{name}.json"))
TASKS += [
    ("more_wheat_latest", "data/public_round9_extracted/kaggriculture-more-wheat-smarter-sales.py",
     "data/eval/v25_full_regression/vs_more_wheat_latest.json"),
    ("v56", "data/public_round9_extracted/kaggriculture-v56-smarter-seeds-and-fertilizer.py",
     "data/eval/v25_full_regression/vs_v56.json"),
]


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def summary_from_detail(raw: dict) -> dict:
    differences = []
    for index in range(0, 10, 2):
        pair = raw["matches_detail"][index:index + 2]
        differences.append(sum(float(match["money"][0]) - float(match["money"][1])
                               for match in pair) / 2)
    return {
        "wins": sum(value > 0 for value in differences),
        "losses": sum(value < 0 for value in differences),
        "draws": sum(value == 0 for value in differences),
        "pair_diff_mean": statistics.mean(differences),
        "pair_diff_stderr": statistics.stdev(differences) / len(differences) ** 0.5,
        # Top-level health is a representative/aggregate field whose older
        # saved files may not equal the sum of per-match losses. The gate is
        # defined over every evaluated match, so derive it from detail rows.
        "animals_lost": sum(int(match["health"]["a"]["animals_lost"])
                            for match in raw["matches_detail"][:10]),
        "exceptions_a": raw["exceptions"]["a"],
    }


def summarize_saved() -> int:
    """Rebuild the final gate from saved matches without rerunning games."""
    rows = []
    for name, _opponent, baseline_path in TASKS:
        raw = json.loads((ROOT / baseline_path).read_text(encoding="utf-8-sig"))
        saved = json.loads((OUT / f"vs_{name}.json").read_text(encoding="utf-8"))
        candidate = saved["comparison"]["v27"]
        baseline = summary_from_detail(raw)
        rows.append({
            "name": name,
            "seed_start": int(raw["matches_detail"][0]["seed"]),
            "v25": baseline,
            "v27": candidate,
            "win_delta": candidate["wins"] - baseline["wins"],
            "mean_delta": candidate["pair_diff_mean"] - baseline["pair_diff_mean"],
        })
    passed = not any(row["win_delta"] < 0 or row["v27"]["exceptions_a"]
                     or row["v27"]["animals_lost"] > row["v25"]["animals_lost"]
                     for row in rows)
    write(OUT / "summary.json", {"passed": passed, "results": rows})
    status("complete", total=len(TASKS), completed=len(TASKS), current=None,
           passed=passed, results=rows, summary=str(OUT / "summary.json"))
    return 0 if passed else 2


def main() -> int:
    rows = []
    status("running", total=len(TASKS), completed=0, current=None, results=[])
    for index, (name, opponent, baseline_path) in enumerate(TASKS, 1):
        raw = json.loads((ROOT / baseline_path).read_text(encoding="utf-8-sig"))
        baseline = summary_from_detail(raw)
        seed = int(raw["matches_detail"][0]["seed"])
        status("running", total=len(TASKS), completed=index - 1, current=name, results=rows)
        candidate, matches = panel.run_set(CANDIDATE, opponent, seed)
        row = {
            "name": name,
            "seed_start": seed,
            "v25": baseline,
            "v27": candidate,
            "win_delta": candidate["wins"] - baseline["wins"],
            "mean_delta": candidate["pair_diff_mean"] - baseline["pair_diff_mean"],
        }
        write(OUT / f"vs_{name}.json", {"comparison": row, "matches": matches})
        rows.append(row)
        status("running", total=len(TASKS), completed=index, current=None, results=rows)
    passed = not any(row["win_delta"] < 0 or row["v27"]["exceptions_a"]
                     or row["v27"]["animals_lost"] > row["v25"]["animals_lost"]
                     for row in rows)
    write(OUT / "summary.json", {"passed": passed, "results": rows})
    status("complete", total=len(TASKS), completed=len(TASKS), current=None,
           passed=passed, results=rows, summary=str(OUT / "summary.json"))
    return 0 if passed else 2


if __name__ == "__main__":
    try:
        raise SystemExit(summarize_saved() if "--summarize-only" in sys.argv else main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
