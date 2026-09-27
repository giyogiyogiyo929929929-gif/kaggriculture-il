from __future__ import annotations
import time
from kaggle_environments import make
import run_v124_econ_gap_probe as r


def bound_game(name, opp_path, seed, swap):
    champ_fn = r.load(r.CHAMP, f'c_{name}_{seed}_{swap}_{time.time_ns()}')
    opp_fn = r.load(opp_path, f'o_{name}_{seed}_{swap}_{time.time_ns()}')
    tc = r.Trace(champ_fn, 'v112')
    to = r.Trace(opp_fn, name)
    env = make('kaggriculture', configuration={'seed': int(seed)}, debug=False)
    env.run([to.__call__, tc.__call__] if swap else [tc.__call__, to.__call__])
    rewards = [float(s.reward) for s in env.state]
    cm, om = (rewards[1], rewards[0]) if swap else (rewards[0], rewards[1])
    c = tc.finish(cm); o = to.finish(om)
    days = sorted(set(c['day_money']) | set(o['day_money']), key=lambda x:int(x))
    gap = {d: float(c['day_money'].get(d,0))-float(o['day_money'].get(d,0)) for d in days if d in c['day_money'] and d in o['day_money']}
    return {'opponent':name,'seed':seed,'swap':swap,'candidate_minus_opponent':cm-om,'v112':c,'opponent_trace':o,'money_gap_by_day':gap}

r.game = bound_game
r.main()
