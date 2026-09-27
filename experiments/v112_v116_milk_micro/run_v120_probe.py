from __future__ import annotations
import copy, importlib.util, json, statistics, sys, time
from collections import Counter
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PROBE = ROOT / "v120_public_market_race_probe.py"
CHAMPION = ROOT / "v112_wheat_lead3_lowdemand.py"
SELF_SEEDS = list(range(308001, 308005))
EXT_SEEDS = list(range(309001, 309005))
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
ITEMS = ("STRAWBERRY", "MELON", "MILK", "WOOL")

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
        for value in vars(mod).values():
            if callable(value):
                fn = value
    if not callable(fn):
        raise RuntimeError(f"no callable entrypoint in {path}")
    return mod, fn

def game(agent_path, opp_path, seed, swap):
    _, fa = load(agent_path, f"a_{seed}_{swap}_{time.time_ns()}")
    _, fb = load(opp_path, f"b_{seed}_{swap}_{time.time_ns()}")
    env = make("kaggriculture", configuration={"seed": int(seed)}, debug=False)
    env.run([fb, fa] if swap else [fa, fb])
    raw = [x.reward for x in env.state]
    if any(x is None for x in raw):
        statuses = [getattr(x, "status", None) for x in env.state]
        raise RuntimeError(f"no rewards seed={seed} swap={swap} status={statuses} rewards={raw}")
    rewards = [float(x) for x in raw]
    ar, br = (rewards[1], rewards[0]) if swap else (rewards[0], rewards[1])
    return {
        "seed": seed, "swap": swap, "agent_reward": ar, "opponent_reward": br,
        "delta": ar - br,
        "probe": copy.deepcopy((getattr(fa, "telemetry", {}) or {}).get("public_market_race_probe") or {}),
    }

def pair(agent_path, opp_path, seed):
    a = game(agent_path, opp_path, seed, False)
    b = game(agent_path, opp_path, seed, True)
    return {"seed": seed, "pair_diff": (a["delta"] + b["delta"]) / 2.0, "games": [a, b]}

def summarize(rows):
    games = [g for r in rows for g in r["games"]]
    out = {
        "pairs": len(rows), "games": len(games),
        "pair_diffs": [r["pair_diff"] for r in rows],
        "errors": sum(int((g["probe"] or {}).get("errors", 0)) for g in games),
        "transitions": sum(int((g["probe"] or {}).get("transitions", 0)) for g in games),
    }
    for key in ("positive_events", "positive_units", "clean_positive_events", "clean_positive_units",
                "excess_events", "excess_units", "joint_excess_price_drop", "negative_events"):
        out[key] = {
            item: sum(float(((g["probe"] or {}).get(key) or {}).get(item, 0)) for g in games)
            for item in ITEMS
        }
    counter = Counter()
    excess_values = {item: [] for item in ITEMS}
    for g in games:
        for ev in (g["probe"] or {}).get("events", []):
            item = ev.get("item")
            if item not in ITEMS:
                continue
            step = int(ev.get("step", -1))
            counter[(item, step)] += 1
            excess_values[item].append(float(ev.get("excess", 0) or 0))
    out["top_event_steps"] = [
        {"item": item, "step": step, "games": count}
        for (item, step), count in counter.most_common(24)
    ]
    out["excess_size"] = {
        item: {
            "n": len(vals),
            "mean": statistics.mean(vals) if vals else 0.0,
            "max": max(vals) if vals else 0.0,
        } for item, vals in excess_values.items()
    }
    return out

def run_panel(name, opp_path, seeds):
    rows = []
    for seed in seeds:
        row = pair(PROBE, opp_path, seed)
        rows.append(row)
        print(name, seed, row["pair_diff"], flush=True)
    return {"name": name, "seeds": seeds, "summary": summarize(rows), "rows": rows}

def main():
    missing = [str(p) for p in [PROBE, CHAMPION, *OPPONENTS.values()] if not p.exists()]
    if missing:
        raise FileNotFoundError("missing: " + ", ".join(missing))
    selfplay = run_panel("v112_clone", CHAMPION, SELF_SEEDS)
    if any(abs(x) > 1e-9 for x in selfplay["summary"]["pair_diffs"]):
        raise SystemExit("SEMANTIC_GATE: v120 vs v112 clone pair diff is nonzero")
    if selfplay["summary"]["errors"]:
        raise SystemExit("SAFETY_GATE: v120 telemetry errors in clone panel")
    external = []
    for name, path in OPPONENTS.items():
        panel = run_panel(name, path, EXT_SEEDS)
        if panel["summary"]["errors"]:
            raise SystemExit(f"SAFETY_GATE: telemetry errors vs {name}")
        external.append(panel)
    report = {
        "engine": "kaggle_environments==1.32.7",
        "champion": "v112_wheat_lead3_lowdemand",
        "probe": "v120_public_market_race_probe",
        "purpose": "action-identical public market race telemetry; not promotion eligible",
        "selfplay": selfplay,
        "external": external,
    }
    (ROOT / "v120_probe.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    compact = {
        "selfplay": selfplay["summary"],
        "external": {p["name"]: p["summary"] for p in external},
    }
    (ROOT / "v120_probe_summary.json").write_text(json.dumps(compact, indent=2), encoding="utf-8")
    print("SUMMARY", json.dumps(compact, indent=2), flush=True)

if __name__ == "__main__":
    main()
