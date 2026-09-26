from __future__ import annotations

import copy
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

from kaggle_environments import make

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]

CHAMPION = ROOT / "v112_wheat_lead3_lowdemand.py"
CANDIDATE = ROOT / "v117_wheat_post_town_delay1.py"
SEEDS = list(range(299001, 299005))

OPPONENTS = {
    "v49": REPO / "opponents/v49/main.py",
    "v50": REPO / "opponents/v50/main.py",
    "metav4_v13": REPO / "opponents/metav4_v13/main.py",
    "k256_h2_q_v1": REPO / "opponents/k256_h2_q_v1/main.py",
    "market_rhythm": REPO / "opponents/market_rhythm/main.py",
    "story_of_seasons": REPO / "opponents/story_of_seasons/main.py",
    "thomas_router_93": REPO / "opponents/thomas_router_93/main.py",
    "tetsutani_dpts_b": REPO / "opponents/tetsutani_dpts_b/main.py",
    "jaxa_2802": REPO / "opponents/jaxa_2802/main.py",
    "ready_stock": REPO / "opponents/ready_stock/main.py",
}


def load(path: Path, tag: str):
    spec = importlib.util.spec_from_file_location(tag, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[tag] = mod
    spec.loader.exec_module(mod)
    fn = getattr(mod, "agent", None)
    if not callable(fn):
        raise RuntimeError(f"{path} does not expose callable agent")
    return mod, fn


def game(agent_path: Path, opp_path: Path, seed: int, swap: bool):
    tag = f"m_{seed}_{int(swap)}_{time.time_ns()}"
    mod_a, fa = load(agent_path, tag + "_a")
    _, fb = load(opp_path, tag + "_b")
    env = make("kaggriculture", configuration={"seed": int(seed)}, debug=False)
    env.run([fb, fa] if swap else [fa, fb])
    rewards = [float(x.reward) for x in env.state]
    ar, br = (rewards[1], rewards[0]) if swap else (rewards[0], rewards[1])
    return {
        "agent_reward": ar,
        "opponent_reward": br,
        "delta": ar - br,
        "telemetry": copy.deepcopy(getattr(mod_a.agent, "telemetry", {})),
    }


def pair(agent_path: Path, opp_path: Path, seed: int):
    a = game(agent_path, opp_path, seed, False)
    b = game(agent_path, opp_path, seed, True)
    return {
        "seed": seed,
        "pair_diff": (a["delta"] + b["delta"]) / 2.0,
        "games": [a, b],
    }


def sign(x: float) -> int:
    return 1 if x > 0 else -1 if x < 0 else 0


def wld(rows):
    vals = [x["pair_diff"] for x in rows]
    return {
        "wins": sum(v > 0 for v in vals),
        "losses": sum(v < 0 for v in vals),
        "draws": sum(v == 0 for v in vals),
        "mean_pair_diff": statistics.mean(vals) if vals else 0.0,
        "median_pair_diff": statistics.median(vals) if vals else 0.0,
        "worst_pair_diff": min(vals) if vals else 0.0,
        "best_pair_diff": max(vals) if vals else 0.0,
    }


def candidate_telemetry(rows):
    out = {}
    steps = []
    for row in rows:
        for game_row in row["games"]:
            d = (game_row.get("telemetry") or {}).get("wheat_post_town_delay1") or {}
            for k, v in d.items():
                if k == "steps":
                    steps.extend(list(v))
                elif isinstance(v, (int, float)):
                    out[k] = out.get(k, 0) + v
    out["steps"] = steps
    return out


def compare_opponent(name: str, opp_path: Path):
    champ_rows = []
    cand_rows = []
    paired = []

    for seed in SEEDS:
        champ = pair(CHAMPION, opp_path, seed)
        cand = pair(CANDIDATE, opp_path, seed)
        champ_rows.append(champ)
        cand_rows.append(cand)

        c0 = champ["pair_diff"]
        c1 = cand["pair_diff"]
        paired.append(
            {
                "seed": seed,
                "champion_pair_diff": c0,
                "candidate_pair_diff": c1,
                "candidate_minus_champion": c1 - c0,
                "champion_outcome": sign(c0),
                "candidate_outcome": sign(c1),
                "outcome_regression": sign(c1) < sign(c0),
                "outcome_improvement": sign(c1) > sign(c0),
            }
        )
        print(
            name,
            seed,
            "champ", c0,
            "cand", c1,
            "delta", c1 - c0,
            flush=True,
        )

    deltas = [x["candidate_minus_champion"] for x in paired]
    return {
        "opponent": name,
        "path": str(opp_path.relative_to(REPO)),
        "seeds": SEEDS,
        "champion": wld(champ_rows),
        "candidate": wld(cand_rows),
        "candidate_minus_champion": {
            "mean": statistics.mean(deltas),
            "median": statistics.median(deltas),
            "worst": min(deltas),
            "best": max(deltas),
        },
        "outcome_regressions": sum(x["outcome_regression"] for x in paired),
        "outcome_improvements": sum(x["outcome_improvement"] for x in paired),
        "candidate_telemetry": candidate_telemetry(cand_rows),
        "rows": paired,
    }


def main():
    missing = [str(p) for p in [CHAMPION, CANDIDATE, *OPPONENTS.values()] if not p.exists()]
    if missing:
        raise FileNotFoundError("missing evaluation files: " + ", ".join(missing))

    results = [compare_opponent(name, path) for name, path in OPPONENTS.items()]

    all_rows = [row for item in results for row in item["rows"]]
    deltas = [x["candidate_minus_champion"] for x in all_rows]
    report = {
        "engine": "kaggle_environments==1.32.7",
        "policy": "bronze-medal external regression panel",
        "sign": "candidate_minus_champion = candidate external pair diff - champion external pair diff",
        "champion": "v112_wheat_lead3_lowdemand",
        "candidate": "v117_wheat_post_town_delay1",
        "seeds": SEEDS,
        "opponents": results,
        "pooled": {
            "seed_opponent_pairs": len(all_rows),
            "outcome_regressions": sum(x["outcome_regression"] for x in all_rows),
            "outcome_improvements": sum(x["outcome_improvement"] for x in all_rows),
            "mean_candidate_minus_champion": statistics.mean(deltas),
            "median_candidate_minus_champion": statistics.median(deltas),
            "worst_candidate_minus_champion": min(deltas),
            "best_candidate_minus_champion": max(deltas),
            "opponents_with_any_regression": [
                x["opponent"] for x in results if x["outcome_regressions"] > 0
            ],
            "opponents_with_any_improvement": [
                x["opponent"] for x in results if x["outcome_improvements"] > 0
            ],
        },
    }
    out = ROOT / "v117_external_eval.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("SUMMARY", json.dumps(report["pooled"], indent=2), flush=True)


if __name__ == "__main__":
    main()
