from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from types import MethodType, SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval import resolve_agent


def chassis_from(spec: str):
    agent = resolve_agent(spec)
    glb = getattr(agent, "__globals__", None) or {}
    cls = glb.get("Chassis")
    if cls is None or not hasattr(cls, "_room_guard"):
        raise AssertionError(f"Chassis._room_guard missing in {spec}")
    return cls


def make_instance(cls, future: dict[str, int]):
    obj = object.__new__(cls)
    obj.cfg = {"turns_per_day": 24, "shed_capacity": 100, "max_orders": 10}

    def future_sells(self, route, item, step):
        return max(0, int(future.get(item, 0)))

    obj.future_sells = MethodType(future_sells, obj)
    return obj


def make_view(*, shed: dict[str, int], prices: dict[str, int], carried: int = 0):
    invs = [] if carried <= 0 else [{"WHEAT": carried}]
    return SimpleNamespace(
        shed=dict(shed),
        prices=dict(prices),
        invs=invs,
        positions=[],
        tiles=[],
    )


def action(market: list[list[Any]] | None = None):
    return {"farmer": ["PASS"], "hands": [], "market": copy.deepcopy(market or [])}


def sells(a: dict[str, Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for o in a.get("market") or []:
        if o and len(o) >= 3 and o[0] == "SELL":
            out[str(o[1])] = out.get(str(o[1]), 0) + int(o[2])
    return out


def run_guard(cls, *, shed, prices, future, carried=0, market=None, step=23):
    inst = make_instance(cls, future)
    a = action(market)
    v = make_view(shed=shed, prices=prices, carried=carried)
    cls._room_guard(inst, a, v, "R", step)
    return a


def check(v144_cls, v146_cls):
    results: dict[str, Any] = {}

    # 1. No overflow: both guards must be no-ops.
    kwargs = dict(
        shed={"WOOL": 40, "MILK": 40},
        prices={"WOOL": 200, "MILK": 160},
        future={"WOOL": 40, "MILK": 20},
        carried=10,
    )
    a144 = run_guard(v144_cls, **kwargs)
    a146 = run_guard(v146_cls, **kwargs)
    assert sells(a144) == {} and sells(a146) == {}, (a144, a146)
    results["no_overflow_noop"] = True

    # 2. Dead/free stock alone resolves overflow: v146 must not touch reserved WOOL.
    # projected=95 shed + 10 carried => needed=6 to target capacity-1=99.
    # WOOL is fully reserved (75/75); MILK has 10 free units (20 shed - 10 future).
    kwargs = dict(
        shed={"WOOL": 75, "MILK": 20},
        prices={"WOOL": 200, "MILK": 160},
        future={"WOOL": 75, "MILK": 10},
        carried=10,
    )
    a144 = run_guard(v144_cls, **kwargs)
    a146 = run_guard(v146_cls, **kwargs)
    s144, s146 = sells(a144), sells(a146)
    assert s144 == {"WOOL": 6}, s144
    assert s146 == {"MILK": 6}, s146
    results["reserve_avoided_when_free_excess_sufficient"] = {"v144": s144, "v146": s146}

    # 3. Free stock insufficient: v146 must use free excess first, then reserved stock.
    # MILK has only 2 free units, so the remaining 4 must come from reserved stock.
    kwargs = dict(
        shed={"WOOL": 75, "MILK": 20},
        prices={"WOOL": 200, "MILK": 160},
        future={"WOOL": 75, "MILK": 18},
        carried=10,
    )
    a146 = run_guard(v146_cls, **kwargs)
    s146 = sells(a146)
    assert sum(s146.values()) == 6, s146
    assert s146.get("MILK", 0) == 2, s146
    assert s146.get("WOOL", 0) == 4, s146
    results["fallback_preserves_overflow_safety"] = s146

    # 4. All stock reserved: first pass sells nothing; fallback must still resolve all need.
    kwargs = dict(
        shed={"WOOL": 75, "MILK": 20},
        prices={"WOOL": 200, "MILK": 160},
        future={"WOOL": 75, "MILK": 20},
        carried=10,
    )
    a146 = run_guard(v146_cls, **kwargs)
    s146 = sells(a146)
    assert s146 == {"WOOL": 6}, s146
    results["all_reserved_fallback"] = s146

    # 5. Existing current-turn SELL must reduce both overflow need and availability.
    # Before the guard, SELL MILK 4 is fillable, so projected 105 becomes 101 and guard need=2.
    kwargs = dict(
        shed={"WOOL": 75, "MILK": 20},
        prices={"WOOL": 200, "MILK": 160},
        future={"WOOL": 75, "MILK": 10},
        carried=10,
        market=[["SELL", "MILK", 4]],
    )
    a146 = run_guard(v146_cls, **kwargs)
    s146 = sells(a146)
    assert s146 == {"MILK": 6}, s146  # existing 4 + guard 2, merged
    results["current_turn_sell_accounted"] = s146

    # 6. Not hour 23: guard must remain inactive even under pressure.
    kwargs = dict(
        shed={"WOOL": 75, "MILK": 20},
        prices={"WOOL": 200, "MILK": 160},
        future={"WOOL": 75, "MILK": 10},
        carried=10,
        step=22,
    )
    a146 = run_guard(v146_cls, **kwargs)
    assert sells(a146) == {}, a146
    results["non_close_noop"] = True

    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v144", required=True)
    ap.add_argument("--v146", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()

    result = {
        "purpose": "focused synthetic validation for gated v146 planned-SELL reserve; not promotion evidence",
        "tests": check(chassis_from(args.v144), chassis_from(args.v146)),
    }
    text = json.dumps(result, indent=2)
    print(text)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
