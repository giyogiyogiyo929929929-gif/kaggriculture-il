#!/usr/bin/env python3
"""Official Kaggriculture 1.32.7 paired evaluator for CI.

Each pair runs two independent official env.run() episodes with seats swapped.
`candidate_minus_baseline` is the average of the candidate's score margin across
the two seats, matching the project's established paired-diff convention.

The PyPI 1.32.7 environment omits observation.step for seat 1. The wrapper below
only restores that intended field from a per-agent call counter; game dynamics
remain entirely inside kaggle_environments 1.32.7.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EXPECTED_VERSION = "1.32.7"
BUILTINS = {"starter", "random", "pass"}


def _resolve(spec: str) -> str:
    if spec in BUILTINS:
        return spec
    p = Path(spec)
    if p.is_dir():
        p = p / "main.py"
    if not p.is_file():
        raise FileNotFoundError(f"agent not found: {spec}")
    return str(p)


def _load_wrapped(spec: str, timing: dict):
    if spec in BUILTINS:
        return spec
    from kaggle_environments.agent import get_last_callable

    path = _resolve(spec)
    raw = Path(path).read_text(encoding="utf-8")
    fn = get_last_callable(raw, path=path)
    call_index = 0

    def wrapped(obs, config=None):
        nonlocal call_index
        if obs.get("step") is None:
            obs["step"] = call_index
        call_index += 1
        t0 = time.perf_counter()
        try:
            return fn(obs, config)
        except Exception:
            timing["exceptions"] += 1
            raise
        finally:
            timing["durations_ms"].append((time.perf_counter() - t0) * 1000.0)

    return wrapped


def _single_game(a: str, b: str, seed: int) -> dict:
    import kaggle_environments
    from kaggle_environments import make

    if kaggle_environments.__version__ != EXPECTED_VERSION:
        raise RuntimeError(
            f"kaggle_environments={kaggle_environments.__version__}, expected {EXPECTED_VERSION}"
        )

    ma = {"durations_ms": [], "exceptions": 0}
    mb = {"durations_ms": [], "exceptions": 0}
    aa = _load_wrapped(_resolve(a), ma)
    bb = _load_wrapped(_resolve(b), mb)
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": int(seed)},
        debug=False,
    )
    env.run([aa, bb])
    final = env.steps[-1]
    rewards = [float(final[i].reward or 0.0) for i in range(2)]
    statuses = [str(final[i].status) for i in range(2)]
    return {
        "seed": int(seed),
        "rewards": rewards,
        "statuses": statuses,
        "timing": [ma, mb],
    }


def _run_isolated(a: str, b: str, seed: int) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name
    try:
        cmd = [
            sys.executable,
            __file__,
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
        cp = subprocess.run(cmd, text=True, capture_output=True)
        if cp.returncode != 0:
            return {
                "seed": seed,
                "rewards": [0.0, 0.0],
                "statuses": ["RUN-EXC", "RUN-EXC"],
                "timing": [
                    {"durations_ms": [], "exceptions": 1},
                    {"durations_ms": [], "exceptions": 1},
                ],
                "runner_error": (cp.stderr or cp.stdout)[-4000:],
            }
        return json.loads(Path(out).read_text(encoding="utf-8"))
    finally:
        try:
            os.unlink(out)
        except OSError:
            pass


def _pair(candidate: str, baseline: str, seed: int) -> dict:
    normal = _run_isolated(candidate, baseline, seed)
    swapped = _run_isolated(baseline, candidate, seed)

    # candidate is seat 0 in normal, seat 1 in swapped.
    n_margin = normal["rewards"][0] - normal["rewards"][1]
    s_margin = swapped["rewards"][1] - swapped["rewards"][0]
    diff = (n_margin + s_margin) / 2.0

    cand_t = normal["timing"][0]["durations_ms"] + swapped["timing"][1]["durations_ms"]
    cand_exc = normal["timing"][0]["exceptions"] + swapped["timing"][1]["exceptions"]
    ok = (
        normal["statuses"] == ["DONE", "DONE"]
        and swapped["statuses"] == ["DONE", "DONE"]
        and cand_exc == 0
        and "runner_error" not in normal
        and "runner_error" not in swapped
    )
    return {
        "seed": seed,
        "candidate_minus_baseline": diff,
        "normal": normal,
        "swapped": swapped,
        "candidate_runtime_ms": cand_t,
        "candidate_exceptions": cand_exc,
        "ok": ok,
    }


def _main_shard(args) -> int:
    seeds = [
        args.seed_start + i
        for i in range(args.seed_count)
        if i % args.shard_count == args.shard_index
    ]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in seeds:
        row = _pair(args.candidate, args.baseline, seed)
        rows.append(row)
        print(
            f"seed={seed} candidate_minus_baseline="
            f"{row['candidate_minus_baseline']:+.3f} ok={row['ok']}",
            flush=True,
        )
    Path(args.out).write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return 0 if all(r["ok"] for r in rows) else 2


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--candidate")
    p.add_argument("--baseline")
    p.add_argument("--seed-start", type=int)
    p.add_argument("--seed-count", type=int)
    p.add_argument("--shard-index", type=int, default=0)
    p.add_argument("--shard-count", type=int, default=1)
    p.add_argument("--out", required=True)
    p.add_argument("--single-game", action="store_true")
    p.add_argument("--a")
    p.add_argument("--b")
    p.add_argument("--seed", type=int)
    args = p.parse_args()

    if args.single_game:
        result = _single_game(args.a, args.b, args.seed)
        Path(args.out).write_text(json.dumps(result), encoding="utf-8")
        return 0
    if not all(v is not None for v in (args.candidate, args.baseline, args.seed_start, args.seed_count)):
        p.error("paired mode requires --candidate --baseline --seed-start --seed-count")
    return _main_shard(args)


if __name__ == "__main__":
    raise SystemExit(main())
