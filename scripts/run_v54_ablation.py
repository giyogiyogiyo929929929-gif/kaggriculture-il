# -*- coding: utf-8 -*-
"""v54追加層を同一seedで比較し、終了状態を記録する。

仕様: docs/experiments/EXP-20260922-40-v54-layer-ablation.md
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = Path("submissions/v22_antiv52_brunchguard/main.py")
OUT = ROOT / "data" / "eval" / "v54_layer_ablation"
STATUS = ROOT / "data" / "eval" / "v54_layer_ablation.monitor.json"
LAYERS = [
    ("opening", Path("data/public_round8_ablation/v54_opening.py")),
    ("mature", Path("data/public_round8_ablation/v54_mature.py")),
]


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def status(state: str, **extra) -> None:
    write_json(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def compact(name: str, result: dict) -> dict:
    return {"name": name, **{key: result[key] for key in
            ("wins", "losses", "draws", "pair_diff_mean", "pair_diff_stderr")},
            "exceptions_a": result["exceptions"]["a"],
            "exceptions_b": result["exceptions"]["b"],
            "animals_lost": result["health"]["a"]["animals_lost"]}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    status("running", total=len(LAYERS), completed=0, current=None, results=[])
    for index, (name, opponent) in enumerate(LAYERS, 1):
        status("running", total=len(LAYERS), completed=index - 1, current=name, results=rows)
        target = OUT / f"vs_{name}.json"
        command = [sys.executable, "scripts/eval.py", str(CANDIDATE), str(opponent),
                   "-n", "10", "-j", "4", "--seed-start", "701", "--json", str(target)]
        subprocess.run(command, cwd=ROOT, check=True)
        result = json.loads(target.read_text(encoding="utf-8-sig"))
        rows.append(compact(name, result))
        status("running", total=len(LAYERS), completed=index, current=None, results=rows)
    final = json.loads((ROOT / "data/eval/v22_top_public_round8/vs_v54_confirm.json").read_text(encoding="utf-8-sig"))
    rows.append(compact("guard_final", final))
    summary = {"candidate": str(CANDIDATE), "seed_start": 701, "pairs": 10, "results": rows}
    write_json(OUT / "summary.json", summary)
    status("complete", total=len(LAYERS), completed=len(LAYERS), current=None,
           results=rows, summary=str(OUT / "summary.json"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
