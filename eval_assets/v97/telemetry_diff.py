#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

EXPECTED_VERSION = '1.32.7'


def load_agent(path: str):
    from kaggle_environments.agent import get_last_callable
    raw = Path(path).read_text(encoding='utf-8')
    fn = get_last_callable(raw, path=path)
    call_index = 0
    def wrapped(obs, config=None):
        nonlocal call_index
        if obs.get('step') is None:
            obs['step'] = call_index
        call_index += 1
        return fn(obs, config)
    return wrapped, fn


def race_telemetry(fn):
    try:
        raw = dict(getattr(fn, 'telemetry', {}) or {})
    except Exception:
        return {'telemetry_error': 1}
    out = {}
    for k, v in raw.items():
        if 'race' in str(k) or 'actual_trade' in str(k):
            if isinstance(v, (str, int, float, bool)) or v is None:
                out[str(k)] = v
    return out


def game(a: str, b: str, seed: int, candidate_seat: int):
    import kaggle_environments
    from kaggle_environments import make
    if kaggle_environments.__version__ != EXPECTED_VERSION:
        raise RuntimeError(kaggle_environments.__version__)
    wa, fa = load_agent(a)
    wb, fb = load_agent(b)
    env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': seed}, debug=False)
    env.run([wa, wb])
    final = env.steps[-1]
    rewards = [float(final[i].reward or 0.0) for i in range(2)]
    statuses = [str(final[i].status) for i in range(2)]
    cfn = fa if candidate_seat == 0 else fb
    return {'rewards': rewards, 'statuses': statuses, 'candidate_telemetry': race_telemetry(cfn)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', required=True)
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--seeds', required=True, help='comma-separated seeds')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    seeds = [int(x) for x in args.seeds.split(',') if x.strip()]
    rows = []
    for seed in seeds:
        normal = game(args.candidate, args.baseline, seed, 0)
        swapped = game(args.baseline, args.candidate, seed, 1)
        rows.append({'seed': seed, 'normal': normal, 'swapped': swapped})
        print('telemetry seed', seed, flush=True)
    Path(args.out).write_text(json.dumps(rows, indent=2), encoding='utf-8')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
