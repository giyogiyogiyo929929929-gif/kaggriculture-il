#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

SOURCE_SHA256 = "114d765d37875afb252466f25381dc3d44ee5c92466f96e638c365d26b691d40"
EXPECTED_SHA256 = "d676ecb5da84b1e40c132c3335c135a03ac7789702b6de68cebe242f0f409267"
OLD_LOOP = "            for u in range(step,due):"
NEW_LOOP = "            for u in range(step+1,due):"

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--out',required=True)
    a=ap.parse_args()
    raw=Path(a.source).read_bytes()
    got=sha(raw)
    if got != SOURCE_SHA256:
        raise RuntimeError(f'unexpected v133_center_only sha256: {got}')
    text=raw.decode('utf-8')
    if text.count(OLD_LOOP)!=1:
        raise RuntimeError(f'expected one town loop, got {text.count(OLD_LOOP)}')
    body=text.replace(OLD_LOOP,NEW_LOOP)
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(body,encoding='utf-8')
    compile(body,str(out),'exec')
    digest=sha(out.read_bytes())
    if digest != EXPECTED_SHA256:
        raise RuntimeError(f'v134 sha256 mismatch: {digest}')
    print(f'v134_sha256={digest}')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
