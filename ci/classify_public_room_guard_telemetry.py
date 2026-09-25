from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# Canonical values re-read from formal screen artifact 10865546301.
# Key is (seed, focal seat); value is v144-v115 direct final-cash margin.
EXPECTED_DIRECT_MARGIN = {
    (683, 0): 492.0,
    (683, 1): 492.0,
    (689, 0): -84.0,
    (689, 1): -84.0,
    (693, 0): 479.0,
    (693, 1): 479.0,
}


def _int(v: Any) -> int:
    try:
        return int(v)
    except Exception:
        return 0


def _sell_qty(action: Any) -> dict[str, int]:
    out: dict[str, int] = {}
    if not isinstance(action, dict):
        return out
    for order in action.get("market") or []:
        if order and len(order) >= 3 and str(order[0]).upper() == "SELL":
            item = str(order[1])
            out[item] = out.get(item, 0) + max(0, _int(order[2]))
    return out


def classify_event(event: dict[str, Any]) -> dict[str, Any]:
    before = _sell_qty(event.get("action_before_guard"))
    after = _sell_qty(event.get("action_after_guard"))
    shed = event.get("current_shed") or {}
    future = event.get("future_planned_sell_qty") or {}
    schedule = event.get("future_sell_schedule") or {}

    items = sorted(set(before) | set(after) | set(shed) | set(future))
    detail: dict[str, Any] = {}
    total_added = 0
    total_reserve_invaded = 0
    for item in items:
        added = max(0, after.get(item, 0) - before.get(item, 0))
        if added <= 0:
            continue
        current_unsold = max(0, _int(shed.get(item, 0)) - before.get(item, 0))
        future_qty = max(0, _int(future.get(item, 0)))
        reserved_current = min(current_unsold, future_qty)
        free_excess = max(0, current_unsold - reserved_current)
        # Only the guard quantity above currently-free stock invades inventory
        # committed to later native SELLs.  Merely having a future SELL is not
        # enough to classify an emergency SELL as reserve invasion.
        invaded = min(reserved_current, max(0, added - free_excess))
        total_added += added
        total_reserve_invaded += invaded
        detail[item] = {
            "guard_added_sell_qty": added,
            "shed_qty_before_guard": _int(shed.get(item, 0)),
            "current_sell_before_guard": before.get(item, 0),
            "current_unsold_before_guard": current_unsold,
            "future_planned_sell_qty": future_qty,
            "current_reserved_qty": reserved_current,
            "free_excess": free_excess,
            "future_reserve_invaded_qty": invaded,
            "has_later_native_sell": bool(schedule.get(item)),
            "future_sell_schedule": schedule.get(item) or [],
        }

    return {
        "room_guard_fired": bool(event.get("room_guard_fired")),
        "guard_added_sell_qty_total": total_added,
        "future_reserve_invaded_qty_total": total_reserve_invaded,
        "planned_sell_reserve_invaded": total_reserve_invaded > 0,
        "items": detail,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("telemetry_json")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    src = json.loads(Path(args.telemetry_json).read_text(encoding="utf-8"))
    rows = src.get("rows") or []
    by_case = {(int(r["seed"]), int(r["seat"])): r for r in rows}

    missing = sorted(set(EXPECTED_DIRECT_MARGIN) - set(by_case))
    if missing:
        raise AssertionError(f"missing telemetry cases: {missing}")

    cases = []
    for key, expected in sorted(EXPECTED_DIRECT_MARGIN.items()):
        row = by_case[key]
        observed = float(row["candidate_direct_margin"])
        if observed != expected:
            raise AssertionError(
                f"formal direct-screen seat mismatch seed={key[0]} seat={key[1]}: "
                f"got={observed} expected={expected}"
            )
        div = row.get("divergence") or {}
        events = div.get("room_guard_probe") or []
        if not events:
            raise AssertionError(f"no room_guard event at first divergence seed={key[0]} seat={key[1]}")
        classified = [classify_event(e) for e in events]
        cases.append({
            "seed": key[0],
            "seat": key[1],
            "candidate_direct_margin": observed,
            "first_divergence_step": div.get("step"),
            "same_observation_at_divergence": div.get("same_observation"),
            "events": classified,
            "reserve_invaded_qty_total": sum(e["future_reserve_invaded_qty_total"] for e in classified),
        })

    def case(seed: int, seat: int) -> dict[str, Any]:
        return next(c for c in cases if c["seed"] == seed and c["seat"] == seat)

    regression = [case(689, 0), case(689, 1)]
    positive_controls = [case(683, 0), case(683, 1), case(693, 0), case(693, 1)]
    regression_both_invade = all(c["reserve_invaded_qty_total"] > 0 for c in regression)
    control_invaded_cases = sum(c["reserve_invaded_qty_total"] > 0 for c in positive_controls)

    out = {
        "purpose": "causal gate for v144 planned-SELL-reserve hypothesis; burned seeds only",
        "formal_screen_seat_validation": "passed",
        "cases": cases,
        "seed689_both_seats_invade_future_reserve": regression_both_invade,
        "positive_control_invaded_case_count": control_invaded_cases,
        "planned_sell_reserve_candidate_gate": (
            "OPEN_FOR_V146_BURNED_COUNTERFACTUAL" if regression_both_invade else "NOT_CONFIRMED"
        ),
        "interpretation": (
            "Gate opening means the regression case mechanically consumes inventory committed to later native SELLs. "
            "It does not by itself prove that this caused the -84; v146 burned-seed counterfactual must test causality."
        ),
    }
    dst = Path(args.out)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
