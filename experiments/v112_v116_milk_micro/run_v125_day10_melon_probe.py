from __future__ import annotations
import copy, importlib.util, json, sys, time
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHAMP = ROOT / 'v112_wheat_lead3_lowdemand.py'
SEEDS = [309001, 309004]
OPPONENTS = {
    'thomas_router_93': REPO/'opponents/thomas_router_93/main.py',
    'metav4_v13': REPO/'opponents/metav4_v13/main.py',
    'k256_h2_q_v1': REPO/'opponents/k256_h2_q_v1/main.py',
    'ready_stock': REPO/'opponents/ready_stock/main.py',
    'jaxa_2802': REPO/'opponents/jaxa_2802/main.py',
}
WATCH = set(range(240, 271))

def load(path, tag):
    path = Path(path)
    spec = importlib.util.spec_from_file_location(tag, path)
    if spec is None or spec.loader is None: raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec); sys.modules[tag] = mod
    sys.path.insert(0, str(path.parent))
    try: spec.loader.exec_module(mod)
    finally:
        try: sys.path.remove(str(path.parent))
        except ValueError: pass
    fn = getattr(mod, 'agent', None)
    if not callable(fn):
        for v in vars(mod).values():
            if callable(v): fn = v; break
    if not callable(fn): raise RuntimeError(path)
    return fn

def call(fn, obs, config=None):
    n = getattr(getattr(fn, '__code__', None), 'co_argcount', 1)
    return fn(*[obs, config][:n])

def getv(obj, key, default=None):
    if isinstance(obj, dict): return obj.get(key, default)
    return getattr(obj, key, default)

def snap(obs, action):
    market = getv(obs, 'market', {}) or {}
    inv = getv(market, 'inventory', {}) or {}
    prices = getv(market, 'prices', {}) or {}
    private = getv(obs, 'private', {}) or {}
    shed = getv(private, 'shed', {}) or {}
    p = int(getv(obs, 'player', 0) or 0)
    farms = getv(obs, 'farms', []) or []
    farm = farms[p] if 0 <= p < len(farms) else {}
    money = getv(farm, 'money', None)
    return {
        'money': money,
        'melon_shed': getv(shed, 'MELON', 0),
        'strawberry_shed': getv(shed, 'STRAWBERRY', 0),
        'milk_shed': getv(shed, 'MILK', 0),
        'wool_shed': getv(shed, 'WOOL', 0),
        'melon_market_inventory': getv(inv, 'MELON', None),
        'melon_price': getv(prices, 'MELON', None),
        'action': copy.deepcopy(action),
    }

def traced(fn, store):
    def wrapped(obs, config=None):
        a = call(fn, obs, config)
        step = int(getv(obs, 'step', 0) or 0)
        if step in WATCH:
            store[str(step)] = snap(obs, a)
        return a
    return wrapped

def one(name, path, seed, swap):
    cfn = load(CHAMP, f'c_{name}_{seed}_{swap}_{time.time_ns()}')
    ofn = load(path, f'o_{name}_{seed}_{swap}_{time.time_ns()}')
    cs, os = {}, {}
    ca, oa = traced(cfn, cs), traced(ofn, os)
    env = make('kaggriculture', configuration={'seed': int(seed)}, debug=False)
    env.run([oa, ca] if swap else [ca, oa])
    rewards = [float(s.reward) for s in env.state]
    return {'opponent':name,'seed':seed,'swap':swap,'rewards':rewards,'v112':cs,'opponent_trace':os}

def main():
    rows=[]
    for name,path in OPPONENTS.items():
        for seed in SEEDS:
            for swap in (False,True):
                r=one(name,path,seed,swap); rows.append(r)
                c=r['v112']; o=r['opponent_trace']
                def line(trace, step):
                    s=trace.get(str(step),{})
                    return {'money':s.get('money'),'melon_shed':s.get('melon_shed'),'melon_price':s.get('melon_price'),'action':s.get('action')}
                print(json.dumps({'opponent':name,'seed':seed,'swap':swap,'c250':line(c,250),'o250':line(o,250),'c264':line(c,264),'o264':line(o,264)}, ensure_ascii=False), flush=True)
    report={'engine':'kaggle_environments==1.32.7','champion':'v112_wheat_lead3_lowdemand','watch_steps':[240,270],'rows':rows}
    (ROOT/'v125_day10_melon_probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__': main()
