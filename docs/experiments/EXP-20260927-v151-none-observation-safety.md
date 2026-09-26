# EXP-20260927-v151-none-observation-safety

## Status

KEEP TESTING — safety-only child of v150; qualification queued.

## Parent / champion

- formal champion: `v115_champion_same_turn_open_squeeze`
- strategic/runtime parent: `v150_skip_noop_second_pass`
- v150 SHA256: `0a5bfa1b9fa91dd7ebdee1f45640719b23a7b895cbd85cc1f4f17bddebb6387d`
- candidate: `v151_none_observation_guard`
- builder: `ci/build_v151_none_observation_guard.py`

## Trigger

Promotion packaging preflight run `36258187466` reconstructed exact v150 successfully and passed:

- `py_compile`
- exact v115/v147/v150 SHA checks
- Kaggle-compatible loader
- stdlib/local-import audit
- normal action-shape check
- malformed observations `{}`, `{'player':0}`, `{'farms':[]}`, and `{'player':5,'farms':[{}]}`
- 720-turn completion
- runtime: median 3.58 ms, p99 16.60 ms, max 158.51 ms

It failed exactly one NFR-2 case:

- `observation is None` -> `AttributeError: 'NoneType' object has no attribute 'get'`

Therefore v150 is not promoted as packaged source even though all normal-game strategic/runtime gates remain clean.

## Change

One bugfix only:

```python
_V151_PARENT = agent

def agent(observation, configuration=None):
    if observation is None:
        return {'farmer': ['PASS'], 'hands': [], 'market': []}
    return _V151_PARENT(observation, configuration)
```

For every non-None observation, v151 delegates directly to v150 with identical arguments and returns the parent result unchanged. No farm, market, SELL ordering, prediction, race, clone detection, or endgame logic changes.

## Hypothesis

v151 should be behaviorally identical to v150 on all normal Kaggriculture observations while satisfying NFR-2 for the one malformed-input case that blocked packaging preflight.

## Qualification plan

Workflow: `.github/workflows/v151-safety-equivalence-preflight-selfhosted.yml`.

It must:

1. reconstruct exact v115/v147/v150 and build v151;
2. `py_compile` all four;
3. run full Kaggle-compatible preflight including all five malformed observations and 720-turn runtime;
4. build `submission.tar.gz` without submitting it;
5. compare complete v150/v151 action traces and rewards on burned seeds `681..692` and sealed seeds `1701..1712`, both seats (48 games);
6. verify archive contains exactly root `main.py` and packed bytes match candidate source;
7. record v151 main SHA256 and archive SHA256.

If all pass, v151 can inherit v150's normal-game strategic evidence by exact action equivalence on the key burned/sealed panels, while the known-opponent/public-diversity gates are either rerun directly or inherited only with an explicitly documented non-None delegation argument.

## Runs

- v150 promotion packaging preflight: `36258187466` — FAIL only on `observation=None` fallback
- v151 safety equivalence/preflight: queued after workflow creation

## Decision

KEEP TESTING. Formal champion remains v115.
