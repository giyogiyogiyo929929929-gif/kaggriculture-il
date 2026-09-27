from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

from kaggle_environments import make


def load(path: str, tag: str):
    p = Path(path).resolve()
    spec = importlib.util.spec_from_file_location(tag, p)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(p.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(p.parent))
    agent = None
    for value in vars(mod).values():
        if callable(value):
            agent = value
    if agent is None:
        raise RuntimeError(path)
    return mod, agent


def report_snapshot(mod):
    r = getattr(mod, "_V153_REPORT", None)
    return dict(r) if isinstance(r, dict) else {}


class Rec:
    def __init__(self, fn, mod=None):
        self.fn = fn
        self.mod = mod
        self.rows = []

    def __call__(self, obs, cfg=None):
        before = report_snapshot(self.mod) if self.mod is not None else {}
        action = self.fn(obs, cfg)
        after = report_snapshot(self.mod) if self.mod is not None else {}
        delta = {k: int(after.get(k, 0)) - int(before.get(k, 0)) for k in set(before) | set(after)}
        farms = obs.get("farms") or [{}, {}]
        priv = obs.get("private") or {}
        market = obs.get("market") or {}
        self.rows.append({
            "step": int(obs.get("step", -1)),
            "seat": int(obs.get("player", 0)),
            "money": [f.get("money") for f in farms],
            "market_inventory": dict(market.get("inventory") or {}),
            "prices": dict(market.get("prices") or {}),
            "market_params": copy.deepcopy(market.get("params") or {}),
            "shed": dict(priv.get("shed") or {}),
            "carried": [dict(x) for x in (priv.get("inventories") or [])],
            "shops": list((obs.get("town") or {}).get("unlocked_shops") or []),
            "action": copy.deepcopy(action),
            "report_before": before,
            "report_after": after,
            "report_delta": delta,
        })
        return action


def run_one(focal_path: str, opp_path: str, seed: int, swap: bool, tag: str):
    mod, focal = load(focal_path, f"{tag}_focal_{seed}_{int(swap)}")
    omod, opp = load(opp_path, f"{tag}_opp_{seed}_{int(swap)}")
    rf = Rec(focal, mod)
    ro = Rec(opp, omod)
    env = make("kaggriculture", configuration={"seed": seed})
    env.run([ro, rf] if swap else [rf, ro])
    return {
        "swap": swap,
        "focal_seat": 1 if swap else 0,
        "rewards": [s.get("reward") for s in env.state],
        "final_report": report_snapshot(mod),
        "focal_rows": rf.rows,
        "opponent_rows": ro.rows,
    }


def by_step(rows):
    return {int(r["step"]): r for r in rows}


def compact_case(candidate_path, champion_path, opp_path, opponent_name, seed, swap):
    cand = run_one(candidate_path, opp_path, seed, swap, "cand")
    champ = run_one(champion_path, opp_path, seed, swap, "champ")
    crows = by_step(cand["focal_rows"])
    hrows = by_step(champ["focal_rows"])
    orows = by_step(cand["opponent_rows"])
    changed = [
        step for step, row in sorted(crows.items())
        if int((row.get("report_delta") or {}).get("changed", 0)) > 0
    ]
    eligible = [
        step for step, row in sorted(crows.items())
        if int((row.get("report_delta") or {}).get("eligible", 0)) > 0
    ]
    keep = set()
    for step in eligible + changed:
        keep.update([step - 1, step, step + 1])
    selected = []
    for step in sorted(x for x in keep if x >= 0):
        selected.append({
            "step": step,
            "candidate": crows.get(step),
            "champion": hrows.get(step),
            "opponent_in_candidate_game": orows.get(step),
        })
    cseat = 1 if swap else 0
    hseat = cseat
    return {
        "opponent": opponent_name,
        "seed": seed,
        "swap": swap,
        "candidate_rewards": cand["rewards"],
        "champion_rewards": champ["rewards"],
        "candidate_money": cand["rewards"][cseat],
        "champion_money": champ["rewards"][hseat],
        "candidate_final_report": cand["final_report"],
        "eligible_steps": eligible,
        "changed_steps": changed,
        "selected": selected,
    }


if __name__ == "__main__":
    candidate, champion, out = sys.argv[1:4]
    cases = [
        ("peak_2950", "opponents/peak_2950/main.py", 520101),
        ("peak_2950", "opponents/peak_2950/main.py", 520102),
        ("peak_2950", "opponents/peak_2950/main.py", 520103),
        ("peak_2950", "opponents/peak_2950/main.py", 520104),
        ("score_2820", "opponents/score_2820/main.py", 520104),
        ("tetsutani_ms", "opponents/tetsutani_ms/main.py", 520104),
    ]
    results = []
    for name, opp, seed in cases:
        for swap in (False, True):
            row = compact_case(candidate, champion, opp, name, seed, swap)
            results.append(row)
            print(json.dumps({
                "opponent": name,
                "seed": seed,
                "swap": swap,
                "candidate_money": row["candidate_money"],
                "champion_money": row["champion_money"],
                "eligible_steps": row["eligible_steps"],
                "changed_steps": row["changed_steps"],
                "report": row["candidate_final_report"],
            }), flush=True)
    Path(out).write_text(json.dumps({"cases": results}, indent=2), encoding="utf-8")
