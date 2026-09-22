# -*- coding: utf-8 -*-
"""v22エージェント分布解析runnerと独立watcherを非表示起動する。"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from background_log import append_event


ROOT = Path(__file__).resolve().parents[1]
MONITOR = ROOT / "data/analysis/v22_agent_landscape.monitor.json"
CONFIRM = ROOT / "data/analysis/v22_agent_landscape.watcher.json"


def spawn(command: list[str], output: Path, error: Path) -> subprocess.Popen:
    flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS if os.name == "nt" else 0
    output.parent.mkdir(parents=True, exist_ok=True)
    out = output.open("w", encoding="utf-8")
    err = error.open("w", encoding="utf-8")
    try:
        return subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                creationflags=flags, close_fds=True)
    finally:
        out.close()
        err.close()


def main() -> int:
    runner_name = "v22 リプレイ・エージェント分布解析 runner"
    watcher_name = "v22 リプレイ・エージェント分布解析 watcher"
    runner = spawn(
        [sys.executable, str(ROOT / "scripts/analysis/run_v22_agent_landscape.py")],
        ROOT / "data/analysis/v22_agent_landscape.runner.log",
        ROOT / "data/analysis/v22_agent_landscape.runner.err.log",
    )
    watcher = spawn(
        [sys.executable, str(ROOT / "scripts/watch_monitor.py"), str(MONITOR), str(CONFIRM),
         "--name", watcher_name, "--runner-pid", str(runner.pid)],
        ROOT / "data/analysis/v22_agent_landscape.watcher.log",
        ROOT / "data/analysis/v22_agent_landscape.watcher.err.log",
    )
    append_event("STARTED", runner_name, runner.pid, "latest_public_replays=24")
    append_event("STARTED", watcher_name, watcher.pid, f"runner_pid={runner.pid}")
    print(f"runner pid: {runner.pid}\nwatcher pid: {watcher.pid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
