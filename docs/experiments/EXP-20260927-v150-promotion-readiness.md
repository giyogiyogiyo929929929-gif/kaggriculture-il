# EXP-20260927-v150-promotion-readiness

## Purpose

Pre-PROMOTE checklist for `v150_skip_noop_second_pass`. This document does not itself promote the candidate.

Formal champion remains `v115_champion_same_turn_open_squeeze` until the last pending regression gate is read and the promotion record is committed.

## Identity / reproducibility

- formal champion: `v115_champion_same_turn_open_squeeze`
- v115 SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- strategic parent: `v147_confirmed_v111_clone`
- v147 SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- promotion candidate: `v150_skip_noop_second_pass`
- v150 SHA256: `0a5bfa1b9fa91dd7ebdee1f45640719b23a7b895cbd85cc1f4f17bddebb6387d`
- v147 builder: `ci/build_v147_confirmed_v111_clone.py`
- v150 builder: `ci/build_v150_skip_noop_second_pass.py`
- formal engine: `kaggle_environments==1.32.7`

The v150 builder performs one guarded source transformation only: the second v111 pass additionally requires `parent_changed`. It requires exactly one source match before replacement and appends the Kaggle-compatible final callable alias. No new external dependency or third-party source is added by v150.

## Evaluation contract

All formal comparisons use:

`candidate_minus_champion = candidate - champion`

with same-seed seat swap and matched-pair interpretation. Single seeds and raw seat signs are not sufficient for promotion.

Legacy runtime requirement from `docs/05_evaluation.md`:

- p99 < 50 ms
- worst/max < 200 ms
- GC included
- exceptions zero

Project-level promotion also requires no meaningful worst regression, sealed reproduction, important-opponent regression checks, and an explainable mechanism.

## Completed gates

### 1. Static / reconstruction

PASS.

Evaluation workflows reconstruct exact v115, build v147, build v150, SHA-check v115/v147, and `py_compile` all relevant agents before game evaluation.

### 2. Burned matched performance

PASS through exact action equivalence to v147.

Prior v147 vs v115 on seeds 681..692, seat swapped:

- 9W / 0L / 3T
- mean +47.5
- worst 0
- best +230
- exceptions 0

v150 vs v147 complete action-equivalence on the same 24 games, run `36249173738`:

- actions identical 24/24
- rewards identical 24/24
- mismatch 0
- exceptions 0
- v111 evaluations 29,058 -> 22,710 (-21.85%)

### 3. Seat dependence / seed691 correction

PASS.

Seed691 raw v147-v115 legs were -52/+56, but exact v115-v115 baseline was about -54/+54; normalized candidate gain is +2 in both seat-relative comparisons. This is not a candidate-specific losing regression.

### 4. Mechanism / telemetry

PASS.

Focused replay telemetry showed the strategic change preserves the SELL multiset and changes only SELL ordering when the confirmed-clone second v111 pass fires. Gains can arise directly from market order processing or cascade into later farm state. No unsupported claim is made about the exact internal priority formula beyond observed behavior.

### 5. Sealed holdout

PASS.

v147 vs v115, unobserved holdout seeds 1701..1712, seat swapped:

- 10W / 0L / 2T
- mean +36.6667
- SE 11.5025
- mean - 2SE +13.6616
- worst 0
- best +112
- exceptions 0

v150 vs v147 sealed equivalence, run `36252365551`:

- actions identical 24/24
- rewards identical 24/24
- mismatch 0
- exceptions 0
- v111 evaluations 32,148 -> 26,210 (-18.47%)

Therefore v150 inherits the exact v147 sealed outcomes on these games.

### 6. Runtime

PASS, run `36252343922`.

Sequential single-process, GC enabled, paired v115/v147/v150 instrumentation, seeds 681/682/689/691/692 with seat swap.

v150:

- calls 7,190
- median 4.229 ms
- p95 9.254 ms
- p99 16.889 ms
- max wall 162.617 ms
- CPU p99 15.625 ms
- CPU max 171.875 ms
- >200 ms 0
- exceptions 0

Formal p99 and max thresholds both PASS.

### 7. Hard-opponent regression

PASS, run `36256381428`.

8 opponents x seeds 520101..520104:

- 32 matched pairs
- 0W / 0L / 32T vs v115
- mean 0
- worst 0
- best 0
- candidate exceptions 0
- champion exceptions 0
- regression_free true

Opponents:

- jaxa_2802
- melon_squeeze
- peak_2950
- salem_2900
- score_2820
- shop_router_v7
- tetsutani_ms
- thomas_router_95

### 8. Runtime-only optimization evidence

PASS for tested observations.

- focused equivalence: 20/20 games identical, evaluations -17.48%
- burned equivalence: 24/24 games identical, evaluations -21.85%
- sealed equivalence: 24/24 games identical, evaluations -18.47%

Alternative duplicate-factor caching was explicitly tested and rejected: 72 duplicates among 436,786 evaluated candidates (~0.0165%), with no useful duplicate concentration on known heavy 20,160-candidate turns.

## Pending gate

### Public diversity direct v150 regression

Run `36257645079`.

Expected panel:

- starter
- beat_v48
- bl_v20
- bl_v21
- farming_v2
- frontier_prvsiyan
- pinned/audited Seyamalam v21
- seeds 621..624

Required before PROMOTE:

- no candidate exceptions
- no meaningful v150-v115 regression
- inspect worst pair, not mean only
- confirm starter/absolute performance remains healthy

Previous v147 result on this panel was 28/28 ties relative to v115 and 56/56 absolute candidate wins. This is background only; v150 is being checked directly.

## Submission / license readiness

- v150 adds no new external code or dependency; it is a local one-guard transformation of the already-attributed v147/v115 lineage.
- Existing source retains upstream notices from the parent lineage.
- Competition rules require the submission entry to be `main.py` at archive root (or a valid multi-file tar.gz), <=100 MiB.
- Submission is a separate operation and is not performed by this promotion checklist.
- Formal Kaggle submission remains user-controlled.

Before any actual Kaggle submission, regenerate the exact submission artifact from the promoted source, record main/archive SHA256, inspect archive contents, rerun static/runtime smoke on the packaged bytes, and confirm the valid submission-slot situation.

## Promotion decision rule

If `36257645079` is clean, the evidence set is sufficient to create a formal PROMOTE record for v150 and change the canonical champion reference from v115 to v150. Do not silently mutate v115 itself.

If public diversity shows any regression, keep v115 as formal champion and analyze the differing opponent/seed observations before deciding whether v150 needs a narrower runtime optimization.

## Current decision

`KEEP TESTING — one direct public-diversity regression gate pending.`
