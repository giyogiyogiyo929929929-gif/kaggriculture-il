# -*- coding: utf-8 -*-
"""pipe18をv12本番seedと代表パネルへ逐次評価する。

仕様: docs/experiments/EXP-20260922-48-pipe18-six-layers.md
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/eval/pipe18_integration"
STATUS = ROOT / "data/eval/pipe18_integration.monitor.json"
V12 = "submissions/v12_v51safe/main.py"
V25 = "submissions/v25_e402_e410/main.py"
PIPE18 = "opponents/pipe18/main.py"

PANELS = [
    ("v25_vs_pipe18", V25, PIPE18, 10, 1201),
    ("pipe18_vs_v56", PIPE18, "data/public_round9_extracted/kaggriculture-v56-smarter-seeds-and-fertilizer.py", 10, 1201),
    ("pipe18_vs_jaxa", PIPE18, "opponents/jaxa_2802/main.py", 5, 241),
    ("pipe18_vs_v49", PIPE18, "opponents/v49/main.py", 5, 241),
    ("pipe18_vs_story", PIPE18, "opponents/story_of_seasons/main.py", 5, 301),
    ("pipe18_vs_more_wheat", PIPE18, "data/public_round9_extracted/kaggriculture-more-wheat-smarter-sales.py", 5, 901),
]


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def fingerprint() -> list[dict]:
    sys.path.insert(0, str(ROOT / "scripts/analysis"))
    import _common as common

    matches = json.loads((ROOT / "data/analysis/v12_recent_opponents/matches.json").read_text(encoding="utf-8"))
    targets = [row for row in matches if "YARN_STORE" in row["shops"][:2]]
    rows = []
    for index, row in enumerate(targets, 1):
        status("running", phase="fingerprint", total=len(targets) + len(PANELS),
               completed=index - 1, current=f"fingerprint:{row['opponent']}", results=rows)
        env = common.play(V12, PIPE18, int(row["seed"]), swap=int(row["me_seat"]) == 1)
        seat_order = [float(x) for x in common.rewards(env)]
        me = int(row["me_seat"])
        actual = [seat_order[me], seat_order[1 - me]]
        expected = [float(x) for x in row["money"]]
        rows.append({
            "opponent": row["opponent"], "episode": row["episode"], "seed": row["seed"],
            "v12_seat": me, "expected_money_v12_first": expected,
            "actual_money_v12_first": actual, "actual_money_seat_order": seat_order,
            "exact_money_match": actual == expected,
        })
    write(OUT / "fingerprint.json", {"results": rows})
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fingerprints = fingerprint()
    summaries = []
    base_completed = len(fingerprints)
    for index, (name, agent_a, agent_b, pairs, seed) in enumerate(PANELS, 1):
        status("running", phase="panel", total=base_completed + len(PANELS),
               completed=base_completed + index - 1, current=name,
               fingerprints=fingerprints, results=summaries)
        output = OUT / f"{name}.json"
        command = [sys.executable, "scripts/eval.py", agent_a, agent_b, "-n", str(pairs),
                   "-j", "1", "--seed-start", str(seed), "--json", str(output)]
        process = subprocess.run(command, cwd=ROOT, check=True, capture_output=True,
                                 text=True, encoding="utf-8")
        result = json.loads(output.read_text(encoding="utf-8"))
        summaries.append({
            "name": name, "wins": result["wins"], "losses": result["losses"],
            "draws": result["draws"], "pair_diff_mean": result["pair_diff_mean"],
            "pair_diff_stderr": result["pair_diff_stderr"],
            "exceptions": result["exceptions"],
            "animals_lost": {"a": result["health"]["a"]["animals_lost"],
                             "b": result["health"]["b"]["animals_lost"]},
            "output": str(output.relative_to(ROOT)), "log": process.stdout.strip(),
        })
    summary = {"fingerprints": fingerprints, "panels": summaries}
    write(OUT / "summary.json", summary)
    status("complete", phase="done", total=base_completed + len(PANELS),
           completed=base_completed + len(PANELS), current=None,
           fingerprints=fingerprints, results=summaries,
           summary=str((OUT / "summary.json").relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
