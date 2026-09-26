from __future__ import annotations
import copy, importlib.util, json, math, statistics, time
from pathlib import Path
from kaggle_environments import make
ROOT=Path(__file__).resolve().parent

def load(path,tag):
    s=importlib.util.spec_from_file_location(tag,path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m,m.agent
class Timed:
    def __init__(self,fn): self.fn=fn; self.ms=[]; self.errors=0
    def __call__(self,obs,config=None):
        t=time.perf_counter()
        try:
            n=self.fn.__code__.co_argcount; return self.fn(*[obs,config][:n])
        except Exception: self.errors+=1; raise
        finally:self.ms.append((time.perf_counter()-t)*1000)
def game(a,b,seed,swap=False,timed=False):
    ma,fa=load(Path(a),f'a{seed}{swap}{time.time_ns()}')
    built=str(b) in {'starter','pass','random'}
    if built:
        mb=None; fb=str(b)
    else:
        mb,fb=load(Path(b),f'b{seed}{swap}{time.time_ns()}')
    ta=Timed(fa); tb=None if built else Timed(fb)
    aa=ta if timed else fa; bb=fb if built else (tb if timed else fb)
    env=make('kaggriculture',configuration={'seed':int(seed)},debug=False); env.run([bb,aa] if swap else [aa,bb]); r=[float(x.reward) for x in env.state]
    ar,br=(r[1],r[0]) if swap else (r[0],r[1])
    return {'a':ar,'b':br,'delta':ar-br,'telemetry':copy.deepcopy(getattr(ma.agent,'telemetry',{})),'ms':ta.ms if timed else [],'errors':ta.errors}
def pair(a,b,seed,timed=False):
    x=game(a,b,seed,False,timed); y=game(a,b,seed,True,timed); return {'seed':seed,'pair_diff':(x['delta']+y['delta'])/2,'games':[x,y]}
def summ(rows):
    v=[x['pair_diff'] for x in rows]; n=len(v); mean=statistics.mean(v); se=statistics.stdev(v)/(n**.5) if n>1 else 0
    return {'n':n,'wins':sum(x>0 for x in v),'losses':sum(x<0 for x in v),'draws':sum(x==0 for x in v),'mean':mean,'median':statistics.median(v),'stderr':se,'mean_minus_2se':mean-2*se,'worst':min(v),'best':max(v),'values':v}
def block(a,b,start,n):
    rows=[]
    for seed in range(start,start+n):
        r=pair(a,b,seed); rows.append(r); print(seed,r['pair_diff'],flush=True)
    return {'summary':summ(rows),'rows':rows}
def tele(block):
    out={}; steps=[]
    for row in block['rows']:
      for g in row['games']:
       d=(g.get('telemetry') or {}).get('milk_micro_lead1') or {}
       for k,v in d.items():
        if k=='steps': steps+=v
        elif isinstance(v,(int,float)): out[k]=out.get(k,0)+v
    out['steps']=steps; return out
def main():
    v110=ROOT/'v110b_wheat_late_batch_lead2.py'; v112=ROOT/'v112_wheat_lead3_lowdemand.py'; v116=ROOT/'v116_milk_micro_lead1.py'
    rep={'engine':'1.32.7','sign':'candidate_minus_champion = candidate - champion'}
    rep['v112_validation']=block(v112,v110,287001,12); rep['v112_sealed']=block(v112,v110,288001,4); rep['v112_stress']=block(v112,v110,289001,8)
    rep['v116_validation']=block(v116,v112,293001,12); rep['v116_sealed']=block(v116,v112,294001,4); rep['v116_stress']=block(v116,v112,295001,8)
    rep['v116_starter']=block(v116,'starter',1,5); rep['v112_starter']=block(v112,'starter',1,5)
    rr=pair(v116,v112,800500,True); ms=sorted([z for g in rr['games'] for z in g['ms']]); idx=min(len(ms)-1,max(0,math.ceil(.99*len(ms))-1))
    rep['runtime']={'callbacks':len(ms),'median_ms':statistics.median(ms),'p99_ms':ms[idx],'max_ms':max(ms),'errors':sum(g['errors'] for g in rr['games'])}
    rep['telemetry_validation']=tele(rep['v116_validation']); rep['telemetry_sealed']=tele(rep['v116_sealed']); rep['telemetry_stress']=tele(rep['v116_stress'])
    Path('current_lineage_initial.json').write_text(json.dumps(rep,indent=2))
    print('SUMMARY',json.dumps({k:(v['summary'] if isinstance(v,dict) and 'summary' in v else v) for k,v in rep.items() if k!='sign'},indent=2),flush=True)
if __name__=='__main__':main()
