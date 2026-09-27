# EXP-20260927-v150-promotion-readiness

## Status

CLOSED — v150 passed all normal-game strategic/regression gates but was not promoted because packaging preflight exposed one NFR-2 defect (`observation=None`). The safety-only child `v151_none_observation_guard` fixed that defect and subsequently passed promotion qualification.

## Identity

- former formal champion: `v115_champion_same_turn_open_squeeze`
- v115 SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- strategic parent: `v147_confirmed_v111_clone`
- v147 SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- runtime candidate: `v150_skip_noop_second_pass`
- v150 SHA256: `0a5bfa1b9fa91dd7ebdee1f45640719b23a7b895cbd85cc1f4f17bddebb6387d`
- final safety child: `v151_none_observation_guard`
- v151 SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- engine: `kaggle_environments==1.32.7`

## v150 evidence

### Burned strategic result inherited from v147

v147 vs v115, seeds 681..692, seat swapped:

- 9W / 0L / 3T
- mean +47.5
- worst 0
- best +230
- exceptions 0

v150 vs v147 on the same 24 games, run `36249173738`:

- actions identical 24/24
- rewards identical 24/24
- mismatches 0
- exceptions 0
- v111 evaluations 29,058 -> 22,710 (-21.85%)

### Sealed

v147 vs v115, unobserved holdout 1701..1712, seat swapped:

- 10W / 0L / 2T
- mean +36.6667
- SE 11.5025
- mean - 2SE +13.6616
- worst 0
- best +112
- exceptions 0

v150 vs v147, run `36252365551`:

- actions identical 24/24
- rewards identical 24/24
- mismatches 0
- exceptions 0
- v111 evaluations 32,148 -> 26,210 (-18.47%)

### Hard opponents

Run `36256381428`, eight opponents x seeds 520101..520104:

- 32 matched pairs
- 0W / 0L / 32T vs v115
- mean 0
- worst 0
- best 0
- candidate/champion exceptions 0
- regression_free true

### Public diversity

Run `36257645079`, seven opponents x seeds 621..624:

- 28 matched pairs
- 0W / 0L / 28T vs v115
- mean 0
- worst 0
- best 0
- candidate/champion exceptions 0
- candidate absolute games: 56
- candidate absolute wins: 56
- candidate absolute losses: 0
- regression_free true

Opponents: starter, beat_v48, bl_v20, bl_v21, farming_v2, frontier_prvsiyan, pinned/audited Seyamalam v21.

### Runtime

Run `36252343922` formally passed for v150:

- p99 16.889 ms
- max 162.617 ms
- >200 ms 0
- exceptions 0

The raw max is GC-sensitive across repetitions; promotion decisions therefore use the explicitly defined GC-on qualification run rather than cherry-picking a favorable control/candidate maximum.

## Why v150 itself was not promoted

Promotion packaging preflight run `36258187466` passed reconstruction, Kaggle-compatible loading, import audit, normal action shape, 720-turn completion, and runtime, but failed one malformed-observation contract:

- `observation=None` -> `AttributeError("'NoneType' object has no attribute 'get'")`

This violated repository NFR-2. The bugfix was separated from the runtime optimization rather than silently editing v150.

## Resolution

`v151_none_observation_guard` adds only an early safe PASS return for `observation is None`; all non-None observations delegate to v150 unchanged.

Run `36259834091` proved v150/v151 action and reward equivalence on 48 burned+sealed games and passed the full packaging preflight. Run `36259995740` passed formal GC-on runtime qualification.

Therefore v150 is closed as an intermediate candidate. The formal promotion target is v151. See:

- `docs/experiments/EXP-20260927-v151-none-observation-safety.md`
- `docs/experiments/PROMOTE-20260927-v151.md`

## Decision

`CLOSED — do not promote v150 directly; promote v151 as its safety-complete successor.`
