from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kaggle_environments import make
from scripts.eval import resolve_agent


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), default=str)


def digest(v: Any) -> str:
    return hashlib.sha256(canon(v).encode()).hexdigest()


def _int(v: Any) -> int:
    try:
        return int(v)
    except Exception:
        return 0


def summarize_obs(obs: dict[str, Any]) -> dict[str, Any]:
    player = _int(obs.get("player", 0))
    step = _int(obs.get("step", 0))
    private = obs.get("private") or {}
    shed = copy.deepcopy(private.get("shed") or {})
    farm = (obs.get("farms") or [{}, {}])[player]
    unit_invs = []
    farmer = farm.get("farmer") or {}
    unit_invs.append(copy.deepcopy(farmer.get("inventory") or farmer.get("inv") or {}))
    for h in farm.get("hands") or []:
        unit_invs.append(copy.deepcopy((h or {}).get("inventory") or (h or {}).get("inv") or {}))
    carried_total = sum(_int(q) for inv in unit_invs for q in inv.values())
    market = obs.get("market") or {}
    return {
        "step": step,
        "day": step // 24,
        "hour": step % 24,
        "player": player,
        "money": _int(farm.get("money", 0)),
        "shed": shed,
        "shed_total": sum(_int(x) for x in shed.values()),
        "unit_inventories": unit_invs,
        "carried_total": carried_total,
        "market_prices": copy.deepcopy(market.get("prices") or {}),
        "market_inventory": copy.deepcopy(market.get("inventory") or {}),
        "town_shops": copy.deepcopy((obs.get("town") or {}).get("unlocked_shops") or []),
    }


class TraceAgent:
    def __init__(self, spec: str):
        self.agent = resolve_agent(spec)
        code = getattr(self.agent, "__code__", None)
        self.argcount = code.co_argcount if code is not None else 2
        self.trace: list[dict[str, Any]] = []
        self.exceptions: list[str] = []

    def __call__(self, obs, config=None):
        before = copy.deepcopy(obs)
        try:
            action = self.agent(*[obs, config][: self.argcount])
        except Exception as exc:
            self.exceptions.append(repr(exc))
            raise
        action = copy.deepcopy(action)
        self.trace.append({
            "step": _int(before.get("step", len(self.trace))),
            "obs_hash": digest(before),
            "obs": summarize_obs(before),
            "action_hash": digest(action),
            "action": action,
        })
        return action


def run(focal_spec: str, opponent_spec: str, seed: int, seat: int) -> dict[str, Any]:
    focal = TraceAgent(focal_spec)
    opponent = resolve_agent(opponent_spec)
    env = make("kaggriculture", configuration={"seed": seed})
    env.run([focal, opponent] if seat == 0 else [opponent, focal])
    rewards = [float(state.get("reward") or 0) for state in env.state]
    return {
        "focal_reward": rewards[seat],
        "rival_reward": rewards[1 - seat],
        "margin": rewards[seat] - rewards[1 - seat],
        "trace": focal.trace,
        "exceptions": focal.exceptions,
    }


def multiset_delta(a: list[list[Any]], b: list[list[Any]]) -> list[list[Any]]:
    left = copy.deepcopy(a)
    for x in b:
        if x in left:
            left.remove(x)
    return left


def market(action: Any) -> list[list[Any]]:
    if not isinstance(action, dict):
        return []
    return [list(x) for x in (action.get("market") or []) if x]


def first_div(base: dict[str, Any], cand: dict[str, Any]) -> dict[str, Any]:
    bt, ct = base["trace"], cand["trace"]
    n = min(len(bt), len(ct))
    idx = next((i for i in range(n) if bt[i]["action_hash"] != ct[i]["action_hash"]), None)
    if idx is None:
        return {"first_action_mismatch": None, "trace_len": [len(bt), len(ct)]}
    b, c = bt[idx], ct[idx]
    bm, cm = market(b["action"]), market(c["action"])
    return {
        "first_action_mismatch": idx,
        "step": b["step"],
        "same_observation": b["obs_hash"] == c["obs_hash"],
        "observation": b["obs"],
        "v115_action": b["action"],
        "room_guard_action": c["action"],
        "added_market_orders": multiset_delta(cm, bm),
        "removed_market_orders": multiset_delta(bm, cm),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v115", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # All seeds below are already consumed by the room-guard screen/runtime.
    # 683 = largest direct gain (+492 pair), 689 = only direct loss (-84 pair),
    # 693 = runtime smoke with +479 direct pair margin.
    cases = [(seed, seat) for seed in (683, 689, 693) for seat in (0, 1)]
    rows = []
    for seed, seat in cases:
        baseline = run(args.v115, args.v115, seed, seat)
        candidate = run(args.candidate, args.v115, seed, seat)
        rows.append({
            "seed": seed,
            "seat": seat,
            "candidate_minus_champion_focal_money": candidate["focal_reward"] - baseline["focal_reward"],
            "candidate_minus_champion_margin": candidate["margin"] - baseline["margin"],
            "baseline_focal_money": baseline["focal_reward"],
            "candidate_focal_money": candidate["focal_reward"],
            "baseline_margin": baseline["margin"],
            "candidate_margin": candidate["margin"],
            "baseline_exceptions": baseline["exceptions"],
            "candidate_exceptions": candidate["exceptions"],
            "divergence": first_div(baseline, candidate),
        })

    out = {
        "purpose": "already-burned public-room-guard causal telemetry; not promotion evidence",
        "candidate": "public_room_guard",
        "champion": "exact_v115",
        "engine": "kaggle_environments==1.32.7",
        "rows": rows,
    }
    dst = Path(args.out)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
