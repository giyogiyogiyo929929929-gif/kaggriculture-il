# EXP-20260926 v147 resumed evaluation

## Status

**Decision: KEEP TESTING. Do not promote.**

This record closes the previously incomplete v147 burned/public evaluation and documents the follow-up telemetry. The formal champion remains the exact v115 `v115_champion_same_turn_open_squeeze` reconstruction.

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
- metric: `candidate_minus_champion = candidate - champion`

## Static / syntax / runtime

- exact champion SHA asserted: pass
- exact candidate SHA asserted: pass
- `py_compile`: pass
- runtime preflight seed 681: pass
- candidate exceptions: 0 in burned/public screen
- workflow result: success

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

The aggregate gain is not a single-seed effect: nine of twelve matched pairs improved. However, seed 691 exposes a material seat-dependent leg regression despite a positive pair average.

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

For the positive representative seeds, the first divergence preserved the same SELL multiset and changed only order sequence:

- seed 681, step 552: `FERTILIZER 15, STRAWBERRY 11, EGG 10` -> `STRAWBERRY 11, EGG 10, FERTILIZER 15`; final +4 / +4.
- seed 682, step 481: `FERTILIZER 14, MILK 9, STRAWBERRY 6, WHEAT 5` -> `FERTILIZER 14, STRAWBERRY 6, MILK 9, WHEAT 5`; final +170 / +170.
- seed 689, step 409: `FERTILIZER 13, WOOL 4, MILK 4, WHEAT 3` -> `WOOL 4, MILK 4, FERTILIZER 13, WHEAT 3`; final +230 / +230.
- seed 683: no action divergence; final 0 / 0.

Health telemetry provides useful contrast:

- seed 682: v147 harvested one additional crop and had one fewer wither/crop loss than v115, indicating that market-order timing can cascade into later farm state.
- seed 689: farm health was identical while final cash improved +230 in both seats, supporting a direct market ordering/timing explanation.

### Seat-risk seed 691

First same-state divergence at step 673:

- champion: `MILK 11, FERTILIZER 11, CARROT 4, CARROT 2, WHEAT 2`
- v147: `MILK 11, FERTILIZER 11, CARROT 4, WHEAT 2, CARROT 2`

This is the representative divergence with **multiple SELL orders for the same item (`CARROT`)**. Its two seat legs are -52 and +56. The matched average (+2) therefore conceals a meaningful seat-dependent downside.

The compact focused telemetry accidentally read money from `private.money`; actual farm money lives under `observation['farms'][player]['money']`. The cash-window field from that diagnostic must not be used. The recorded observations/actions, first-divergence steps, action equality/differences, and final rewards are unaffected.

## Interpretation

v147 establishes that a confirmed second-pass order reorder can materially improve final cash on direct v115 matchups without changing sale quantities. The strongest clean evidence is seed 689: identical farm health and +230 in both seats.

The remaining weakness is not the general reorder idea but the duplicate-same-item SELL case, where moving one fragment relative to another can interact with market processing order and produce seat-sensitive outcomes.

## Decision

**KEEP TESTING; do not promote v147.**

Reasons:

- strong burned matched improvement and no pair-level losses;
- public known-opponent panel has no regression;
- runtime / exceptions are clean;
- causal mechanism is explainable;
- but seed 691 contains a -52 single-seat regression and seat dependence;
- no sealed unused-seed reproduction has yet been completed;
- no final stress screen has yet been completed.

## Next hypothesis

Create v148 with one safety change only: preserve v147's confirmed second-pass reorder when SELL item kinds are unique, but skip that second-pass when an action contains multiple SELL orders for the same item. Evaluate against exact v115 on burned matched seeds with seat swap, then known-opponent regression, and only if the guard preserves the gains proceed to unused sealed seeds.
