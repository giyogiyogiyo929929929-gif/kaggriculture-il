# Exact v115 continuation — execution-layer experiments

Date: 2026-09-25

## Non-negotiable baseline

Formal Champion remains `v115_champion_same_turn_open_squeeze.py`.
Exact source SHA256:
`c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`

Evaluation standard: `kaggle_environments==1.32.7`, matched seed + both seats.
Diff convention: `candidate_minus_champion = candidate - champion`.
Never use v66. Do not substitute old main.py, the mirror-day28 v115, v119, or v121.

## v131 — pure-cash SELL 1-unit preempt

Hypothesis: move exactly 1 unit of a next-turn non-funding-critical pure-cash SELL one turn earlier, preserving total planned SELL quantity through a one-unit debt reduction next turn.

Official development: seeds 410001..410024, 24 matched pairs / 48 games.

- 3W / 3L / 18D
- mean: 0.0
- SE: 0.5742
- mean-2SE: -1.1484
- worst: -6
- best: +8
- exceptions: 0
- fires: 30

Differing seeds: 410004 -6, 410005 +8, 410007 +4, 410008 -5, 410012 -5, 410019 +4.
All differing pair effects were seat-symmetric.

Telemetry showed all differing recorded final fires were WOOL at quoted price 1. The inherited EXP293 sale-advance safety contract refuses sales below price 2, so v131 had weakened an existing safety rule.

Decision: **REJECT**.

## v132 — restore inherited min sale price 2

Single refinement: retain v131 mechanism but require market price >=2, matching inherited EXP293 safety.

Same development panel 410001..410024:

- 0W / 0L / 24D
- mean: 0
- exceptions: 0
- fires: 0

Decision: **REJECT / CLOSE SELL1 FAMILY**. Once the inherited safety contract is restored, the mechanism is dormant.

## v138 — R37 ordering of V92-generated multi-item SELL block

Mechanism really activated (including multi-item order changes), but direct exact-v115 screen seeds 601..612 was 0W / 0L / 12D.

Decision: **REJECT**. Do not tune order ranking further without new execution evidence.

## v139 — global `_V92_P_K: 1 -> 2`

Direct exact-v115 seeds 621..632:

- 3W / 6L / 3D
- mean: -107
- SE: 58.37
- mean-2SE: -223.73
- worst: -662 (seed 628)
- best: +6
- exceptions: 0

Source audit then found a confound: `_V92_P_K` is consumed by both the primary `_v92_predict` wrapper and later KIL-v52 copy-preempt. Thus v139 changed two mechanisms at once. Its result is not valid evidence against primary V92 K2 by itself.

Decision: **REJECT AS CONFOUNDED**.

## v140 — isolated primary V92 K2; KIL remains K1

Clean implementation changes only the primary V92 comparison from `>= _V92_P_K` to `>= 2`; shared `_V92_P_K = 1` stays unchanged, so KIL-v52 remains K1.

Direct exact-v115 development seeds 641..652:

- 5W / 1L / 6D
- mean: -0.5
- median: 0
- SE: 3.6442
- mean-2SE: -7.7884
- worst: -38 (seed 642)
- best: +12
- seat0 mean = seat1 mean = -0.5
- exceptions: 0

Small opponent panels, seeds 641..644:

- starter: 3W / 0L / 1D, mean +55.25, worst 0
- beat_v48: 1W / 2L / 1D, mean -4, worst -16
- farming_v2: same 1W / 2L / 1D, mean -4, worst -16
- bl_v20: 2W / 0L / 2D, mean +7.5, worst 0
- frontier_prvsiyan: 2W / 1L / 1D, mean +23.5, worst -1

State-aligned first primary divergence contrast:

- seed 642, direct -38: suppressing `SELL WOOL 2`, market price 5 was harmful.
- seed 641, direct +4: suppressing `SELL STRAWBERRY 8`, market price 1 was beneficial.
- seed 651, direct +12: suppressing `SELL MILK 1`, market price 38 was beneficial.
- seed 652, direct +12: suppressing `SELL STRAWBERRY 6`, market price 1 was beneficial.

Decision: **REJECT**. Global primary K2 is too broad; no sealed evaluation.

## v141 — item-isolated primary threshold

Current candidate.

Single primary V92 rule:

- WOOL remains K1.
- MILK and STRAWBERRY require K2.
- KIL-v52 remains exactly K1.
- No route, quantities, horizon, opening, herd, farm, or downstream wrapper changes.

Rationale: the only large v140 direct regression was caused by suppressing a K1 WOOL preempt, whereas three positive contrast worlds were MILK/STRAWBERRY suppressions. This is an item-level mechanism split, not another global threshold sweep.

Burned seeds 641/642/651/652 are diagnostic only and excluded from promotion evidence.
Fresh development reserved: 440001..440024, official 1.32.7, both seats.

Status: **RUNNING / DO NOT PROMOTE YET**.
