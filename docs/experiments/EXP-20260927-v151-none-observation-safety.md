# EXP-20260927-v151-none-observation-safety

## Status

PROMOTE — safety-complete successor to v150.

## Parent / former champion

- former formal champion: `v115_champion_same_turn_open_squeeze`
- v115 SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- strategic/runtime parent: `v150_skip_noop_second_pass`
- v150 SHA256: `0a5bfa1b9fa91dd7ebdee1f45640719b23a7b895cbd85cc1f4f17bddebb6387d`
- candidate: `v151_none_observation_guard`
- v151 SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- builder: `ci/build_v151_none_observation_guard.py`
- engine: `kaggle_environments==1.32.7`

## Trigger

v150 packaging preflight run `36258187466` passed all normal-game checks but failed `observation=None` with:

`AttributeError("'NoneType' object has no attribute 'get'")`

The failure was isolated to malformed-input safety and did not justify altering the validated strategy/runtime optimization in-place.

## Change

One bugfix only:

```python
_V151_PARENT = agent

def agent(observation, configuration=None):
    if observation is None:
        return {'farmer': ['PASS'], 'hands': [], 'market': []}
    return _V151_PARENT(observation, configuration)
```

Every non-None observation delegates directly to v150 and returns its result unchanged. No farm, market, SELL ordering, prediction, race, clone detection, or endgame policy changes.

## Safety / semantic qualification

Run `36259834091` — SUCCESS.

### Exact identity

- v151 source SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- source size: 1,056,333 bytes

### v150 -> v151 action equivalence

Panels:

- burned seeds 681..692, both seats
- sealed seeds 1701..1712, both seats

Total:

- 48 games
- action traces identical: 48/48
- rewards identical: 48/48
- mismatches: 0
- errors: 0
- `action_equivalent: true`

Thus all tested normal-game strategic evidence for v150 is inherited by v151 on these key panels.

### Full preflight

All checks PASS:

- submission file present
- last function is `agent`
- Kaggle-compatible loader works
- standard library / local imports only
- no imitation-model dependency
- action shape valid
- all five malformed-observation patterns safe, including `None`
- 720-turn episode DONE

Preflight timing in this run:

- median 2.42 ms
- p99 9.91 ms
- max 131.39 ms

### Packaging

Generated package was not submitted to Kaggle.

- archive members: exactly `main.py`
- packed main bytes match source: true
- archive bytes: 621,369
- archive SHA256: `4220541594344fab249835fa8e453494709eff4b4f3895d764bb9596687a5ad0`
- packed/source main SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`

## Formal runtime qualification

Run `36259995740` — SUCCESS / formal PASS.

Configuration:

- sequential single-process
- GC enabled
- `perf_counter_ns` + `process_time_ns`
- seeds 681, 682, 689, 691, 692
- seat swap
- 7,190 v151 calls

v151:

- median 4.167 ms
- p95 9.1638 ms
- p99 16.8518 ms
- max wall 162.0771 ms
- CPU p99 15.625 ms
- CPU max 171.875 ms
- >50 ms: 12
- >200 ms: 0
- errors: 0
- formal pass: true

Formal thresholds:

- p99 < 50 ms: PASS
- max < 200 ms: PASS

The same run again demonstrated that isolated GC tails can vary substantially between agents/runs; the v151 formal measurement itself satisfies the configured gate.

## Inherited strategic evidence

Because v151 is identical to v150 for all non-None observations and exact equivalence was verified across the burned+sealed panels, the promotion decision uses the already-completed v150/v147 evidence:

### Burned direct improvement lineage

v147 vs v115, seeds 681..692, seat swapped:

- 9W / 0L / 3T
- mean +47.5
- worst 0
- best +230
- exceptions 0

v150 matched v147 exactly on all 24 burned games while reducing v111 evaluations by 21.85%.

### Sealed holdout

v147 vs v115, seeds 1701..1712, seat swapped:

- 10W / 0L / 2T
- mean +36.6667
- worst 0
- best +112
- exceptions 0

v150 matched v147 exactly on all 24 sealed games; v151 then matched v150 exactly on those same 24 games.

### Hard opponents

v150 vs v115, run `36256381428`:

- 32 matched pairs
- 0W / 0L / 32T
- mean 0
- worst 0
- exceptions 0
- regression_free true

### Public diversity

v150 vs v115, run `36257645079`:

- 28 matched pairs
- 0W / 0L / 28T
- mean 0
- worst 0
- exceptions 0
- 56/56 absolute wins against the seven tested opponents
- regression_free true

The v151 wrapper activates only for `observation is None`; normal Kaggriculture observations in these opponent evaluations therefore follow the v150 path unchanged.

## Decision

PROMOTE `v151_none_observation_guard` as the new formal champion.

Promotion rationale:

- replicated positive burned improvement
- sealed improvement with no losing seed
- seat-swapped matched evaluation
- mechanism explained by replay telemetry
- no hard-opponent regression
- no public-diversity regression
- exact v150/v151 equivalence on 48 key games
- formal runtime PASS
- full malformed-observation preflight PASS
- package/source identity verified
- exceptions/errors zero

Kaggle submission is **not** part of this promotion and has not been performed by this workflow.
