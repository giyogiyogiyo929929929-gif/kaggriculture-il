# -*- coding: utf-8 -*-
"""V56のE402/E410をv22上で分離し、直戦後に小型安全性パネルを回す。"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/eval/v24_v25_isolation"
STATUS = ROOT / "data/eval/v24_v25_isolation.monitor.json"
V22 = Path("submissions/v22_antiv52_brunchguard/main.py")
V24 = Path("submissions/v24_e402_seed_cap/main.py")
V25 = Path("submissions/v25_e402_e410/main.py")

TASKS = [
    ("v24_vs_v22", V24, V22, 10, 1001),
    ("v25_vs_v22", V25, V22, 10, 1001),
    ("v25_vs_v24", V25, V24, 10, 1001),
    ("v24_vs_jaxa", V24, Path("opponents/jaxa_2802/main.py"), 5, 241),
    ("v25_vs_jaxa", V25, Path("opponents/jaxa_2802/main.py"), 5, 241),
    ("v24_vs_v49", V24, Path("opponents/v49/main.py"), 5, 241),
    ("v25_vs_v49", V25, Path("opponents/v49/main.py"), 5, 241),
    ("v24_vs_v52", V24, Path("opponents/v52/main.py"), 5, 851),
    ("v25_vs_v52", V25, Path("opponents/v52/main.py"), 5, 851),
]


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def status(state: str, **extra) -> None:
    write(STATUS, {"state": state, "updated": datetime.now().isoformat(), **extra})


def main() -> int:
    rows = []
    status("running", total=len(TASKS), completed=0, current=None, results=[])
    for index, (name, candidate, opponent, pairs, seed) in enumerate(TASKS, 1):
        status("running", total=len(TASKS), completed=index - 1, current=name, results=rows)
        target = OUT / f"{name}.json"
        subprocess.run(
            [sys.executable, "scripts/eval.py", str(candidate), str(opponent),
             "-n", str(pairs), "-j", "4", "--seed-start", str(seed), "--json", str(target)],
            cwd=ROOT, check=True,
        )
        result = json.loads(target.read_text(encoding="utf-8-sig"))
        rows.append({
            "name": name,
            **{key: result[key] for key in
               ("pairs", "wins", "losses", "draws", "pair_diff_mean", "pair_diff_stderr")},
            "exceptions_a": result["exceptions"]["a"],
            "exceptions_b": result["exceptions"]["b"],
            "animals_lost": result["health"]["a"]["animals_lost"],
        })
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
