#!/usr/bin/env python3
"""Aggregate Kaggriculture paired H2H shard JSON files."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path


def percentile(xs, q):
    if not xs:
        return None
    s = sorted(xs)
    pos = (len(s) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return s[lo]
    f = pos - lo
    return s[lo] * (1 - f) + s[hi] * f


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True)
    p.add_argument("--candidate", required=True)
    p.add_argument("--baseline", required=True)
    p.add_argument("--seed-start", type=int, required=True)
    p.add_argument("--seed-count", type=int, required=True)
    p.add_argument("--json-out", default="h2h_summary.json")
    p.add_argument("--md-out", default="h2h_summary.md")
    args = p.parse_args()

    rows = []
    for path in sorted(Path(args.input_dir).rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, list) and data and "candidate_minus_baseline" in data[0]:
            rows.extend(data)

    rows.sort(key=lambda r: r["seed"])
    diffs = [float(r["candidate_minus_baseline"]) for r in rows]
    runtime = [x for r in rows for x in r.get("candidate_runtime_ms", [])]
    n = len(diffs)
    mean = statistics.mean(diffs) if diffs else 0.0
    se = statistics.stdev(diffs) / math.sqrt(n) if n > 1 else 0.0
    summary = {
        "candidate": args.candidate,
        "baseline": args.baseline,
        "metric": "candidate_minus_baseline",
        "seed_start": args.seed_start,
        "seed_count_requested": args.seed_count,
        "pairs_completed": n,
        "games_completed": 2 * n,
        "wins": sum(d > 0 for d in diffs),
        "losses": sum(d < 0 for d in diffs),
        "draws": sum(d == 0 for d in diffs),
        "mean": mean,
        "median": statistics.median(diffs) if diffs else 0.0,
        "stderr": se,
        "mean_minus_2se": mean - 2 * se,
        "min": min(diffs) if diffs else 0.0,
        "max": max(diffs) if diffs else 0.0,
        "failed_pairs": sum(not r.get("ok", False) for r in rows),
        "candidate_exceptions": sum(int(r.get("candidate_exceptions", 0)) for r in rows),
        "runtime_ms": {
            "callbacks": len(runtime),
            "median": statistics.median(runtime) if runtime else None,
            "p95": percentile(runtime, 0.95),
            "p99": percentile(runtime, 0.99),
            "max": max(runtime) if runtime else None,
        },
        "rows": rows,
    }
    Path(args.json_out).write_text(json.dumps(summary, indent=2), encoding="utf-8")

    rt = summary["runtime_ms"]
    md = f"""# Kaggriculture H2H

- candidate: `{args.candidate}`
- baseline: `{args.baseline}`
- metric: `candidate_minus_baseline`
- seeds: `{args.seed_start}..{args.seed_start + args.seed_count - 1}`
- pairs: **{n}** / requested {args.seed_count}
- games: **{2*n}**
- W/L/D: **{summary['wins']}/{summary['losses']}/{summary['draws']}**
- mean: **{mean:+.3f}**
- median: **{summary['median']:+.3f}**
- stderr: **{se:.3f}**
- mean - 2SE: **{summary['mean_minus_2se']:+.3f}**
- min / max: **{summary['min']:+.3f} / {summary['max']:+.3f}**
- failed pairs: **{summary['failed_pairs']}**
- candidate exceptions: **{summary['candidate_exceptions']}**
- runtime callbacks: **{rt['callbacks']}**
- runtime median / p95 / p99 / max ms: **{rt['median']} / {rt['p95']} / {rt['p99']} / {rt['max']}**

`candidate_minus_baseline` is the average candidate score margin across the two seat-swapped games.
"""
    Path(args.md_out).write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
