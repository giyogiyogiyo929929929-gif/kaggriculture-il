from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval import evaluate


def _stderr(values: list[float]) -> float:
    return statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else 0.0


def _by_seed(summary: dict) -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = {}
    for game in summary["matches_detail"]:
        out.setdefault(int(game["seed"]), []).append(game)
    return out


def _paired_seed_metrics(summary: dict, seed: int) -> dict:
    games = sorted(_by_seed(summary)[seed], key=lambda g: bool(g["swap"]))
    margins = [float(g["money"][0]) - float(g["money"][1]) for g in games]
    own_money = [float(g["money"][0]) for g in games]
    opp_money = [float(g["money"][1]) for g in games]
    return {
        "pair_margin": statistics.mean(margins),
        "own_money": statistics.mean(own_money),
        "opponent_money": statistics.mean(opp_money),
        "seats": [
            {
                "swap": bool(g["swap"]),
                "own_money": float(g["money"][0]),
                "opponent_money": float(g["money"][1]),
                "margin": float(g["money"][0]) - float(g["money"][1]),
            }
            for g in games
        ],
    }


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

    rows = []
    margin_deltas: list[float] = []
    own_deltas: list[float] = []
    opp_deltas: list[float] = []
    seat_margin_deltas = {False: [], True: []}
    wins = losses = ties = 0

    for seed in range(args.seed_start, args.seed_start + args.seed_count):
        c = _paired_seed_metrics(cand, seed)
        h = _paired_seed_metrics(champ, seed)
        margin_delta = c["pair_margin"] - h["pair_margin"]
        own_delta = c["own_money"] - h["own_money"]
        opp_delta = c["opponent_money"] - h["opponent_money"]
        margin_deltas.append(margin_delta)
        own_deltas.append(own_delta)
        opp_deltas.append(opp_delta)
        if margin_delta > 0:
            wins += 1
        elif margin_delta < 0:
            losses += 1
        else:
            ties += 1

        seats = []
        c_seats = {bool(x["swap"]): x for x in c["seats"]}
        h_seats = {bool(x["swap"]): x for x in h["seats"]}
        for swap in (False, True):
            cs = c_seats[swap]
            hs = h_seats[swap]
            smd = cs["margin"] - hs["margin"]
            seat_margin_deltas[swap].append(smd)
            seats.append({
                "swap": swap,
                "candidate_margin": cs["margin"],
                "champion_margin": hs["margin"],
                "candidate_minus_champion_margin": smd,
                "candidate_own_money": cs["own_money"],
                "champion_own_money": hs["own_money"],
                "candidate_minus_champion_own_money": cs["own_money"] - hs["own_money"],
                "candidate_opponent_money": cs["opponent_money"],
                "champion_opponent_money": hs["opponent_money"],
            })
        rows.append({
            "seed": seed,
            "candidate_minus_champion_margin": margin_delta,
            "candidate_minus_champion_own_money": own_delta,
            "candidate_minus_champion_opponent_money": opp_delta,
            "seats": seats,
        })

    mean = statistics.mean(margin_deltas) if margin_deltas else 0.0
    se = _stderr(margin_deltas)
    out = {
        "metric_primary": "candidate_minus_champion = (candidate margin vs opponent) - (champion margin vs same opponent), each seed averaged across both seats",
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
        "worst": min(margin_deltas) if margin_deltas else 0.0,
        "best": max(margin_deltas) if margin_deltas else 0.0,
        "seat0_margin_delta_mean": statistics.mean(seat_margin_deltas[False]) if seat_margin_deltas[False] else 0.0,
        "seat1_margin_delta_mean": statistics.mean(seat_margin_deltas[True]) if seat_margin_deltas[True] else 0.0,
        "own_money_delta_mean": statistics.mean(own_deltas) if own_deltas else 0.0,
        "opponent_money_delta_mean": statistics.mean(opp_deltas) if opp_deltas else 0.0,
        "candidate_exceptions": int(cand["exceptions"]["a"]),
        "champion_exceptions": int(champ["exceptions"]["a"]),
        "rows": rows,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
