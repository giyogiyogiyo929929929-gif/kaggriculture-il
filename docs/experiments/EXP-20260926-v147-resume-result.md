# EXP-20260926 v147 resumed evaluation

## Status

**Decision: KEEP TESTING. Do not promote.**

The formal champion remains the exact v115 `v115_champion_same_turn_open_squeeze` reconstruction. v147 remains the leading candidate. v148 and v149 are rejected follow-up guards; neither replaces v147.

## Version / parent / champion

- candidate: `v147_confirmed_v111_clone`
- builder: `ci/build_v147_confirmed_v111_clone.py`
- candidate SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- parent/reference implementation: exact formal v115 plus one guarded second-pass v111 reorder layer
- formal champion: `v115_champion_same_turn_open_squeeze`
- champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`

The workflow label/history contained older v115/v121 naming ambiguity. SHA verification resolves it: the resumed formal comparison used the exact canonical v115 SHA above.

## Hypothesis

A strategic clone may match v115 farm/sale quantities without sharing the final v111 order layer. Use a first-pass v111 change as a no-intervention probe. On the following observation, only confirm clone-like behavior when own and rival realized farm-money deltas are identical; after confirmation, permit a second `_v111_reorder` pass.

## Changes

1. Track a pending probe after the parent v111 layer changes an action.
2. On the next observation, confirm only when realized own/rival money deltas match; permanently reject after a mismatch.
3. When confirmed and existing standard/clone gates pass, apply one additional `_v111_reorder` pass.

No farm-strategy or sale-quantity policy was intentionally changed.

## Environment

- repository: `giyogiyogiyo929929929-gif/kaggriculture-il`
- evaluation branch: `eval-v147-resume-selfhosted-20260926`
- engine: `kaggle_environments==1.32.7`
- runner: self-hosted Windows X64 (`CIYOI`)
- resumed evaluation workflow run: `36222557449`
- focused telemetry workflow run: `36225937947`
- focused telemetry artifact id: `10900648604`
- sealed workflow run: `36237858136` (`1701..1712`, queued at last check)
- final runtime qualification run: `36238602914` (queued at last check)
- hard-opponent stress run: `36238658392` (queued at last check)
- metric: `candidate_minus_champion = candidate - champion`

## Static / syntax / preflight

- exact champion SHA asserted: pass
- exact candidate SHA asserted: pass
- `py_compile`: pass
- runtime preflight seed 681: pass
- candidate exceptions: 0 in burned/public screen
- resumed workflow result: success

Final sequential runtime qualification is tracked separately and is not yet complete in this record.

## Burned matched direct evaluation

Seeds `681..692`, same seeds with seat swap, 12 matched pairs.

- wins: 9
- losses: 0
- ties: 3
- mean candidate-minus-champion: **+47.5**
- worst matched-pair regression: **0**
- best matched-pair gain: **+230**

Pair-normalized deltas:

| seed | candidate - champion | seat legs |
|---:|---:|---|
| 681 | +4 | +4 / +4 |
| 682 | +170 | +170 / +170 |
| 683 | 0 | 0 / 0 |
| 684 | +2 | +2 / +2 |
| 685 | +38 | +38 / +38 |
| 686 | +23 | +23 / +23 |
| 687 | 0 | 0 / 0 |
| 688 | +58 | +58 / +58 |
| 689 | +230 | +230 / +230 |
| 690 | 0 | 0 / 0 |
| 691 | +2 | **-52 / +56** |
| 692 | +43 | +43 / +43 |

The aggregate gain is not a single-seed effect: nine of twelve matched pairs improved.

### Seed 691 seat-bias correction

The raw v147-v115 legs at seed 691 are -52 / +56. A direct v115-v115 baseline on the same seed is approximately -54 / +54. Relative to the same-seat baseline, v147 therefore improves both legs by approximately +2. The raw -52 leg is evidence of strong environment/seat asymmetry, but it is **not** evidence of a v147-specific -52 regression.

This correction invalidates the earlier interpretation that seed 691 itself required a duplicate-SELL or late-game safety guard.

## Public known-opponent regression panel

Opponents:

- starter
- beat_v48
- bl_v20
- bl_v21
- farming_v2
- frontier_prvsiyan

Seeds `661..664` for each opponent, 24 candidate-vs-champion rows total.

- wins: 0
- losses: 0
- ties: 24
- mean: 0
- worst: 0
- exceptions: 0

No known-public-opponent regression was observed, but this panel is behaviorally inactive for v147 and is not evidence of generalization by itself.

## Focused telemetry / replay findings

Focused same-state first-divergence analysis used seeds 681, 682, 683, 689, and 691 with both seats.

### Mechanism

At first divergence the observation is identical, the SELL multiset is preserved, and only market-order sequence changes. This matches the intended second-pass `_v111_reorder` intervention rather than a farm-policy or sale-quantity change.

Representative cases:

- seed 681, step 552: `FERTILIZER 15, STRAWBERRY 11, EGG 10` -> `STRAWBERRY 11, EGG 10, FERTILIZER 15`; final +4 / +4.
- seed 682, step 481: `FERTILIZER 14, MILK 9, STRAWBERRY 6, WHEAT 5` -> `FERTILIZER 14, STRAWBERRY 6, MILK 9, WHEAT 5`; final +170 / +170.
- seed 689, step 409: `FERTILIZER 13, WOOL 4, MILK 4, WHEAT 3` -> `WOOL 4, MILK 4, FERTILIZER 13, WHEAT 3`; final +230 / +230.
- seed 683: no action divergence; final 0 / 0.
- seed 691, step 673: `MILK 11, FERTILIZER 11, CARROT 4, CARROT 2, WHEAT 2` -> `MILK 11, FERTILIZER 11, CARROT 4, WHEAT 2, CARROT 2`; pair-normalized +2 after seat swap.

Health telemetry provides useful contrast:

- seed 682: v147 harvested one additional crop and had one fewer wither/crop loss than v115, indicating that market-order timing can cascade into later farm state.
- seed 689: farm health was identical while final cash improved +230 in both seats, supporting a direct market-order processing explanation.

The compact focused telemetry accidentally read money from `private.money`; actual farm money lives under `observation['farms'][player]['money']`. The cash-window field from that diagnostic must not be used. Recorded observations/actions, first-divergence steps, action equality/differences, and final rewards are unaffected.

### What is and is not established about `_v111_reorder`

The exact v115 implementation is reconstructed from a compressed patch. The patch is available and SHA-verified, but the GitHub connector truncates the one-line compressed payload before it can be decoded in this evaluation session. Therefore this record does **not** infer the internal priority function of `_v111_reorder` beyond what the replay directly establishes: v147 preserves the SELL multiset and changes order sequence when the confirmed-clone gates allow the second pass.

## Rejected follow-up guards

### v148 `v148_v147_unique_sell_guard` — REJECT

Single change: skip v147's second reorder if multiple SELL fragments target the same item.

Burned `681..692` vs v115:

- 7W / 0L / 5T
- mean +33.5833
- worst 0
- best +204
- exceptions 0

Versus v147, seed 691 loses 2 matched money. The guard removes useful v147 behavior and was based on the now-invalid raw-seat interpretation of seed 691.

### v149 `v149_v147_late_guard` — REJECT

Single change: skip the second reorder from step 648 onward.

Burned `681..692` vs v115:

- 7W / 0L / 5T
- mean +39
- worst 0
- exceptions/timeouts 0

Versus v147, seed 691 again loses 2 matched money. The late-game-risk premise is not supported after baseline seat normalization.

## Sealed holdout

A dedicated v147-v115 sealed screen is queued on self-hosted runner run `36237858136`.

- seeds: `1701..1712`
- seat swap: yes
- candidate/reference SHA assertions: required
- this range was not observed in the repository/workflow checks performed before freezing it
- GitHub code search reported `incomplete_results=true`, so this is documented as an **unobserved holdout**, not an absolute proof that the seeds were never used anywhere

Do not tune v147 from these seeds before the sealed result is recorded.

## Hard-opponent stress

Run `36238658392` tests v147 against the full eight-opponent universe used by the historical v115 hard-opponent selector:

- peak_2950
- salem_2900
- score_2820
- jaxa_2802
- thomas_router_95
- tetsutani_ms
- melon_squeeze
- shop_router_v7

Stress seeds are `520101..520104` with seat swap. All eight are retained rather than reconstructing an uncertain historical selected subset. The primary regression metric remains candidate-minus-champion against the same opponent and seed.

## Final runtime qualification

Run `36238602914` is queued for the final runtime gate.

Qualification method:

- exact v147 SHA asserted
- exact v115 SHA asserted
- engine `kaggle_environments==1.32.7`
- sequential, single-process execution
- GC remains enabled
- seeds 681, 682, 689, 691, 692 with both candidate seats
- candidate invocation wall-time measured by `perf_counter_ns`
- pass thresholds: p99 < 50 ms, max < 200 ms, zero execution errors

## Interpretation

v147 currently establishes a repeatable mechanism: after clone confirmation, a second application of the existing v111 order layer changes SELL processing order without changing the SELL multiset. On burned direct seeds this converts multiple ties/low-margin cases into stable matched improvements, including +230 on seed 689 with identical farm health.

The earlier apparent seed-691 single-seat regression was a baseline seat-asymmetry artifact. Consequently v148 and v149 are rejected as over-guards that remove positive v147 behavior rather than repairing a demonstrated candidate-specific defect.

The remaining evidence gap is generalization, not a known burned regression: sealed holdout, hard-opponent stress, and final sequential runtime qualification are still required.

## Decision

**KEEP TESTING; do not promote v147 yet. Formal champion remains v115.**

Evidence already satisfied:

- exact static/SHA reconstruction;
- burned matched improvement: 9W / 0L / 3T, mean +47.5, worst 0;
- gains survive seat swap at pair level;
- nine of twelve burned seeds improve;
- no exceptions in burned/public screen;
- first-divergence telemetry supports an order-only mechanism;
- older public-opponent panel has no regression.

Open promotion gates:

1. sealed `1701..1712` must reproduce non-regressing matched behavior without seed/seat concentration;
2. hard-opponent stress must show no material known-opponent regression;
3. final sequential runtime must satisfy p99 < 50 ms and max < 200 ms with GC enabled and zero errors;
4. any new negative seed must be replayed/telemetrized before promotion.

## Next hypothesis

Do not create another tactical guard until the three pending gates complete. If v147 fails on a new seed/opponent, derive the next candidate from that new counterexample rather than reusing the disproven duplicate-SELL or late-step hypotheses.
