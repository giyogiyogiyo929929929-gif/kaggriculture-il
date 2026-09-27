# EXP-20260927 — v125_day10_melon_probe

## Status

**PROBE COMPLETE — DAY10 SELL GAP CONFIRMED; INVENTORY ORIGIN NEEDS FOLLOW-UP**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Parent / environment

- source: exact `v112_wheat_lead3_lowdemand`
- engine: `kaggle_environments==1.32.7`
- workflow run: `36311788633`
- job: `108599018185`
- head: `d0b6b94c001fc64d4b1140be467648efafa8302e`
- artifact: `v112-v125-day10-melon-probe`, ID `10928987847`

## Motivation

v124 external economic-gap attribution showed that the first large persistent deficit against the important external panel appears around day 10, with step 250 the strongest common early negative event. External opponents begin a MELON liquidation wave there while v112 cash-in lags.

## Panel

Five important external opponents: `thomas_router_93`, `metav4_v13`, `k256_h2_q_v1`, `ready_stock`, `jaxa_2802`; seeds `309001` and `309004`; both seats; 20 games.

Exact runtime observations/actions were recorded for steps 240–270 for both v112 and the opponent.

## Findings

At step 250 v112 has `private.shed.MELON=0`, public MELON price `266`, and no MELON sell. The external opponents already request `SELL MELON 24` and continue a MELON liquidation wave around steps 251–255.

v112 begins its corresponding runtime sell wave later:

- step 256: `SELL MELON 12`, price ~226;
- step 258: `SELL MELON 24`, price ~213;
- step 259: `SELL MELON 12`, price ~178;
- step 261: `SELL MELON 12`, price ~156;
- step 264: `SELL MELON 12`, price ~131.

Money trajectories confirm economically material cash-in rather than inert requests. The simple hypothesis that v112 already has MELON in shed at step 250 and merely waits to sell is not supported.

However, the observation also contains `private.inventories`; v125 did not record them. Opponents can request MELON sales while their shed snapshot is also zero, so shed alone cannot determine whether an early sale is executable.

## Decision

- telemetry only; no promotion decision;
- do not create a blind step-250 MELON SELL candidate;
- follow with v126 exact carry/inventory tracing.
