from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from kaggle_environments import make
from scripts.preflight import call_like_kaggle, load_like_kaggle


def extract_money(env, seat: int) -> float:
    candidates = [
        env.state[seat].get("observation"),
        env.steps[-1][seat].get("observation") if env.steps else None,
    ]
    for obs in candidates:
        if not isinstance(obs, dict):
            continue
        farms = obs.get("farms")
        if isinstance(farms, list) and len(farms) > seat and isinstance(farms[seat], dict):
            for key in ("money", "cash"):
                if key in farms[seat]:
                    return float(farms[seat][key])
    return float(env.state[seat].get("reward") or 0.0)


def load_runner(spec: str, errors: list[str]):
    if spec == "starter":
        return "starter"
    agent = load_like_kaggle(Path(spec))

    def wrapped(obs, config=None):
        try:
            return call_like_kaggle(agent, obs, config)
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            return {"farmer": ["PASS"], "hands": [], "market": []}

    return wrapped


def run_game(subject: str, opponent: str, seed: int, subject_seat: int) -> dict:
    subject_errors: list[str] = []
    opponent_errors: list[str] = []
    s = load_runner(subject, subject_errors)
    o = load_runner(opponent, opponent_errors)
    agents = [s, o] if subject_seat == 0 else [o, s]
    env = make("kaggriculture", configuration={"seed": seed})
    env.run(agents)
    opp_seat = 1 - subject_seat
    sm = extract_money(env, subject_seat)
    om = extract_money(env, opp_seat)
    return {
        "seed": seed,
        "subject_seat": subject_seat,
        "subject_money": sm,
        "opponent_money": om,
        "margin": sm - om,
        "subject_errors": subject_errors,
        "opponent_errors": opponent_errors,
        "statuses": [x.get("status") for x in env.state],
    }


def mean(xs):
    return statistics.mean(xs) if xs else 0.0


def outcome(v: float) -> str:
    return "W" if v > 0 else "L" if v < 0 else "D"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", required=True)
    p.add_argument("--champion", required=True)
    p.add_argument("--seed-start", type=int, default=621)
    p.add_argument("--seed-count", type=int, default=4)
    p.add_argument("--opponent", action="append", default=[], help="label=path or label=starter")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    opponents = []
    for raw in args.opponent:
        label, spec = raw.split("=", 1)
        if spec != "starter" and not Path(spec).exists():
            opponents.append({"label": label, "spec": spec, "status": "missing"})
        else:
            opponents.append({"label": label, "spec": spec, "status": "ready"})

    payload = {
        "metric": "candidate_minus_champion = candidate final money - champion final money, same opponent/seed/seat; seed value is the mean across both seats",
        "candidate": args.candidate,
        "champion": args.champion,
        "seed_start": args.seed_start,
        "seed_count": args.seed_count,
        "opponents": [],
    }

    for opp in opponents:
        if opp["status"] != "ready":
            payload["opponents"].append({**opp, "rows": []})
            print(f"SKIP missing opponent {opp['label']}: {opp['spec']}")
            continue

        rows = []
        for seed in range(args.seed_start, args.seed_start + args.seed_count):
            seats = []
            for seat in (0, 1):
                c = run_game(args.candidate, opp["spec"], seed, seat)
                h = run_game(args.champion, opp["spec"], seed, seat)
                seats.append({
                    "seat": seat,
                    "candidate": c,
                    "champion": h,
                    "candidate_minus_champion_money": c["subject_money"] - h["subject_money"],
                    "candidate_minus_champion_margin": c["margin"] - h["margin"],
                })
            pair_delta = mean([x["candidate_minus_champion_money"] for x in seats])
            pair_margin_delta = mean([x["candidate_minus_champion_margin"] for x in seats])
            cand_pair_margin = mean([x["candidate"]["margin"] for x in seats])
            champ_pair_margin = mean([x["champion"]["margin"] for x in seats])
            rows.append({
                "seed": seed,
                "candidate_minus_champion_money": pair_delta,
                "candidate_minus_champion_margin": pair_margin_delta,
                "candidate_pair_margin": cand_pair_margin,
                "champion_pair_margin": champ_pair_margin,
                "candidate_pair_result_vs_opponent": outcome(cand_pair_margin),
                "champion_pair_result_vs_opponent": outcome(champ_pair_margin),
                "seats": seats,
            })

        ds = [r["candidate_minus_champion_money"] for r in rows]
        md = [r["candidate_minus_champion_margin"] for r in rows]
        candidate_errors = sum(len(s["candidate"]["subject_errors"]) for r in rows for s in r["seats"])
        champion_errors = sum(len(s["champion"]["subject_errors"]) for r in rows for s in r["seats"])
        opponent_errors = sum(
            len(s["candidate"]["opponent_errors"]) + len(s["champion"]["opponent_errors"])
            for r in rows for s in r["seats"]
        )
        non_done = sum(
            any(x != "DONE" for x in s[side]["statuses"])
            for r in rows for s in r["seats"] for side in ("candidate", "champion")
        )
        result = {
            "label": opp["label"],
            "spec": opp["spec"],
            "status": "completed",
            "candidate_minus_champion_wld": {
                k: sum(outcome(v) == k for v in ds) for k in ("W", "L", "D")
            },
            "candidate_minus_champion_mean_money": mean(ds),
            "candidate_minus_champion_median_money": statistics.median(ds) if ds else 0.0,
            "candidate_minus_champion_worst_money": min(ds) if ds else 0.0,
            "candidate_minus_champion_best_money": max(ds) if ds else 0.0,
            "candidate_minus_champion_mean_margin": mean(md),
            "candidate_pair_wld_vs_opponent": {
                k: sum(r["candidate_pair_result_vs_opponent"] == k for r in rows) for k in ("W", "L", "D")
            },
            "champion_pair_wld_vs_opponent": {
                k: sum(r["champion_pair_result_vs_opponent"] == k for r in rows) for k in ("W", "L", "D")
            },
            "candidate_exceptions": candidate_errors,
            "champion_exceptions": champion_errors,
            "opponent_exceptions_across_both_subject_runs": opponent_errors,
            "non_done_subject_runs": non_done,
            "rows": rows,
        }
        payload["opponents"].append(result)
        print("PANEL", json.dumps({k: v for k, v in result.items() if k != "rows"}, ensure_ascii=False))

    completed = [x for x in payload["opponents"] if x.get("status") == "completed"]
    payload["summary"] = {
        "completed_opponents": len(completed),
        "missing_opponents": [x["label"] for x in payload["opponents"] if x.get("status") == "missing"],
        "mean_of_opponent_means_money": mean([x["candidate_minus_champion_mean_money"] for x in completed]),
        "opponents_positive_mean": sum(x["candidate_minus_champion_mean_money"] > 0 for x in completed),
        "opponents_negative_mean": sum(x["candidate_minus_champion_mean_money"] < 0 for x in completed),
        "opponents_zero_mean": sum(x["candidate_minus_champion_mean_money"] == 0 for x in completed),
        "worst_opponent_mean_money": min((x["candidate_minus_champion_mean_money"] for x in completed), default=0.0),
        "worst_single_seed_money": min((x["candidate_minus_champion_worst_money"] for x in completed), default=0.0),
        "candidate_exceptions": sum(x["candidate_exceptions"] for x in completed),
        "champion_exceptions": sum(x["champion_exceptions"] for x in completed),
        "opponent_exceptions": sum(x["opponent_exceptions_across_both_subject_runs"] for x in completed),
        "non_done_subject_runs": sum(x["non_done_subject_runs"] for x in completed),
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("SUMMARY", json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
