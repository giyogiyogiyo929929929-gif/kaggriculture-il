from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

NEEDLE = '''        qty = min(int(stock.get(item, 0)), ours)\n        if qty > 0:\n'''
REPLACEMENT = '''        qty = min(int(stock.get(item, 0)), ours)\n        # v142: keep v115 at zero quote exposure (typically the price floor),\n        # where an early one-unit sale cannot front-run a meaningful rival quote\n        # and may still be useful for cash/shed clearing. For a one-unit preempt\n        # with positive quote exposure, require stronger replay evidence: at least\n        # one top replay predicts >=2 units over the immediate two-turn window.\n        if qty == 1 and _r37_quote_priority(obs, ["SELL", item, qty], stock) > 0 and not any(\n            ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= 2\n            for ev in best\n        ):\n            continue\n        if qty > 0:\n'''


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
    print(f"v142_sha256={hashlib.sha256(dst.read_bytes()).hexdigest()}")
    print(f"v142_bytes={dst.stat().st_size}")
    print("change=primary V92 only: positive-exposure qty1 weak-prediction abstention")
    print("zero_exposure=v115 behavior")
    print("multi_unit_preempt=v115 behavior")
    print("kil_v52=_V92_P_K=1 preserved")


if __name__ == "__main__":
    main()
