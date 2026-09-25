from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from scripts.eval import evaluate


def game_map(summary: dict) -> dict[tuple[int, bool], dict]:
    return {(int(g["seed"]), bool(g["swap"])): g for g in summary["matches_detail"]}


def stderr(values: list[float]) -> float:
    return statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0.0


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", required=True)
    p.add_argument("--champion", required=True)
    p.add_argument("--opponent", required=True)
    p.add_argument("--seed-start", type=int, required=True)
    p.add_argument("--seed-count", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--jobs", type=int, default=4)
    args = p.parse_args()

    cand = evaluate(args.candidate, args.opponent, pairs=args.seed_count, jobs=args.jobs, seed_start=args.seed_start)
    champ = evaluate(args.champion, args.opponent, pairs=args.seed_count, jobs=args.jobs, seed_start=args.seed_start)
    cm, hm = game_map(cand), game_map(champ)

    rows = []
    seat_deltas = {False: [], True: []}
    seed_deltas = []
    margin_deltas = []
    wins = losses = ties = 0
    for seed in range(args.seed_start, args.seed_start + args.seed_count):
        seat_rows = []
        for swap in (False, True):
            c = cm[(seed, swap)]
            h = hm[(seed, swap)]
            c_money = float(c["money"][0])
            h_money = float(h["money"][0])
            c_margin = float(c["money"][0]) - float(c["money"][1])
            h_margin = float(h["money"][0]) - float(h["money"][1])
            money_delta = c_money - h_money
            margin_delta = c_margin - h_margin
            seat_deltas[swap].append(money_delta)
            seat_rows.append({
                "swap": swap,
                "candidate_money": c_money,
                "champion_money": h_money,
                "candidate_minus_champion_money": money_delta,
                "candidate_margin": c_margin,
                "champion_margin": h_margin,
                "candidate_minus_champion_margin": margin_delta,
            })
        money_delta = statistics.mean(r["candidate_minus_champion_money"] for r in seat_rows)
        margin_delta = statistics.mean(r["candidate_minus_champion_margin"] for r in seat_rows)
        seed_deltas.append(money_delta)
        margin_deltas.append(margin_delta)
        if money_delta > 0: wins += 1
        elif money_delta < 0: losses += 1
        else: ties += 1
        rows.append({
            "seed": seed,
            "candidate_minus_champion_money": money_delta,
            "candidate_minus_champion_margin": margin_delta,
            "seats": seat_rows,
        })

    mean = statistics.mean(seed_deltas) if seed_deltas else 0.0
    se = stderr(seed_deltas)
    out = {
        "metric_primary": "candidate_minus_champion_money = candidate money - champion money, averaged across both seats against the same opponent and seed",
        "candidate": args.candidate,
        "champion": args.champion,
        "opponent": args.opponent,
        "seed_start": args.seed_start,
        "seed_count": args.seed_count,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "candidate_minus_champion_mean": mean,
        "candidate_minus_champion_se": se,
        "mean_ge_2se": bool(mean > 0 and mean >= 2 * se),
        "worst": min(seed_deltas) if seed_deltas else 0.0,
        "best": max(seed_deltas) if seed_deltas else 0.0,
        "seat0_mean": statistics.mean(seat_deltas[False]) if seat_deltas[False] else 0.0,
        "seat1_mean": statistics.mean(seat_deltas[True]) if seat_deltas[True] else 0.0,
        "margin_delta_mean": statistics.mean(margin_deltas) if margin_deltas else 0.0,
        "candidate_exceptions": int(cand["exceptions"]["a"]),
        "champion_exceptions": int(champ["exceptions"]["a"]),
        "rows": rows,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
