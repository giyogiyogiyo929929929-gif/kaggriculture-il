from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"
V130_SHA256 = "6e673773e76eb0ebb0b561570da10c5125193ca30681f14aac63d83ae5a1f976"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('base'); ap.add_argument('out'); a=ap.parse_args()
    base=Path(a.base); out=Path(a.out)
    got=sha256(base)
    if got != V115_SHA256:
        raise SystemExit(f"v115 sha256 mismatch: {got} != {V115_SHA256}")
    s=base.read_text(encoding='utf-8')
    old="    for item in sorted({it for _,it,_ in plan},key=lambda it:-int(prices.get(it,0))):"
    new="""    # v130: the earlier R37 quote-priority layer runs before _adv_apply, so newly
    # advanced SELLs would otherwise be ordered only by headline price. Rank just
    # these candidate items by the same public-state quote-exposure model already
    # used by v115, without changing quantities, horizon, or native route orders.
    def _adv_priority(it):
        avail=max(0,int(stock.get(it,0))-selling.get(it,0))
        q=min(avail,sum(q for _,item,q in plan if item==it))
        return _r37_quote_priority(obs,['SELL',it,q],stock)
    for item in sorted({it for _,it,_ in plan},key=_adv_priority,reverse=True):"""
    if s.count(old) != 1:
        raise SystemExit(f'expected exactly one ADV ordering target, got {s.count(old)}')
    s=s.replace(old,new,1)
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(s,encoding='utf-8')
    got=sha256(out)
    if got != V130_SHA256:
        raise SystemExit(f"v130 sha256 mismatch: {got} != {V130_SHA256}")
    print(f'v130_sha256={got}')
    print(f'v130_bytes={out.stat().st_size}')

if __name__=='__main__': main()
