# uploaded 127ed3 safety-v3 — dedicated runtime result

## Identity

- candidate: safety-v3
- candidate SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- comparison champion: v147 SHA256 `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- Actions run: `36237376092`
- artifact: `uploaded-127ed3-safe-v3-stress-runtime`
- environment: Python 3.11, `kaggle-environments==1.32.7`, self-hosted Windows X64

## Method

Dedicated serial runtime gate matching the v147 methodology:

- opponent: starter
- seeds: 641, 642
- both seats
- single-process / serial
- thresholds: max per-game p99 < 50 ms; worst turn < 200 ms; exceptions = 0; non-DONE = 0

## safety-v3 result

| seed | seat | median ms | p99 ms | worst ms |
|---:|:---:|---:|---:|---:|
| 641 | 0 | 1.8289 | 11.5115 | 151.1681 |
| 641 | 1 | 2.0560 | 14.3596 | 105.1169 |
| 642 | 0 | 2.1219 | 17.2066 | 169.2014 |
| 642 | 1 | 2.2369 | 16.5425 | 158.2254 |

Aggregate gate values:

- median of game medians: **2.08895 ms**
- max game p99: **17.2066 ms**
- worst turn: **169.2014 ms**
- exceptions: **0**
- non-DONE: **0**
- runtime gate: **PASS**

The broad H2H/stress instrumentation had previously observed isolated turns above 200 ms, but the formal dedicated serial benchmark is the decision methodology and passes the stated NFR.

## v147 reference in the same benchmark

- median of game medians: 3.38135 ms
- max game p99: 15.1117 ms
- worst turn: 224.4123 ms
- exceptions: 0
- non-DONE: 0

This reference is recorded for context only; safety-v3 promotion is judged against the candidate runtime threshold, which it passes.

## Decision

**RUNTIME PASS.**

Together with the canonical sealed result (11W/1L, mean +722.625, mean-2SE +398.536), the remaining promotion blocker is known-opponent regression, not runtime.
