from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics
import time
from pathlib import Path

import kaggle_environments
from kaggle_environments import make


def load_agent(path: str, tag: str):
    spec = importlib.util.spec_from_file_location(tag, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.agent


def game(candidate: str, champion: str, seed: int, swap: bool):
    ca = load_agent(candidate, f"candidate_{seed}_{swap}_{time.time_ns()}")
    ch = load_agent(champion, f"champion_{seed}_{swap}_{time.time_ns()}")
    env = make("kaggriculture", configuration={"seed": int(seed)}, debug=False)
    if swap:
        env.run([ch, ca])
        rewards = [float(env.state[i].reward) for i in range(2)]
        return rewards[1], rewards[0]
    env.run([ca, ch])
    rewards = [float(env.state[i].reward) for i in range(2)]
    return rewards[0], rewards[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--champion", required=True)
    ap.add_argument("--seed-start", type=int, required=True)
    ap.add_argument("--pairs", type=int, required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    version = getattr(kaggle_environments, "__version__", None)
    if version != "1.32.7":
        raise SystemExit(f"wrong kaggle_environments version: {version}")

    rows = []
    deltas = []
    exception_pairs = 0
    for seed in range(args.seed_start, args.seed_start + args.pairs):
        runs = []
        try:
            c1, h1 = game(args.candidate, args.champion, seed, False)
            c2, h2 = game(args.candidate, args.champion, seed, True)
            delta = ((c1 - h1) + (c2 - h2)) / 2.0
            runs = [[c1, h1], [c2, h2]]
            deltas.append(delta)
            rows.append({
                "seed": seed,
                "candidate_minus_champion": delta,
                "runs_candidate_champion": runs,
                "exception": None,
            })
            print(json.dumps(rows[-1]), flush=True)
        except Exception as exc:
            exception_pairs += 1
            rows.append({
                "seed": seed,
                "candidate_minus_champion": None,
                "runs_candidate_champion": runs,
                "exception": repr(exc),
            })
            print(json.dumps(rows[-1]), flush=True)

    if not deltas:
        raise SystemExit("no successful pairs")
    mean = statistics.mean(deltas)
    median = statistics.median(deltas)
    stderr = statistics.stdev(deltas) / math.sqrt(len(deltas)) if len(deltas) > 1 else 0.0
    result = {
        "engine": "kaggle_environments",
        "engine_version": version,
        "candidate": args.candidate,
        "champion": args.champion,
        "seed_start": args.seed_start,
        "pairs_requested": args.pairs,
        "pairs_successful": len(deltas),
        "exceptions": exception_pairs,
        "wins": sum(d > 0 for d in deltas),
        "losses": sum(d < 0 for d in deltas),
        "draws": sum(d == 0 for d in deltas),
        "candidate_minus_champion_mean": mean,
        "candidate_minus_champion_median": median,
        "candidate_minus_champion_stderr": stderr,
        "candidate_minus_champion_mean_minus_2stderr": mean - 2 * stderr,
        "candidate_minus_champion_min": min(deltas),
        "candidate_minus_champion_max": max(deltas),
        "candidate_minus_champion": deltas,
        "rows": rows,
    }
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("SUMMARY=" + json.dumps({k: result[k] for k in [
        "engine_version", "wins", "losses", "draws", "exceptions",
        "candidate_minus_champion_mean", "candidate_minus_champion_median",
        "candidate_minus_champion_stderr", "candidate_minus_champion_mean_minus_2stderr",
        "candidate_minus_champion_min", "candidate_minus_champion_max"
    ]}), flush=True)


if __name__ == "__main__":
    main()
