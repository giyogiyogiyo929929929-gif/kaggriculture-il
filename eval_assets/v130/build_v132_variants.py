#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

SOURCE_SHA256 = "4c044ce934b55a9cb77dd16d87bdde5f29c9682dced3443b9dd8266113aba6b2"
EXPECTED = {
    "h2": "214e016a5830710f3da474ce945ac8bcf23c4c156d1edaeb6fbeaecb86a6a16f",
    "lastday": "2f0921f8131b75053031346137ce9a238414e3fb206b9c7cddc4a2f6982f10e6",
}
OLD_FILTER = "plan=[x for x in plan if not _draw_before_due(x[1],x[0])]"
NEW_FILTER_H2 = "plan=[x for x in plan if not ((x[0]-step)<=2 and _draw_before_due(x[1],x[0]))]"
OLD_GATE = "if step>=577 and _ADV_LATE_DRAW_GATE.get(player,False) and (float(obs['farms'][player]['money'])-float(obs['farms'][1-player]['money'])>=5000.0):"
NEW_GATE_LASTDAY = "if step>=577 and step<696 and _ADV_LATE_DRAW_GATE.get(player,False) and (float(obs['farms'][player]['money'])-float(obs['farms'][1-player]['money'])>=5000.0):"

def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--out-dir',required=True)
    args=ap.parse_args()
    src=Path(args.source)
    raw=src.read_bytes()
    if sha_bytes(raw)!=SOURCE_SHA256:
        raise RuntimeError(f"unexpected v131 sha256: {sha_bytes(raw)}")
    text=raw.decode('utf-8')
    if text.count(OLD_FILTER)!=1: raise RuntimeError(f"expected one filter, got {text.count(OLD_FILTER)}")
    if text.count(OLD_GATE)!=1: raise RuntimeError(f"expected one gate, got {text.count(OLD_GATE)}")
    variants={
        'h2': text.replace(OLD_FILTER,NEW_FILTER_H2),
        'lastday': text.replace(OLD_GATE,NEW_GATE_LASTDAY),
    }
    outdir=Path(args.out_dir); outdir.mkdir(parents=True,exist_ok=True)
    for name,body in variants.items():
        out=outdir/f"v132_{name}.py"
        out.write_text(body,encoding='utf-8')
        compile(body,str(out),'exec')
        got=sha_bytes(out.read_bytes())
        if got!=EXPECTED[name]: raise RuntimeError(f"{name} sha256 mismatch: {got}")
        print(f"{name}_sha256={got}")
    return 0

if __name__=='__main__': raise SystemExit(main())
