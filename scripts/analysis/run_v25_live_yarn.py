# -*- coding: utf-8 -*-
"""v25をv12本番の早期YARN同一seed・席で台帳評価する。

仕様: docs/experiments/EXP-20260922-47-v25-live-yarn-seeds.md
"""
from __future__ import annotations

import json
import pickle
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V25 = "submissions/v25_e402_e410/main.py"
OUT = ROOT / "data/analysis/v25_live_yarn"
MONITOR = ROOT / "data/analysis/v25_live_yarn.monitor.json"
BASE = ROOT / "data/analysis/v12_recent_ledgers"
TASKS = [
    ("integ_pipe16", "opponents/pipe16/main.py", 885147097, False,
     BASE / "111717975_姜上（Integ）.pkl"),
    ("fishwg_story", "opponents/story_of_seasons/main.py", 1599345183, True,
     BASE / "111682301_fishwg.pkl"),
    ("irabala_v54", "data/public_round8_extracted/kaggriculture-v54-productive-wheat-and-patient.py", 33032402, True,
     BASE / "111653849_Irabala.pkl"),
    ("mozayed_v52", "opponents/v52/main.py", 683604278, False,
     BASE / "111646413_MoZayed.pkl"),
]


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(MONITOR, {"state": state, "updated": datetime.now().isoformat(), **extra})


def wool(pickle_path: Path) -> dict:
    game = pickle.loads(pickle_path.read_bytes())
    me = int(game["a_seat"])
    values = {me: [], 1 - me: []}
    for _step, seat, op, item, price in game["ledger"]:
        if op == "SELL" and item == "WOOL":
            values[seat].append(float(price))
    result = {}
    for label, seat in (("me", me), ("op", 1 - me)):
        prices = values[seat]
        result[label] = {"units": len(prices), "revenue": sum(prices),
                         "mean_price": sum(prices) / len(prices) if prices else None}
    return result


def game_result(pickle_path: Path) -> dict:
    game = pickle.loads(pickle_path.read_bytes())
    me = int(game["a_seat"])
    mine, rival = float(game["final"][me]), float(game["final"][1 - me])
    return {"money": [mine, rival], "diff": mine - rival,
            "result": "win" if mine > rival else ("loss" if mine < rival else "draw"),
            "wool": wool(pickle_path)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    status("running", total=len(TASKS), completed=0, current=None, results=[])
    for index, (name, opponent, seed, swap, baseline_path) in enumerate(TASKS, 1):
        status("running", total=len(TASKS), completed=index - 1, current=name, results=rows)
        output = OUT / f"{name}.pkl"
        command = [sys.executable, "scripts/analysis/ledger_match.py", V25, opponent,
                   str(seed), str(output)]
        if swap:
            command.append("--swap")
        process = subprocess.run(command, cwd=ROOT, check=True, capture_output=True,
                                 text=True, encoding="utf-8")
        baseline = game_result(baseline_path)
        candidate = game_result(output)
        rows.append({"name": name, "seed": seed, "v25_seat": 1 if swap else 0,
                     "v12": baseline, "v25": candidate,
                     "diff_improvement": candidate["diff"] - baseline["diff"],
                     "check": process.stdout.strip()})
        status("running", total=len(TASKS), completed=index, current=None, results=rows)
    write(OUT / "summary.json", {"results": rows})
    status("complete", total=len(TASKS), completed=len(TASKS), current=None,
           results=rows, summary=str(OUT / "summary.json"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
