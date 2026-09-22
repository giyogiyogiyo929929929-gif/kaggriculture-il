# -*- coding: utf-8 -*-
"""v19の集中ゲートを実行し、合格時だけ21相手回帰へ自動継続する。"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = Path("submissions/v19_antiv52_actualsales/main.py")
OUT = ROOT / "data" / "eval" / "v19_antiv52_actualsales"
REG = ROOT / "data" / "eval" / "v19_antiv52_actualsales_regression"
BASELINE = ROOT / "data" / "eval" / "v16_antiv52_regression"


def evaluate(name: str, seed: int, target: Path) -> dict:
    target.parent.mkdir(parents=True, exist_ok=True)
    opponent = ("submissions/v12_v51safe/main.py" if name == "v12"
                else f"opponents/{name}/main.py")
    command = [sys.executable, "scripts/eval.py", str(CANDIDATE),
               opponent, "-n", "10", "-j", "4",
               "--seed-start", str(seed), "--json", str(target)]
    print(f"\n=== {name} (seed {seed}-) ===", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)
    return json.loads(target.read_text(encoding="utf-8"))


def main() -> int:
    focused = {}
    for name, seed in (("v52", 501), ("v49", 241), ("v50", 241)):
        target = OUT / f"vs_{name}.json"
        focused[name] = (json.loads(target.read_text(encoding="utf-8-sig"))
                         if target.exists() else evaluate(name, seed, target))
    gate = (focused["v52"]["wins"] >= 8 and focused["v52"]["losses"] <= 1
            and focused["v52"]["pair_diff_mean"] > 0
            and all(focused[name]["wins"] == 10 and focused[name]["losses"] == 0
                    for name in ("v49", "v50")))
    (OUT / "gate.json").write_text(
        json.dumps({"passed": gate,
                    "results": {name: {key: result[key] for key in
                                ("wins", "losses", "draws", "pair_diff_mean", "pair_diff_stderr")}
                                for name, result in focused.items()}},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== focused gate: {'PASS' if gate else 'FAIL'} ===", flush=True)
    if not gate:
        return 2

    REG.mkdir(parents=True, exist_ok=True)
    for name in ("v49", "v50"):
        shutil.copy2(OUT / f"vs_{name}.json", REG / f"vs_{name}.json")
    baseline_summary = json.loads((BASELINE / "summary.json").read_text(encoding="utf-8-sig"))
    rows = []
    for base in baseline_summary["results"]:
        name = base["name"]
        target = REG / f"vs_{name}.json"
        baseline_detail = json.loads(
            (BASELINE / f"vs_{name}.json").read_text(encoding="utf-8-sig"))
        seed_start = int(baseline_detail["matches_detail"][0]["seed"])
        if name in focused:
            result = focused[name]
        elif target.exists():
            result = json.loads(target.read_text(encoding="utf-8-sig"))
        else:
            result = evaluate(name, seed_start, target)
        rows.append({"name": name, "wins": result["wins"], "losses": result["losses"],
                     "draws": result["draws"], "pair_diff_mean": result["pair_diff_mean"],
                     "pair_diff_stderr": result["pair_diff_stderr"],
                     "baseline_wins": base["baseline_wins"],
                     "baseline_losses": base["baseline_losses"],
                     "baseline_draws": base["baseline_draws"],
                     "baseline_pair_diff_mean": base["baseline_pair_diff_mean"],
                     "win_regression": (result["wins"] < base["baseline_wins"] or
                                        result["losses"] > base["baseline_losses"]),
                     "mean_delta": result["pair_diff_mean"] - base["baseline_pair_diff_mean"],
                     "exceptions_a": result["exceptions"]["a"],
                     "exceptions_b": result["exceptions"]["b"],
                     "animals_lost": result["health"]["a"]["animals_lost"]})
    summary = {"results": rows,
               "passed": not any(row["win_regression"] or row["exceptions_a"]
                                 or row["animals_lost"] for row in rows)}
    (REG / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== regression gate: {'PASS' if summary['passed'] else 'FAIL'} ===", flush=True)
    return 0 if summary["passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
