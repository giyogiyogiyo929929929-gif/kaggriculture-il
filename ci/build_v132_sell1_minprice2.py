#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source'); ap.add_argument('out'); a=ap.parse_args()
    s=Path(a.source).read_text(encoding='utf-8')
    needle="    due,item,orig_q,orig_idx=target\n"
    insert="""    due,item,orig_q,orig_idx=target
    # Preserve v115/EXP293 minimum sale-price safety contract.
    try:
        if int((obs.get('market') or {}).get('prices',{}).get(item,0)) < 2:
            if changed:
                out=dict(action);out['market']=market;return out
            return action
    except Exception:
        if changed:
            out=dict(action);out['market']=market;return out
        return action
"""
    if s.count(needle)!=1: raise SystemExit(f'expected one insertion point, got {s.count(needle)}')
    out=Path(a.out); out.write_text(s.replace(needle,insert),encoding='utf-8')
    expected='d62360c16f4229976695714ee233b858d6b0ad703464244285312b1cf6689209'
    got=sha(out)
    if got!=expected: raise SystemExit(f'v132 sha mismatch {got} != {expected}')
    print(f'v132_sha256={got}')
if __name__=='__main__': main()
