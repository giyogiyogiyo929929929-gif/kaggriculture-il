#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

SOURCE_SHA256 = "114d765d37875afb252466f25381dc3d44ee5c92466f96e638c365d26b691d40"
OLD = """        def _draw_before_due(due):
            for u in range(step,due):
                if u%24==0 and any(item in _RACE_SHOPS.get(s,()) for s in _shops):
                    return True
            return False
"""
NEW = """        def _draw_before_due(due):
            # The observation/action at `step` is after that turn's town consumption.
            # Only a town-center tick strictly after the current action can consume
            # inventory before a planned SELL due on a later turn.
            for u in range(step+1,due):
                if u%24==0 and any(item in _RACE_SHOPS.get(s,()) for s in _shops):
                    return True
            return False
"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    raw = Path(args.source).read_bytes()
    got = sha(raw)
    if got != SOURCE_SHA256:
        raise RuntimeError(f"unexpected v133 center-only sha256: {got}")

    text = raw.decode("utf-8")
    if text.count(OLD) != 1:
        raise RuntimeError(f"expected exactly one v133 draw-before-due block, got {text.count(OLD)}")

    body = text.replace(OLD, NEW)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body.encode("utf-8"))
    compile(body, str(out), "exec")
    print(f"v134_sha256={sha(out.read_bytes())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
