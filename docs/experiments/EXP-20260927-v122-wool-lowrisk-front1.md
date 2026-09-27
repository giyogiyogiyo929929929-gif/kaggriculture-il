# EXP-20260927 — v122_wool_lowrisk_front1

## Status

**KEEP TESTING — DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Parent / lineage

- parent: `v112_wheat_lead3_lowdemand`
- sibling candidate; no stacking with v121
- branch: `eval/v112-v122-wool-lowrisk-front-20260927`
- canonical engine: `kaggle_environments==1.32.7`

## Motivation from v120b / v119 / v121

v120b found 40 executable WOOL clean-signal overlap events across seeds 309001, 309003 and 309004. However most do not justify a quantity/timing change:

- step 432 is the dominant multi-seed WOOL event, but v112 already places `SELL WOOL 24` first and sells the full shed stock, so there is no safe quantity/timing improvement to make;
- step 598–600 would require a quantity lead and is concentrated in fewer opponent/seed states;
- v119 already showed that broad premium front-running is harmful;
- v121 showed that identical public inventory/price state can still have opponent-sensitive economics when quantity is moved across turns.

The remaining narrow, previously untested state is the step-456 pattern. In the v120b 80-game external panel, the gate below selects exactly six games:

- `metav4_v13`, seed 309004, both seats;
- `story_of_seasons`, seed 309004, both seats;
- `tetsutani_dpts_b`, seed 309003, both seats.

Observed state:

- clean WOOL inventory increase: +3 or +4;
- WOOL price after signal: 214 or 225;
- market inventory remains below 10000;
- shed WOOL: 8;
- parent same-turn WOOL SELL: 8;
- parent static order shape at step 456: `STRAWBERRY 14 -> WHEAT 4 -> WOOL 8 -> HIRE...`.

## Hypothesis

When an external clean WOOL sell-pressure signal is already visible and v112 is selling all available WOOL on the same turn, moving WOOL forward across exactly one low-risk WHEAT SELL may reduce one unit of opponent interleaving before the WOOL sale without disturbing premium-to-premium order or changing quantity/timing.

This tests order timing only.

## Change

Single major change:

- if the narrow public-state WOOL gate fires, transform only
  `... SELL WHEAT q, SELL WOOL q2 ...`
  into
  `... SELL WOOL q2, SELL WHEAT q ...`.

Safety gates:

- step 400–520;
- previous WOOL market inventory available;
- our previous-turn WOOL SELL quantity is zero;
- current WOOL market inventory increase >=3;
- current WOOL price >=210;
- current WOOL market inventory <10000;
- no BUY / BUY_PRODUCT / BUY_SEED style order in the parent market action;
- exactly one positive WOOL SELL;
- current shed WOOL equals current parent WOOL SELL quantity, so no quantity decision is introduced;
- WOOL is immediately preceded by exactly one `SELL WHEAT`;
- candidate never crosses a premium SELL;
- candidate never crosses two low-risk SELLs.

No quantity, turn, repayment, farm, BUY, or other premium logic changes.

## Telemetry

`agent.telemetry["wool_lowrisk_front1"]` records:

- reorders;
- units;
- moved_slots;
- signal / price / inventory / shed / BUY / current-SELL / shape blocks;
- errors;
- activation step/state details.

## Focused evaluation

### Synthetic/static

Focused synthetic covers:

- canonical one-slot WHEAT/WOOL swap;
- no signal;
- low price;
- market inventory >=10000;
- shed mismatch;
- premium-cross prevention;
- two-low-risk-cross prevention;
- BUY dependency block;
- prior own WOOL SELL block;
- seat-state independence.

### Fresh self-H2H

Seeds 314001–314004, same seed and seat swap, `candidate_minus_champion = v122 - v112`.

Expected result is no regression; activation may be zero if the external-only signal is absent.

### Targeted external replay

Seeds 309003 and 309004 against all 10 bronze-panel opponents, champion and candidate both seat-swapped.

Prior telemetry predicts activation only in the six games listed above. This broader 20 pair replay checks for accidental extra activations as well as economics.

## Decision rule

Immediate REJECT if:

- errors >0;
- fresh self-H2H introduces a reproducible regression;
- activation appears outside the evidence-backed shape without a clear reason;
- any intended activated opponent shows a reproducible material regression;
- aggregate active-pair economics are negative without an outcome improvement.

Proceed to fresh external seeds only if the targeted active pairs are consistently non-negative or beneficial and no outcome regression appears.

Even a positive focused result cannot promote v122 directly. Fresh external, sealed/stress and runtime gates remain required.
