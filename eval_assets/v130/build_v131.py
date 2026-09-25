#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

SOURCE_SHA256 = "7a8e337b5651ba3bf0f805b588ba871ba1ad629f515e47bc4c42494862eacfa8"
V131_SHA256 = "4c044ce934b55a9cb77dd16d87bdde5f29c9682dced3443b9dd8266113aba6b2"
OLD = "if step>=577 and _ADV_LATE_DRAW_GATE.get(player,False):"
NEW = "if step>=577 and _ADV_LATE_DRAW_GATE.get(player,False) and (float(obs['farms'][player]['money'])-float(obs['farms'][1-player]['money'])>=5000.0):"

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--source',required=True); ap.add_argument('--out',required=True); args=ap.parse_args()
    src=Path(args.source); out=Path(args.out)
    if sha(src)!=SOURCE_SHA256: raise RuntimeError(f"unexpected v130 sha256: {sha(src)}")
    text=src.read_text(encoding='utf-8')
    if text.count(OLD)!=1: raise RuntimeError(f"expected exactly one gate, found {text.count(OLD)}")
    text=text.replace(OLD,NEW)
    out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(text.encode('utf-8'))
    compile(text,str(out),'exec')
    if sha(out)!=V131_SHA256: raise RuntimeError(f"v131 sha256 mismatch: {sha(out)}")
    print(f"v131_sha256={V131_SHA256}")
    return 0
if __name__=='__main__': raise SystemExit(main())
