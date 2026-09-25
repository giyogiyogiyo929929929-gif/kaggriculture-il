from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

NEEDLE = "'room_guard': False"
REPLACEMENT = "'room_guard': True"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    args = ap.parse_args()

    src = Path(args.source)
    dst = Path(args.output)
    text = src.read_text(encoding="utf-8")

    # v144 is intentionally one public-notebook-derived change only.
    # Fail closed if exact-v115 no longer has the dormant switch, so we never
    # accidentally duplicate a mechanism or patch an unrelated occurrence.
    if text.count(NEEDLE) != 1:
        raise SystemExit(
            f"expected exact-v115 to contain one disabled room_guard, found {text.count(NEEDLE)}"
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

    text = text.replace(NEEDLE, REPLACEMENT, 1)
    if text.count(REPLACEMENT) != 1 or NEEDLE in text:
        raise SystemExit("room_guard toggle replacement failed")

    dst.write_text(text, encoding="utf-8")
    print(f"v144_sha256={hashlib.sha256(dst.read_bytes()).hexdigest()}")
    print(f"v144_bytes={dst.stat().st_size}")
    print("change=public tetsutani room_guard only: False -> True")
    print("budget_guard=False preserved")
    print("clamp_sells=False preserved")
    print("dead_stock=False preserved")
    print("terminal_liquidation=False preserved")
    print("front_run=False preserved")


if __name__ == "__main__":
    main()
