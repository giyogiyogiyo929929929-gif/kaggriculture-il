from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V125D_SHA256 = "9c40d37d8d6999e230a5be451f6a663fd86a6f1947e8ef9948014a779592ea40"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('base'); ap.add_argument('out'); a=ap.parse_args()
    base=Path(a.base); out=Path(a.out)
    got=sha256(base)
    if got != V115_SHA256:
        raise SystemExit(f"v115 sha256 mismatch: {got} != {V115_SHA256}")
    s=base.read_text(encoding='utf-8')
    old='            take=min(q,avail);booked.append((t,item,take));n+=take;avail-=take'
    new='            take=min(q,avail,max(0,1-added-n));booked.append((t,item,take));n+=take;avail-=take'
    if s.count(old) != 1:
        raise SystemExit(f'expected exactly one ADV take target, got {s.count(old)}')
    s=s.replace(old,new,1)
    s += "\n# v125d candidate: one-unit cap only; inherited non-booking semantics preserved.\nkaggle_submission_agent_v125d = agent\n"
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(s,encoding='utf-8')
    got=sha256(out)
    if got != V125D_SHA256:
        raise SystemExit(f"v125d sha256 mismatch: {got} != {V125D_SHA256}")
    print(f'v125d_sha256={got}')
    print(f'v125d_bytes={out.stat().st_size}')

if __name__=='__main__': main()
