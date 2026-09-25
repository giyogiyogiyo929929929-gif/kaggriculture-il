from __future__ import annotations
import argparse, hashlib
from pathlib import Path

V115_SHA='c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2'
OLD="votes = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= _V92_P_K)"
NEW="votes = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= (1 if item == \"WOOL\" else 2))"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source'); ap.add_argument('output'); a=ap.parse_args()
    src=Path(a.source)
    if hashlib.sha256(src.read_bytes()).hexdigest()!=V115_SHA: raise SystemExit('exact v115 sha mismatch')
    text=src.read_text(encoding='utf-8')
    if text.count(OLD)!=1: raise SystemExit(f'primary V92 target count={text.count(OLD)}')
    if text.count('_V92_P_K = 1')!=1: raise SystemExit('shared K constant not uniquely preserved')
    text=text.replace(OLD,NEW,1)
    out=Path(a.output); out.write_text(text,encoding='utf-8')
    print('v141_sha256='+hashlib.sha256(out.read_bytes()).hexdigest())
    print('change=primary V92 only; WOOL K1, MILK/STRAWBERRY K2; shared KIL constant remains K1')
if __name__=='__main__': main()
