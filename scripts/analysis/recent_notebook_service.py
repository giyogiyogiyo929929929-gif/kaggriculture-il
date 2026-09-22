# -*- coding: utf-8 -*-
"""Kaggriculture の recently run 公開ノートを安全に抽出し既存 eval.py で対戦する。

仕様: docs/experiments/EXP-20260922-53-recent-notebook-automation.md
公開ノートのセルは実行しない。既存の静的抽出・監査を通過した Python だけを
preflight と対戦へ進める。
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import audit_agent


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
from background_log import append_event

DEFAULT_DATA = ROOT / "data" / "automation" / "recent_notebooks"
DEFAULT_CANDIDATE = ROOT / "submissions" / "v27_orderbook_layer_d" / "main.py"
TERMINAL_STATES = {"stopped", "fatal", "complete"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat(timespec="seconds")


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def parse_kernel_list(text: str) -> list[dict[str, Any]]:
    """Kaggle CLI のJSON配列（将来のラッパー形式も含む）を読む。"""
    starts = [p for p in (text.find("["), text.find("{")) if p >= 0]
    if not starts:
        raise ValueError("Kaggle CLI output does not contain JSON")
    payload = json.loads(text[min(starts):])
    if isinstance(payload, dict):
        payload = payload.get("kernels", payload.get("data", []))
    if not isinstance(payload, list):
        raise ValueError("Kaggle CLI JSON is not a list")
    return [item for item in payload if isinstance(item, dict) and item.get("ref")]


def version_key(kernel: dict[str, Any]) -> str:
    stamp = str(kernel.get("lastRunTime") or kernel.get("dateRun") or "unknown")
    return f"{kernel['ref']}@{stamp}"


def safe_name(value: str, limit: int = 120) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return (cleaned or "unknown")[:limit]


def run_command(command: list[str], cwd: Path, log_path: Path) -> subprocess.CompletedProcess[str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.write_text(completed.stdout or "", encoding="utf-8")
    return completed


def query_recent(page_size: int, log_path: Path) -> list[dict[str, Any]]:
    command = [
        sys.executable, "-m", "kaggle", "kernels", "list",
        "--competition", "kaggriculture", "--sort-by", "dateRun",
        "--page-size", str(page_size), "--format", "json",
    ]
    result = run_command(command, ROOT, log_path)
    if result.returncode:
        raise RuntimeError(f"kernels list failed ({result.returncode})")
    return parse_kernel_list(result.stdout)


def strict_static_audit(path: Path) -> list[tuple[Any, ...]]:
    """既存監査を使い、構文エラーも拒否する。警告の自動例外化はしない。"""
    code = path.read_text(encoding="utf-8")
    ast.parse(code)
    return audit_agent.audit_file(str(path))


class Monitor:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.started_at = iso_now()

    def write(self, state: str, **fields: Any) -> None:
        value = {
            "state": state,
            "pid": os.getpid(),
            "started_at": self.started_at,
            "updated_at": iso_now(),
            **fields,
        }
        atomic_json(self.path, value)


def initial_state() -> dict[str, Any]:
    return {"schema": 1, "seen": {}, "hashes": {}, "last_cycle": None}


def mark_record(state: dict[str, Any], key: str, record: dict[str, Any]) -> None:
    state.setdefault("seen", {})[key] = record


def process_kernel(
    kernel: dict[str, Any], state: dict[str, Any], data_dir: Path,
    candidate: Path, pairs: int, monitor: Monitor,
) -> dict[str, Any]:
    key = version_key(kernel)
    ref = str(kernel["ref"])
    version = safe_name(str(kernel.get("lastRunTime") or "unknown"))
    artifact = data_dir / "artifacts" / safe_name(ref.replace("/", "__")) / version
    raw_parent = artifact / "raw"
    pull_dir = raw_parent / "notebook"
    extracted = artifact / "extracted"
    logs = artifact / "logs"
    results = artifact / "results"
    for directory in (pull_dir, extracted, logs, results):
        directory.mkdir(parents=True, exist_ok=True)

    record: dict[str, Any] = {
        "ref": ref,
        "title": kernel.get("title"),
        "author": kernel.get("author"),
        "lastRunTime": kernel.get("lastRunTime"),
        "totalVotes": kernel.get("totalVotes"),
        "discovered_at": iso_now(),
        "status": "pulling",
        "artifact": str(artifact.relative_to(ROOT)),
    }
    mark_record(state, key, record)
    monitor.write("processing", current=key, stage="pull")

    pulled = run_command(
        [sys.executable, "-m", "kaggle", "kernels", "pull", ref,
         "-p", str(pull_dir), "--metadata"], ROOT, logs / "pull.log",
    )
    if pulled.returncode:
        record.update(status="pull_failed", finished_at=iso_now())
        return record

    monitor.write("processing", current=key, stage="extract")
    extraction = run_command(
        [sys.executable, str(ROOT / "scripts" / "analysis" / "extract_notebook_agents.py"),
         str(raw_parent), str(extracted)], ROOT, logs / "extract.log",
    )
    agents = sorted(extracted.glob("*.py"))
    if extraction.returncode or len(agents) != 1:
        record.update(status="extract_failed", extracted_count=len(agents), finished_at=iso_now())
        return record

    agent = agents[0]
    digest = hashlib.sha256(agent.read_bytes()).hexdigest()
    record["sha256"] = digest
    if digest in state.setdefault("hashes", {}):
        record.update(
            status="duplicate",
            duplicate_of=state["hashes"][digest],
            finished_at=iso_now(),
        )
        return record

    monitor.write("processing", current=key, stage="static_audit")
    try:
        problems = strict_static_audit(agent)
    except (OSError, UnicodeError, SyntaxError) as exc:
        (logs / "audit.log").write_text(repr(exc), encoding="utf-8")
        record.update(status="audit_failed", audit_error=repr(exc), finished_at=iso_now())
        return record
    (logs / "audit.log").write_text(
        json.dumps(problems, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if problems:
        record.update(status="quarantined", audit_warnings=len(problems), finished_at=iso_now())
        return record

    monitor.write("processing", current=key, stage="preflight")
    preflight_json = results / "preflight.json"
    preflight = run_command(
        [sys.executable, str(ROOT / "scripts" / "preflight.py"),
         "--main", str(agent), "--episode-steps", "20", "--json", str(preflight_json)],
        ROOT, logs / "preflight.log",
    )
    if preflight.returncode:
        record.update(status="preflight_failed", finished_at=iso_now())
        return record

    monitor.write("processing", current=key, stage="evaluation")
    eval_json = results / "vs_candidate.json"
    seed_start = int(digest[:8], 16) % 1_000_000 + 1
    evaluation = run_command(
        [sys.executable, str(ROOT / "scripts" / "eval.py"), str(candidate), str(agent),
         "-n", str(pairs), "-j", "1", "--seed-start", str(seed_start),
         "--json", str(eval_json)], ROOT, logs / "evaluation.log",
    )
    if evaluation.returncode:
        record.update(status="evaluation_failed", finished_at=iso_now())
        return record

    summary = load_json(eval_json, {})
    record.update(
        status="evaluated",
        result=str(eval_json.relative_to(ROOT)),
        wins=summary.get("wins"), losses=summary.get("losses"), draws=summary.get("draws"),
        pair_diff_mean=summary.get("pair_diff_mean"),
        finished_at=iso_now(),
    )
    state["hashes"][digest] = key
    return record


def run_cycle(args: argparse.Namespace, state: dict[str, Any], monitor: Monitor) -> int:
    cycle_started = iso_now()
    monitor.write("querying", cycle_started_at=cycle_started)
    try:
        kernels = query_recent(args.page_size, args.data_dir / "logs" / "kernels-list.log")
    except Exception as exc:
        monitor.write("cycle_error", error=repr(exc), cycle_started_at=cycle_started)
        state["last_cycle"] = {"started_at": cycle_started, "error": repr(exc)}
        atomic_json(args.state_file, state)
        return 1

    unseen = [item for item in kernels if version_key(item) not in state.get("seen", {})]
    first_run = not state.get("seen")
    if first_run and not args.evaluate_existing:
        for item in kernels:
            mark_record(state, version_key(item), {
                "ref": item["ref"], "title": item.get("title"),
                "lastRunTime": item.get("lastRunTime"), "status": "baseline",
                "discovered_at": iso_now(),
            })
        state["last_cycle"] = {
            "started_at": cycle_started, "finished_at": iso_now(),
            "listed": len(kernels), "new": 0, "baselined": len(kernels),
        }
        atomic_json(args.state_file, state)
        monitor.write("cycle_complete", **state["last_cycle"])
        return 0

    counts: dict[str, int] = {}
    for item in reversed(unseen):
        record = process_kernel(item, state, args.data_dir, args.candidate, args.pairs, monitor)
        counts[record["status"]] = counts.get(record["status"], 0) + 1
        atomic_json(args.state_file, state)

    state["last_cycle"] = {
        "started_at": cycle_started, "finished_at": iso_now(),
        "listed": len(kernels), "new": len(unseen), "outcomes": counts,
    }
    atomic_json(args.state_file, state)
    monitor.write("cycle_complete", **state["last_cycle"])
    return 0


def acquire_lock(path: Path):
    """Windowsの非ブロッキング1バイトロック。プロセス終了時にOSが解放する。"""
    import msvcrt
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+b")
    handle.seek(0)
    if path.stat().st_size == 0:
        handle.write(b"0")
        handle.flush()
        handle.seek(0)
    try:
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        handle.close()
        raise RuntimeError("recent notebook service is already running")
    return handle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="recently run 公開ノートの自動対戦")
    parser.add_argument("--interval-seconds", type=int, default=3600)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--pairs", type=int, default=3)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--evaluate-existing", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.data_dir = args.data_dir.resolve()
    args.candidate = args.candidate.resolve()
    args.state_file = args.data_dir / "state.json"
    args.data_dir.mkdir(parents=True, exist_ok=True)
    if not args.candidate.exists():
        raise SystemExit(f"candidate not found: {args.candidate}")
    monitor = Monitor(args.data_dir / "monitor.json")
    lock = None if args.once else acquire_lock(args.data_dir / "runner.lock")
    state = load_json(args.state_file, initial_state())
    try:
        while True:
            cycle_at = time.monotonic()
            code = run_cycle(args, state, monitor)
            if args.once:
                monitor.write("complete", exit_code=code, last_cycle=state.get("last_cycle"))
                return code
            next_at = utc_now() + timedelta(seconds=max(60, args.interval_seconds))
            monitor.write(
                "sleeping", next_poll_at=next_at.isoformat(timespec="seconds"),
                last_cycle=state.get("last_cycle"),
            )
            remaining = max(60, args.interval_seconds - (time.monotonic() - cycle_at))
            stop_file = args.data_dir / "STOP"
            while remaining > 0 and not stop_file.exists():
                chunk = min(60, remaining)
                time.sleep(chunk)
                remaining -= chunk
            if stop_file.exists():
                monitor.write("stopped", reason=f"stop file: {stop_file}")
                append_event(
                    "STOPPED", "Kaggriculture 公開ノート自動対戦 runner", os.getpid(),
                    "STOPファイルを検出",
                )
                return 0
    except BaseException as exc:
        monitor.write("fatal", error=repr(exc))
        if not args.once:
            append_event(
                "FAILED", "Kaggriculture 公開ノート自動対戦 runner", os.getpid(), repr(exc),
            )
        raise
    finally:
        if lock is not None:
            lock.close()


if __name__ == "__main__":
    raise SystemExit(main())
