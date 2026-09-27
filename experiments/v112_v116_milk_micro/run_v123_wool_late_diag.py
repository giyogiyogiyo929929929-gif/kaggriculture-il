from __future__ import annotations
import copy, importlib.util, json, sys, time
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHAMP = ROOT / 'v112_wheat_lead3_lowdemand.py'
CASES = [
    ('metav4_v13', REPO/'opponents/metav4_v13/main.py', 309001),
    ('k256_h2_q_v1', REPO/'opponents/k256_h2_q_v1/main.py', 309001),
    ('story_of_seasons', REPO/'opponents/story_of_seasons/main.py', 309001),
]

def load(path, tag):
    spec = importlib.util.spec_from_file_location(tag, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[tag] = mod
    sys.path.insert(0, str(Path(path).parent))
    try: spec.loader.exec_module(mod)
    finally:
        try: sys.path.remove(str(Path(path).parent))
        except ValueError: pass
    fn = getattr(mod, 'agent', None)
    if not callable(fn):
        for v in vars(mod).values():
            if callable(v): fn = v; break
    if not callable(fn): raise RuntimeError(path)
    return mod, fn

def call(fn, obs, config=None):
    n = getattr(getattr(fn, '__code__', None), 'co_argcount', 1)
    return fn(*[obs, config][:n])

def snap(obs, action):
    market = obs.get('market', {}) if isinstance(obs, dict) else getattr(obs, 'market', {})
    inv = market.get('inventory', {}) if isinstance(market, dict) else {}
    prices = market.get('prices', {}) if isinstance(market, dict) else {}
    private = obs.get('private', {}) if isinstance(obs, dict) else getattr(obs, 'private', {})
    shed = private.get('shed', {}) if isinstance(private, dict) else {}
    orders = copy.deepcopy((action or {}).get('market', []) if isinstance(action, dict) else [])
    return {
        'wool_inventory': inv.get('WOOL'),
        'wool_price': prices.get('WOOL'),
        'wool_shed': shed.get('WOOL'),
        'market_orders': orders,
        'wool_sell': sum(float(o[2]) for o in orders if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == 'SELL' and o[1] == 'WOOL'),
        'buy_orders': [o for o in orders if isinstance(o, (list, tuple)) and len(o) >= 1 and str(o[0]).startswith('BUY')],
    }

def one(name, opp, seed, swap):
    _, base = load(CHAMP, f'c_{name}_{seed}_{swap}_{time.time_ns()}')
    _, other = load(opp, f'o_{name}_{seed}_{swap}_{time.time_ns()}')
    rec = {}
    def traced(obs, config=None):
        a = call(base, obs, config)
        step = int(obs.get('step', 0) if isinstance(obs, dict) else getattr(obs, 'step', 0))
        if step in (597, 598, 599, 600, 601): rec[str(step)] = snap(obs, a)
        return a
    env = make('kaggriculture', configuration={'seed': seed}, debug=False)
    env.run([other, traced] if swap else [traced, other])
    return {'opponent': name, 'seed': seed, 'swap': swap, 'steps': rec, 'rewards': [s.reward for s in env.state]}

def main():
    rows = []
    for name, opp, seed in CASES:
        for swap in (False, True):
            r = one(name, opp, seed, swap)
            rows.append(r)
            print(json.dumps(r, ensure_ascii=False), flush=True)
    (ROOT/'v123_wool_late_diag.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')

if __name__ == '__main__': main()
