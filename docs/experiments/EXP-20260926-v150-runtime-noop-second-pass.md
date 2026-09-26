# EXP-20260926-v150-runtime-noop-second-pass

## Status
KEEP TESTING — focused equivalence/runtime run queued.

## Parent / champion
- parent candidate: `v147_confirmed_v111_clone`
- formal champion: `v115_champion_same_turn_open_squeeze`
- v147 SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`

## Motivation
v147 has strong strategic evidence (burned matched seeds, sealed holdout, hard-opponent stress, public diversity) but its final runtime qualification exceeded the absolute `<200 ms` max threshold. Follow-up paired runtime diagnostics showed that extreme tails are strongly GC-dependent, while targeted cProfile identified `_v111_reorder` as a real hot path on some late turns.

The v147 wrapper calls the parent v115 agent, detects whether the parent's v111 pass changed the action via `_V111_REPORT['changed_turns']`, and then may call `_v111_reorder` again after clone confirmation. When the parent v111 pass made no change, repeating the same final reorder is expected to be a redundant no-op. Avoiding that call should reduce candidate enumeration, margin evaluation, temporary allocations, and GC pressure without changing strategic actions.

## Candidate
`v150_skip_noop_second_pass`

Builder: `ci/build_v150_skip_noop_second_pass.py`

### Change
One guard only:

- v147: run confirmed second `_v111_reorder` whenever clone/standard gates pass.
- v150: run that second pass only when `parent_changed` is also true.

No farm policy, market scoring, SELL quantity, order priority, prediction, race detection, or endgame parameter is changed.

## Hypothesis
If the parent v111 pass did not change the final market action, a second deterministic v111 pass on the same final action cannot change the returned action. Skipping such calls should therefore preserve v147 action traces while lowering runtime and allocation pressure.

## Validation plan
1. Build exact v115 and v147 and verify their known SHA256 values.
2. Build v150 and `py_compile` all three agents.
3. Focused action-equivalence test on seeds `681,682,689,691,692`, both seats, two repetitions:
   - compare every candidate action returned by v147 and v150 against the same v115 opponent,
   - require identical complete action traces and identical final rewards,
   - require no exceptions.
4. Compare per-call runtime distribution for v147 and v150 with GC enabled.
5. If action-equivalent and materially faster, broaden equivalence to the full burned panel and then rerun formal runtime qualification.
6. Only after runtime passes, retain v147's strategic evidence for promotion; do not change the formal champion before all gates pass.

## Runs
- duplicate-candidate diagnostic: `36245268147` (queued; supplementary, not required for v150 correctness)
- focused v150 equivalence/runtime: `36245566714` (queued)

## Decision
PENDING.
