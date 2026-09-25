#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, subprocess, sys, tempfile, time, statistics, math
from pathlib import Path
EXPECTED='1.32.7'; BUILTINS={'starter','random','pass'}
def resolve(s):
    if s in BUILTINS:return s
    p=Path(s); p=p/'main.py' if p.is_dir() else p
    if not p.is_file(): raise FileNotFoundError(s)
    return str(p)
def load(spec,timing):
    if spec in BUILTINS:return spec,None
    from kaggle_environments.agent import get_last_callable
    path=resolve(spec); fn=get_last_callable(Path(path).read_text(),path=path); n=0
    def wrapped(obs,cfg=None):
        nonlocal n
        if obs.get('step') is None: obs['step']=n
        n+=1; t=time.perf_counter()
        try:return fn(obs,cfg)
        except Exception: timing['exceptions']+=1; raise
        finally: timing['durations_ms'].append((time.perf_counter()-t)*1000)
    return wrapped,fn
def single(a,b,seed):
    import kaggle_environments
    from kaggle_environments import make
    assert kaggle_environments.__version__==EXPECTED
    ta={'durations_ms':[],'exceptions':0}; tb={'durations_ms':[],'exceptions':0}
    aa,fa=load(resolve(a),ta); bb,fb=load(resolve(b),tb)
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=False); env.run([aa,bb])
    fin=env.steps[-1]
    def tel(f):
        x=getattr(f,'telemetry',{}) if f is not None else {}
        try:return json.loads(json.dumps(x,default=str))
        except Exception:return {'repr':repr(x)}
    return {'seed':seed,'rewards':[float(fin[i].reward or 0) for i in range(2)],'statuses':[str(fin[i].status) for i in range(2)],'timing':[ta,tb],'telemetry':[tel(fa),tel(fb)]}
def iso(a,b,seed):
    with tempfile.NamedTemporaryFile(suffix='.json',delete=False) as f: out=f.name
    try:
        cp=subprocess.run([sys.executable,__file__,'--single','--a',a,'--b',b,'--seed',str(seed),'--out',out],capture_output=True,text=True)
        if cp.returncode:return {'seed':seed,'rewards':[0,0],'statuses':['RUN-EXC']*2,'timing':[{'durations_ms':[],'exceptions':1}]*2,'telemetry':[{},{}],'runner_error':(cp.stderr or cp.stdout)[-4000:]}
        return json.loads(Path(out).read_text())
    finally:
        try:os.unlink(out)
        except OSError:pass
def pair(c,b,seed):
    n=iso(c,b,seed); s=iso(b,c,seed)
    nm=n['rewards'][0]-n['rewards'][1]; sm=s['rewards'][1]-s['rewards'][0]; d=(nm+sm)/2
    rt=n['timing'][0]['durations_ms']+s['timing'][1]['durations_ms']; exc=n['timing'][0]['exceptions']+s['timing'][1]['exceptions']
    ok=n['statuses']==['DONE','DONE'] and s['statuses']==['DONE','DONE'] and exc==0 and 'runner_error' not in n and 'runner_error' not in s
    return {'seed':seed,'candidate_minus_champion':d,'normal_margin':nm,'swapped_margin':sm,'candidate_runtime_ms':rt,'candidate_exceptions':exc,'candidate_telemetry_normal':n['telemetry'][0],'candidate_telemetry_swapped':s['telemetry'][1],'ok':ok,'normal':n,'swapped':s}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--candidate'); ap.add_argument('--champion'); ap.add_argument('--seed-start',type=int); ap.add_argument('--seed-count',type=int); ap.add_argument('--out',required=True); ap.add_argument('--single',action='store_true'); ap.add_argument('--a');ap.add_argument('--b');ap.add_argument('--seed',type=int); a=ap.parse_args()
    if a.single:
        Path(a.out).write_text(json.dumps(single(a.a,a.b,a.seed))); return
    rows=[pair(a.candidate,a.champion,a.seed_start+i) for i in range(a.seed_count)]
    ds=[r['candidate_minus_champion'] for r in rows]; n=len(ds); sd=statistics.stdev(ds) if n>1 else 0; se=sd/math.sqrt(n) if n else 0
    times=[x for r in rows for x in r['candidate_runtime_ms']]; times.sort()
    def pct(q): return times[min(len(times)-1,int(q*(len(times)-1)))] if times else 0
    summary={'engine':EXPECTED,'candidate_minus_champion':'candidate - champion','seed_start':a.seed_start,'seed_count':a.seed_count,'wins':sum(x>0 for x in ds),'losses':sum(x<0 for x in ds),'draws':sum(x==0 for x in ds),'mean':statistics.fmean(ds) if ds else 0,'median':statistics.median(ds) if ds else 0,'se':se,'mean_minus_2se':(statistics.fmean(ds)-2*se) if ds else 0,'worst':min(ds) if ds else 0,'best':max(ds) if ds else 0,'exceptions':sum(r['candidate_exceptions'] for r in rows),'runtime_median_ms':statistics.median(times) if times else 0,'runtime_p95_ms':pct(.95),'runtime_p99_ms':pct(.99),'runtime_max_ms':max(times) if times else 0,'fires':sum(int(r['candidate_telemetry_normal'].get('fires',0))+int(r['candidate_telemetry_swapped'].get('fires',0)) for r in rows),'all_ok':all(r['ok'] for r in rows),'rows':rows}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(summary,indent=2)); print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2))
    if not summary['all_ok']: raise SystemExit(2)
if __name__=='__main__':main()
