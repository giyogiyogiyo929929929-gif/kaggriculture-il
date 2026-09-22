# -*- coding: utf-8 -*-
"""recent notebook runner と独立 watcher を非表示バックグラウンド起動する。"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from background_log import append_event


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "automation" / "recent_notebooks"


def spawn(command: list[str], stdout_path: Path, stderr_path: Path) -> subprocess.Popen:
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    out = stdout_path.open("a", encoding="utf-8")
    err = stderr_path.open("a", encoding="utf-8")
    try:
        return subprocess.Popen(
            command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
            creationflags=flags, close_fds=True,
        )
    finally:
        out.close()
        err.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="recent notebook service launcher")
    parser.add_argument("--interval-seconds", type=int, default=3600)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--pairs", type=int, default=3)
    parser.add_argument("--candidate", type=Path,
                        default=ROOT / "submissions" / "v27_orderbook_layer_d" / "main.py")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--evaluate-existing", action="store_true")
    args = parser.parse_args()
    data = args.data_dir.resolve()
    stop_file = data / "STOP"
    if stop_file.exists():
        stop_file.unlink()

    runner_command = [
        sys.executable, str(ROOT / "scripts" / "analysis" / "recent_notebook_service.py"),
        "--interval-seconds", str(args.interval_seconds), "--page-size", str(args.page_size),
        "--pairs", str(args.pairs), "--candidate", str(args.candidate.resolve()),
        "--data-dir", str(data),
    ]
    if args.evaluate_existing:
        runner_command.append("--evaluate-existing")
    runner = spawn(runner_command, data / "runner.log", data / "runner.err.log")
    data.mkdir(parents=True, exist_ok=True)
    (data / "monitor.json").write_text(json.dumps({
        "state": "launching",
        "pid": runner.pid,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    watcher = spawn(
        [sys.executable, str(ROOT / "scripts" / "analysis" / "watch_recent_notebook_service.py"),
         "--data-dir", str(data)],
        data / "watcher.log", data / "watcher.err.log",
    )
    append_event(
        "STARTED", "Kaggriculture 公開ノート自動対戦 runner", runner.pid,
        f"interval={args.interval_seconds}s candidate={args.candidate.resolve().name}",
    )
    append_event(
        "STARTED", "Kaggriculture 公開ノート自動対戦 watcher", watcher.pid,
        f"runner_pid={runner.pid}",
    )
    launch = {
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "runner_pid": runner.pid,
        "watcher_pid": watcher.pid,
        "python": sys.executable,
        "data_dir": str(data),
        "runner_command": runner_command,
    }
    (data / "launch.json").write_text(
        json.dumps(launch, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(launch, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
