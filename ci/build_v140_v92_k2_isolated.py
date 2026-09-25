from __future__ import annotations
import argparse, hashlib
from pathlib import Path
OLD = "votes = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= _V92_P_K)"
NEW = "votes = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= 2)"
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source'); ap.add_argument('output'); a=ap.parse_args()
    p=Path(a.source); text=p.read_text(encoding='utf-8')
    if hashlib.sha256(p.read_bytes()).hexdigest()!='c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2': raise SystemExit('exact v115 sha mismatch')
    if text.count(OLD)!=1 or text.count('_V92_P_K = 1')!=1: raise SystemExit('unexpected exact source')
    text=text.replace(OLD,NEW,1); out=Path(a.output); out.write_text(text,encoding='utf-8')
    print('v140_sha256='+hashlib.sha256(out.read_bytes()).hexdigest())
if __name__=='__main__': main()
