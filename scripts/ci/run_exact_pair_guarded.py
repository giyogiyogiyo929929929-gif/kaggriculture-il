#!/usr/bin/env python3
"""Timeout-guarded wrapper for scripts/ci/run_exact_pair.py.

This keeps the exact Kaggriculture evaluator unchanged while preventing one
hung isolated game from blocking an entire self-hosted workflow indefinitely.
The paired evaluator already runs every game in a child process; this wrapper
only adds a generous wall-clock timeout around that child process.

Configuration:
    KAGGRICULTURE_SINGLE_GAME_TIMEOUT_SECONDS (default: 180)

A timed-out game is returned as technical failure (RUN-TIMEOUT, ok=False), so
it can never be mistaken for promotion evidence.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "run_exact_pair.py"

spec = importlib.util.spec_from_file_location("_kaggriculture_exact_pair_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load base evaluator: {BASE_PATH}")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

TIMEOUT_SECONDS = float(os.environ.get("KAGGRICULTURE_SINGLE_GAME_TIMEOUT_SECONDS", "180"))
if TIMEOUT_SECONDS <= 0:
    raise ValueError("KAGGRICULTURE_SINGLE_GAME_TIMEOUT_SECONDS must be > 0")


def _technical_failure(seed: int, status: str, message: str) -> dict:
    return {
        "seed": int(seed),
        "rewards": [0.0, 0.0],
        "statuses": [status, status],
        "timing": [
            {"durations_ms": [], "exceptions": 1},
            {"durations_ms": [], "exceptions": 1},
        ],
        "runner_error": message[-4000:],
    }


def _guarded_run_isolated(a: str, b: str, seed: int) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name
    try:
        cmd = [
            sys.executable,
            str(BASE_PATH),
            "--single-game",
            "--a",
            a,
            "--b",
            b,
            "--seed",
            str(seed),
            "--out",
            out,
        ]
        try:
            cp = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                timeout=TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            detail = (
                f"single game exceeded {TIMEOUT_SECONDS:.1f}s wall timeout; "
                f"seed={seed} a={a} b={b}; stdout={exc.stdout!r}; stderr={exc.stderr!r}"
            )
            return _technical_failure(seed, "RUN-TIMEOUT", detail)

        if cp.returncode != 0:
            return _technical_failure(
                seed,
                "RUN-EXC",
                (cp.stderr or cp.stdout or f"returncode={cp.returncode}"),
            )
        try:
            return json.loads(Path(out).read_text(encoding="utf-8"))
        except Exception as exc:
            return _technical_failure(
                seed,
                "RUN-EXC",
                f"failed to read isolated result: {type(exc).__name__}: {exc}",
            )
    finally:
        try:
            os.unlink(out)
        except OSError:
            pass


# Patch only the isolation boundary. Game dynamics, score calculation, seat swap,
# engine-version check, and candidate_minus_baseline convention remain in base.
base._run_isolated = _guarded_run_isolated


if __name__ == "__main__":
    raise SystemExit(base.main())
