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
}
WATCH = set(range(238, 251))
SHED_POS = (4, 4)


def load(path, tag):
    path = Path(path)
    spec = importlib.util.spec_from_file_location(tag, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[tag] = mod
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        try:
            sys.path.remove(str(path.parent))
        except ValueError:
            pass
    fn = getattr(mod, 'agent', None)
    if not callable(fn):
        for v in vars(mod).values():
            if callable(v):
                fn = v
                break
    if not callable(fn):
        raise RuntimeError(path)
    return fn


def call(fn, obs, config=None):
    n = getattr(getattr(fn, '__code__', None), 'co_argcount', 1)
    return fn(*[obs, config][:n])


def getv(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def melon_qty(entry):
    if isinstance(entry, dict):
        v = entry.get('MELON', 0)
        return float(v) if isinstance(v, (int, float)) else 0.0
    return 0.0


def snap(obs, action):
    market = getv(obs, 'market', {}) or {}
    prices = getv(market, 'prices', {}) or {}
    private = getv(obs, 'private', {}) or {}
    inventories = copy.deepcopy(getv(private, 'inventories', None))
    shed = copy.deepcopy(getv(private, 'shed', {}) or {})
    p = int(getv(obs, 'player', 0) or 0)
    farms = getv(obs, 'farms', []) or []
    farm = farms[p] if 0 <= p < len(farms) else {}
    return {
        'money': getv(farm, 'money', None),
        'farmer': copy.deepcopy(getv(farm, 'farmer', None)),
        'hands': copy.deepcopy(getv(farm, 'hands', None)),
        'inventories': inventories,
        'shed': shed,
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


def hand_action(snap_obj, hand_idx):
    action = (snap_obj or {}).get('action') or {}
    hands = action.get('hands') or []
    return copy.deepcopy(hands[hand_idx]) if 0 <= hand_idx < len(hands) else None


def hand_position(snap_obj, hand_idx):
    hands = (snap_obj or {}).get('hands') or []
    if not (0 <= hand_idx < len(hands)):
        return None
    pos = hands[hand_idx]
    if isinstance(pos, (list, tuple)) and len(pos) >= 2 and all(isinstance(x, (int, float)) for x in pos[:2]):
        return [int(pos[0]), int(pos[1])]
    if isinstance(pos, dict):
        p = pos.get('position') or pos.get('pos')
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return [int(p[0]), int(p[1])]
    return copy.deepcopy(pos)


def first_acquisitions(trace):
    out = []
    steps = sorted(int(k) for k in trace)
    if not steps:
        return out
    first_snap = trace[str(steps[0])]
    invs = first_snap.get('inventories') or []
    max_hands = max(0, len(invs) - 1)
    for hand_idx in range(max_hands):
        prev_qty = None
        for step in steps:
            s = trace[str(step)]
            cur_invs = s.get('inventories') or []
            inv_idx = hand_idx + 1
            qty = melon_qty(cur_invs[inv_idx]) if inv_idx < len(cur_invs) else 0.0
            if prev_qty is not None and prev_qty < 6 <= qty:
                prev = trace.get(str(step - 1), {})
                pos = hand_position(s, hand_idx)
                dist = None
                if isinstance(pos, list) and len(pos) >= 2 and all(isinstance(x, int) for x in pos[:2]):
                    dist = abs(pos[0] - SHED_POS[0]) + abs(pos[1] - SHED_POS[1])
                out.append({
                    'hand_index': hand_idx,
                    'visible_step': step,
                    'qty': qty,
                    'position': pos,
                    'manhattan_to_shed_4_4': dist,
                    'previous_step': step - 1,
                    'previous_action': hand_action(prev, hand_idx),
                    'current_action': hand_action(s, hand_idx),
                    'melon_price': s.get('melon_price'),
                })
                break
            prev_qty = qty
    return out


def one(name, path, seed, swap):
    cfn = load(CHAMP, f'c_{name}_{seed}_{swap}_{time.time_ns()}')
    ofn = load(path, f'o_{name}_{seed}_{swap}_{time.time_ns()}')
    cs, os = {}, {}
    ca, oa = traced(cfn, cs), traced(ofn, os)
    env = make('kaggriculture', configuration={'seed': int(seed)}, debug=False)
    env.run([oa, ca] if swap else [ca, oa])
    rewards = [float(s.reward) for s in env.state]
    return {
        'opponent': name,
        'seed': seed,
        'swap': swap,
        'rewards': rewards,
        'v112': cs,
        'opponent_trace': os,
        'v112_first_acquisitions': first_acquisitions(cs),
        'opponent_first_acquisitions': first_acquisitions(os),
    }


def main():
    rows = []
    for name, path in OPPONENTS.items():
        for seed in SEEDS:
            for swap in (False, True):
                r = one(name, path, seed, swap)
                rows.append(r)
                print(json.dumps({
                    'opponent': name,
                    'seed': seed,
                    'swap': swap,
                    'v112_first': r['v112_first_acquisitions'],
                    'opponent_first': r['opponent_first_acquisitions'],
                }, ensure_ascii=False), flush=True)
    report = {
        'engine': 'kaggle_environments==1.32.7',
        'champion': 'v112_wheat_lead3_lowdemand',
        'purpose': 'locate first visible MELON harvest and safest one-hand early-return diversion point',
        'watch_steps': [238, 250],
        'shed_reference_position': list(SHED_POS),
        'rows': rows,
    }
    (ROOT/'v127_current_day10_melon_firstharvest_probe.json').write_text(
        json.dumps(report, indent=2), encoding='utf-8'
    )


if __name__ == '__main__':
    main()
