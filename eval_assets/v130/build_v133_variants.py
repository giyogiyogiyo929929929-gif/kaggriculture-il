#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

SOURCE_SHA256 = "2f0921f8131b75053031346137ce9a238414e3fb206b9c7cddc4a2f6982f10e6"
EXPECTED = {
    "center_only": "114d765d37875afb252466f25381dc3d44ee5c92466f96e638c365d26b691d40",
    "lead9000": "3b6f4cf55e6e4e6b7b7a29f2218e1bd641d7877ac2353179de830c4a7ff6b192",
}
SHOP_BRANCH = """                if u%4==0 and any(item in _RACE_SHOPS.get(s,()) for s in _shops):\n                    return True\n"""
GATE_5000 = "if step>=577 and step<696 and _ADV_LATE_DRAW_GATE.get(player,False) and (float(obs['farms'][player]['money'])-float(obs['farms'][1-player]['money'])>=5000.0):"
GATE_9000 = "if step>=577 and step<696 and _ADV_LATE_DRAW_GATE.get(player,False) and (float(obs['farms'][player]['money'])-float(obs['farms'][1-player]['money'])>=9000.0):"

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--out-dir',required=True)
    a=ap.parse_args()
    raw=Path(a.source).read_bytes()
    got=sha(raw)
    if got != SOURCE_SHA256:
        raise RuntimeError(f'unexpected v132_lastday sha256: {got}')
    text=raw.decode('utf-8')
    if text.count(SHOP_BRANCH)!=1:
        raise RuntimeError(f'expected one shop branch, got {text.count(SHOP_BRANCH)}')
    if text.count(GATE_5000)!=1:
        raise RuntimeError(f'expected one 5000 gate, got {text.count(GATE_5000)}')
    variants={
        'center_only': text.replace(SHOP_BRANCH,''),
        'lead9000': text.replace(GATE_5000,GATE_9000),
    }
    outdir=Path(a.out_dir); outdir.mkdir(parents=True,exist_ok=True)
    for name,body in variants.items():
        out=outdir/f'v133_{name}.py'
        out.write_text(body,encoding='utf-8')
        compile(body,str(out),'exec')
        digest=sha(out.read_bytes())
        if digest != EXPECTED[name]:
            raise RuntimeError(f'{name} sha256 mismatch: {digest}')
        print(f'{name}_sha256={digest}')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
