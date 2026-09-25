from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V115_SHA256 = "c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(s: str, old: str, new: str) -> str:
    n=s.count(old)
    if n != 1:
        raise SystemExit(f"expected 1 target, got {n}: {old[:80]!r}")
    return s.replace(old,new,1)


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('base'); ap.add_argument('out'); a=ap.parse_args()
    base=Path(a.base); out=Path(a.out)
    if sha256(base) != V115_SHA256:
        raise SystemExit('not exact v115')
    s=base.read_text(encoding='utf-8')
    s=replace_once(s,'_ADV_BOOK=False','_ADV_BOOK=True')
    s=replace_once(s,
        "                if _ADV_SUBTRACT_DEBTS:q-=debts.get(t,{}).get(o[1],0)   # already reserved by the sale-reservation layer\n                if q>0:plan.append((t,o[1],q))",
        "                if debts.get(t,{}).get(o[1],0)>0:\n                    continue\n                if q>0:plan.append((t,o[1],q))")
    s=replace_once(s,
        '            take=min(q,avail);booked.append((t,item,take));n+=take;avail-=take',
        '            take=min(q,avail,max(0,1-added-n));booked.append((t,item,take));n+=take;avail-=take')
    s=replace_once(s,
        '_ADV_REPORT=dict(adv_turns=0,adv_units=0,adv_errors=0)',
        '_ADV_REPORT=dict(adv_turns=0,adv_units=0,adv_errors=0)\n_ADV_EVENTS=[]')
    s=replace_once(s,
        "    _ADV_REPORT['adv_turns']+=1;_ADV_REPORT['adv_units']+=added\n    return dict(action,market=extra+market)",
        "    _ADV_REPORT['adv_turns']+=1;_ADV_REPORT['adv_units']+=added\n    _ADV_EVENTS.append({'step':step,'player':player,'booked':[list(x) for x in booked if x[2]>0],\n                        'prices':{it:int(prices.get(it,0)) for _,it,take in booked if take>0},\n                        'stock':{it:int(stock.get(it,0)) for _,it,take in booked if take>0},\n                        'selling_before':dict(selling),'market_before':[list(o) for o in (action.get('market') or [])],\n                        'market_after':[list(o) for o in (extra+market)]})\n    return dict(action,market=extra+market)")
    s += "\n# telemetry-only alias; behavior is v125c.\nkaggle_submission_agent_v125c_telemetry = agent\n"
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(s,encoding='utf-8')
    print('telemetry_sha256='+sha256(out))

if __name__=='__main__': main()
