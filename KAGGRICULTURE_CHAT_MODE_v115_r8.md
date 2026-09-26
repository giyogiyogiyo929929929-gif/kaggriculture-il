# KAGGRICULTURE_CHAT_MODE_v115_r8.md

## 1. Canonical state

- Formal Champion: `v115_champion_same_turn_open_squeeze.py`
- Champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- Promotion candidate: `v150_skip_noop_second_pass`
- v150 SHA256: `0a5bfa1b9fa91dd7ebdee1f45640719b23a7b895cbd85cc1f4f17bddebb6387d`
- Strategic parent: `v147_confirmed_v111_clone`
- v147 SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- Engine: `kaggle_environments==1.32.7`
- Never edit the formal champion directly. Promotion must be an explicit gated record.

## 2. v150 change

Builder: `ci/build_v150_skip_noop_second_pass.py`

Single major change only:

- v147 runs the confirmed second `_v111_reorder` when clone/standard gates pass.
- v150 additionally requires `parent_changed` before running that second pass.

No farm policy, SELL quantity, market scoring, priority rule, predictor, race detector, or endgame parameter is intentionally changed.

Reason: profiling showed `_v111_reorder` is a real hot path. A duplicate-candidate cache was tested and rejected because only 72 of 436,786 evaluated candidates were duplicates (~0.0165%). The useful optimization is avoiding redundant second full searches.

## 3. Strategic evidence inherited from v147

### Burned matched seeds 681..692

v147 vs exact v115, seat swapped:

- 9W / 0L / 3T
- mean candidate-minus-champion: +47.5
- matched-pair worst: 0
- best: +230
- exceptions: 0

Seed691 raw legs were -52/+56, but exact v115-v115 baseline was about -54/+54. Pair-normalized candidate improvement is therefore +2; the raw sign is environment/seat asymmetry, not a v147-specific regression.

### Sealed unobserved holdout 1701..1712

v147 vs exact v115, seat swapped:

- 10W / 0L / 2T
- mean: +36.6667
- SE: 11.5025
- mean - 2SE: +13.6616
- worst: 0
- best: +112
- exceptions: 0

### Mechanism

Focused telemetry established that v147 preserves the SELL multiset and changes only SELL order sequence when confirmed-clone gates allow the second `_v111_reorder` pass. Representative gains were observed without changing sale quantities. The exact internal priority function is not inferred beyond what replay establishes.

## 4. v150 semantic-equivalence evidence

### Focused equivalence

Run `36245566714`:

- seeds 681, 682, 689, 691, 692
- both seats
- 2 repetitions
- 20/20 complete v147/v150 action traces identical
- rewards identical
- mismatch 0
- exceptions 0
- v111 evaluations: 26,724 -> 22,052 (-17.48%)

### Full burned equivalence

Run `36249173738`:

- seeds 681..692
- both seats
- 24/24 complete action traces identical
- rewards identical
- mismatch 0
- exceptions 0
- v111 evaluations: 29,058 -> 22,710 (-21.85%)

### Sealed equivalence

Run `36252365551`:

- seeds 1701..1712
- both seats
- 24/24 complete action traces identical
- rewards identical
- mismatch 0
- exceptions 0
- v111 evaluations: 32,148 -> 26,210 (-18.47%)

Therefore v150 behaviorally inherits the v147 burned and sealed results on those exact observations.

## 5. Runtime qualification

Run `36252343922`, sequential single-process, GC enabled, paired v115/v147/v150 instrumentation.

v150:

- calls: 7,190
- median: 4.229 ms
- p95: 9.254 ms
- p99: 16.889 ms
- max wall: 162.617 ms
- CPU p99: 15.625 ms
- CPU max: 171.875 ms
- >200 ms: 0
- exceptions: 0

Formal runtime thresholds:

- p99 < 50 ms: PASS
- max < 200 ms: PASS
- exceptions zero: PASS

For context, the same run produced >200 ms GC-associated tails in v115 and v147, while v150 remained below 200 ms.

## 6. Known-opponent regression

Run `36256381428`, v150 vs exact v115, same 8-opponent hard universe, seeds 520101..520104:

- 32 matched pairs
- 0W / 0L / 32T
- mean 0
- worst 0
- best 0
- candidate exceptions 0
- champion exceptions 0
- regression_free: true

Hard-opponent gate: PASS.

## 7. Public diversity final gate

Workflow run `36257645079` is the final direct v150 public-diversity regression panel.

Panel:

- starter
- beat_v48
- bl_v20
- bl_v21
- farming_v2
- frontier_prvsiyan
- pinned audited `Seyamalam/Kaggriculture` v21 opponent
- seeds 621..624

At creation of this revision the run is queued. Do not PROMOTE before reading its artifact and confirming no regression / no exceptions.

Previous v147 public-diversity evidence on the same panel was 28/28 matched ties vs v115 with zero exceptions; v150 must be checked directly rather than assumed equivalent across different opponent-induced observations.

## 8. Promotion gate status

- exact v115 reconstruction / SHA: PASS
- v147 build / SHA: PASS
- v150 build / SHA: PASS
- syntax/preflight path: PASS in evaluation workflows
- burned matched performance: PASS via v147 + exact v150 action equivalence
- seat swap: PASS
- worst regression on burned panel: 0
- sealed validation: PASS via v147 + exact v150 action equivalence
- mechanism telemetry: PASS / observable SELL-order mechanism
- runtime: PASS
- hard-opponent regression: PASS
- exceptions/timeouts: 0 in completed promotion gates
- public diversity v150 direct regression: PENDING (`36257645079`)
- formal PROMOTE record: NOT YET

## 9. Decision

```text
FORMAL CHAMPION:
v115_champion_same_turn_open_squeeze.py

PROMOTION CANDIDATE:
v150_skip_noop_second_pass

STATUS:
KEEP TESTING
PUBLIC DIVERSITY FINAL GATE PENDING
NO PROMOTE YET
```

If public diversity is clean, next actions are:

1. record the public-diversity artifact and exact result;
2. finalize the v150 experiment decision as PROMOTE;
3. create/update promotion record and canonical chat mode with v150 as formal champion;
4. update handover / score summary where present;
5. run one final reconstruction/runtime smoke if promotion packaging changes any bytes;
6. do not make a Kaggle submission automatically.
