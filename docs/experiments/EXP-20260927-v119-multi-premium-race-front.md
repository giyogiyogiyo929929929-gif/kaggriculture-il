# EXP-20260927 — v119_multi_premium_race_front

## Status

**REJECT — canonical activation is real, but the reorder is consistently harmful.**

Formal champion remains `v112_wheat_lead3_lowdemand`.

v119 is a sibling candidate built directly on v112. It does not stack rejected v117/v118 tactical logic.

## Hypothesis

v118 showed that single-premium scarce-front ordering did not activate because multi-premium actions were common. v119 therefore tested whether, inside an all-SELL multi-premium action, moving the premium item with the strongest public scarcity signal to slot 0 could exploit alternating market-order execution without changing turn, quantity, order count, or the order multiset.

Premium items: `STRAWBERRY`, `MELON`, `MILK`, `WOOL`.

## Change

For step >=239 and an all-SELL action with at least two positive premium SELLs:

1. find premium items with market inventory <10000 and price/base >=1.10;
2. rank by price/base, then lower inventory;
3. require the selected item not already be first;
4. allow preceding non-premium orders only from WHEAT/EGG/FERTILIZER and only when they are not themselves scarce/racing;
5. when another premium precedes the selected item, require >=0.03 price/base dominance;
6. move only the selected premium SELL to market position 0.

The market-order multiset, quantities, action turn, and order count remain unchanged.

## Canonical environment

- engine: `kaggle_environments==1.32.7`
- run: `36283893966`
- job: `108520855126`
- candidate SHA-256: `2c7f5a6c40d540fd0cd5335938483f6b50eb159a565b9573bfdf1f4f98ef2468`
- champion SHA-256: `1c6e00ff0bd46b16189b1f6a93ce5e498ff8ffb5b0acb33591cdd247cd8b4771`
- sign: `candidate_minus_champion = candidate - champion`
- same-seed + seat-swap throughout

Synthetic, source reconstruction, py_compile, exact evaluation, activation gate, external panel, and artifact upload all completed successfully.

## Exact matched results

### Validation — 304001–304012

Pair diffs:

`[0, -44, -846, -77, -149, -35, -619, 0, -17, 0, -89, 0]`

- 0W / 8L / 4D
- mean: -156.33
- median: -39.5
- worst: -846
- best: 0

### Sealed — 305001–305004

Pair diffs:

`[-17, -15, -15, -1308]`

- 0W / 4L / 0D
- mean: -338.75
- median: -16
- worst: -1308

### Stress — 306001–306008

Pair diffs:

`[-18, -18, -1, -1233, -17, -6, -879, -17]`

- 0W / 8L / 0D
- mean: -273.625
- median: -17.5
- worst: -1233

Starter seeds 1–5 were unchanged from v112 and remained 5/5 wins.

## Runtime / safety

1438 timed callbacks:

- median: 0.558 ms
- p99: 1.159 ms
- max: 2.114 ms
- callback errors: 0
- telemetry errors: 0

Runtime and safety are not the rejection reason.

## Activation telemetry

Activation was substantial, unlike v117/v118:

- validation: 60 reorders / 232 units
- sealed: 18 reorders / 74 units
- stress: 44 reorders / 170 units
- total canonical H2H reorders: 122

Validation item counts: STRAWBERRY 8, MILK 24, WOOL 28, MELON 0.

Common activation steps were 502, 525, 569, 615, 646, 662, 715, and 716.

## Seed-level replay/telemetry finding

Artifact `10920457516` was inspected at per-seed and per-seat granularity. Both seats showed the same activation family and the same pair regression for each seed, so the loss is not a seat artifact.

Key contrasts:

- no activation: seeds 304001/304008/304010/304012 -> exactly 0 regression;
- STRAWBERRY-only at step 525: 304009 -17; sealed 305001 -17, 305002 -15, 305003 -15; stress 306001 -18, 306002 -18, 306005 -17, 306006 -6, 306008 -17;
- MILK-heavy: 304003 eight MILK reorders -> -846; 305004 six MILK reorders -> -1308; 306004 five MILK plus one STRAWBERRY reorder -> -1233; 304007 one MILK plus one STRAWBERRY -> -619;
- WOOL-heavy: validation 304004/304005/304006 were -77/-149/-35; stress 306003 four WOOL reorders was only -1, but 306007 six WOOL plus one STRAWBERRY reorder was -879.

This establishes that premium-front reordering is not a free race advantage. STRAWBERRY@525 is reproducibly mildly harmful rather than beneficial, while disturbing the existing MILK order is especially dangerous and WOOL can also create large downstream regressions depending on the world state. The candidate improves the chosen item's execution slot at the cost of the other premium order sequence and subsequent market-price path.

## Bronze external panel

Seeds 307001–307004 against 10 heterogeneous opponents, seat-swapped:

- 40 seed-opponent pairs
- outcome regressions: 0
- outcome improvements: 0
- mean candidate-minus-champion: -0.05
- median: 0
- worst: -2
- best: 0

Only `tetsutani_dpts_b`, seed 307001, changed money by -2. No external outcome sign changed. This does not rescue v119 because canonical champion H2H is uniformly harmful across validation, sealed, and stress.

## Decision

**REJECT. Formal champion remains `v112_wheat_lead3_lowdemand`.**

Do not repeat broad same-turn premium-front reordering. In particular, do not reorder MILK/WOOL merely from current price/base scarcity rank. Future work should preserve the learned parent premium order and instead react to opponent-specific public-state changes with a separately gated mechanism.
