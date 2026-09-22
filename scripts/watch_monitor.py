# -*- coding: utf-8 -*-
"""監視JSONがcomplete/failedになるまで軽量に監視し、確認結果を別JSONへ残す。"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from background_log import append_event


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("monitor", type=Path)
    parser.add_argument("confirmation", type=Path)
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--name", default=None)
    parser.add_argument("--runner-pid", type=int, default=None)
    args = parser.parse_args()
    last = None
    while True:
        try:
            value = json.loads(args.monitor.read_text(encoding="utf-8"))
            last = value
            if value.get("state") in {"complete", "failed"}:
                break
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        time.sleep(args.interval)
    result = {
        "state": "observed",
        "observed_at": datetime.now().isoformat(),
        "terminal_state": last.get("state"),
        "monitor": str(args.monitor),
        "monitor_updated": last.get("updated"),
    }
    args.confirmation.parent.mkdir(parents=True, exist_ok=True)
    temp = args.confirmation.with_suffix(args.confirmation.suffix + ".tmp")
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(args.confirmation)
    if args.name:
        event = "STOPPED" if last.get("state") == "complete" else "FAILED"
        append_event(event, args.name, os.getpid(),
                     f"runner_pid={args.runner_pid} terminal_state={last.get('state')}")
    return 0 if last.get("state") == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
