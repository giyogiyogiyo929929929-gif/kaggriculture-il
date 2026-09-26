# EXP-20260927 — runtime-v150 skip no-op second pass

## Status

ORTHOGONAL RUNTIME OPTIMIZATION. Do not confuse this with the tactical singleton-v150 lineage. Formal tactical champion remains v147 unless separately promoted. This experiment does not change policy intentionally; it only skips a redundant v147 second-pass reorder call when the parent v111 layer did not change the action.

## Parent / candidate

- parent: exact v147 (`8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`)
- candidate: runtime-v150 (`0a5bfa1b9fa91dd7ebdee1f45640719b23a7b895cbd85cc1f4f17bddebb6387d`)
- builder: `ci/build_v150_skip_noop_second_pass.py`

## Change

The v147 second-pass guard changes from:

`if st['confirmed'] and not st['rejected'] and _v105_standard(configuration) and _v44y_clone_gate(observation):`

to:

`if parent_changed and st['confirmed'] and not st['rejected'] and _v105_standard(configuration) and _v44y_clone_gate(observation):`

Rationale: when the current parent v111 pass made no change, the second `_v111_reorder` call is expected to be a no-op and can be skipped.

## Action-equivalence test

Self-hosted run `36252365551`, already-consumed sealed panel seeds 1701..1712, both seats:

- 24 games
- action-equivalent: true
- reward-equivalent: true for every row
- mismatches: 0
- errors: 0
- v147 reorder evaluations: 32148
- runtime-v150 reorder evaluations: 26210
- evaluation reduction: 18.4708%

These seeds were already consumed by earlier v147 work; this test does not create fresh sealed evidence.

## Hard-opponent regression run

Self-hosted run `36256381428`, opponents `peak_2950`, `salem_2900`, `score_2820`, `jaxa_2802`, `thomas_router_95`, `tetsutani_ms`, `melon_squeeze`, `shop_router_v7`; seeds 520101..520104.

The workflow compared runtime-v150 against v115 rather than v147, so treat this as secondary regression evidence rather than the primary equivalence proof.

Observed aggregate:

- 32 matched seed pairs
- 0 wins / 0 losses / 32 ties in candidate-minus-reference cash
- mean 0
- worst 0
- best 0
- candidate exceptions 0
- reference exceptions 0
- workflow conclusion: success

The stronger policy-preservation evidence remains the direct v150-v147 action/reward equivalence test above.

## Decision

KEEP as an orthogonal runtime optimization candidate. Do not merge it into v153 while v153 tactical evaluation is unresolved. If v153 (or a successor) becomes the tactical winner, rebase this single runtime change onto that winner and repeat action-equivalence plus runtime measurement before promotion/submission.
