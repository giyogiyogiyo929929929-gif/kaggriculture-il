# KAGGRICULTURE_CHAT_MODE_v115_r9.md

## 1. Canonical state

- Formal Champion: `v115_champion_same_turn_open_squeeze`
- Champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- Formal engine: `kaggle_environments==1.32.7`
- Do not overwrite v115 directly.
- Candidate comparisons use `candidate_minus_champion = candidate - champion`.

## 2. Strategic candidate lineage

### v147

`v147_confirmed_v111_clone`

SHA256:
`8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`

Key evidence vs exact v115:

- burned seeds 681..692, seat swapped: 9W / 0L / 3T, mean +47.5, worst 0
- sealed holdout 1701..1712: 10W / 0L / 2T, mean +36.6667, worst 0
- hard opponents: 32/32 matched ties, regression 0
- public diversity: prior v147 panel 28/28 relative ties

Mechanism from replay: SELL multiset is preserved; only SELL ordering changes when the confirmed-clone second v111 pass fires.

### v150

`v150_skip_noop_second_pass`

SHA256:
`0a5bfa1b9fa91dd7ebdee1f45640719b23a7b895cbd85cc1f4f17bddebb6387d`

Change from v147: skip the second `_v111_reorder` when the parent v111 pass did not change the action.

Evidence:

- focused v147/v150 action equivalence: 20/20 games
- burned equivalence: 24/24 games, v111 evaluations -21.85%
- sealed equivalence: 24/24 games, v111 evaluations -18.47%
- formal runtime run 36252343922: p99 16.889 ms, max 162.617 ms, >200 ms 0, exceptions 0
- hard-opponent run 36256381428: 32/32 ties vs v115, worst 0, exceptions 0

v150's normal-game strategic/runtime evidence is strong.

## 3. v150 packaging blocker

Promotion packaging preflight run `36258187466` failed exactly one repository NFR-2 check:

- `observation=None` -> `AttributeError("'NoneType' object has no attribute 'get'")`

Everything else in that run passed:

- exact reconstruction / SHA
- py_compile
- Kaggle-compatible loader
- stdlib-only import audit
- normal action shape
- other four malformed observations
- 720-turn completion
- runtime median 3.58 ms / p99 16.60 ms / max 158.51 ms

Therefore do **not** promote v150 as final packaged source.

## 4. Current promotion candidate: v151

`v151_none_observation_guard`

Builder:
`ci/build_v151_none_observation_guard.py`

One bugfix only:

```python
_V151_PARENT = agent

def agent(observation, configuration=None):
    if observation is None:
        return {'farmer': ['PASS'], 'hands': [], 'market': []}
    return _V151_PARENT(observation, configuration)
```

For every non-None observation, v151 delegates directly to v150 with identical arguments and returns the result unchanged.

No strategic logic changes.

Qualification workflow:
`.github/workflows/v151-safety-equivalence-preflight-selfhosted.yml`

Run:
`36259834091`

Required:

- all preflight checks PASS including `None`
- burned 681..692 and sealed 1701..1712, both seats: complete v150/v151 action + reward equivalence
- 720-turn runtime PASS
- archive root exactly `main.py`
- packaged main bytes equal source bytes
- record v151 main/archive SHA256

## 5. Public diversity gate

v150 direct public-diversity run:
`36257645079`

Panel:

- starter
- beat_v48
- bl_v20
- bl_v21
- farming_v2
- frontier_prvsiyan
- pinned/audited Seyamalam v21
- seeds 621..624

Status at this snapshot: in progress.

Because v151 delegates exactly to v150 on every normal non-None observation, a clean v150 public panel may be inherited only after the v151 equivalence/preflight workflow proves the safety wrapper does not alter valid-game behavior.

## 6. Decision rule

PROMOTE target is now **v151**, not v150, only if all of the following hold:

1. v150 public diversity is regression-free;
2. v151 full preflight passes;
3. v151 action/reward equivalence to v150 is exact on burned + sealed panels;
4. v151 runtime satisfies p99 < 50 ms and max < 200 ms;
5. package source/hash checks pass;
6. no exceptions/timeouts are observed.

Then create a formal PROMOTE record and change the canonical champion reference to v151. Do not mutate the historical v115 or v150 sources.

Kaggle submission is a separate operation and must not be performed automatically.

## 7. Current decision

```text
FORMAL CHAMPION:
v115_champion_same_turn_open_squeeze

PROMOTION CANDIDATE:
v151_none_observation_guard

STATUS:
KEEP TESTING
NO PROMOTE YET

PENDING:
v150 public diversity + v151 safety/equivalence/preflight
```
