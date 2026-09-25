from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = 'c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2'

def sha(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('champion'); ap.add_argument('out'); a=ap.parse_args()
    s=Path(a.champion).read_text(encoding='utf-8')
    got=sha(s)
    if got!=V115_SHA256: raise SystemExit(f'v115 sha mismatch {got}')
    # Change the primary V92 predictor threshold only.
    if s.count('_V92_P_K = 1')!=1: raise SystemExit('unexpected primary K declaration count')
    s=s.replace('_V92_P_K = 1','_V92_P_K = 2',1)
    # The same global constant is also consumed by the later KIL-v52 preempt wrapper.
    # Preserve that inherited wrapper at its v115 K=1 contract explicitly, so this
    # candidate isolates only the primary V92 predictor.
    old='''        if not any(sum(event.get((target + off, index), 0) for off in (3, 4, 5, 6, 7)) >= _V92_P_K\n                   for event in best):'''
    new='''        if not any(sum(event.get((target + off, index), 0) for off in (3, 4, 5, 6, 7)) >= 1\n                   for event in best):'''
    if s.count(old)!=1: raise SystemExit(f'unexpected KIL K target count {s.count(old)}')
    s=s.replace(old,new,1)
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(s,encoding='utf-8')
    print('v140_sha256='+sha(s)); print('v140_bytes='+str(len(s.encode('utf-8'))))

if __name__=='__main__': main()
