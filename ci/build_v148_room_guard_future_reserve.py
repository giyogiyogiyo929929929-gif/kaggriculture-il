from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOM_OFF = "'room_guard': False"
ROOM_ON = "'room_guard': True"
AVAIL_OLD = "avail = max(0, view.shed.get(item, 0) - planned_sells.get(item, 0))"
AVAIL_NEW = (
    "avail = max(0, view.shed.get(item, 0) - planned_sells.get(item, 0) "
    "- self.future_sells(route, item, step + 1))"
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    args = ap.parse_args()

    src = Path(args.source)
    dst = Path(args.output)
    text = src.read_text(encoding="utf-8")

    # v148 is deliberately v144 plus one localized safety restriction:
    # room_guard may sell only stock above all future planned SELL quantity.
    # Everything else, including the existing v115 SHEDROOM wrapper, is untouched.
    if text.count(ROOM_OFF) != 1:
        raise SystemExit(
            f"expected exact-v115 to contain one disabled room_guard, found {text.count(ROOM_OFF)}"
        )
    if text.count(AVAIL_OLD) != 1:
        raise SystemExit(
            f"expected one room_guard availability expression, found {text.count(AVAIL_OLD)}"
        )
    for unchanged in (
        "'budget_guard': False",
        "'clamp_sells': False",
        "'dead_stock': False",
        "'terminal_liquidation': False",
        "'front_run': False",
    ):
        if text.count(unchanged) != 1:
            raise SystemExit(f"expected one unchanged dormant switch: {unchanged}")

    text = text.replace(ROOM_OFF, ROOM_ON, 1)
    text = text.replace(AVAIL_OLD, AVAIL_NEW, 1)

    if text.count(ROOM_ON) != 1 or ROOM_OFF in text:
        raise SystemExit("room_guard toggle replacement failed")
    if text.count(AVAIL_NEW) != 1 or AVAIL_OLD in text:
        raise SystemExit("room_guard future-sell reserve replacement failed")

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"v148_sha256={hashlib.sha256(dst.read_bytes()).hexdigest()}")
    print(f"v148_bytes={dst.stat().st_size}")
    print("change_1=public room_guard False -> True")
    print("change_2=room_guard avail reserves future planned SELL quantity")
    print("budget_guard=False preserved")
    print("clamp_sells=False preserved")
    print("dead_stock=False preserved")
    print("terminal_liquidation=False preserved")
    print("front_run=False preserved")


if __name__ == "__main__":
    main()
