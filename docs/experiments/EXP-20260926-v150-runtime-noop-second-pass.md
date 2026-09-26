# EXP-20260926-v150-runtime-noop-second-pass

## Status
KEEP TESTING — burned + sealed action equivalence PASS, formal runtime PASS, hard-opponent regression queued.

## Parent / champion
- parent candidate: `v147_confirmed_v111_clone`
- formal champion: `v115_champion_same_turn_open_squeeze`
- v115 SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- v147 SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- v150 SHA256: `0a5bfa1b9fa91dd7ebdee1f45640719b23a7b895cbd85cc1f4f17bddebb6387d`

## Motivation
v147 has strong strategic evidence but repeatedly exposed rare runtime tails. Profiling showed `_v111_reorder` is a real hot path and that extreme maxima are strongly GC-dependent. v147 may call `_v111_reorder` a second time after clone confirmation even when the parent v111 pass made no change.

## Candidate
`v150_skip_noop_second_pass`

Builder: `ci/build_v150_skip_noop_second_pass.py`

### Change
One guard only:
- v147: run confirmed second `_v111_reorder` whenever clone/standard gates pass.
- v150: run that second pass only when `parent_changed` is also true.

No farm policy, market scoring, SELL quantity, order priority, prediction, race detection, or endgame parameter is changed.

## Duplicate-candidate probe
Run `36245268147` — success.
- evaluated candidates: 436,786
- duplicate evaluated candidates: 72
- duplicate fraction: ~0.0165%
- heavy 20,160-candidate turns had no useful duplicate concentration

Alternative factor-cache idea: REJECT. Duplicate reuse is too rare to materially reduce the hot path.

## Focused equivalence/runtime
Run `36245566714` — success.
Seeds `681,682,689,691,692`, both seats, 2 repetitions.
- complete v147/v150 action traces identical in all 20 games
- final rewards identical
- mismatches 0, exceptions 0
- v111 evaluations: 26,724 -> 22,052 (-17.48%)
- median: 4.379 -> 4.297 ms
- p99: 18.821 -> 18.378 ms
- >50 ms: 51 -> 42

Focused raw max remained GC-noisy and was not used as formal qualification.

## Full burned action equivalence
Run `36249173738` — success.
Seeds `681..692`, both seats = 24 games.
- action traces identical: 24/24
- final rewards identical: 24/24
- mismatches 0, exceptions 0
- v111 evaluations: 29,058 -> 22,710 (-21.8459632459%)

## Sealed-panel action equivalence
Run `36252365551` — success.
Seeds `1701..1712`, both seats = 24 games.
- action traces identical: 24/24
- final rewards identical: 24/24
- mismatches 0, exceptions 0
- v111 evaluations: 32,148 -> 26,210 (-18.4708224462%)

Because v150 returned exactly the same actions and rewards as v147 on every previously sealed game, the prior v147 sealed performance result (10W/0L/2T vs v115, mean +36.6667, worst 0) is behaviorally inherited on this panel.

## Final runtime qualification
Run `36252343922` — success.
Engine `kaggle_environments==1.32.7`, sequential single-process, GC enabled, `perf_counter_ns` + `process_time_ns`, seeds `681,682,689,691,692`, seat swap.

| metric | v115 | v147 | v150 |
|---|---:|---:|---:|
| calls | 7,190 | 7,190 | 7,190 |
| median | 4.122 ms | 4.168 ms | 4.229 ms |
| p95 | 8.821 ms | 9.240 ms | 9.254 ms |
| p99 | 15.793 ms | 18.292 ms | 16.889 ms |
| max | 774.735 ms | 1490.984 ms | **162.617 ms** |
| CPU p99 | 15.625 ms | 15.625 ms | 15.625 ms |
| CPU max | 765.625 ms | 1484.375 ms | **171.875 ms** |
| >50 ms | 7 | 27 | 16 |
| >200 ms | 1 | 2 | **0** |

Formal thresholds:
- p99 < 50 ms: PASS (`16.889 ms`)
- max < 200 ms: PASS (`162.617 ms`)
- exceptions: 0
- workflow `formal_pass`: true

Notably, under the same GC-on instrumentation v115 and v147 both had >200 ms GC-associated tails, while v150 did not in this qualification run.

## Remaining validation
1. exact reconstruction / syntax: PASS
2. focused action equivalence: PASS
3. full burned action equivalence: PASS
4. sealed action equivalence: PASS
5. final GC-on runtime: PASS
6. hard-opponent regression: QUEUED (`v150` vs `v115`, same 8-opponent universe and seeds `520101..520104`)
7. public diversity regression: run if needed after hard panel; do not infer from v147 alone
8. final documentation / PROMOTE only after known-opponent regression is clean

## Runs
- duplicate-candidate diagnostic: `36245268147` — success
- focused v150 equivalence/runtime: `36245566714` — success
- full burned action equivalence: `36249173738` — success
- final runtime qualification: `36252343922` — success / formal PASS
- sealed action equivalence: `36252365551` — success
- hard-opponent regression: workflow added, pending run completion

## Decision
KEEP TESTING. Formal champion remains v115 until the known-opponent regression gate is clean and promotion records are updated.
