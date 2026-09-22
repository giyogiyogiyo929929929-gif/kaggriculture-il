# -*- coding: utf-8 -*-
"""Order BookとPipe19をv25・異系統代表へ逐次評価する。

仕様: docs/experiments/EXP-20260922-50-orderbook-pipe19.md
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/eval/orderbook_pipe19"
STATUS = ROOT / "data/eval/orderbook_pipe19.monitor.json"
ORDER = "opponents/order_book/main.py"
PIPE19 = "opponents/pipe19/main.py"
V25 = "submissions/v25_e402_e410/main.py"

TASKS = [
    ("order_vs_v25", ORDER, V25, 10, 1501),
    ("pipe19_vs_v25", PIPE19, V25, 10, 1501),
    ("order_vs_pipe19", ORDER, PIPE19, 10, 1501),
    ("pipe19_vs_pipe18", PIPE19, "opponents/pipe18/main.py", 10, 1501),
    ("order_vs_v56", ORDER, "data/public_round9_extracted/kaggriculture-v56-smarter-seeds-and-fertilizer.py", 5, 1501),
    ("order_vs_jaxa", ORDER, "opponents/jaxa_2802/main.py", 5, 241),
    ("pipe19_vs_jaxa", PIPE19, "opponents/jaxa_2802/main.py", 5, 241),
    ("order_vs_v49", ORDER, "opponents/v49/main.py", 5, 241),
    ("pipe19_vs_v49", PIPE19, "opponents/v49/main.py", 5, 241),
    ("order_vs_more_wheat", ORDER, "data/public_round9_extracted/kaggriculture-more-wheat-smarter-sales.py", 5, 901),
    ("pipe19_vs_more_wheat", PIPE19, "data/public_round9_extracted/kaggriculture-more-wheat-smarter-sales.py", 5, 901),
]


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    status("running", total=len(TASKS), completed=0, current=None, results=[])
    for index, (name, a, b, pairs, seed) in enumerate(TASKS, 1):
        status("running", total=len(TASKS), completed=index - 1, current=name, results=results)
        output = OUT / f"{name}.json"
        process = subprocess.run(
            [sys.executable, "scripts/eval.py", a, b, "-n", str(pairs), "-j", "1",
             "--seed-start", str(seed), "--json", str(output)],
            cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8",
        )
        value = json.loads(output.read_text(encoding="utf-8"))
        results.append({
            "name": name, "wins": value["wins"], "losses": value["losses"],
            "draws": value["draws"], "pair_diff_mean": value["pair_diff_mean"],
            "pair_diff_stderr": value["pair_diff_stderr"],
            "exceptions": value["exceptions"],
            "animals_lost": {"a": value["health"]["a"]["animals_lost"],
                             "b": value["health"]["b"]["animals_lost"]},
            "timing_max_ms": {"a": value["timings"]["a"]["max"] * 1000,
                              "b": value["timings"]["b"]["max"] * 1000},
            "output": str(output.relative_to(ROOT)), "log": process.stdout.strip(),
        })
        status("running", total=len(TASKS), completed=index, current=None, results=results)
    write(OUT / "summary.json", {"results": results})
    status("complete", total=len(TASKS), completed=len(TASKS), current=None,
           results=results, summary=str((OUT / "summary.json").relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
