from __future__ import annotations
import copy, importlib.util, json, statistics, sys, time, hashlib
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHAMPION = ROOT / "v112_wheat_lead3_lowdemand.py"
CANDIDATE = ROOT / "v122_wool_lowrisk_front1.py"
H2H_SEEDS = list(range(314001, 314005))
SIGNAL_SEEDS = [309003, 309004]
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
    parent = str(path.parent)
    sys.path.insert(0, parent)
    try:
        spec.loader.exec_module(mod)
    finally:
        try: sys.path.remove(parent)
        except ValueError: pass
    fn = getattr(mod, "agent", None)
    if not callable(fn):
        for v in vars(mod).values():
            if callable(v): fn = v
    if not callable(fn):
        raise RuntimeError(f"no callable agent in {path}")
    return mod, fn


def game(a, b, seed, swap=False):
    _, fa = load(a, f"a_{seed}_{swap}_{time.time_ns()}")
    _, fb = load(b, f"b_{seed}_{swap}_{time.time_ns()}")
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


def pair(a, b, seed):
    x = game(a, b, seed, False)
    y = game(a, b, seed, True)
    return {"seed": seed, "pair_diff": (x["delta"] + y["delta"]) / 2.0, "games": [x, y]}


def telemetry(rows):
    out = {"steps": []}
    for row in rows:
        for g in row["games"]:
            d = (g.get("telemetry") or {}).get("wool_lowrisk_front1") or {}
            for k, v in d.items():
                if k == "steps":
                    out["steps"].extend(list(v))
                elif isinstance(v, (int, float)):
                    out[k] = out.get(k, 0) + v
    return out


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0


def main():
    missing = [str(p) for p in [CHAMPION, CANDIDATE, *OPPONENTS.values()] if not p.exists()]
    if missing:
        raise FileNotFoundError("missing files: " + ", ".join(missing))

    h2h = []
    for seed in H2H_SEEDS:
        r = pair(CANDIDATE, CHAMPION, seed)
        h2h.append(r)
        print("h2h", seed, r["pair_diff"], flush=True)

    external = []
    for name, opp in OPPONENTS.items():
        for seed in SIGNAL_SEEDS:
            champ = pair(CHAMPION, opp, seed)
            cand = pair(CANDIDATE, opp, seed)
            delta = cand["pair_diff"] - champ["pair_diff"]
            rec = {
                "opponent": name,
                "seed": seed,
                "champion_pair_diff": champ["pair_diff"],
                "candidate_pair_diff": cand["pair_diff"],
                "candidate_minus_champion": delta,
                "champion_outcome": sign(champ["pair_diff"]),
                "candidate_outcome": sign(cand["pair_diff"]),
                "outcome_regression": sign(cand["pair_diff"]) < sign(champ["pair_diff"]),
                "outcome_improvement": sign(cand["pair_diff"]) > sign(champ["pair_diff"]),
                "candidate_telemetry": telemetry([cand]),
            }
            external.append(rec)
            print("external", name, seed, "champ", champ["pair_diff"], "cand", cand["pair_diff"], "delta", delta, "reorders", rec["candidate_telemetry"].get("reorders", 0), flush=True)

    hvals = [x["pair_diff"] for x in h2h]
    evals = [x["candidate_minus_champion"] for x in external]
    active = [x for x in external if x["candidate_telemetry"].get("reorders", 0) > 0]
    avals = [x["candidate_minus_champion"] for x in active]
    report = {
        "engine": "kaggle_environments==1.32.7",
        "champion": "v112_wheat_lead3_lowdemand",
        "candidate": "v122_wool_lowrisk_front1",
        "sha256": {"champion": sha(CHAMPION), "candidate": sha(CANDIDATE)},
        "sign": "candidate_minus_champion = candidate - champion",
        "h2h": {
            "seeds": H2H_SEEDS,
            "wins": sum(v > 0 for v in hvals),
            "losses": sum(v < 0 for v in hvals),
            "draws": sum(v == 0 for v in hvals),
            "mean": statistics.mean(hvals),
            "worst": min(hvals),
            "rows": h2h,
            "telemetry": telemetry(h2h),
        },
        "targeted_external": {
            "seeds": SIGNAL_SEEDS,
            "pairs": len(external),
            "mean_candidate_minus_champion": statistics.mean(evals),
            "median_candidate_minus_champion": statistics.median(evals),
            "worst_candidate_minus_champion": min(evals),
            "best_candidate_minus_champion": max(evals),
            "outcome_regressions": sum(x["outcome_regression"] for x in external),
            "outcome_improvements": sum(x["outcome_improvement"] for x in external),
            "active_pairs": len(active),
            "active_mean": statistics.mean(avals) if avals else 0.0,
            "active_worst": min(avals) if avals else 0.0,
            "active_best": max(avals) if avals else 0.0,
            "rows": external,
        },
    }
    (ROOT / "v122_focused.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("SUMMARY", json.dumps({
        "h2h": {k: report["h2h"][k] for k in ("wins", "losses", "draws", "mean", "worst")},
        "targeted_external": {k: report["targeted_external"][k] for k in ("mean_candidate_minus_champion", "median_candidate_minus_champion", "worst_candidate_minus_champion", "best_candidate_minus_champion", "outcome_regressions", "outcome_improvements", "active_pairs", "active_mean", "active_worst", "active_best")},
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
