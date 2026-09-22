# -*- coding: utf-8 -*-
"""v22直近敗戦を主要公開版へ絞ってfingerprint照合する。

仕様: docs/experiments/EXP-20260922-49-v22-public-score-analysis.md
"""
from __future__ import annotations

import json
from datetime import datetime

import _common as C

ROOT = C.ROOT
SOURCE = ROOT / "data/analysis/v22_recent_opponents/matches.json"
OUT = ROOT / "data/analysis/v22_loss_fingerprint"
MONITOR = ROOT / "data/analysis/v22_loss_fingerprint.monitor.json"
MINE = ROOT / "submissions/v22_antiv52_brunchguard/main.py"
CANDIDATES = {
    "v49": ROOT / "opponents/v49/main.py",
    "v52": ROOT / "opponents/v52/main.py",
    "v53": ROOT / "opponents/v53/main.py",
    "v54": ROOT / "data/public_round8_extracted/kaggriculture-v54-productive-wheat-and-patient.py",
    "v56": ROOT / "data/public_round9_extracted/kaggriculture-v56-smarter-seeds-and-fertilizer.py",
    "more_wheat": ROOT / "data/public_round9_extracted/kaggriculture-more-wheat-smarter-sales.py",
    "pipe16": ROOT / "opponents/pipe16/main.py",
    "pipe18": ROOT / "opponents/pipe18/main.py",
    "story": ROOT / "opponents/story_of_seasons/main.py",
    "jaxa": ROOT / "opponents/jaxa_2802/main.py",
}
COPY_SET = ("v52", "v53", "v54", "v56", "more_wheat", "pipe16", "pipe18", "story")
NONCOPY_SET = ("v49", "v54", "v56", "more_wheat", "pipe18", "story", "jaxa")


def write(path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(MONITOR, {"state": state, "updated": datetime.now().isoformat(), **extra})


def main() -> int:
    targets = [row for row in json.loads(SOURCE.read_text(encoding="utf-8"))
               if row["result"] == "loss"]
    loaded_mine = C.load(MINE)
    loaded = {name: C.load(path) for name, path in CANDIDATES.items()}
    total = sum(len(COPY_SET if row["physical_copy_167"] else NONCOPY_SET) for row in targets)
    completed, results = 0, []
    status("running", total=total, completed=0, current=None, results=[])
    for target in targets:
        names = COPY_SET if target["physical_copy_167"] else NONCOPY_SET
        found, trials = [], []
        expected = tuple(target["money"])
        for name in names:
            status("running", total=total, completed=completed,
                   current={"opponent": target["opponent"], "candidate": name}, results=results)
            try:
                env = C.play(loaded_mine, loaded[name], int(target["seed"]),
                             swap=int(target["me_seat"]) == 1)
                got = (env.state[int(target["me_seat"])] ["reward"],
                       env.state[1 - int(target["me_seat"])] ["reward"])
                exact = got == expected
                trials.append({"candidate": name, "money": got, "exact": exact})
                if exact:
                    found.append(name)
            except Exception as error:
                trials.append({"candidate": name, "error": repr(error)})
            completed += 1
        results.append({"episode": target["episode"], "opponent": target["opponent"],
                        "physical_copy_167": target["physical_copy_167"],
                        "exact_matches": found, "trials": trials})
        write(OUT / "results.partial.json", results)
    write(OUT / "results.json", results)
    status("complete", total=total, completed=total, current=None, results=results,
           output=str(OUT / "results.json"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        status("failed", error=repr(error))
        raise
