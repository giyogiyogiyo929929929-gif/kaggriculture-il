#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, statistics
from pathlib import Path


def _margin(row: dict, seat: int) -> float:
    if seat == 0:
        r = row["normal"]["rewards"]
        return float(r[0]) - float(r[1])
    r = row["swapped"]["rewards"]
    return float(r[1]) - float(r[0])


def _runtime(rows: list[dict]) -> list[float]:
    out=[]
    for row in rows:
        out.extend(float(x) for x in row.get("candidate_runtime_ms", []))
    return out


def _pct(xs: list[float], q: float) -> float:
    if not xs: return 0.0
    ys=sorted(xs); k=(len(ys)-1)*q; lo=math.floor(k); hi=math.ceil(k)
    if lo==hi: return ys[lo]
    return ys[lo]*(hi-k)+ys[hi]*(k-lo)


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate-json", required=True)
    ap.add_argument("--champion-json", required=True)
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--out", required=True)
    args=ap.parse_args()
    cand=json.loads(Path(args.candidate_json).read_text(encoding="utf-8"))
    champ=json.loads(Path(args.champion_json).read_text(encoding="utf-8"))
    cm={int(r["seed"]):r for r in cand}; hm={int(r["seed"]):r for r in champ}
    seeds=sorted(set(cm)&set(hm))
    rows=[]
    for seed in seeds:
        c,h=cm[seed],hm[seed]
        s0=_margin(c,0)-_margin(h,0)
        s1=_margin(c,1)-_margin(h,1)
        d=(s0+s1)/2.0
        rows.append({"seed":seed,"seat0_candidate_minus_champion":s0,"seat1_candidate_minus_champion":s1,"candidate_minus_champion":d,"candidate_ok":bool(c.get("ok")),"champion_ok":bool(h.get("ok"))})
    diffs=[r["candidate_minus_champion"] for r in rows]
    s0=[r["seat0_candidate_minus_champion"] for r in rows]; s1=[r["seat1_candidate_minus_champion"] for r in rows]
    n=len(diffs); mean=statistics.fmean(diffs) if diffs else 0.0
    sd=statistics.stdev(diffs) if n>1 else 0.0; se=sd/math.sqrt(n) if n else 0.0
    crt=_runtime(cand); hrt=_runtime(champ)
    out={
      "opponent":args.opponent,"seeds":seeds,"n":n,
      "wins":sum(x>0 for x in diffs),"losses":sum(x<0 for x in diffs),"draws":sum(x==0 for x in diffs),
      "mean_candidate_minus_champion":mean,"se":se,"mean_minus_2se":mean-2*se,
      "worst_regression":min(diffs) if diffs else 0.0,"best_improvement":max(diffs) if diffs else 0.0,"stdev":sd,
      "seat0_mean":statistics.fmean(s0) if s0 else 0.0,"seat1_mean":statistics.fmean(s1) if s1 else 0.0,
      "seat_mean_gap":(statistics.fmean(s0)-statistics.fmean(s1)) if s0 else 0.0,
      "candidate_exceptions":sum(int(r.get("candidate_exceptions",0)) for r in cand),
      "champion_exceptions":sum(int(r.get("candidate_exceptions",0)) for r in champ),
      "all_ok":all(r["candidate_ok"] and r["champion_ok"] for r in rows) and n==len(cand)==len(champ),
      "candidate_runtime_ms":{"calls":len(crt),"mean":statistics.fmean(crt) if crt else 0.0,"p95":_pct(crt,.95),"p99":_pct(crt,.99),"max":max(crt) if crt else 0.0},
      "champion_runtime_ms":{"calls":len(hrt),"mean":statistics.fmean(hrt) if hrt else 0.0,"p95":_pct(hrt,.95),"p99":_pct(hrt,.99),"max":max(hrt) if hrt else 0.0},
      "rows":rows,
    }
    Path(args.out).write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k!="rows"},indent=2))
    return 0 if out["all_ok"] else 2
if __name__=="__main__": raise SystemExit(main())
