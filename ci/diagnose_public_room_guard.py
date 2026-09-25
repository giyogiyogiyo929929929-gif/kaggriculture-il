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


# Original v144-v115 direct-screen values are pair-averaged across the two seats,
# not per-seat margins. Example: seed 683 margins +984 and 0 average to +492.
EXPECTED_SCREEN_PAIR_CASH_DELTA = {
    683: 492.0,
    689: -84.0,
    693: 479.0,
}


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
    farms = obs.get("farms") or [{}, {}]
    farm = farms[player] if player < len(farms) else {}
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


def make_trace_runner(spec: str):
    """Return a normal function closure so kaggle_environments invokes it normally."""
    agent = resolve_agent(spec)
    code = getattr(agent, "__code__", None)
    argcount = code.co_argcount if code is not None else 2
    trace: list[dict[str, Any]] = []
    exceptions: list[str] = []

    def runner(obs, config=None):
        before = copy.deepcopy(obs)
        try:
            action = agent(*[obs, config][:argcount])
        except Exception as exc:
            exceptions.append(repr(exc))
            raise
        action = copy.deepcopy(action)
        trace.append({
            "step": _int(before.get("step", len(trace))),
            "obs_hash": digest(before),
            "obs": summarize_obs(before),
            "action_hash": digest(action),
            "action": action,
        })
        return action

    return runner, trace, exceptions


def run(focal_spec: str, opponent_spec: str, seed: int, seat: int) -> dict[str, Any]:
    focal, trace, exceptions = make_trace_runner(focal_spec)
    opponent = resolve_agent(opponent_spec)
    env = make("kaggriculture", configuration={"seed": seed})
    env.run([focal, opponent] if seat == 0 else [opponent, focal])
    rewards = [float(state.get("reward") or 0) for state in env.state]
    statuses = [state.get("status") for state in env.state]
    if len(trace) < 700:
        raise RuntimeError(
            f"trace unexpectedly short seed={seed} seat={seat}: len={len(trace)} statuses={statuses} rewards={rewards}"
        )
    return {
        "focal_reward": rewards[seat],
        "rival_reward": rewards[1 - seat],
        "margin": rewards[seat] - rewards[1 - seat],
        "trace": trace,
        "trace_len": len(trace),
        "exceptions": exceptions,
        "statuses": statuses,
        "steps": len(env.steps),
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


def compact_obs(entry: dict[str, Any]) -> dict[str, Any]:
    obs = entry["obs"]
    return {
        "step": entry["step"],
        "day": obs["day"],
        "hour": obs["hour"],
        "money": obs["money"],
        "shed": obs["shed"],
        "shed_total": obs["shed_total"],
        "carried_total": obs["carried_total"],
        "unit_inventories": obs["unit_inventories"],
        "market_prices": obs["market_prices"],
        "market_inventory": obs["market_inventory"],
        "market": market(entry["action"]),
    }


def sell_events(trace: list[dict[str, Any]], start_idx: int, item: str, horizon: int = 96) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    end = min(len(trace), start_idx + horizon + 1)
    for i in range(start_idx + 1, end):
        entry = trace[i]
        for order in market(entry["action"]):
            if len(order) >= 3 and str(order[0]).upper() == "SELL" and str(order[1]) == item:
                out.append({
                    "trace_index": i,
                    "step": entry["step"],
                    "day": entry["obs"]["day"],
                    "hour": entry["obs"]["hour"],
                    "item": item,
                    "qty": _int(order[2]),
                    "visible_price": _int((entry["obs"].get("market_prices") or {}).get(item, 0)),
                    "shed_qty": _int((entry["obs"].get("shed") or {}).get(item, 0)),
                })
    return out


def post_divergence_window(base: dict[str, Any], cand: dict[str, Any], idx: int, horizon: int = 48) -> list[dict[str, Any]]:
    bt, ct = base["trace"], cand["trace"]
    end = min(len(bt), len(ct), idx + horizon + 1)
    rows = []
    for i in range(idx, end):
        b, c = bt[i], ct[i]
        rows.append({
            "trace_index": i,
            "same_observation": b["obs_hash"] == c["obs_hash"],
            "same_action": b["action_hash"] == c["action_hash"],
            "v115": compact_obs(b),
            "room_guard": compact_obs(c),
        })
    return rows


def first_div(base: dict[str, Any], cand: dict[str, Any]) -> dict[str, Any]:
    bt, ct = base["trace"], cand["trace"]
    n = min(len(bt), len(ct))
    idx = next((i for i in range(n) if bt[i]["action_hash"] != ct[i]["action_hash"]), None)
    if idx is None:
        return {"first_action_mismatch": None, "trace_len": [len(bt), len(ct)]}
    b, c = bt[idx], ct[idx]
    bm, cm = market(b["action"]), market(c["action"])
    added = multiset_delta(cm, bm)
    removed = multiset_delta(bm, cm)
    added_sell_items = sorted({
        str(order[1]) for order in added if len(order) >= 3 and str(order[0]).upper() == "SELL"
    })
    future = {}
    for item in added_sell_items:
        future[item] = {
            "v115_next_96_turn_sell_events": sell_events(bt, idx, item, 96),
            "room_guard_next_96_turn_sell_events": sell_events(ct, idx, item, 96),
        }
    return {
        "first_action_mismatch": idx,
        "step": b["step"],
        "same_observation": b["obs_hash"] == c["obs_hash"],
        "observation": b["obs"],
        "v115_action": b["action"],
        "room_guard_action": c["action"],
        "added_market_orders": added,
        "removed_market_orders": removed,
        "added_sell_items": added_sell_items,
        "future_sell_evidence": future,
        "post_divergence_window_turns": 48,
        "post_divergence_window": post_divergence_window(base, cand, idx, 48),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v115", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cases = [(seed, seat) for seed in (683, 689, 693) for seat in (0, 1)]
    rows = []
    for seed, seat in cases:
        baseline = run(args.v115, args.v115, seed, seat)
        candidate = run(args.candidate, args.v115, seed, seat)
        divergence = first_div(baseline, candidate)
        if divergence["first_action_mismatch"] is None:
            raise AssertionError(f"expected v115/v144 action divergence missing seed={seed} seat={seat}")
        rows.append({
            "seed": seed,
            "seat": seat,
            "candidate_direct_margin": candidate["margin"],
            "candidate_minus_selfplay_focal_money": candidate["focal_reward"] - baseline["focal_reward"],
            "candidate_minus_selfplay_rival_money": candidate["rival_reward"] - baseline["rival_reward"],
            "candidate_minus_selfplay_margin": candidate["margin"] - baseline["margin"],
            "baseline_focal_money": baseline["focal_reward"],
            "baseline_rival_money": baseline["rival_reward"],
            "baseline_margin": baseline["margin"],
            "candidate_focal_money": candidate["focal_reward"],
            "candidate_rival_money": candidate["rival_reward"],
            "baseline_trace_len": baseline["trace_len"],
            "candidate_trace_len": candidate["trace_len"],
            "baseline_statuses": baseline["statuses"],
            "candidate_statuses": candidate["statuses"],
            "baseline_exceptions": baseline["exceptions"],
            "candidate_exceptions": candidate["exceptions"],
            "divergence": divergence,
        })

    screen_validation = {}
    for seed, expected in EXPECTED_SCREEN_PAIR_CASH_DELTA.items():
        seat_rows = [r for r in rows if r["seed"] == seed]
        if len(seat_rows) != 2:
            raise AssertionError(f"missing seat rows for seed={seed}: {len(seat_rows)}")
        observed = sum(r["candidate_direct_margin"] for r in seat_rows) / 2.0
        seat_margins = [r["candidate_direct_margin"] for r in seat_rows]
        screen_validation[str(seed)] = {
            "expected_pair_cash_delta": expected,
            "observed_pair_cash_delta": observed,
            "seat_direct_margins": seat_margins,
        }
        if observed != expected:
            raise AssertionError(
                f"candidate screen pair delta mismatch seed={seed}: got={observed} expected={expected}; seat_margins={seat_margins}"
            )

    out = {
        "purpose": "already-burned public-room-guard causal telemetry; not promotion evidence",
        "candidate": "public_room_guard",
        "champion": "exact_v115",
        "engine": "kaggle_environments==1.32.7",
        "validation": "average of the two candidate-v115 direct seat margins must reproduce the original screen pair cash delta for each seed",
        "screen_validation": screen_validation,
        "rows": rows,
    }
    dst = Path(args.out)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
