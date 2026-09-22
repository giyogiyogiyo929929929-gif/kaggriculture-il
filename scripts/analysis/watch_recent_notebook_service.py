# -*- coding: utf-8 -*-
"""recent_notebook_service の独立ヘルス監視。仕様: EXP-20260922-53。"""
from __future__ import annotations

import argparse
import json
import os
import time
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
from background_log import append_event


TERMINAL = {"stopped", "fatal", "complete"}


def now() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def health(monitor: dict, grace_seconds: int) -> tuple[str, str]:
    state = str(monitor.get("state", "missing"))
    if state in TERMINAL:
        return "runner_terminal", state
    current = now()
    if state == "sleeping":
        deadline = parse_time(monitor.get("next_poll_at"))
        if deadline and current <= deadline + timedelta(seconds=grace_seconds):
            return "healthy", state
    updated = parse_time(monitor.get("updated_at"))
    if updated and current <= updated + timedelta(seconds=grace_seconds):
        return "healthy", state
    return "stale", state


def main() -> int:
    parser = argparse.ArgumentParser(description="recent notebook runner watcher")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--check-seconds", type=int, default=60)
    parser.add_argument("--grace-seconds", type=int, default=1200)
    args = parser.parse_args()
    monitor_path = args.data_dir / "monitor.json"
    output = args.data_dir / "watcher.json"
    launched = time.monotonic()
    while True:
        try:
            monitor = json.loads(monitor_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            monitor = {}
        watcher_state, runner_state = health(monitor, args.grace_seconds)
        if not monitor and time.monotonic() - launched <= args.grace_seconds:
            watcher_state, runner_state = "starting", "missing"
        atomic_json(output, {
            "state": watcher_state,
            "runner_state": runner_state,
            "runner_pid": monitor.get("pid"),
            "checked_at": now().isoformat(timespec="seconds"),
            "monitor": str(monitor_path),
        })
        if watcher_state in {"runner_terminal", "stale"}:
            event = "STOPPED" if watcher_state == "runner_terminal" else "FAILED"
            append_event(
                event, "Kaggriculture 公開ノート自動対戦 watcher", os.getpid(),
                f"runner_pid={monitor.get('pid')} runner_state={runner_state}",
            )
            return 0 if watcher_state == "runner_terminal" else 1
        time.sleep(max(10, args.check_seconds))


if __name__ == "__main__":
    raise SystemExit(main())
