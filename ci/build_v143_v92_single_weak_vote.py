from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

NEEDLE = '''        qty = min(int(stock.get(item, 0)), ours)\n        if qty > 0:\n'''
REPLACEMENT = '''        qty = min(int(stock.get(item, 0)), ours)\n        # v143: abstain only when exactly one replay gives a weak one-unit\n        # immediate forecast and the order has positive quote exposure.\n        # Burned stress showed unanimous [1,1,1] weak forecasts should keep\n        # v115 behavior, while the beneficial seed651 case was [0,0,1].\n        if qty == 1 and _r37_quote_priority(obs, ["SELL", item, qty], stock) > 0:\n            _v143_preds = [\n                ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0)\n                for ev in best\n            ]\n            if (\n                sum(1 for x in _v143_preds if x >= 1) == 1\n                and not any(x >= 2 for x in _v143_preds)\n            ):\n                continue\n        if qty > 0:\n'''


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
    print(f"v143_sha256={hashlib.sha256(dst.read_bytes()).hexdigest()}")
    print(f"v143_bytes={dst.stat().st_size}")
    print("change=primary V92 only: positive-exposure qty1 abstention only for exactly one weak vote")
    print("unanimous_weak_votes=v115 behavior")
    print("zero_exposure=v115 behavior")
    print("multi_unit_preempt=v115 behavior")
    print("kil_v52=_V92_P_K=1 preserved")


if __name__ == "__main__":
    main()
