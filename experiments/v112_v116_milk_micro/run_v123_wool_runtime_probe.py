from __future__ import annotations
import copy, importlib.util, json, sys, time
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHAMP = ROOT / 'v112_wheat_lead3_lowdemand.py'
SEEDS = (309001, 309003, 309004)
OPPONENTS = (
    'v49','v50','metav4_v13','k256_h2_q_v1','market_rhythm',
    'story_of_seasons','thomas_router_93','tetsutani_dpts_b','jaxa_2802','ready_stock',
)
WINDOW_LO, WINDOW_HI = 560, 620


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


def market_maps(obs):
    market = obs.get('market', {}) if isinstance(obs, dict) else getattr(obs, 'market', {})
    if not isinstance(market, dict): market = {}
    return market.get('inventory', {}) or {}, market.get('prices', {}) or {}


def wool_shed(obs):
    private = obs.get('private', {}) if isinstance(obs, dict) else getattr(obs, 'private', {})
    if not isinstance(private, dict): return 0.0
    shed = private.get('shed', {}) or {}
    try: return float(shed.get('WOOL', 0) or 0)
    except Exception: return 0.0


def wool_sell(action):
    q = 0.0
    if not isinstance(action, dict): return q
    for o in action.get('market', []) or []:
        try:
            if len(o) >= 3 and o[0] == 'SELL' and o[1] == 'WOOL': q += max(0.0, float(o[2]))
        except Exception: pass
    return q


def snap(step, obs, action):
    inv, prices = market_maps(obs)
    orders = copy.deepcopy((action or {}).get('market', []) if isinstance(action, dict) else [])
    return {
        'step': step,
        'wool_inventory': inv.get('WOOL'),
        'wool_price': prices.get('WOOL'),
        'wool_shed': wool_shed(obs),
        'wool_sell': wool_sell(action),
        'market_orders': orders,
        'buy_orders': [o for o in orders if isinstance(o,(list,tuple)) and len(o)>=1 and str(o[0]).startswith('BUY')],
    }


def one(name, seed, swap):
    opp = REPO / 'opponents' / name / 'main.py'
    _, base = load(CHAMP, f'c_{name}_{seed}_{swap}_{time.time_ns()}')
    _, other = load(opp, f'o_{name}_{seed}_{swap}_{time.time_ns()}')
    prev_inv = None
    prev_own_sell = 0.0
    events = []
    pending = []

    def traced(obs, config=None):
        nonlocal prev_inv, prev_own_sell
        action = call(base, obs, config)
        step = int(obs.get('step', 0) if isinstance(obs, dict) else getattr(obs, 'step', 0))
        inv, _ = market_maps(obs)
        try: now_inv = float(inv.get('WOOL', 0) or 0)
        except Exception: now_inv = 0.0

        if WINDOW_LO <= step <= WINDOW_HI and prev_inv is not None:
            delta = now_inv - prev_inv
            if delta > 0 and prev_own_sell <= 0:
                ev = {
                    'signal_step': step,
                    'delta': delta,
                    'frames': [snap(step, obs, action)],
                }
                events.append(ev)
                pending.append((step + 3, ev))

        for end_step, ev in list(pending):
            if step > ev['signal_step'] and step <= end_step:
                ev['frames'].append(snap(step, obs, action))
            if step >= end_step:
                pending.remove((end_step, ev))

        prev_inv = now_inv
        prev_own_sell = wool_sell(action)
        return action

    env = make('kaggriculture', configuration={'seed': seed}, debug=False)
    env.run([other, traced] if swap else [traced, other])
    return {
        'opponent': name,
        'seed': seed,
        'swap': swap,
        'events': events,
        'rewards': [s.reward for s in env.state],
    }


def main():
    rows = []
    for seed in SEEDS:
        for name in OPPONENTS:
            for swap in (False, True):
                r = one(name, seed, swap)
                rows.append(r)
                sig = [(e['signal_step'], e['delta']) for e in r['events']]
                print(json.dumps({'opponent':name,'seed':seed,'swap':swap,'signals':sig}, ensure_ascii=False), flush=True)
    out = {'window':[WINDOW_LO,WINDOW_HI], 'rows':rows}
    (ROOT/'v123_wool_runtime_probe.json').write_text(json.dumps(out, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
