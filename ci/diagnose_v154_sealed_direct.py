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
    fn = getattr(mod, "agent")
    return mod, fn


def report_snapshot(mod):
    r = getattr(mod, "_V154_REPORT", None)
    return dict(r) if isinstance(r, dict) else {}


class CandidateRec:
    def __init__(self, cand_fn, cand_mod, shadow_fn):
        self.cand_fn = cand_fn
        self.cand_mod = cand_mod
        self.shadow_fn = shadow_fn
        self.rows = []

    def __call__(self, obs, cfg=None):
        before = report_snapshot(self.cand_mod)
        shadow_action = self.shadow_fn(copy.deepcopy(obs), cfg)
        action = self.cand_fn(obs, cfg)
        after = report_snapshot(self.cand_mod)
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
            "action": copy.deepcopy(action),
            "shadow_v147_action": copy.deepcopy(shadow_action),
            "report_before": before,
            "report_after": after,
            "report_delta": delta,
        })
        return action


class OppRec:
    def __init__(self, fn):
        self.fn = fn
        self.rows = []

    def __call__(self, obs, cfg=None):
        action = self.fn(obs, cfg)
        farms = obs.get("farms") or [{}, {}]
        self.rows.append({
            "step": int(obs.get("step", -1)),
            "seat": int(obs.get("player", 0)),
            "money": [f.get("money") for f in farms],
            "action": copy.deepcopy(action),
        })
        return action


def by_step(rows):
    return {int(r["step"]): r for r in rows}


def run_case(candidate_path: str, champion_path: str, seed: int, swap: bool):
    cmod, cand = load(candidate_path, f"cand_{seed}_{int(swap)}")
    smod, shadow = load(champion_path, f"shadow_{seed}_{int(swap)}")
    omod, opp = load(champion_path, f"opp_{seed}_{int(swap)}")
    rc = CandidateRec(cand, cmod, shadow)
    ro = OppRec(opp)
    env = make("kaggriculture", configuration={"seed": seed})
    env.run([ro, rc] if swap else [rc, ro])
    rewards = [s.get("reward") for s in env.state]
    cseat = 1 if swap else 0
    crows = by_step(rc.rows)
    orows = by_step(ro.rows)
    changed = [step for step, row in sorted(crows.items()) if int((row.get("report_delta") or {}).get("changed", 0)) > 0]
    eligible = [step for step, row in sorted(crows.items()) if int((row.get("report_delta") or {}).get("eligible", 0)) > 0]
    ahead_skips = [step for step, row in sorted(crows.items()) if int((row.get("report_delta") or {}).get("ahead_skips", 0)) > 0]
    keep = set()
    for step in changed:
        keep.update([step - 1, step, step + 1])
    selected=[]
    for step in sorted(x for x in keep if x >= 0):
        selected.append({"step": step, "candidate": crows.get(step), "opponent": orows.get(step)})
    return {
        "seed": seed,
        "swap": swap,
        "candidate_seat": cseat,
        "rewards": rewards,
        "candidate_money": rewards[cseat],
        "champion_money": rewards[1-cseat],
        "candidate_minus_champion": rewards[cseat] - rewards[1-cseat],
        "final_report": report_snapshot(cmod),
        "eligible_steps": eligible,
        "changed_steps": changed,
        "ahead_skip_steps": ahead_skips,
        "selected": selected,
    }


if __name__ == "__main__":
    candidate, champion, out = sys.argv[1:4]
    seeds = [1802, 1806, 1809, 1810]
    cases=[]
    for seed in seeds:
        for swap in (False, True):
            row=run_case(candidate, champion, seed, swap)
            cases.append(row)
            print(json.dumps({
                "seed":seed,
                "swap":swap,
                "diff":row["candidate_minus_champion"],
                "eligible":row["eligible_steps"],
                "changed":row["changed_steps"],
                "ahead_skips":len(row["ahead_skip_steps"]),
                "report":row["final_report"],
            }), flush=True)
    Path(out).write_text(json.dumps({"cases":cases}, indent=2), encoding="utf-8")
