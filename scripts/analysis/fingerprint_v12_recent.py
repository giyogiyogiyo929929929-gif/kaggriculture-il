# -*- coding: utf-8 -*-
"""v12直近戦の早期YARN相手を主要公開版へ絞って指紋照合する。

仕様: docs/experiments/EXP-20260922-46-v12-recent-opponents.md
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import _common as C

ROOT = C.ROOT
SOURCE = ROOT / "data/analysis/v12_recent_opponents/matches.json"
OUT = ROOT / "data/analysis/v12_recent_fingerprint"
MONITOR = ROOT / "data/analysis/v12_recent_fingerprint.monitor.json"
MINE = ROOT / "submissions/v12_v51safe/main.py"
CANDIDATES = {
    "v49": ROOT / "opponents/v49/main.py",
    "v50": ROOT / "opponents/v50/main.py",
    "v51": ROOT / "opponents/v51/main.py",
    "v52": ROOT / "opponents/v52/main.py",
    "v53": ROOT / "opponents/v53/main.py",
    "v54": ROOT / "data/public_round8_extracted/kaggriculture-v54-productive-wheat-and-patient.py",
    "v56": ROOT / "data/public_round9_extracted/kaggriculture-v56-smarter-seeds-and-fertilizer.py",
    "more_wheat_latest": ROOT / "data/public_round9_extracted/kaggriculture-more-wheat-smarter-sales.py",
    "pipe16": ROOT / "opponents/pipe16/main.py",
    "dz_more_wheat_old": ROOT / "opponents/dz_more_wheat/main.py",
    "story_of_seasons": ROOT / "opponents/story_of_seasons/main.py",
    "thomas_router_93": ROOT / "opponents/thomas_router_93/main.py",
    "metav4_v13": ROOT / "opponents/metav4_v13/main.py",
    "v9_4": ROOT / "submissions/thomas_v94_safe/main.py",
}


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(MONITOR, {"state": state, "updated": datetime.now().isoformat(), **extra})


def main() -> int:
    matches = json.loads(SOURCE.read_text(encoding="utf-8"))
    targets = [row for row in matches if "YARN_STORE" in row["shops"][:2]]
    total = len(targets) * len(CANDIDATES)
    completed = 0
    results = []
    status("running", total=total, completed=0, current=None, results=[])
    loaded_mine = C.load(MINE)
    loaded = {name: C.load(path) for name, path in CANDIDATES.items()}
    for target in targets:
        found = []
        trials = []
        expected = tuple(target["money"])
        for name, candidate in loaded.items():
            status("running", total=total, completed=completed,
                   current={"opponent": target["opponent"], "candidate": name}, results=results)
            try:
                env = C.play(loaded_mine, candidate, int(target["seed"]), swap=int(target["me_seat"]) == 1)
                got = (env.state[int(target["me_seat"])]["reward"],
                       env.state[1 - int(target["me_seat"])]["reward"])
                exact = tuple(got) == expected
                trials.append({"candidate": name, "money": got, "exact": exact})
                if exact:
                    found.append(name)
            except Exception as error:
                trials.append({"candidate": name, "error": repr(error)})
            completed += 1
        results.append({"episode": target["episode"], "opponent": target["opponent"],
                        "seed": target["seed"], "me_seat": target["me_seat"],
                        "expected": expected, "exact_matches": found, "trials": trials})
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
