from __future__ import annotations
import copy, importlib.util, json, math, statistics, time, hashlib
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parent

def load(path, tag):
    spec = importlib.util.spec_from_file_location(tag, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, mod.agent

class Timed:
    def __init__(self, fn):
        self.fn = fn
        self.ms = []
        self.errors = 0
    def __call__(self, obs, config=None):
        t = time.perf_counter()
        try:
            n = self.fn.__code__.co_argcount
            return self.fn(*[obs, config][:n])
        except Exception:
            self.errors += 1
            raise
        finally:
            self.ms.append((time.perf_counter() - t) * 1000)

def game(a, b, seed, swap=False, timed=False):
    ma, fa = load(Path(a), f'a{seed}{swap}{time.time_ns()}')
    built = str(b) in {'starter', 'pass', 'random'}
    if built:
        fb = str(b)
    else:
        _, fb = load(Path(b), f'b{seed}{swap}{time.time_ns()}')
    ta = Timed(fa)
    aa = ta if timed else fa
    bb = fb
    env = make('kaggriculture', configuration={'seed': int(seed)}, debug=False)
    env.run([bb, aa] if swap else [aa, bb])
    rewards = [float(x.reward) for x in env.state]
    ar, br = (rewards[1], rewards[0]) if swap else (rewards[0], rewards[1])
    return {
        'a': ar,
        'b': br,
        'delta': ar - br,
        'telemetry': copy.deepcopy(getattr(ma.agent, 'telemetry', {})),
        'ms': ta.ms if timed else [],
        'errors': ta.errors,
    }

def pair(a, b, seed, timed=False):
    x = game(a, b, seed, False, timed)
    y = game(a, b, seed, True, timed)
    return {
        'seed': seed,
        'pair_diff': (x['delta'] + y['delta']) / 2,
        'games': [x, y],
    }

def summ(rows):
    vals = [x['pair_diff'] for x in rows]
    n = len(vals)
    mean = statistics.mean(vals)
    se = statistics.stdev(vals) / (n ** .5) if n > 1 else 0
    return {
        'n': n,
        'wins': sum(x > 0 for x in vals),
        'losses': sum(x < 0 for x in vals),
        'draws': sum(x == 0 for x in vals),
        'mean': mean,
        'median': statistics.median(vals),
        'stderr': se,
        'mean_minus_2se': mean - 2 * se,
        'worst': min(vals),
        'best': max(vals),
        'values': vals,
    }

def block(a, b, start, n):
    rows = []
    for seed in range(start, start + n):
        row = pair(a, b, seed)
        rows.append(row)
        print(seed, row['pair_diff'], flush=True)
    return {'summary': summ(rows), 'rows': rows}

def tele(block):
    out, steps = {}, []
    for row in block['rows']:
        for g in row['games']:
            d = (g.get('telemetry') or {}).get('wheat_post_town_delay1') or {}
            for k, v in d.items():
                if k == 'steps':
                    steps += list(v)
                elif isinstance(v, (int, float)):
                    out[k] = out.get(k, 0) + v
    out['steps'] = steps
    return out

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    v112 = ROOT / 'v112_wheat_lead3_lowdemand.py'
    v117 = ROOT / 'v117_wheat_post_town_delay1.py'
    rep = {
        'engine': '1.32.7',
        'sign': 'candidate_minus_champion = candidate - champion',
        'champion': 'v112_wheat_lead3_lowdemand',
        'candidate': 'v117_wheat_post_town_delay1',
        'sha256': {'v112': sha(v112), 'v117': sha(v117)},
    }
    rep['validation'] = block(v117, v112, 296001, 12)
    rep['sealed'] = block(v117, v112, 297001, 4)
    rep['stress'] = block(v117, v112, 298001, 8)
    rep['v117_starter'] = block(v117, 'starter', 1, 5)
    rep['v112_starter'] = block(v112, 'starter', 1, 5)
    rr = pair(v117, v112, 800501, True)
    ms = sorted(z for g in rr['games'] for z in g['ms'])
    idx = min(len(ms) - 1, max(0, math.ceil(.99 * len(ms)) - 1))
    rep['runtime'] = {
        'callbacks': len(ms),
        'median_ms': statistics.median(ms),
        'p99_ms': ms[idx],
        'max_ms': max(ms),
        'errors': sum(g['errors'] for g in rr['games']),
    }
    rep['telemetry_validation'] = tele(rep['validation'])
    rep['telemetry_sealed'] = tele(rep['sealed'])
    rep['telemetry_stress'] = tele(rep['stress'])
    Path('v117_eval.json').write_text(json.dumps(rep, indent=2))
    print('SUMMARY', json.dumps({
        k: (v['summary'] if isinstance(v, dict) and 'summary' in v else v)
        for k, v in rep.items()
        if k != 'sign'
    }, indent=2), flush=True)

if __name__ == '__main__':
    main()
