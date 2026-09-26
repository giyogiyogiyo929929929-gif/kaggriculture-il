# EXP-20260926 v149 late-game second-pass guard

## Status

**Decision: REJECT. Do not promote.**

Formal champion remains exact `v115_champion_same_turn_open_squeeze`.

## Version / parent / champion

- candidate: `v149_v147_late_guard`
- builder: `ci/build_v149_v147_late_guard.py`
- parent behavior: `v147_confirmed_v111_clone`
- formal champion: `v115_champion_same_turn_open_squeeze`
- champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- metric: `candidate_minus_champion = candidate - champion`

## Hypothesis

Disable v147's confirmed second `_v111_reorder` pass during the final 72 turns (`step >= 648`) to reduce the previously suspected late-game seat-sensitive downside while preserving earlier order gains.

## Change

One tactical change only:

- if `step >= 648`, skip the confirmed second `_v111_reorder` pass;
- farm strategy, sale quantities, clone confirmation, and earlier second-pass behavior remain unchanged.

## Focused synthetic test

Deterministic wrapper test: PASS. The second pass remains active before step 648 and is suppressed from step 648 onward; wrapper errors 0.

## Environment

- engine: `kaggle_environments==1.32.7`
- runner: self-hosted Windows X64 (`CIYOI`)
- formal workflow run: `36234914455`
- GitHub-hosted run `36234808209` failed before any job step (`runner_id=0`) and is not model evidence.

## Results

Trusted formal evidence is `v149_screen_summary.json` from the self-hosted artifact. A generic `summary.json` in the same artifact belongs to a different experiment (`v149_room_guard_buy_netting`) and is explicitly excluded.

### Burned matched screen

Seeds `681..692`, seat swap, 12 matched pairs versus exact v115:

- wins: 7
- losses: 0
- ties: 5
- mean candidate-minus-champion: **+39**
- worst matched-pair regression: **0**
- exceptions/timeouts: none in the completed screen

This is weaker than parent v147's 9-0-3 and **+47.5** on the same burned panel.

### Focused seed 691

Against parent v147 on the same focused comparison, v149 is **-2**. Thus the late guard removes the small +2 same-seat improvement retained by v147 rather than improving it.

Follow-up baseline-seat analysis also invalidated the motivating premise: the raw `-52 / +56` v147 legs at seed 691 mainly reflect an intrinsic v115-v115 seat asymmetry (`-54 / +54`). Relative to the same-seat champion baseline, v147 is +2 in both seats. The supposed v147-specific late seat regression therefore was not established.

### Known-opponent regression

Six public opponents x seeds `661..664`: **24/24 ties**, no observed regression, but also no compensating gain.

## Decision

**REJECT v149.**

Reasons:

- motivating seat-risk premise was invalidated by same-seat baseline analysis;
- burned mean drops from v147 +47.5 to v149 +39;
- improved-pair count drops from 9/12 to 7/12;
- focused seed 691 is -2 versus v147;
- public regression is neutral rather than beneficial;
- spending sealed seeds on a dominated guard is not justified.

No sealed seeds were consumed by v149.

## Next hypothesis

Return to v147 as the leading candidate and test its confirmed second-pass reorder on genuinely unused sealed seeds with seat swap. If sealed gains reproduce, complete stress, sequential runtime/p99, and targeted telemetry before any promotion decision. Do not add another safety guard until a reproducible regression mechanism is demonstrated against the same-seat champion baseline.
