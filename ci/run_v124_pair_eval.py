from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path

from kaggle_environments import make
from scripts.preflight import call_like_kaggle, load_like_kaggle, turn_time_stats


def parse_seeds(text: str) -> list[int]:
    out: list[int] = []
    for part in text.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def money(env, seat: int) -> float:
    for src in (env.state[seat].get('observation'), env.steps[-1][seat].get('observation')):
        if isinstance(src, dict):
            farms = src.get('farms')
            if isinstance(farms, list) and len(farms) > seat and isinstance(farms[seat], dict) and 'money' in farms[seat]:
                return float(farms[seat]['money'])
    return float(env.state[seat]['reward'])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', required=True)
    ap.add_argument('--champion', required=True)
    ap.add_argument('--seeds', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    candidate = Path(args.candidate)
    champion = Path(args.champion)
    seeds = parse_seeds(args.seeds)
    rows = []

    for seed in seeds:
        for candidate_seat in (0, 1):
            ca = load_like_kaggle(candidate)
            ch = load_like_kaggle(champion)
            agents = [ca, ch] if candidate_seat == 0 else [ch, ca]
            times = [[], []]
            errors = [[], []]
            wrapped = []
            for seat, impl in enumerate(agents):
                def wrapper(obs, cfg=None, _impl=impl, _seat=seat):
                    t0 = time.perf_counter()
                    try:
                        return call_like_kaggle(_impl, obs, cfg)
                    except Exception as exc:
                        errors[_seat].append(f'{type(exc).__name__}: {exc}')
                        return {'farmer': ['PASS'], 'hands': [], 'market': []}
                    finally:
                        times[_seat].append(time.perf_counter() - t0)
                wrapped.append(wrapper)

            env = make('kaggriculture', configuration={'seed': seed})
            env.run(wrapped)
            cash = [money(env, 0), money(env, 1)]
            champion_seat = 1 - candidate_seat
            rows.append({
                'seed': seed,
                'candidate_seat': candidate_seat,
                'candidate_money': cash[candidate_seat],
                'champion_money': cash[champion_seat],
                'candidate_minus_champion': cash[candidate_seat] - cash[champion_seat],
                'statuses': [x.get('status') for x in env.state],
                'errors': errors,
                'candidate_runtime': turn_time_stats(times[candidate_seat]),
            })

    pairs = []
    for seed in seeds:
        rr = [r for r in rows if r['seed'] == seed]
        rr.sort(key=lambda r: r['candidate_seat'])
        legs = [r['candidate_minus_champion'] for r in rr]
        pair = sum(legs) / len(legs)
        pairs.append({
            'seed': seed,
            'seat0': legs[0],
            'seat1': legs[1],
            'candidate_minus_champion': pair,
            'outcome': 'W' if pair > 0 else 'L' if pair < 0 else 'D',
        })

    vals = [p['candidate_minus_champion'] for p in pairs]
    se = statistics.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
    result = {
        'seeds': seeds,
        'pairs': pairs,
        'wld': {k: sum(p['outcome'] == k for p in pairs) for k in 'WLD'},
        'mean': statistics.mean(vals) if vals else 0.0,
        'median': statistics.median(vals) if vals else 0.0,
        'stderr': se,
        'mean_minus_2stderr': (statistics.mean(vals) - 2 * se) if vals else 0.0,
        'worst': min(vals) if vals else 0.0,
        'best': max(vals) if vals else 0.0,
        'seat0_mean': statistics.mean(r['candidate_minus_champion'] for r in rows if r['candidate_seat'] == 0),
        'seat1_mean': statistics.mean(r['candidate_minus_champion'] for r in rows if r['candidate_seat'] == 1),
        'exceptions': sum(len(e) for r in rows for e in r['errors']),
        'non_done': sum(any(s != 'DONE' for s in r['statuses']) for r in rows),
        'max_p99_ms': max(1000 * r['candidate_runtime']['p99'] for r in rows),
        'max_worst_ms': max(1000 * r['candidate_runtime']['worst'] for r in rows),
        'rows': rows,
    }
    Path(args.out).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['wld','mean','median','stderr','mean_minus_2stderr','worst','best','seat0_mean','seat1_mean','exceptions','non_done','max_p99_ms','max_worst_ms']}, indent=2))


if __name__ == '__main__':
    main()
