# -*- coding: utf-8 -*-
"""最新v22リプレイ取得→相手分類を1本で実行する。仕様: EXP-20260922-54。"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from background_log import append_event

MONITOR = ROOT / "data/analysis/v22_agent_landscape.monitor.json"
OUT = ROOT / "data/analysis/v22_agent_landscape"
NAME = "v22 リプレイ・エージェント分布解析 runner"


def write(value: dict) -> None:
    MONITOR.parent.mkdir(parents=True, exist_ok=True)
    temp = MONITOR.with_suffix(".json.tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, MONITOR)


def run(script: str, log_name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / log_name).open("w", encoding="utf-8") as log:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/analysis" / script)], cwd=ROOT,
            stdout=log, stderr=subprocess.STDOUT, text=True, encoding="utf-8", check=False,
        )
    if result.returncode:
        raise RuntimeError(f"{script} failed ({result.returncode})")


def main() -> int:
    try:
        write({"state": "running", "updated": datetime.now().isoformat(), "stage": "fetch_analyze",
               "pid": os.getpid()})
        run("v22_recent_opponents.py", "refresh.log")
        write({"state": "running", "updated": datetime.now().isoformat(), "stage": "classify",
               "pid": os.getpid()})
        run("classify_v22_agent_landscape.py", "classify.log")
        write({"state": "complete", "updated": datetime.now().isoformat(), "stage": "done",
               "pid": os.getpid(), "summary": str(OUT / "summary.md")})
        append_event("STOPPED", NAME, os.getpid(), "解析完了")
        return 0
    except BaseException as exc:
        write({"state": "failed", "updated": datetime.now().isoformat(), "pid": os.getpid(),
               "error": repr(exc)})
        append_event("FAILED", NAME, os.getpid(), repr(exc))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
