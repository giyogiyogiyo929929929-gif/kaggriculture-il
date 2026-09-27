from __future__ import annotations
import copy, importlib.util, json, sys, time
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHAMP = ROOT / 'v112_wheat_lead3_lowdemand.py'
SEEDS = (309001, 309004)
OPPONENTS = {
    'thomas_router_93': REPO/'opponents/thomas_router_93/main.py',
    'metav4_v13': REPO/'opponents/metav4_v13/main.py',
    'k256_h2_q_v1': REPO/'opponents/k256_h2_q_v1/main.py',
    'ready_stock': REPO/'opponents/ready_stock/main.py',
    'jaxa_2802': REPO/'opponents/jaxa_2802/main.py',
}
WATCH = set(range(248, 257))


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


def melon_total(obj):
    if isinstance(obj, dict):
        total = 0.0
        for k, v in obj.items():
            if str(k).upper() == 'MELON' and isinstance(v, (int, float)):
                total += float(v)
            else:
                total += melon_total(v)
        return total
    if isinstance(obj, (list, tuple)):
        return sum(melon_total(v) for v in obj)
    return 0.0


def snap(obs, action):
    market = getv(obs, 'market', {}) or {}
    inv = getv(market, 'inventory', {}) or {}
    prices = getv(market, 'prices', {}) or {}
    private = getv(obs, 'private', {}) or {}
    shed = getv(private, 'shed', {}) or {}
    inventories = copy.deepcopy(getv(private, 'inventories', None))
    p = int(getv(obs, 'player', 0) or 0)
    farms = getv(obs, 'farms', []) or []
    farm = farms[p] if 0 <= p < len(farms) else {}
    return {
        'money': getv(farm, 'money', None),
        'farmer': copy.deepcopy(getv(farm, 'farmer', None)),
        'hands': copy.deepcopy(getv(farm, 'hands', None)),
        'shed': copy.deepcopy(shed),
        'inventories': inventories,
        'melon_carry_total': melon_total(inventories),
        'melon_shed': getv(shed, 'MELON', 0),
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


def compact(trace, step):
    s = trace.get(str(step), {})
    action = s.get('action') or {}
    mel = [o for o in (action.get('market') or []) if isinstance(o,(list,tuple)) and len(o)>=3 and o[0]=='SELL' and o[1]=='MELON']
    return {
        'money': s.get('money'),
        'melon_carry_total': s.get('melon_carry_total'),
        'melon_shed': s.get('melon_shed'),
        'melon_price': s.get('melon_price'),
        'melon_sell_orders': mel,
        'inventories': s.get('inventories'),
    }


def main():
    rows=[]
    for name,path in OPPONENTS.items():
        for seed in SEEDS:
            for swap in (False,True):
                r=one(name,path,seed,swap); rows.append(r)
                print(json.dumps({
                    'opponent':name,'seed':seed,'swap':swap,
                    'c249':compact(r['v112'],249),'c250':compact(r['v112'],250),'c255':compact(r['v112'],255),'c256':compact(r['v112'],256),
                    'o249':compact(r['opponent_trace'],249),'o250':compact(r['opponent_trace'],250),
                }, ensure_ascii=False), flush=True)
    report={'engine':'kaggle_environments==1.32.7','champion':'v112_wheat_lead3_lowdemand','watch_steps':[248,256],'rows':rows}
    (ROOT/'v126_day10_melon_inventory_probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__': main()
