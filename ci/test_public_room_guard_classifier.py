from __future__ import annotations

from classify_public_room_guard_telemetry import classify_event


def event(*, shed: int, before: int, added: int, future: int):
    return {
        "action_before_guard": {"market": [["SELL", "MILK", before]] if before else []},
        "action_after_guard": {"market": [["SELL", "MILK", before + added]] if before + added else []},
        "current_shed": {"MILK": shed},
        "future_planned_sell_qty": {"MILK": future},
        "future_sell_schedule": {"MILK": ([{"step": 100, "qty": future}] if future else [])},
        "room_guard_fired": added > 0,
    }


def invaded(**kwargs) -> int:
    return classify_event(event(**kwargs))["future_reserve_invaded_qty_total"]


def main() -> None:
    # 20 unsold, 10 future reserve => 10 genuinely free. Selling 6 is safe.
    assert invaded(shed=20, before=0, added=6, future=10) == 0
    # Selling 12 uses 10 free + 2 reserved.
    assert invaded(shed=20, before=0, added=12, future=10) == 2
    # Current-turn SELL is removed before computing current reserved/free stock:
    # shed20 - current4 =16 unsold, future10 => free6; guard adds6 => safe.
    assert invaded(shed=20, before=4, added=6, future=10) == 0
    # No free stock: all guard units invade reserve.
    assert invaded(shed=20, before=0, added=6, future=20) == 6
    # Future commitment above current stock reserves only physically present stock.
    assert invaded(shed=20, before=0, added=6, future=30) == 6
    # No future commitment => no reserve invasion.
    assert invaded(shed=20, before=0, added=20, future=0) == 0
    print("classifier_reserve_invasion_tests=PASS")


if __name__ == "__main__":
    main()
