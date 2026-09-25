#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, statistics
from pathlib import Path
import kaggle_environments
from scripts.ci.run_exact_pair import _pair


def pct(xs, p):
    if not xs: return None
    ys=sorted(float(x) for x in xs); i=(len(ys)-1)*p; lo=int(i); hi=min(lo+1,len(ys)-1); f=i-lo
    return ys[lo]*(1-f)+ys[hi]*f

def stats(xs):
    if not xs: return {"n":0,"median":None,"p95":None,"p99":None,"max":None}
    return {"n":len(xs),"median":statistics.median(xs),"p95":pct(xs,.95),"p99":pct(xs,.99),"max":max(xs)}

def seat_margins(row):
    n=row['normal']['rewards']; s=row['swapped']['rewards']
    return float(n[0])-float(n[1]), float(s[1])-float(s[0])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidate',required=True); ap.add_argument('--champion',required=True); ap.add_argument('--opponent',required=True)
    ap.add_argument('--seeds',required=True,help='comma-separated integers'); ap.add_argument('--out',required=True)
    a=ap.parse_args(); seeds=[int(x) for x in a.seeds.split(',') if x.strip()]
    rows=[]; crt=[]; hrt=[]; cexc=hexc=0
    for seed in seeds:
        c=_pair(a.candidate,a.opponent,seed); h=_pair(a.champion,a.opponent,seed)
        c0,c1=seat_margins(c); h0,h1=seat_margins(h)
        d0=c0-h0; d1=c1-h1; pair=(d0+d1)/2.0
        ok=bool(c.get('ok')) and bool(h.get('ok'))
        ce=int(c.get('candidate_exceptions',0)); he=int(h.get('candidate_exceptions',0)); cexc+=ce; hexc+=he
        crt.extend(c.get('candidate_runtime_ms') or []); hrt.extend(h.get('candidate_runtime_ms') or [])
        rows.append({'seed':seed,'ok':ok,'candidate_minus_champion':pair,'seat0_diff':d0,'seat1_diff':d1,
                     'candidate_pair_margin':(c0+c1)/2.0,'champion_pair_margin':(h0+h1)/2.0,
                     'candidate_exceptions':ce,'champion_exceptions':he,
                     'candidate_statuses':[c['normal']['statuses'],c['swapped']['statuses']],
                     'champion_statuses':[h['normal']['statuses'],h['swapped']['statuses']]})
        print(json.dumps(rows[-1],sort_keys=True),flush=True)
    vals=[r['candidate_minus_champion'] for r in rows if r['ok']]
    n=len(vals); mean=statistics.mean(vals) if vals else None; se=(statistics.stdev(vals)/math.sqrt(n) if n>1 else 0.0 if n==1 else None)
    summary={'engine':getattr(kaggle_environments,'__version__','unknown'),'candidate':a.candidate,'champion':a.champion,'opponent':a.opponent,
             'seeds':seeds,'n':n,'wins':sum(v>0 for v in vals),'losses':sum(v<0 for v in vals),'draws':sum(v==0 for v in vals),
             'mean_candidate_minus_champion':mean,'se':se,'mean_minus_2se':(mean-2*se if mean is not None and se is not None else None),
             'worst_regression':min(vals) if vals else None,'best_improvement':max(vals) if vals else None,
             'seat0_mean':statistics.mean([r['seat0_diff'] for r in rows if r['ok']]) if vals else None,
             'seat1_mean':statistics.mean([r['seat1_diff'] for r in rows if r['ok']]) if vals else None,
             'candidate_runtime_ms':stats(crt),'champion_runtime_ms':stats(hrt),'candidate_exceptions':cexc,'champion_exceptions':hexc,
             'rows':rows}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2))
    if n!=len(seeds) or cexc or hexc: raise SystemExit(2)
if __name__=='__main__': main()
