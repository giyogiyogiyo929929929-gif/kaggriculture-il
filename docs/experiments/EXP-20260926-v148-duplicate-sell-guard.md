# EXP-20260926 v148 duplicate-SELL guard

## Status

**Decision: REJECT. Do not promote.**

Formal champion remains exact `v115_champion_same_turn_open_squeeze`.

## Version / parent / champion

- candidate: `v148_v147_unique_sell_guard`
- builder: `ci/build_v148_v147_unique_sell_guard.py`
- candidate SHA256: `6b8b43a460190ecd96fb33055a58778e7829ee624a58c39cf278560b94b99789`
- parent behavior: `v147_confirmed_v111_clone`
- formal champion: `v115_champion_same_turn_open_squeeze`
- champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- metric: `candidate_minus_champion = candidate - champion`

## Hypothesis

v147's representative seat-risk seed 691 first diverged on an action containing two CARROT SELL fragments. Preserve v147's confirmed second-pass reorder when SELL item kinds are unique, but skip the second-pass when an action contains multiple SELL orders for the same item.

## Change

One tactical safety change only: duplicate-same-item SELL guard around the confirmed second `_v111_reorder` pass.

## Environment

- branch: `eval-v147-resume-selfhosted-20260926`
- engine: `kaggle_environments==1.32.7`
- self-hosted Windows X64 runner
- workflow run: `36226283572` (`success`)
- artifact: `v148-v115-guard-screen`, id `10901242631`

## Static / syntax / runtime

- exact champion SHA assertion: pass
- exact v147 SHA assertion: pass
- `py_compile`: pass
- runtime preflight: completed, exceptions 0
- runtime seed 681: candidate median about 4.23 ms, max about 163.42 ms
- the screen JSON does not expose p99, so this is not used as a final promotion runtime qualification

## Burned matched direct evaluation

Seeds `681..692`, same seeds with seat swap, 12 matched pairs.

- wins: 7
- losses: 0
- ties: 5
- mean candidate-minus-champion: **+33.5833**
- worst matched-pair regression: **0**
- best matched-pair gain: **+204**
- exceptions: 0

Pair-normalized deltas:

| seed | candidate - champion | seat legs |
|---:|---:|---|
| 681 | +4 | +4 / +4 |
| 682 | +57 | +57 / +57 |
| 683 | 0 | 0 / 0 |
| 684 | 0 | 0 / 0 |
| 685 | +36 | +36 / +36 |
| 686 | +23 | +23 / +23 |
| 687 | 0 | 0 / 0 |
| 688 | +58 | +58 / +58 |
| 689 | +204 | +204 / +204 |
| 690 | 0 | 0 / 0 |
| 691 | 0 | **-54 / +54** |
| 692 | +21 | +21 / +21 |

Compared with v147's +47.5 burned mean and 9-0-3 pair signs, the guard removes useful gains on several seeds while failing to remove the single-seat risk it was designed to address.

## Focus seed 691

Direct v148-vs-v147 matched pair:

- pair mean: **-2**
- seat legs: **-56 / +52**

Direct v148-vs-v115 on the same seed remains **-54 / +54**. Therefore the duplicate-SELL guard does not eliminate the seat-sensitive mechanism; it only changes the pair average from v147's +2 to 0 against the champion.

## Public known-opponent regression panel

Six known opponents × seeds 661..664 = 24 rows.

- wins: 0
- losses: 0
- ties: 24
- mean: 0
- worst: 0

This panel is behaviorally inactive and does not rescue the failed target hypothesis.

## Decision

**REJECT.**

Reasons:

- target failure: seed 691 still contains a material negative single-seat leg (`-54`);
- burned mean falls from v147 `+47.5` to v148 `+33.58`;
- positive-pair count falls from 9 to 7;
- no public regression, exceptions, or matched-pair negative mean occurred, but the safety change does not solve the reason v147 was held back;
- sealed seeds are intentionally not consumed for a candidate that already fails its focused safety objective.

## Next hypothesis

The problem is more consistent with *late-game* order perturbation than duplicate-same-item SELL alone. v147's known seat-risk first divergence is at step 673, while representative clean positive first divergences occur earlier (681: 552, 682: 481, 689: 409). Test one change: preserve v147 before step 648, but disable the confirmed second-pass reorder during the final 72 turns. This is v149.
