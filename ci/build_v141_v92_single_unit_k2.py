from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

NEEDLE = '''        qty = min(int(stock.get(item, 0)), ours)\n        if qty > 0:\n'''
REPLACEMENT = '''        qty = min(int(stock.get(item, 0)), ours)\n        # v141: preserve v115's multi-unit preempts.  Only a one-unit preempt\n        # needs stronger evidence: at least one top replay must predict >=2\n        # units over the immediate two-turn signal window.  Keep _V92_P_K=1\n        # globally so the independent KIL v52 path remains exactly v115.\n        if qty == 1 and not any(\n            ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= 2\n            for ev in best\n        ):\n            continue\n        if qty > 0:\n'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    args = ap.parse_args()

    src = Path(args.source)
    dst = Path(args.output)
    text = src.read_text(encoding="utf-8")
    if text.count(NEEDLE) != 1:
        raise SystemExit(f"expected one primary V92 qty block, found {text.count(NEEDLE)}")
    if text.count("_V92_P_K = 1") != 1:
        raise SystemExit("exact v115 _V92_P_K=1 not found uniquely")
    if text.count(">= _V92_P_K") != 2:
        raise SystemExit("expected primary V92 + KIL shared K references in exact v115")

    text = text.replace(NEEDLE, REPLACEMENT, 1)
    dst.write_text(text, encoding="utf-8")
    print(f"v141_sha256={hashlib.sha256(dst.read_bytes()).hexdigest()}")
    print(f"v141_bytes={dst.stat().st_size}")
    print("change=primary V92 only: weak prediction abstention when actual preempt qty == 1")
    print("multi_unit_preempt=v115 behavior")
    print("kil_v52=_V92_P_K=1 preserved")


if __name__ == "__main__":
    main()
