from __future__ import annotations
import copy, importlib.util, json, sys, time
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHAMP = ROOT / 'v112_wheat_lead3_lowdemand.py'
SEED = 309004
OPPONENTS = (
    'v49','v50','metav4_v13','k256_h2_q_v1','market_rhythm',
    'story_of_seasons','thomas_router_93','tetsutani_dpts_b','jaxa_2802','ready_stock',
)


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
    return fn


def call(fn, obs, config=None):
    n = getattr(getattr(fn, '__code__', None), 'co_argcount', 1)
    return fn(*[obs, config][:n])


def maps(obs):
    market = obs.get('market', {}) if isinstance(obs, dict) else getattr(obs, 'market', {})
    private = obs.get('private', {}) if isinstance(obs, dict) else getattr(obs, 'private', {})
    if not isinstance(market, dict): market = {}
    if not isinstance(private, dict): private = {}
    return market.get('inventory', {}) or {}, market.get('prices', {}) or {}, private.get('shed', {}) or {}


def orders(action):
    return copy.deepcopy((action or {}).get('market', []) if isinstance(action, dict) else [])


def sell_qty(action, item='WOOL'):
    q = 0.0
    for o in orders(action):
        try:
            if len(o) >= 3 and o[0] == 'SELL' and o[1] == item:
                q += max(0.0, float(o[2]))
        except Exception: pass
    return q


def buy_orders(action):
    return [o for o in orders(action) if isinstance(o,(list,tuple)) and len(o)>=1 and str(o[0]).startswith('BUY')]


def one(name, swap):
    base = load(CHAMP, f'c_{name}_{swap}_{time.time_ns()}')
    other = load(REPO/'opponents'/name/'main.py', f'o_{name}_{swap}_{time.time_ns()}')
    prev_inv = None
    prev_own_sell = 0.0
    active = None
    events = []

    def traced(obs, config=None):
        nonlocal prev_inv, prev_own_sell, active
        action = call(base, obs, config)
        step = int(obs.get('step', 0) if isinstance(obs, dict) else getattr(obs, 'step', 0))
        inv, prices, shed = maps(obs)
        now_inv = float(inv.get('WOOL', 0) or 0)
        price = float(prices.get('WOOL', 0) or 0)
        shed_q = float(shed.get('WOOL', 0) or 0)
        w_sell = sell_qty(action)
        buys = buy_orders(action)

        if active is not None and step > active['signal_step']:
            active['min_price_until_sell'] = min(active['min_price_until_sell'], price)
            active['max_price_until_sell'] = max(active['max_price_until_sell'], price)
            active['max_shed_until_sell'] = max(active['max_shed_until_sell'], shed_q)
            active['buy_steps'] += int(bool(buys))
            if w_sell > 0:
                active['next_sell_step'] = step
                active['next_sell_price'] = price
                active['next_sell_qty'] = w_sell
                active['next_sell_shed_before'] = shed_q
                active['next_sell_orders'] = orders(action)
                events.append(active)
                active = None
            elif step >= 650:
                active['next_sell_step'] = None
                events.append(active)
                active = None

        if active is None and prev_inv is not None and 560 <= step <= 620:
            delta = now_inv - prev_inv
            if delta > 0 and prev_own_sell <= 0 and price >= 220 and shed_q >= 2 and w_sell <= 0:
                active = {
                    'signal_step': step,
                    'delta': delta,
                    'signal_inventory': now_inv,
                    'signal_price': price,
                    'signal_shed': shed_q,
                    'signal_orders': orders(action),
                    'signal_buy_orders': buys,
                    'min_price_until_sell': price,
                    'max_price_until_sell': price,
                    'max_shed_until_sell': shed_q,
                    'buy_steps': int(bool(buys)),
                    'next_sell_step': None,
                    'next_sell_price': None,
                    'next_sell_qty': None,
                    'next_sell_shed_before': None,
                    'next_sell_orders': None,
                }

        prev_inv = now_inv
        prev_own_sell = w_sell
        return action

    env = make('kaggriculture', configuration={'seed':SEED}, debug=False)
    env.run([other,traced] if swap else [traced,other])
    if active is not None:
        events.append(active)
    return {'opponent':name,'seed':SEED,'swap':swap,'events':events,'rewards':[s.reward for s in env.state]}


def main():
    rows=[]
    for name in OPPONENTS:
        for swap in (False,True):
            r=one(name,swap); rows.append(r)
            print(json.dumps({'opponent':name,'swap':swap,'events':r['events']},ensure_ascii=False),flush=True)
    (ROOT/'v124_wool_nextsell_probe.json').write_text(json.dumps({'rows':rows},indent=2),encoding='utf-8')

if __name__=='__main__': main()
