"""Start one hidden round-robin runner with an independent terminal watcher."""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

from background_log import append_event
from start_recent_notebook_service import spawn

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/automation/round_robin_20260923"
SITE_PACKAGES = ROOT / ".venv" / "Lib" / "site-packages"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replace", action="store_true", help="stop the logged prior runner/watch before resuming")
    args = parser.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    monitor_path = DATA / "monitor.json"
    if monitor_path.exists():
        old = json.loads(monitor_path.read_text(encoding="utf-8"))
        if old.get("state") in {"launching", "running", "processing", "sleeping"}:
            if not args.replace:
                raise SystemExit(f"Existing tournament active: pid={old.get('pid')}")
            launch = json.loads((DATA / "launch.json").read_text(encoding="utf-8"))
            if old.get("pid") != launch.get("runner_pid"):
                raise SystemExit("Runner PID does not match launch record")
            for label, pid in (("runner", launch["runner_pid"]),
                               ("watcher", launch["watcher_pid"])):
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                append_event("STOPPED", f"Kaggriculture round robin {label}", pid,
                             "controlled restart for dynamic enrollment")
    if SITE_PACKAGES.is_dir():
        os.environ["PYTHONPATH"] = str(SITE_PACKAGES) + os.pathsep + os.environ.get("PYTHONPATH", "")
    runner = spawn([sys.executable, str(ROOT / "scripts/analysis/round_robin.py")],
                   DATA / "runner.log", DATA / "runner.err.log")
    monitor_path.write_text(json.dumps({"state": "launching", "pid": runner.pid,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}, indent=2), encoding="utf-8")
    watcher = spawn([sys.executable, str(ROOT / "scripts/analysis/watch_recent_notebook_service.py"),
                     "--data-dir", str(DATA), "--name", "Kaggriculture round robin watcher"],
                    DATA / "watcher.log", DATA / "watcher.err.log")
    append_event("STARTED", "Kaggriculture round robin runner", runner.pid)
    append_event("STARTED", "Kaggriculture round robin watcher", watcher.pid,
                 f"runner_pid={runner.pid}")
    launch = {"started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "runner_pid": runner.pid, "watcher_pid": watcher.pid, "python": sys.executable}
    (DATA / "launch.json").write_text(json.dumps(launch, indent=2), encoding="utf-8")
    print(json.dumps(launch, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
