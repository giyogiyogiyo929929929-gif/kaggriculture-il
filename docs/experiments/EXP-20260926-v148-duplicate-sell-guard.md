# EXP-20260926 — v148 duplicate-SELL guard

## Version / parent / champion

- Candidate: `v148_v147_unique_sell_guard`
- Parent behavior: `v147_confirmed_v111_clone`
- Formal champion/reference: `v115_champion_same_turn_open_squeeze`
- Engine: `kaggle_environments==1.32.7`
- Evaluation run: GitHub Actions `36226283572` (`v148 vs v115 duplicate-sell guard screen`)
- Run head: `c661146e941b690ae624bc4adf0141d3b09c82f0`
- Artifact: `v148-v115-guard-screen`, artifact id `10901242631`
- Metric sign: `candidate_minus_champion = candidate - champion`

## Hypothesis

Burned seed 691 showed a seat-reversing first divergence when the same item appeared in multiple `SELL` orders (`CARROT` split across two orders). Suppress v147's confirmed second-pass reorder only when duplicate SELL item kinds are present, while preserving v147 behavior for unique-item SELL sets.

## Change

`ci/build_v148_v147_unique_sell_guard.py` wrapped v147 and added `_v148_duplicate_sell_item(action)`. When duplicate SELL items were detected, the additional v148 second-pass reorder was skipped.

## Static / runtime

- `v115` SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- `v147` SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- `v148` SHA256: `6b8b43a460190ecd96fb33055a58778e7829ee624a58c39cf278560b94b99789`
- py_compile/build checks: PASS
- Runtime seed 681: no exception; median action time about 0.00423 s for v148 vs 0.00414 s for v115; max about 0.163 s vs 0.089 s in this one-pair preflight.

## Results

### Burned contiguous screen (seeds 681–692, seat swap)

- pairs: 12
- wins / losses / ties: `7 / 0 / 5`
- mean pair delta: `+33.5833`
- worst pair delta: `0`
- best pair delta: `+204`
- exceptions: `0 / 0`

Important seat-level result:

- seed 691: pair delta `0`, but raw seat deltas were `-54 / +54`.

Thus the target seat-reversing instability remained.

### Direct seed 691 v148 vs v147

- pair delta: `-2`
- raw seat deltas: `-56 / +52`
- exceptions: `0 / 0`

v148 was therefore slightly worse than its parent on the exact target seed and did not remove the seat dependence.

### Public known-opponent panel

Six opponents × four matched pairs = 24 pairs:

- wins / losses / ties: `0 / 0 / 24`
- mean: `0`
- worst: `0`

No public-panel regression was observed, but the change was behaviorally inactive there.

## Telemetry / implementation finding

The failed hypothesis was caused by guard placement rather than the duplicate-item predicate itself.

`_V148_PARENT = agent` captures v147. Calling `_V148_PARENT(...)` therefore lets v147 execute its confirmed second-pass `_v111_reorder(...)` before v148 inspects the returned action. The duplicate-SELL guard only prevents v148's own later reorder attempt; it cannot undo the reorder already performed by v147.

This explains why seed 691 retained the seat-reversing behavior despite the new guard.

## Decision

**REJECT v148.**

Reasons:

1. The intended failure mode on seed 691 was not fixed (`-54/+54` vs v115).
2. Directly against v147 on seed 691, v148 was `-2` pair-average.
3. The guard is structurally downstream of the action it intends to block.
4. Public neutrality and zero exceptions are insufficient to offset failure of the primary hypothesis.

Formal champion remains **v115**. v147 remains **KEEP TESTING**, not promoted.

## Next hypothesis

Build v149 directly on formal v115 using v147's confirmation logic, but place the duplicate-SELL check immediately before the confirmed second-pass `_v111_reorder(...)`. This should block the dangerous reorder before it occurs while preserving v147 behavior on unique-item SELL sets.
