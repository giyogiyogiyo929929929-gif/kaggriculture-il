# EXP-20260927-v150-promotion-readiness

## Purpose

Pre-PROMOTE checklist for `v150_skip_noop_second_pass`. This document does not itself promote the candidate.

Formal champion remains `v115_champion_same_turn_open_squeeze` until all remaining gates and submission-readiness checks are clean.

## Identity / reproducibility

- formal champion: `v115_champion_same_turn_open_squeeze`
- v115 SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- strategic parent: `v147_confirmed_v111_clone`
- v147 SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- promotion candidate before packaging preflight: `v150_skip_noop_second_pass`
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

Project-level promotion also requires no meaningful worst regression, sealed reproduction, important-opponent regression checks, an explainable mechanism, and clean packaging/preflight behavior.

## Completed strategic/runtime gates

### 1. Static / reconstruction

PASS.

Evaluation workflows reconstruct exact v115, build v147, build v150, SHA-check v115/v147/v150, and `py_compile` all relevant agents before game evaluation.

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

### 8. Runtime-only optimization evidence

PASS for tested normal observations.

- focused equivalence: 20/20 games identical, evaluations -17.48%
- burned equivalence: 24/24 games identical, evaluations -21.85%
- sealed equivalence: 24/24 games identical, evaluations -18.47%

Alternative duplicate-factor caching was explicitly tested and rejected: 72 duplicates among 436,786 evaluated candidates (~0.0165%), with no useful duplicate concentration on known heavy 20,160-candidate turns.

## Packaging preflight blocker

Run `36258187466` reconstructed exact v150 and then executed `scripts/preflight.py` against the exact packaged source candidate.

PASS items:

- exact SHA reconstruction
- `py_compile`
- Kaggle-compatible loader
- stdlib/local-import audit
- normal action shape
- four malformed-observation shapes other than `None`
- 720-turn completion
- runtime: median 3.58 ms / p99 16.60 ms / max 158.51 ms

FAIL item:

- `observation=None` raises `AttributeError("'NoneType' object has no attribute 'get'")`

This violates the repository's NFR-2 preflight contract, so v150 is **not** promoted as the final packaged champion source even if public diversity is clean.

The failure is isolated from normal-game strategic behavior. A separate bugfix candidate `v151_none_observation_guard` was created rather than modifying v150 in-place. See `docs/experiments/EXP-20260927-v151-none-observation-safety.md`.

## Remaining gates

### Public diversity direct v150 regression

Run `36257645079` is currently executing the same seven-opponent panel used for v147:

- starter
- beat_v48
- bl_v20
- bl_v21
- farming_v2
- frontier_prvsiyan
- pinned/audited Seyamalam v21
- seeds 621..624

This still matters because v151 delegates exactly to v150 for every non-None observation. A clean v150 public panel can therefore be combined with v151's non-None equivalence proof, but the final promotion record must state that inheritance explicitly.

### v151 safety qualification

Workflow `.github/workflows/v151-safety-equivalence-preflight-selfhosted.yml` has been added.

Required:

- full preflight PASS including `observation=None`
- package root contains exactly `main.py`
- packed source bytes equal candidate source bytes
- exact v150/v151 action and reward equivalence on burned `681..692` and sealed `1701..1712`, both seats
- record v151 SHA256 and archive SHA256
- final runtime remains within formal limits

## Submission / license readiness

- v150/v151 add no new external code or dependency; both are local transformations of the already-attributed parent lineage.
- Existing source retains upstream notices from the parent lineage.
- Competition rules require the submission entry to be `main.py` at archive root (or a valid multi-file tar.gz), <=100 MiB.
- Submission is a separate operation and is not performed by these qualification workflows.
- Formal Kaggle submission remains user-controlled.

## Promotion decision rule

v150 itself is now blocked by the repository's malformed-observation preflight contract. If public diversity is clean and v151 passes its safety/equivalence/preflight qualification, promotion should target **v151**, not v150.

Do not silently mutate v115 or v150.

## Current decision

`KEEP TESTING — v150 normal-game gates are strong, but packaging NFR-2 blocks promotion; v151 safety child is under qualification.`
