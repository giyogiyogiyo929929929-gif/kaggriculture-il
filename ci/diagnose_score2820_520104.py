from __future__ import annotations
import copy, importlib.util, json, sys
from pathlib import Path
from kaggle_environments import make


def load(path, tag):
    p=Path(path).resolve(); spec=importlib.util.spec_from_file_location(tag,p); mod=importlib.util.module_from_spec(spec)
    sys.path.insert(0,str(p.parent))
    try: spec.loader.exec_module(mod)
    finally: sys.path.remove(str(p.parent))
    agent=None
    for v in vars(mod).values():
        if callable(v): agent=v
    if agent is None: raise RuntimeError(path)
    return mod,agent

class Rec:
    def __init__(self, fn, seat_name): self.fn=fn; self.name=seat_name; self.rows=[]
    def __call__(self, obs, cfg=None):
        action=self.fn(obs,cfg)
        seat=int(obs.get('player',0)); farms=obs.get('farms') or [{},{}]; priv=obs.get('private') or {}; market=obs.get('market') or {}
        invs=priv.get('inventories') or []
        self.rows.append({
          'step':int(obs.get('step',-1)),'seat':seat,'money':[farms[0].get('money'),farms[1].get('money')],
          'market_inventory':dict(market.get('inventory') or {}),'prices':dict(market.get('prices') or {}),
          'shops':list((obs.get('town') or {}).get('unlocked_shops') or []),
          'shed':dict(priv.get('shed') or {}),'carried':[dict(x) for x in invs],
          'action':copy.deepcopy(action),
        })
        return action

def run(v147, opp, seed, swap):
    m0,a0=load(v147,'v147diag'); m1,a1=load(opp,'oppdiag')
    ra,rb=Rec(a0,'v147'),Rec(a1,'opp')
    env=make('kaggriculture',configuration={'seed':seed})
    env.run([rb,ra] if swap else [ra,rb])
    seat=1 if swap else 0
    rows_v=ra.rows; rows_o=rb.rows
    # retain every market-active turn and terminal window; enough to reconstruct inventory/price timing.
    active=[]
    byv={r['step']:r for r in rows_v}; byo={r['step']:r for r in rows_o}
    for step in sorted(set(byv)|set(byo)):
        v=byv.get(step); o=byo.get(step)
        vm=(v or {}).get('action',{}).get('market') or []; om=(o or {}).get('action',{}).get('market') or []
        if vm or om or step>=690:
            active.append({'step':step,'v147':v,'opponent':o})
    tel={k:v for k,v in vars(m0).items() if k.endswith('REPORT') and isinstance(v,dict)}
    return {'swap':swap,'v147_seat':seat,'rewards':[s.get('reward') for s in env.state], 'active':active,'telemetry':tel}

if __name__=='__main__':
    v147,opp,out=sys.argv[1:4]
    result={'seed':520104,'games':[run(v147,opp,520104,False),run(v147,opp,520104,True)]}
    Path(out).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'seed':520104,'rewards':[g['rewards'] for g in result['games']], 'active_turns':[len(g['active']) for g in result['games']]},indent=2))
