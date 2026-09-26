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
        for item in priority:
            avail = max(0, view.shed.get(item, 0) - planned_sells.get(item, 0))
            if avail <= 0:
                continue

            # v149: if this emergency sale would churn an item bought earlier in
            # the same turn, make room by shrinking that BUY_PRODUCT first. This
            # preserves the end-of-turn inventory effect without injecting extra
            # supply into the shared market. Reduce later duplicate buys first so
            # earlier order/race positions are disturbed as little as possible.
            to_net = min(needed, sum(max(0, _int(o[2])) for o in market
                                     if o and o[0] == "BUY_PRODUCT" and len(o) >= 3 and o[1] == item))
            if to_net > 0:
                remaining = to_net
                for o in reversed(market):
                    if remaining <= 0:
                        break
                    if not (o and o[0] == "BUY_PRODUCT" and len(o) >= 3 and o[1] == item):
                        continue
                    cut = min(remaining, max(0, _int(o[2])))
                    o[2] = max(0, _int(o[2]) - cut)
                    remaining -= cut
                needed -= to_net
                if needed <= 0:
                    break

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
        raise SystemExit(f"expected exact room_guard block once, found {text.count(OLD)}")
    text = text.replace(ROOM_OFF, ROOM_ON, 1).replace(OLD, NEW, 1)
    if text.count(ROOM_ON) != 1 or ROOM_OFF in text or OLD in text:
        raise SystemExit("v149 replacement validation failed")
    if text.count("v149: if this emergency sale") != 1:
        raise SystemExit("v149 localized change marker missing")
    dst.write_text(text, encoding="utf-8")
    print(f"v149_sha256={hashlib.sha256(dst.read_bytes()).hexdigest()}")
    print(f"v149_bytes={dst.stat().st_size}")
    print("change=room_guard enabled + same-item current-turn BUY_PRODUCT netting before emergency SELL")


if __name__ == "__main__":
    main()
