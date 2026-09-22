# -*- coding: utf-8 -*-
"""バックグラウンド処理の起動・停止を共通ログへ追記する。AGENTS.md §4。"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG = ROOT / "data" / "automation" / "background-processes.log"
JST = timezone(timedelta(hours=9), "JST")


def append_event(
    event: str, name: str, pid: int, detail: str = "", log_path: Path = DEFAULT_LOG,
) -> str:
    """1イベントをJST・1行形式で追記する。複数プロセス間はロックで直列化する。"""
    event = event.upper().strip()
    timestamp = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S JST")
    suffix = f" | {detail.strip()}" if detail.strip() else ""
    line = f"{timestamp} | {event} | {name.strip()} | pid: {int(pid)}{suffix}\n"
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = log_path.with_suffix(log_path.suffix + ".lock")
    if os.name == "nt":
        import msvcrt
        with lock_path.open("a+b") as lock:
            lock.seek(0)
            if lock_path.stat().st_size == 0:
                lock.write(b"0")
                lock.flush()
                lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
            try:
                with log_path.open("a", encoding="utf-8") as output:
                    output.write(line)
            finally:
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        with log_path.open("a", encoding="utf-8") as output:
            output.write(line)
    return line.rstrip("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="バックグラウンド処理の共通履歴へ1行追記")
    parser.add_argument("event")
    parser.add_argument("name")
    parser.add_argument("pid", type=int)
    parser.add_argument("--detail", default="")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    args = parser.parse_args()
    print(append_event(args.event, args.name, args.pid, args.detail, args.log))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
