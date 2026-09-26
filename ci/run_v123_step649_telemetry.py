from __future__ import annotations
import argparse, copy, importlib.util, json, statistics, sys, time
from pathlib import Path


def load_agent(path: str, tag: str):
    p = Path(path).resolve()
    spec = importlib.util.spec_from_file_location(f'_v123_{tag}_{time.time_ns()}', p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    sys.path.insert(0, str(p.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(p.parent))
    agent = None
    for value in vars(mod).values():
        if callable(value):
            agent = value
    if agent is None:
        raise RuntimeError(f'no callable in {path}')
    return mod, agent


def obs_at(env, seat: int, step_no: int):
    for frame in env.steps:
        if seat >= len(frame):
            continue
        obs = frame[seat].get('observation') or {}
        if int(obs.get('step', -1)) == step_no:
            return obs
    return None


def delta_dict(before, after):
    keys = sorted(set(before or {}) | set(after or {}))
    return {k: (after or {}).get(k, 0) - (before or {}).get(k, 0) for k in keys
            if (after or {}).get(k, 0) != (before or {}).get(k, 0)}


def run_one(v123: str, v104: str, seed: int, swap: bool):
    from kaggle_environments import make
    mod_c, cand = load_agent(v123, f'c_{seed}_{int(swap)}')
    _, opp = load_agent(v104, f'o_{seed}_{int(swap)}')
    env = make('kaggriculture', configuration={'seed': seed})
    env.run([opp, cand] if swap else [cand, opp])
    seat = 1 if swap else 0
    other = 1 - seat
    pre = obs_at(env, seat, 649) or {}
    post = obs_at(env, seat, 650) or {}
    pre_other = obs_at(env, other, 649) or {}
    post_other = obs_at(env, other, 650) or {}
    def money(obs, s):
        farms=obs.get('farms') or []
        return farms[s].get('money') if s < len(farms) else None
    pre_priv=pre.get('private') or {}; post_priv=post.get('private') or {}
    pre_mkt=pre.get('market') or {}; post_mkt=post.get('market') or {}
    report=copy.deepcopy(getattr(mod_c,'_V123_REPORT',{}))
    v122_report=copy.deepcopy(getattr(mod_c,'_V122_REPORT',{}))
    tele=(report.get('step649') or [])[-1] if report.get('step649') else None
    rewards=[state.get('reward') for state in env.state]
    return {
        'seed':seed,'swap':swap,'candidate_seat':seat,
        'candidate_money_final':rewards[seat],'opponent_money_final':rewards[other],
        'candidate_minus_opponent':rewards[seat]-rewards[other],
        'telemetry':tele,'v123_errors':report.get('errors'),'v122_report':v122_report,
        'step649_to_650':{
            'own_money_before':money(pre,seat),'own_money_after':money(post,seat),
            'own_money_delta':None if money(pre,seat) is None or money(post,seat) is None else money(post,seat)-money(pre,seat),
            'rival_money_before':money(pre_other,other),'rival_money_after':money(post_other,other),
            'rival_money_delta':None if money(pre_other,other) is None or money(post_other,other) is None else money(post_other,other)-money(pre_other,other),
            'shed_delta':delta_dict(pre_priv.get('shed') or {}, post_priv.get('shed') or {}),
            'market_inventory_delta':delta_dict(pre_mkt.get('inventory') or {}, post_mkt.get('inventory') or {}),
            'market_price_delta':delta_dict(pre_mkt.get('prices') or {}, post_mkt.get('prices') or {}),
        }
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--v123', required=True); ap.add_argument('--v104', required=True)
    ap.add_argument('--seeds', required=True, help='comma list; ranges a-b allowed')
    ap.add_argument('--out', required=True)
    args=ap.parse_args()
    seeds=[]
    for tok in args.seeds.split(','):
        tok=tok.strip()
        if not tok: continue
        if '-' in tok:
            a,b=map(int,tok.split('-',1)); seeds.extend(range(a,b+1))
        else: seeds.append(int(tok))
    rows=[]
    for seed in seeds:
        for swap in (False,True):
            print(f'run seed={seed} swap={swap}', flush=True)
            rows.append(run_one(args.v123,args.v104,seed,swap))
    pairs=[]
    for seed in seeds:
        legs=[r for r in rows if r['seed']==seed]
        vals=[r['candidate_minus_opponent'] for r in legs]
        pairs.append({'seed':seed,'pair_delta':statistics.fmean(vals),'seat_diffs':vals,
                      'fires':[bool((r.get('telemetry') or {}).get('v122_fired_this_call')) for r in legs]})
    out={'candidate':'v123 diagnostic (behavior-identical to v122)','opponent':'exact v104',
         'metric':'candidate_minus_opponent; pair_delta averages both seats',
         'seeds':seeds,'rows':rows,'pairs':pairs}
    Path(args.out).write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps({'pairs':pairs},indent=2))

if __name__=='__main__': main()
