from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOM_OFF = "'room_guard': False"
ROOM_ON = "'room_guard': True"

OLD = '''        priority = sorted(PRODUCTS, key=lambda it: (self.future_sells(route, it, step + 1) > 0,
                                                   -view.prices.get(it, 0), it))
        for item in priority:
            avail = max(0, view.shed.get(item, 0) - planned_sells.get(item, 0))
            qty = min(needed, avail)
            if qty <= 0 or view.prices.get(item, 0) < 1:
                continue
            if not self._add_sell(action, item, qty, cfg["max_orders"]):
                continue
            planned_sells[item] = planned_sells.get(item, 0) + qty
            needed -= qty
            if needed <= 0:
                break
'''

NEW = '''        priority = sorted(PRODUCTS, key=lambda it: (self.future_sells(route, it, step + 1) > 0,
                                                   -view.prices.get(it, 0), it))
        # v146 planned-SELL reserve: first use only stock above all later native
        # SELL commitments.  If that cannot make physical room, fall back to the
        # original priority and consume reserved stock rather than allow overflow.
        for protect_future in (True, False):
            for item in priority:
                avail = max(0, view.shed.get(item, 0) - planned_sells.get(item, 0))
                if protect_future:
                    reserve = max(0, self.future_sells(route, item, step + 1))
                    avail = max(0, avail - reserve)
                qty = min(needed, avail)
                if qty <= 0 or view.prices.get(item, 0) < 1:
                    continue
                if not self._add_sell(action, item, qty, cfg["max_orders"]):
                    continue
                planned_sells[item] = planned_sells.get(item, 0) + qty
                needed -= qty
                if needed <= 0:
                    return
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    args = ap.parse_args()

    src = Path(args.source)
    dst = Path(args.output)
    text = src.read_text(encoding="utf-8")

    if text.count(ROOM_OFF) != 1:
        raise SystemExit(f"expected one disabled room_guard, found {text.count(ROOM_OFF)}")
    if text.count(OLD) != 1:
        raise SystemExit(f"expected exact room_guard sell block once, found {text.count(OLD)}")

    text = text.replace(ROOM_OFF, ROOM_ON, 1)
    text = text.replace(OLD, NEW, 1)

    if text.count(ROOM_ON) != 1 or ROOM_OFF in text or OLD in text:
        raise SystemExit("v146 replacement validation failed")
    if text.count("for protect_future in (True, False):") != 1:
        raise SystemExit("v146 reserve loop validation failed")

    dst.write_text(text, encoding="utf-8")
    print(f"v146_sha256={hashlib.sha256(dst.read_bytes()).hexdigest()}")
    print(f"v146_bytes={dst.stat().st_size}")
    print("change=room_guard enabled + future planned SELL reserve first pass")
    print("fallback=original room_guard priority only if reserve-safe stock cannot make room")
    print("status=gated builder; do not treat as active candidate until telemetry gate opens")


if __name__ == "__main__":
    main()
