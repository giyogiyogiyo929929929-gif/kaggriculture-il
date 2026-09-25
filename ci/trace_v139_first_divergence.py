#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable

def load(path):
    p=str(Path(path).resolve()); return get_last_callable(Path(p).read_text(),path=p)

def slim_obs(obs):
    p=int(obs['player']); farm=obs['farms'][p]; rival=obs['farms'][1-p]
    def yields(f):
        out={}
        for row in f.get('tiles',[]):
            for t in row:
                if not isinstance(t,dict): continue
                key=t.get('crop') or t.get('animal')
                if key: out[key]=out.get(key,0)+int(t.get('yield_units',0) or 0)
        return out
    return {
        'step':int(obs['step']),'player':p,'money':farm.get('money'),'rival_money':rival.get('money'),
        'shed':dict((obs.get('private') or {}).get('shed',{})),
        'market_inventory':dict((obs.get('market') or {}).get('inventory',{})),
        'market_prices':dict((obs.get('market') or {}).get('prices',{})),
        'shops':list((obs.get('town') or {}).get('unlocked_shops',[])),
        'own_yield':yields(farm),'rival_yield':yields(rival),
    }

def run(seed,v115_path,v139_path):
    f115=load(v115_path); f139=load(v139_path); diffs=[]
    def probe(obs,cfg=None):
        a=f115(obs,cfg); b=f139(obs,cfg)
        if a!=b and not diffs:
            diffs.append({'obs':slim_obs(obs),'v115_action':a,'v139_action':b,
                          'v115_tel':dict(getattr(f115,'telemetry',{}) or {}),
                          'v139_tel':dict(getattr(f139,'telemetry',{}) or {})})
        return a
    env=make('kaggriculture',configuration={'episodeSteps':720,'seed':int(seed)},debug=False)
    env.run([probe,v115_path])
    fin=env.steps[-1]
    return {'seed':seed,'first_divergence':diffs[0] if diffs else None,
            'rewards':[float(fin[i].reward or 0) for i in range(2)],
            'statuses':[str(fin[i].status) for i in range(2)]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--v115',required=True);ap.add_argument('--v139',required=True);ap.add_argument('--seeds',nargs='+',type=int,required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    out=[run(s,a.v115,a.v139) for s in a.seeds]
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,default=str))
    print(json.dumps(out,indent=2,default=str))
if __name__=='__main__': main()
