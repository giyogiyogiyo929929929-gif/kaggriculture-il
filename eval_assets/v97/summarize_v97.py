#!/usr/bin/env python3
from __future__ import annotations
import json, math, statistics
from pathlib import Path

R = Path('results')

def load(name):
    return json.loads((R/name).read_text(encoding='utf-8'))

def stats(rows):
    d = [float(r['candidate_minus_baseline']) for r in rows]
    n = len(d)
    mean = statistics.fmean(d) if d else 0.0
    se = statistics.stdev(d)/math.sqrt(n) if n > 1 else 0.0
    normal = [float(r['normal']['rewards'][0]) - float(r['normal']['rewards'][1]) for r in rows]
    swapped = [float(r['swapped']['rewards'][1]) - float(r['swapped']['rewards'][0]) for r in rows]
    return {
        'pairs': n,
        'wins': sum(x > 0 for x in d), 'losses': sum(x < 0 for x in d), 'draws': sum(x == 0 for x in d),
        'mean': mean, 'median': statistics.median(d) if d else 0.0, 'stderr': se,
        'mean_minus_2se': mean - 2*se, 'min': min(d) if d else 0.0, 'max': max(d) if d else 0.0,
        'candidate_exceptions': sum(int(r.get('candidate_exceptions', 0)) for r in rows),
        'failed_pairs': sum(not bool(r.get('ok')) for r in rows),
        'seat0_margin_mean': statistics.fmean(normal) if normal else 0.0,
        'seat1_margin_mean': statistics.fmean(swapped) if swapped else 0.0,
        'diff_seeds': [int(r['seed']) for r in rows if float(r['candidate_minus_baseline']) != 0.0],
        'per_seed': [{'seed': int(r['seed']), 'candidate_minus_champion': float(r['candidate_minus_baseline'])} for r in rows],
    }

def pct(xs, p):
    xs = sorted(float(x) for x in xs)
    if not xs: return 0.0
    if len(xs) == 1: return xs[0]
    pos = (len(xs)-1)*p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi: return xs[lo]
    return xs[lo] + (xs[hi]-xs[lo])*(pos-lo)

validation = load('validation.json')
sealed = load('sealed.json')
starter_c = load('starter_candidate.json')
starter_b = load('starter_champion.json')
runtime = load('runtime.json')
vs = stats(validation); ss = stats(sealed)

starter = []
for c, b in zip(starter_c, starter_b):
    assert c['seed'] == b['seed']
    starter.append({
        'seed': c['seed'],
        'candidate_pair_margin': c['candidate_minus_baseline'],
        'champion_pair_margin': b['candidate_minus_baseline'],
        'delta': c['candidate_minus_baseline'] - b['candidate_minus_baseline'],
        'normal_rewards_identical': c['normal']['rewards'] == b['normal']['rewards'],
        'swapped_rewards_identical': c['swapped']['rewards'] == b['swapped']['rewards'],
        'candidate_exceptions': c.get('candidate_exceptions', 0),
    })

durations = [x for r in runtime for x in r.get('candidate_runtime_ms', [])]
runtime_summary = {
    'callbacks': len(durations), 'median_ms': statistics.median(durations) if durations else 0.0,
    'p95_ms': pct(durations, .95), 'p99_ms': pct(durations, .99), 'max_ms': max(durations) if durations else 0.0,
    'exceptions': sum(int(r.get('candidate_exceptions',0)) for r in runtime),
}

summary = {
    'candidate': 'v97_candidate_actual_trade_race.py',
    'champion': 'v96_champion_lead11_milkshops2.py',
    'engine': 'kaggle_environments==1.32.7',
    'validation_328001_328020': vs,
    'sealed_329001_329020': ss,
    'starter_1_5': starter,
    'runtime_330001': runtime_summary,
    'promotion_gate': {
        'validation_mean_gt_2se': vs['mean'] > 2*vs['stderr'],
        'sealed_mean_gt_2se': ss['mean'] > 2*ss['stderr'],
        'starter_no_score_regression': all(x['delta'] == 0 for x in starter),
        'starter_rewards_identical': all(x['normal_rewards_identical'] and x['swapped_rewards_identical'] for x in starter),
        'runtime_safe': runtime_summary['p99_ms'] < 50 and runtime_summary['max_ms'] < 200 and runtime_summary['exceptions'] == 0,
    },
}
(R/'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
lines = [
    '# v97 official 1.32.7 evaluation', '',
    f"Validation: {vs['wins']}W/{vs['losses']}L/{vs['draws']}D, mean={vs['mean']:.3f}, SE={vs['stderr']:.3f}, mean-2SE={vs['mean_minus_2se']:.3f}, min={vs['min']:.3f}, max={vs['max']:.3f}",
    f"Validation diff seeds: {vs['diff_seeds'] or 'none'}", '',
    f"Sealed: {ss['wins']}W/{ss['losses']}L/{ss['draws']}D, mean={ss['mean']:.3f}, SE={ss['stderr']:.3f}, mean-2SE={ss['mean_minus_2se']:.3f}, min={ss['min']:.3f}, max={ss['max']:.3f}",
    f"Sealed diff seeds: {ss['diff_seeds'] or 'none'}", '',
    f"Starter deltas: {[x['delta'] for x in starter]}",
    f"Starter raw rewards identical: {summary['promotion_gate']['starter_rewards_identical']}", '',
    f"Runtime: callbacks={runtime_summary['callbacks']}, median={runtime_summary['median_ms']:.3f}ms, p95={runtime_summary['p95_ms']:.3f}ms, p99={runtime_summary['p99_ms']:.3f}ms, max={runtime_summary['max_ms']:.3f}ms, exceptions={runtime_summary['exceptions']}", '',
    f"Promotion gates: {summary['promotion_gate']}",
]
(R/'summary.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print('\n'.join(lines))
