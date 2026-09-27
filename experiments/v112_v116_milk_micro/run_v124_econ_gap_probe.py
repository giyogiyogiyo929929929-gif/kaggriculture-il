from __future__ import annotations
import collections, copy, importlib.util, json, sys, time
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

ITEMS = ('WHEAT','CARROT','TOMATO','STRAWBERRY','MELON','EGG','MILK','WOOL','FERTILIZER')


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
    if not callable(fn): raise RuntimeError(f'no agent in {path}')
    return fn


def call(fn, obs, config=None):
    n = getattr(getattr(fn, '__code__', None), 'co_argcount', 1)
    return fn(*[obs, config][:n])


def getv(obj, key, default=None):
    if isinstance(obj, dict): return obj.get(key, default)
    return getattr(obj, key, default)


def own_money(obs):
    p = int(getv(obs, 'player', 0) or 0)
    farms = getv(obs, 'farms', []) or []
    try: farm = farms[p]
    except Exception: return None
    v = getv(farm, 'money', None)
    try: return float(v)
    except Exception: return None


def own_shed(obs):
    private = getv(obs, 'private', {}) or {}
    shed = getv(private, 'shed', {}) or {}
    return {k: float(getv(shed, k, 0) or 0) for k in ITEMS}


def market_price(obs, item):
    market = getv(obs, 'market', {}) or {}
    prices = getv(market, 'prices', {}) or {}
    try: return float(getv(prices, item, 0) or 0)
    except Exception: return 0.0


def classify_market(orders):
    ops = [str(o[0]) for o in orders if isinstance(o,(list,tuple)) and o]
    has_sell = any(x == 'SELL' for x in ops)
    has_buy = any(x.startswith('BUY') for x in ops)
    has_hire = any(x == 'HIRE' for x in ops)
    if not ops: return 'none'
    if has_sell and not has_buy and not has_hire: return 'sell_only'
    if has_buy and not has_sell and not has_hire: return 'buy_only'
    if has_hire and not has_sell and not has_buy: return 'hire_only'
    return 'mixed'


class Trace:
    def __init__(self, fn, label):
        self.fn = fn; self.label = label
        self.prev_money = None; self.prev_class = None; self.prev_step = None
        self.sell_qty = collections.defaultdict(float)
        self.buy_qty = collections.defaultdict(float)
        self.order_counts = collections.Counter()
        self.preprice_sell_value = collections.defaultdict(float)
        self.money_delta_by_prev_class = collections.defaultdict(float)
        self.money_delta_events = []
        self.day_money = {}
        self.nonempty_market = []
        self.last_shed = {}
        self.last_money = None
        self.dense_sell_turns = 0
        self.dense_sell_events = []

    def __call__(self, obs, config=None):
        step = int(getv(obs, 'step', 0) or 0)
        money = own_money(obs)
        if money is not None:
            if self.prev_money is not None:
                d = money - self.prev_money
                self.money_delta_by_prev_class[self.prev_class or 'unknown'] += d
                if abs(d) > 1e-9:
                    self.money_delta_events.append({'step': step, 'delta_from_prev': d, 'prev_step': self.prev_step, 'prev_class': self.prev_class})
            self.last_money = money
            if step % 24 == 0: self.day_money[str(step//24)] = money
        self.last_shed = own_shed(obs)

        action = call(self.fn, obs, config)
        orders = copy.deepcopy((action or {}).get('market', []) if isinstance(action, dict) else [])
        sell_families_10 = 0
        for o in orders:
            if not isinstance(o,(list,tuple)) or not o: continue
            op = str(o[0]); self.order_counts[op] += 1
            if op == 'SELL' and len(o) >= 3:
                item = str(o[1]); q = max(0.0, float(o[2] or 0)); self.sell_qty[item] += q
                self.preprice_sell_value[item] += q * market_price(obs, item)
                if q >= 10: sell_families_10 += 1
            elif op.startswith('BUY') and len(o) >= 3:
                item = str(o[1]); q = max(0.0, float(o[2] or 0)); self.buy_qty[f'{op}:{item}'] += q
        if sell_families_10 >= 3:
            self.dense_sell_turns += 1
            if len(self.dense_sell_events) < 64:
                self.dense_sell_events.append({'step': step, 'families_ge10': sell_families_10, 'orders': orders})
        if orders and len(self.nonempty_market) < 256:
            self.nonempty_market.append({'step': step, 'orders': orders})
        self.prev_money = money; self.prev_class = classify_market(orders); self.prev_step = step
        return action

    def finish(self, final_money):
        if self.last_money is not None:
            d = float(final_money) - self.last_money
            self.money_delta_by_prev_class[self.prev_class or 'unknown'] += d
            if abs(d) > 1e-9:
                self.money_delta_events.append({'step': 720, 'delta_from_prev': d, 'prev_step': self.prev_step, 'prev_class': self.prev_class})
        self.day_money['30'] = float(final_money)
        return {
            'label': self.label,
            'final_money': float(final_money),
            'sell_qty': dict(self.sell_qty),
            'buy_qty': dict(self.buy_qty),
            'order_counts': dict(self.order_counts),
            'preprice_sell_value': dict(self.preprice_sell_value),
            'money_delta_by_prev_class': dict(self.money_delta_by_prev_class),
            'day_money': self.day_money,
            'last_observed_shed': self.last_shed,
            'dense_sell_turns_proxy': self.dense_sell_turns,
            'dense_sell_events_proxy': self.dense_sell_events,
            'nonempty_market': self.nonempty_market,
            'money_delta_events': self.money_delta_events,
        }


def game(name, opp_path, seed, swap):
    champ_fn = load(CHAMP, f'c_{name}_{seed}_{swap}_{time.time_ns()}')
    opp_fn = load(opp_path, f'o_{name}_{seed}_{swap}_{time.time_ns()}')
    tc = Trace(champ_fn, 'v112')
    to = Trace(opp_fn, name)
    env = make('kaggriculture', configuration={'seed': int(seed)}, debug=False)
    env.run([to, tc] if swap else [tc, to])
    rewards = [float(s.reward) for s in env.state]
    cm, om = (rewards[1], rewards[0]) if swap else (rewards[0], rewards[1])
    c = tc.finish(cm); o = to.finish(om)
    days = sorted(set(c['day_money']) | set(o['day_money']), key=lambda x:int(x))
    gap = {d: float(c['day_money'].get(d,0))-float(o['day_money'].get(d,0)) for d in days if d in c['day_money'] and d in o['day_money']}
    return {'opponent':name,'seed':seed,'swap':swap,'candidate_minus_opponent':cm-om,'v112':c,'opponent_trace':o,'money_gap_by_day':gap}


def slim_summary(rows):
    out = {}
    for name in OPPONENTS:
        rr = [r for r in rows if r['opponent']==name]
        out[name] = {
            'games': len(rr),
            'mean_final_gap': sum(r['candidate_minus_opponent'] for r in rr)/len(rr),
            'final_gaps': [r['candidate_minus_opponent'] for r in rr],
            'v112_sell_qty_mean': {it: sum(r['v112']['sell_qty'].get(it,0) for r in rr)/len(rr) for it in ITEMS},
            'opp_sell_qty_mean': {it: sum(r['opponent_trace']['sell_qty'].get(it,0) for r in rr)/len(rr) for it in ITEMS},
            'v112_preprice_sell_value_mean': {it: sum(r['v112']['preprice_sell_value'].get(it,0) for r in rr)/len(rr) for it in ITEMS},
            'opp_preprice_sell_value_mean': {it: sum(r['opponent_trace']['preprice_sell_value'].get(it,0) for r in rr)/len(rr) for it in ITEMS},
            'v112_order_counts_mean': {k: sum(r['v112']['order_counts'].get(k,0) for r in rr)/len(rr) for k in set().union(*(r['v112']['order_counts'] for r in rr))},
            'opp_order_counts_mean': {k: sum(r['opponent_trace']['order_counts'].get(k,0) for r in rr)/len(rr) for k in set().union(*(r['opponent_trace']['order_counts'] for r in rr))},
            'v112_dense_sell_turns_proxy_mean': sum(r['v112']['dense_sell_turns_proxy'] for r in rr)/len(rr),
            'opp_dense_sell_turns_proxy_mean': sum(r['opponent_trace']['dense_sell_turns_proxy'] for r in rr)/len(rr),
        }
    return out


def main():
    rows=[]
    for name,path in OPPONENTS.items():
        for seed in SEEDS:
            for swap in (False,True):
                r=game(name,path,seed,swap); rows.append(r)
                print(name,seed,swap,r['candidate_minus_opponent'],flush=True)
    report={'engine':'kaggle_environments==1.32.7','champion':'v112_wheat_lead3_lowdemand','purpose':'action-identical external economics gap attribution; preprice_sell_value is an exposure proxy, not realized revenue','seeds':SEEDS,'summary':slim_summary(rows),'rows':rows}
    (ROOT/'v124_econ_gap_probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('SUMMARY',json.dumps(report['summary'],indent=2),flush=True)

if __name__=='__main__': main()
