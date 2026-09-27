from __future__ import annotations
import copy, importlib.util, json, statistics, sys, time
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHAMPION = ROOT / "v112_wheat_lead3_lowdemand.py"
CANDIDATE = ROOT / "v121_strawberry_race_shift4.py"
SEEDS = list(range(313001, 313005))
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


def load(path, tag):
    path = Path(path)
    spec = importlib.util.spec_from_file_location(tag, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[tag] = mod
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        try: sys.path.remove(str(path.parent))
        except ValueError: pass
    fn = getattr(mod, "agent", None)
    if not callable(fn):
        for v in vars(mod).values():
            if callable(v): fn = v
    if not callable(fn):
        raise RuntimeError(f"no callable agent in {path}")
    return mod, fn


def game(agent_path, opp_path, seed, swap):
    _, fa = load(agent_path, f"a_{seed}_{swap}_{time.time_ns()}")
    _, fb = load(opp_path, f"b_{seed}_{swap}_{time.time_ns()}")
    env = make("kaggriculture", configuration={"seed": int(seed)}, debug=False)
    env.run([fb, fa] if swap else [fa, fb])
    raw = [x.reward for x in env.state]
    if any(x is None for x in raw):
        statuses = [getattr(x, "status", None) for x in env.state]
        raise RuntimeError(f"missing reward seed={seed} swap={swap} status={statuses} rewards={raw}")
    rewards = [float(x) for x in raw]
    ar, br = (rewards[1], rewards[0]) if swap else (rewards[0], rewards[1])
    return {
        "agent_reward": ar,
        "opponent_reward": br,
        "delta": ar - br,
        "telemetry": copy.deepcopy(getattr(fa, "telemetry", {})),
    }


def pair(agent_path, opp_path, seed):
    a = game(agent_path, opp_path, seed, False)
    b = game(agent_path, opp_path, seed, True)
    return {"seed": seed, "pair_diff": (a["delta"] + b["delta"]) / 2.0, "games": [a, b]}


def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0


def tele(rows):
    out = {"activation_steps": [], "repay_steps": []}
    for row in rows:
        for g in row["games"]:
            d = (g.get("telemetry") or {}).get("strawberry_race_shift4") or {}
            for k, v in d.items():
                if k in ("activation_steps", "repay_steps"):
                    out[k].extend(list(v))
                elif isinstance(v, (int, float)):
                    out[k] = out.get(k, 0) + v
    return out


def wld(rows):
    vals = [r["pair_diff"] for r in rows]
    return {
        "wins": sum(v > 0 for v in vals),
        "losses": sum(v < 0 for v in vals),
        "draws": sum(v == 0 for v in vals),
        "mean": statistics.mean(vals),
        "median": statistics.median(vals),
        "worst": min(vals),
        "best": max(vals),
    }


def main():
    results = []
    for name, opp in OPPONENTS.items():
        champ_rows, cand_rows, paired = [], [], []
        for seed in SEEDS:
            champ = pair(CHAMPION, opp, seed)
            cand = pair(CANDIDATE, opp, seed)
            champ_rows.append(champ); cand_rows.append(cand)
            d = cand["pair_diff"] - champ["pair_diff"]
            paired.append({
                "seed": seed,
                "champion_pair_diff": champ["pair_diff"],
                "candidate_pair_diff": cand["pair_diff"],
                "candidate_minus_champion": d,
                "outcome_regression": sign(cand["pair_diff"]) < sign(champ["pair_diff"]),
                "outcome_improvement": sign(cand["pair_diff"]) > sign(champ["pair_diff"]),
            })
            print(name, seed, "delta", d, flush=True)
        ds = [x["candidate_minus_champion"] for x in paired]
        results.append({
            "opponent": name,
            "champion": wld(champ_rows),
            "candidate": wld(cand_rows),
            "candidate_minus_champion": {"mean": statistics.mean(ds), "median": statistics.median(ds), "worst": min(ds), "best": max(ds)},
            "outcome_regressions": sum(x["outcome_regression"] for x in paired),
            "outcome_improvements": sum(x["outcome_improvement"] for x in paired),
            "candidate_telemetry": tele(cand_rows),
            "rows": paired,
        })
    allrows = [r for x in results for r in x["rows"]]
    ds = [r["candidate_minus_champion"] for r in allrows]
    report = {
        "engine": "kaggle_environments==1.32.7",
        "champion": "v112_wheat_lead3_lowdemand",
        "candidate": "v121_strawberry_race_shift4",
        "seeds": SEEDS,
        "opponents": results,
        "pooled": {
            "pairs": len(allrows),
            "mean_candidate_minus_champion": statistics.mean(ds),
            "median_candidate_minus_champion": statistics.median(ds),
            "worst_candidate_minus_champion": min(ds),
            "best_candidate_minus_champion": max(ds),
            "outcome_regressions": sum(r["outcome_regression"] for r in allrows),
            "outcome_improvements": sum(r["outcome_improvement"] for r in allrows),
            "total_activations": sum(x["candidate_telemetry"].get("activations", 0) for x in results),
            "total_repayments": sum(x["candidate_telemetry"].get("repayments", 0) for x in results),
            "total_repay_shortfalls": sum(x["candidate_telemetry"].get("repay_shortfalls", 0) for x in results),
            "total_errors": sum(x["candidate_telemetry"].get("errors", 0) for x in results),
        },
    }
    (ROOT / "v121_fresh_external.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("SUMMARY", json.dumps(report["pooled"], indent=2), flush=True)


if __name__ == "__main__":
    main()
