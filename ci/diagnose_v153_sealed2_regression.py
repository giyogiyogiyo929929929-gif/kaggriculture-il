from __future__ import annotations

import collections
import copy
import importlib.util
import json
import sys
from pathlib import Path

from kaggle_environments import make
from scripts.analysis import _common as C


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


class Recorder:
    def __init__(self, mod, fn, label: str):
        self.mod = mod
        self.fn = fn
        self.label = label
        self.rows = []
        self.triggers = []

    def __call__(self, obs, cfg=None):
        report = getattr(self.mod, "_V153_REPORT", None)
        before = dict(report) if isinstance(report, dict) else {}
        action = self.fn(obs, cfg)
        after = dict(report) if isinstance(report, dict) else {}
        step = int(obs.get("step", -1))
        seat = int(obs.get("player", -1))
        row = {
            "step": step,
            "seat": seat,
            "money": [f.get("money") for f in (obs.get("farms") or [{}, {}])],
            "market_inventory": dict((obs.get("market") or {}).get("inventory") or {}),
            "prices": dict((obs.get("market") or {}).get("prices") or {}),
            "shed": dict((obs.get("private") or {}).get("shed") or {}),
            "action": copy.deepcopy(action),
        }
        self.rows.append(row)
        if before or after:
            de = int(after.get("eligible", 0)) - int(before.get("eligible", 0))
            dc = int(after.get("changed", 0)) - int(before.get("changed", 0))
            dx = int(after.get("errors", 0)) - int(before.get("errors", 0))
            if de or dc or dx:
                trig = dict(row)
                trig.update({"eligible_delta": de, "changed_delta": dc, "error_delta": dx})
                market_orders = [list(o) for o in (action.get("market") or [])]
                block = []
                for order in market_orders:
                    if not order or order[0] != "SELL":
                        break
                    block.append(order)
                scored = []
                try:
                    stock = self.mod.projected_shed(action, self.mod.FarmView(obs))
                    for i, order in enumerate(block):
                        scored.append({
                            "index": i,
                            "order": order,
                            "self_exposure": float(self.mod._v153_self_exposure(obs, order, stock)),
                        })
                except Exception as exc:
                    scored = [{"score_error": repr(exc)}]
                trig["leading_sell_scores_after"] = scored
                self.triggers.append(trig)
        return action


def summarize_sell_rows(rows, step: int, seat: int):
    picked = [r for r in rows if int(r[0]) == step and int(r[1]) == seat and r[2] == "SELL"]
    seq = [str(r[3]) for r in picked]
    prices = [float(r[4]) for r in picked]
    by_item = collections.defaultdict(list)
    for r in picked:
        by_item[str(r[3])].append(float(r[4]))
    return {
        "units": len(picked),
        "sequence": seq,
        "gross": sum(prices),
        "items": {
            item: {
                "qty": len(ps),
                "gross": sum(ps),
                "avg": sum(ps) / len(ps),
                "first": ps[0],
                "last": ps[-1],
                "realized_drop": ps[0] - ps[-1],
            }
            for item, ps in by_item.items()
        },
    }


def run(candidate_path: str, champion_path: str, seed: int, swap: bool):
    cm, ca = load(candidate_path, f"candidate_{seed}_{int(swap)}")
    hm, ha = load(champion_path, f"champion_{seed}_{int(swap)}")
    cr = Recorder(cm, ca, "candidate")
    hr = Recorder(hm, ha, "champion")
    ledger = C.Ledger()
    try:
        env = make("kaggriculture", configuration={"seed": seed})
        env.run([hr, cr] if swap else [cr, hr])
    finally:
        ledger.close()
    candidate_seat = 1 if swap else 0
    champion_seat = 1 - candidate_seat
    rewards = [s.get("reward") for s in env.state]
    delta = float(rewards[candidate_seat]) - float(rewards[champion_seat])
    champ_by_step = {r["step"]: r for r in hr.rows}
    triggers = []
    for t in cr.triggers:
        t = copy.deepcopy(t)
        t["candidate_sell_execution"] = summarize_sell_rows(ledger.rows, t["step"], candidate_seat)
        t["champion_same_game_action"] = copy.deepcopy((champ_by_step.get(t["step"]) or {}).get("action"))
        t["champion_sell_execution"] = summarize_sell_rows(ledger.rows, t["step"], champion_seat)
        triggers.append(t)
    return {
        "seed": seed,
        "swap": swap,
        "candidate_seat": candidate_seat,
        "rewards": rewards,
        "candidate_minus_champion": delta,
        "candidate_report": dict(getattr(cm, "_V153_REPORT", {})),
        "triggers": triggers,
    }


def main():
    candidate_path, champion_path, out = sys.argv[1:4]
    seeds = [961200427, 949799007]
    games = []
    for seed in seeds:
        for swap in (False, True):
            game = run(candidate_path, champion_path, seed, swap)
            games.append(game)
            print("DIAG_GAME", json.dumps({
                "seed": seed,
                "swap": swap,
                "delta": game["candidate_minus_champion"],
                "report": game["candidate_report"],
                "trigger_steps": [t["step"] for t in game["triggers"]],
            }))
            for t in game["triggers"]:
                print("DIAG_TRIGGER", json.dumps({
                    "seed": seed,
                    "swap": swap,
                    "step": t["step"],
                    "eligible_delta": t["eligible_delta"],
                    "changed_delta": t["changed_delta"],
                    "candidate_market": t["action"].get("market"),
                    "scores": t["leading_sell_scores_after"],
                    "candidate_sell_execution": t["candidate_sell_execution"],
                    "champion_market_same_game": (t.get("champion_same_game_action") or {}).get("market") if isinstance(t.get("champion_same_game_action"), dict) else None,
                    "champion_sell_execution": t["champion_sell_execution"],
                }))
    result = {
        "candidate": "v153 exact source, externally observed",
        "champion": "v147",
        "seeds": seeds,
        "games": games,
    }
    Path(out).write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
