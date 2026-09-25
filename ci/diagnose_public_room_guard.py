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

# Original direct-screen values are pair averages of candidate-v115 margins
# over the two seats. They are burned diagnostic seeds, never promotion evidence.
EXPECTED_SCREEN_PAIR_CASH_DELTA = {683: 492.0, 689: -84.0, 693: 479.0}
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")
ANIMAL_PRODUCT = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}
ANIMAL_STRUCTURE = {"GOOSE": "COOP", "COW": "PASTURE", "SHEEP": "PASTURE"}


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), default=str)


def digest(v: Any) -> str:
    return hashlib.sha256(canon(v).encode()).hexdigest()


def _int(v: Any) -> int:
    try:
        return int(v)
    except Exception:
        return 0


def _get(v: Any, key: str, default: Any = None) -> Any:
    if isinstance(v, dict):
        return v.get(key, default)
    getter = getattr(v, "get", None)
    if callable(getter):
        try:
            return getter(key, default)
        except Exception:
            pass
    return getattr(v, key, default)


def _tile_at(tiles: Any, pos: Any) -> Any:
    try:
        x, y = int(pos[0]), int(pos[1])
        return tiles[y][x]
    except Exception:
        return "LOCKED"


def market(action: Any) -> list[list[Any]]:
    if not isinstance(action, dict):
        return []
    return [list(x) for x in (action.get("market") or []) if x]


def multiset_delta(a: list[list[Any]], b: list[list[Any]]) -> list[list[Any]]:
    left = copy.deepcopy(a)
    for x in b:
        if x in left:
            left.remove(x)
    return left


def _sum_orders(orders: list[list[Any]], kind: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for o in orders:
        if len(o) >= 3 and str(o[0]).upper() == kind:
            out[str(o[1])] = out.get(str(o[1]), 0) + max(0, _int(o[2]))
    return out


def _production_consumption(action: dict[str, Any], view: Any) -> tuple[dict[str, int], dict[str, int]]:
    units = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
    produced: dict[str, int] = {}
    consumed: dict[str, int] = {}
    positions = list(getattr(view, "positions", []) or [])
    tiles = getattr(view, "tiles", []) or []
    for i in range(min(len(units), len(positions))):
        a = units[i]
        if not a:
            continue
        op = str(a[0]).upper()
        tile = _tile_at(tiles, positions[i])
        if op == "HARVEST" and isinstance(tile, dict):
            qty = max(0, _int(_get(tile, "yield_units", 0)))
            if qty:
                kind = _get(tile, "kind")
                if kind == "PLANT":
                    item = str(_get(tile, "crop", "UNKNOWN"))
                else:
                    animal = str(_get(tile, "animal", ""))
                    item = ANIMAL_PRODUCT.get(animal, animal or "UNKNOWN")
                produced[item] = produced.get(item, 0) + qty
        elif op == "COLLECT_FERTILIZER" and isinstance(tile, dict) and _get(tile, "fertilizer_available"):
            produced["FERTILIZER"] = produced.get("FERTILIZER", 0) + 1
        elif op == "FEED":
            consumed["WHEAT"] = consumed.get("WHEAT", 0) + 1
        elif op == "FERTILIZE":
            consumed["FERTILIZER"] = consumed.get("FERTILIZER", 0) + 1
        elif op == "PLACE" and len(a) > 1 and str(a[1]) in ANIMAL_STRUCTURE:
            item = str(a[1])
            consumed[item] = consumed.get(item, 0) + 1
    return produced, consumed


def _future_sell_schedule(chassis: Any, route: Any, step: int) -> dict[str, list[dict[str, int]]]:
    out = {p: [] for p in PRODUCTS}
    try:
        tape = chassis.routes[route]
    except Exception:
        return out
    for t in range(step + 1, len(tape)):
        row = tape[t]
        if not isinstance(row, dict):
            continue
        per_step: dict[str, int] = {}
        for o in row.get("market") or []:
            if o and len(o) >= 3 and str(o[0]).upper() == "SELL" and str(o[1]) in out:
                item = str(o[1])
                per_step[item] = per_step.get(item, 0) + max(0, _int(o[2]))
        for item, qty in per_step.items():
            out[item].append({"step": t, "day": t // 24, "hour": t % 24, "qty": qty})
    return out


def _room_guard_snapshot(chassis: Any, action: dict[str, Any], view: Any, route: Any, step: int) -> dict[str, Any]:
    cfg = chassis.cfg
    orders = market(action)
    current_sells = _sum_orders(orders, "SELL")
    buy_orders = [o for o in orders if o and str(o[0]).upper() in ("BUY_PRODUCT", "BUY_ANIMAL")]
    buy_by_item: dict[str, int] = {}
    for o in buy_orders:
        if len(o) >= 3:
            buy_by_item[str(o[1])] = buy_by_item.get(str(o[1]), 0) + max(0, _int(o[2]))
    planned_buys = sum(buy_by_item.values())

    carried_by_item: dict[str, int] = {}
    for inv in list(getattr(view, "invs", []) or []):
        for item, qty in dict(inv or {}).items():
            q = max(0, _int(qty))
            carried_by_item[str(item)] = carried_by_item.get(str(item), 0) + q
    carried_total = sum(carried_by_item.values())
    produced_by_item, consumed_by_item = _production_consumption(action, view)
    produced_total = sum(produced_by_item.values())
    consumed_total = sum(consumed_by_item.values())

    shed = dict(getattr(view, "shed", {}) or {})
    shed_total = sum(max(0, _int(v)) for v in shed.values())
    fillable = sum(min(max(0, _int(shed.get(it, 0))), qty) for it, qty in current_sells.items())
    cap = _int(cfg.get("shed_capacity", 100))
    projected_total = shed_total + carried_total + produced_total - consumed_total + planned_buys - fillable
    guard_needed = max(0, projected_total - (cap - 1))
    physical_overflow = max(0, projected_total - cap)

    future_qty: dict[str, int] = {}
    free_excess: dict[str, int] = {}
    for item in PRODUCTS:
        try:
            fq = max(0, _int(chassis.future_sells(route, item, step + 1)))
        except Exception:
            fq = 0
        future_qty[item] = fq
        avail_after_current = max(0, _int(shed.get(item, 0)) - current_sells.get(item, 0))
        free_excess[item] = max(0, avail_after_current - fq)

    return {
        "step": step, "day": step // 24, "hour": step % 24, "route": route,
        "current_shed": copy.deepcopy(shed), "current_shed_total": shed_total,
        "carried_by_item": carried_by_item, "carried_total": carried_total,
        "current_turn_production_by_item": produced_by_item, "current_turn_production_total": produced_total,
        "current_turn_consumption_by_item": consumed_by_item, "current_turn_consumption_total": consumed_total,
        "buy_orders_before_guard": buy_orders, "buy_qty_by_item_before_guard": buy_by_item,
        "current_turn_sell_qty_before_guard": current_sells,
        "fillable_current_sells_from_shed": fillable,
        "projected_eod_shed_total_before_guard": projected_total,
        "physical_overflow_over_capacity": physical_overflow,
        "guard_needed_to_target_capacity_minus_one": guard_needed,
        "future_planned_sell_qty": future_qty,
        "free_excess_after_current_sell_and_future_reserve": free_excess,
        "future_sell_schedule": _future_sell_schedule(chassis, route, step),
    }


def _install_room_guard_probe(agent: Any, events: list[dict[str, Any]]) -> bool:
    glb = getattr(agent, "__globals__", None) or {}
    cls = glb.get("Chassis")
    if cls is None or not hasattr(cls, "_room_guard"):
        return False
    original = cls._room_guard

    def wrapped(self, action, view, route, step):
        turns = _int(self.cfg.get("turns_per_day", 24))
        if turns > 0 and step % turns == turns - 1:
            before = copy.deepcopy(action)
            snap = _room_guard_snapshot(self, before, view, route, step)
            result = original(self, action, view, route, step)
            after = copy.deepcopy(action)
            snap["action_before_guard"] = before
            snap["action_after_guard"] = after
            snap["guard_added_market_orders"] = multiset_delta(market(after), market(before))
            snap["guard_removed_market_orders"] = multiset_delta(market(before), market(after))
            snap["room_guard_fired"] = before != after
            events.append(snap)
            return result
        return original(self, action, view, route, step)

    cls._room_guard = wrapped
    return True


def summarize_obs(obs: dict[str, Any]) -> dict[str, Any]:
    player = _int(obs.get("player", 0))
    step = _int(obs.get("step", 0))
    private = obs.get("private") or {}
    shed = copy.deepcopy(private.get("shed") or {})
    farms = obs.get("farms") or [{}, {}]
    farm = farms[player] if player < len(farms) else {}
    unit_invs = [copy.deepcopy(inv or {}) for inv in (private.get("inventories") or [])]
    market_obs = obs.get("market") or {}
    town = obs.get("town") or {}
    return {
        "step": step, "day": step // 24, "hour": step % 24, "player": player,
        "money": _int(farm.get("money", 0)), "shed": shed,
        "shed_total": sum(_int(x) for x in shed.values()),
        "unit_inventories": unit_invs,
        "carried_total": sum(_int(q) for inv in unit_invs for q in inv.values()),
        "market_prices": copy.deepcopy(market_obs.get("prices") or {}),
        "market_inventory": copy.deepcopy(market_obs.get("inventory") or {}),
        "town_shops": copy.deepcopy(town.get("unlocked_shops") or []),
        "town_consumption_clock": {
            "step_mod_4": step % 4,
            "hour": step % 24,
            "unlocked_shops": copy.deepcopy(town.get("unlocked_shops") or []),
        },
    }


def make_trace_runner(spec: str, probe_room_guard: bool = False):
    agent = resolve_agent(spec)
    code = getattr(agent, "__code__", None)
    argcount = code.co_argcount if code is not None else 2
    trace: list[dict[str, Any]] = []
    exceptions: list[str] = []
    guard_events: list[dict[str, Any]] = []
    probe_installed = _install_room_guard_probe(agent, guard_events) if probe_room_guard else False

    def runner(obs, config=None):
        before = copy.deepcopy(obs)
        try:
            action = agent(*[obs, config][:argcount])
        except Exception as exc:
            exceptions.append(repr(exc))
            raise
        action = copy.deepcopy(action)
        step = _int(before.get("step", len(trace)))
        step_guard = [copy.deepcopy(e) for e in guard_events if _int(e.get("step", -1)) == step]
        trace.append({
            "step": step, "obs_hash": digest(before), "obs": summarize_obs(before),
            "action_hash": digest(action), "action": action, "room_guard_events": step_guard,
        })
        return action

    return runner, trace, exceptions, probe_installed


def run(focal_spec: str, opponent_spec: str, seed: int, seat: int, probe_room_guard: bool = False) -> dict[str, Any]:
    focal, trace, exceptions, probe_installed = make_trace_runner(focal_spec, probe_room_guard)
    opponent = resolve_agent(opponent_spec)
    env = make("kaggriculture", configuration={"seed": seed})
    env.run([focal, opponent] if seat == 0 else [opponent, focal])
    rewards = [float(state.get("reward") or 0) for state in env.state]
    statuses = [state.get("status") for state in env.state]
    if len(trace) < 700:
        raise RuntimeError(
            f"trace unexpectedly short seed={seed} seat={seat}: len={len(trace)} statuses={statuses} rewards={rewards}"
        )
    if probe_room_guard and not probe_installed:
        raise RuntimeError("failed to install room_guard probe on candidate module")
    return {
        "focal_reward": rewards[seat], "rival_reward": rewards[1 - seat],
        "margin": rewards[seat] - rewards[1 - seat], "trace": trace,
        "trace_len": len(trace), "exceptions": exceptions, "statuses": statuses,
        "steps": len(env.steps), "probe_installed": probe_installed,
    }


def sell_events(trace: list[dict[str, Any]], start_idx: int, item: str, horizon: int = 96) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    end = min(len(trace), start_idx + horizon + 1)
    for i in range(start_idx + 1, end):
        entry = trace[i]
        for order in market(entry["action"]):
            if len(order) >= 3 and str(order[0]).upper() == "SELL" and str(order[1]) == item:
                out.append({
                    "trace_index": i, "step": entry["step"], "day": entry["obs"]["day"],
                    "hour": entry["obs"]["hour"], "item": item, "qty": _int(order[2]),
                    "visible_price": _int((entry["obs"].get("market_prices") or {}).get(item, 0)),
                    "shed_qty": _int((entry["obs"].get("shed") or {}).get(item, 0)),
                })
    return out


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
    guard_events = c.get("room_guard_events") or []
    return {
        "first_action_mismatch": idx, "step": b["step"], "day": b["obs"]["day"], "hour": b["obs"]["hour"],
        "same_observation": b["obs_hash"] == c["obs_hash"],
        "champion_action": b["action"], "candidate_action": c["action"],
        "added_market_orders_final_action": added, "removed_market_orders_final_action": removed,
        "added_sell_items": added_sell_items, "room_guard_probe": guard_events,
        "market_inventory": b["obs"]["market_inventory"], "price_quote": b["obs"]["market_prices"],
        "town_shop_context": {
            "unlocked_shops": b["obs"]["town_shops"],
            "consumption_clock": b["obs"]["town_consumption_clock"],
        },
        "future_sell_evidence_next_96": future,
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
        baseline = run(args.v115, args.v115, seed, seat, probe_room_guard=False)
        candidate = run(args.candidate, args.v115, seed, seat, probe_room_guard=True)
        divergence = first_div(baseline, candidate)
        if divergence["first_action_mismatch"] is None:
            raise AssertionError(f"expected v115/v144 action divergence missing seed={seed} seat={seat}")
        if not divergence.get("room_guard_probe"):
            raise AssertionError(
                f"first divergence was not accompanied by room_guard telemetry seed={seed} seat={seat} step={divergence.get('step')}"
            )
        rows.append({
            "seed": seed, "seat": seat, "candidate_direct_margin": candidate["margin"],
            "candidate_minus_selfplay_focal_money": candidate["focal_reward"] - baseline["focal_reward"],
            "candidate_minus_selfplay_rival_money": candidate["rival_reward"] - baseline["rival_reward"],
            "candidate_minus_selfplay_margin": candidate["margin"] - baseline["margin"],
            "baseline_focal_money": baseline["focal_reward"], "baseline_rival_money": baseline["rival_reward"],
            "baseline_margin": baseline["margin"], "candidate_focal_money": candidate["focal_reward"],
            "candidate_rival_money": candidate["rival_reward"], "baseline_trace_len": baseline["trace_len"],
            "candidate_trace_len": candidate["trace_len"], "baseline_statuses": baseline["statuses"],
            "candidate_statuses": candidate["statuses"], "baseline_exceptions": baseline["exceptions"],
            "candidate_exceptions": candidate["exceptions"], "divergence": divergence,
        })

    screen_validation = {}
    for seed, expected in EXPECTED_SCREEN_PAIR_CASH_DELTA.items():
        seat_rows = [r for r in rows if r["seed"] == seed]
        if len(seat_rows) != 2:
            raise AssertionError(f"missing seat rows for seed={seed}: {len(seat_rows)}")
        observed = sum(r["candidate_direct_margin"] for r in seat_rows) / 2.0
        seat_margins = [r["candidate_direct_margin"] for r in seat_rows]
        screen_validation[str(seed)] = {
            "expected_pair_cash_delta": expected, "observed_pair_cash_delta": observed,
            "seat_direct_margins": seat_margins,
        }
        if observed != expected:
            raise AssertionError(
                f"candidate screen pair delta mismatch seed={seed}: got={observed} expected={expected}; seat_margins={seat_margins}"
            )

    out = {
        "purpose": "burned public-room-guard causal telemetry; not promotion evidence",
        "candidate": "v144_public_room_guard", "champion": "exact_v115",
        "engine": "kaggle_environments==1.32.7",
        "diff_convention": "candidate_minus_champion = candidate - champion",
        "validation": "average of the two candidate-v115 direct seat margins must reproduce the original direct-screen pair cash delta",
        "screen_validation": screen_validation, "rows": rows,
    }
    dst = Path(args.out)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
