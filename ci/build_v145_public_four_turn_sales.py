from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

NEEDLE = "    end=min(695,step+_R37_HORIZONS.get(int(obs['player']),2),(step//72+1)*72-1)\n"
REPLACEMENT = """    # v145: public V36 / Market-Smart-derived guarded four-turn reservation.\n    # Only extend the sale lookahead inside the published safe window; keep\n    # the existing stock, debt, purchase, block-boundary and terminal guards.\n    _v145_horizon = _R37_HORIZONS.get(int(obs['player']), 2)\n    if 288 <= step < 696:\n        _v145_horizon = max(_v145_horizon, 4)\n    end=min(695,step+_v145_horizon,(step//72+1)*72-1)\n"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    args = ap.parse_args()

    src = Path(args.source)
    dst = Path(args.output)
    text = src.read_text(encoding="utf-8")

    # Fail closed: exact-v115 must expose exactly the same R37 sale-window
    # expression as the audited public lineage.  If v115 already changed this
    # mechanism, do not create an ambiguous candidate.
    count = text.count(NEEDLE)
    if count != 1:
        raise SystemExit(f"expected one R37 horizon expression in exact v115, found {count}")
    if "_v145_horizon" in text:
        raise SystemExit("v145 marker already present")
    if "if 288 <= step < 696:_R37_HORIZONS" in text:
        raise SystemExit("exact v115 already appears to contain public four-turn override")

    text = text.replace(NEEDLE, REPLACEMENT, 1)
    dst.write_text(text, encoding="utf-8")

    print(f"v145_sha256={hashlib.sha256(dst.read_bytes()).hexdigest()}")
    print(f"v145_bytes={dst.stat().st_size}")
    print("change=R37 eligible-sale horizon only: max(existing,4) on steps 288..695")
    print("existing_stock_debt_purchase_boundary_terminal_guards=preserved")


if __name__ == "__main__":
    main()
