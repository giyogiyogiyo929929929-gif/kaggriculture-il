# -*- coding: utf-8 -*-
"""v19の確定・先回り・不一致解除が起きるstepだけを記録する。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.eval import resolve_agent  # noqa: E402


def trace(opponent: str, seed: int, candidate: str = "v19_antiv52_actualsales"):
    from kaggle_environments import make

    agent = resolve_agent(f"submissions/{candidate}/main.py")
    rival = resolve_agent(f"opponents/{opponent}/main.py")
    namespace = agent.__globals__
    events = []
    mismatch_details = []
    last = {"copy": False, "mismatches": 0, "preempt_fires": 0}

    def watched(observation, configuration=None):
        player = int(observation["player"])
        step = int(observation["step"])
        prior = namespace.get("_KIL_V52_STATE", {}).get(player, {})
        previous = (namespace.get("_V9_RACE", {}).get(player) or {}).get("prev")
        actual = prior.get("actual_prev")
        if previous and previous.get("step") == step - 1:
            accounting = actual if actual and actual.get("step") == step - 1 else previous
            draw = namespace["_v9_town_draw"](accounting.get("shops", []), accounting["step"])
            inventory = observation["market"]["inventory"]
            for item in namespace["_V92_P_ITEMS"]:
                baseline = int(previous.get("own", {}).get(item, 0))
                executed = int(accounting.get("own", {}).get(item, 0))
                rival_sale = (int(inventory[item]) - int(accounting["inventory"][item])
                              + int(draw.get(item, 0)) - executed)
                if step >= namespace["_KIL_V52_START"] and (baseline >= 2 or rival_sale >= 2) and baseline != rival_sale:
                    mismatch_details.append({"step": step, "item": item, "baseline": baseline,
                                             "executed": executed, "rival": rival_sale})
        action = agent(observation, configuration)
        state = namespace.get("_KIL_V52_STATE", {}).get(player, {})
        report = namespace.get("_KIL_V52_REPORT", {})
        current = {"copy": bool(state.get("copy")),
                   "abandoned": bool(state.get("abandoned")),
                   "mismatches": int(report.get("mismatches", 0)),
                   "preempt_fires": int(report.get("preempt_fires", 0)),
                   "evidence": int(state.get("evidence", 0))}
        if any(current.get(key) != last.get(key) for key in ("copy", "mismatches", "preempt_fires")):
            events.append({"step": int(observation["step"]), **current})
        last.update(current)
        return action

    env = make("kaggriculture", configuration={"seed": seed})
    env.run([watched, rival])
    final = namespace.get("_KIL_V52_STATE", {}).get(0, {})
    return {"candidate": candidate, "opponent": opponent, "seed": seed,
            "reward": [state["reward"] for state in env.state], "events": events,
            "mismatch_details": mismatch_details[:8],
            "final_state": {key: final.get(key) for key in
                            ("step", "same_farm", "same_sales", "copy", "abandoned", "evidence")},
            "report": namespace.get("_KIL_V52_REPORT", {})}


if __name__ == "__main__":
    cases = (("v17_antiv52_strict", "v52", 242),
             ("v17_antiv52_strict", "v49", 242))
    for candidate, opponent, seed in cases:
        print(json.dumps(trace(opponent, seed, candidate), ensure_ascii=False, default=str))
