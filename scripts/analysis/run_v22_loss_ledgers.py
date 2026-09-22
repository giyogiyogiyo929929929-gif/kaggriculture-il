# -*- coding: utf-8 -*-
"""v22直近24戦の敗戦を台帳再生する。

仕様: docs/experiments/EXP-20260922-49-v22-public-score-analysis.md
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATCHES = ROOT / "data/analysis/v22_recent_opponents/matches.json"
RAW = ROOT / "data/raw/own_v22_recent"
OUT = ROOT / "data/analysis/v22_loss_ledgers"
MONITOR = ROOT / "data/analysis/v22_loss_ledgers.monitor.json"


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(MONITOR, {"state": state, "updated": datetime.now().isoformat(), **extra})


def main() -> int:
    rows = json.loads(MATCHES.read_text(encoding="utf-8"))
    targets = [row for row in rows if row["result"] == "loss"]
    OUT.mkdir(parents=True, exist_ok=True)
    completed, outputs = [], []
    status("running", total=len(targets), completed=0, current=None, results=[])
    for index, target in enumerate(targets, 1):
        episode = str(target["episode"])
        replay = next(iter(RAW.glob(f"*{episode}*.json")))
        output = OUT / f"{episode}_{target['opponent'].replace('/', '_')}.pkl"
        status("running", total=len(targets), completed=index - 1,
               current=int(episode), results=completed)
        process = subprocess.run(
            [sys.executable, "scripts/analysis/ledger_replay.py", str(replay), str(output)],
            cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8",
        )
        completed.append({"episode": int(episode), "opponent": target["opponent"],
                          "output": str(output), "check": process.stdout.strip()})
        outputs.append(output)
    report = subprocess.run(
        [sys.executable, "scripts/analysis/ledger_report.py", *map(str, outputs)],
        cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout
    (OUT / "report.txt").write_text(report, encoding="utf-8")
    status("complete", total=len(targets), completed=len(targets), current=None,
           results=completed, report=str(OUT / "report.txt"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
