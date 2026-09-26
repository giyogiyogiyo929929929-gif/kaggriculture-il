# EXP-20260927-v118-premium-scarce-sell-front

## Status

KEEP TESTING — DO NOT PROMOTE

Formal champion remains `v112_wheat_lead3_lowdemand`.

`v118_premium_scarce_sell_front` is a sibling of v116/v117 and is built directly on v112. It must not be stacked with unpromoted v116/v117 evidence.

## Hypothesis

Kaggriculture market orders are processed one order at a time with alternating players. Earlier SELL orders can therefore obtain the pre-race price before an opponent's same-item sell increases market inventory.

Premium items (`STRAWBERRY`, `MELON`, `MILK`, `WOOL`) have much steeper oversupply-side price collapse than WHEAT/EGG/FERTILIZER. When exactly one premium item is currently scarce and it appears behind only low-risk, non-scarce SELLs in the same action, moving that premium SELL to the front may improve race robustness without changing quantity, turn, slots, or cash dependencies.

## Changes

One major change only:

- Reorder exactly one premium SELL to market position 0 when all gates pass.

Safety gates:

1. step >= 239;
2. at least two market orders;
3. every market order is `SELL`;
4. exactly one positive-quantity premium SELL among `STRAWBERRY`, `MELON`, `MILK`, `WOOL`;
5. premium item is publicly scarce: market inventory < 10000 and current price >= 110% of base;
6. the premium SELL is not already first;
7. every preceding SELL is one of `WHEAT`, `EGG`, `FERTILIZER`;
8. no preceding low-risk item is itself scarce/racing: inventory < 10000 and price >= 105% of base blocks the reorder.

The candidate preserves:

- market order count;
- every item quantity;
- action turn;
- relative order of every non-moved order;
- no BUY/SELL cash-order interaction because mixed actions are blocked.

## Telemetry

`agent.telemetry["premium_scarce_sell_front"]` records:

- `reorders`
- `units`
- `moved_positions`
- per-item counts: `strawberry`, `melon`, `milk`, `wool`
- `non_sell_blocks`
- `multi_premium_blocks`
- `already_front_blocks`
- `scarcity_blocks`
- `unsafe_prefix_blocks`
- `front_race_blocks`
- `errors`
- activation `steps`

## Static / synthetic

Local dependency-free synthetic suite:

- scarce MILK behind WHEAT -> reorder;
- premium already first -> no reorder;
- premium not scarce -> block;
- multiple premium SELLs -> block;
- unsafe TOMATO prefix -> block;
- scarce/racing WHEAT prefix -> block;
- mixed BUY/SELL action -> block;
- scarce STRAWBERRY behind EGG + FERTILIZER -> reorder while preserving quantities/order.

Result:

`v118 synthetic checks: PASS`

Syntax compilation of suffix, synthetic test, exact eval runner, and external eval runner: PASS.

## Planned canonical evaluation

Engine: `kaggle_environments==1.32.7`.

Sign:

`candidate_minus_champion = candidate - champion`

Same-seed seat-swap throughout.

### Champion H2H

- validation: seeds 300001–300012
- sealed: seeds 301001–301004
- stress: seeds 302001–302008
- starter regression: seeds 1–5 for v118 and v112
- runtime: seed 800502

### Bronze external panel

Seeds 303001–303004, seat swap, against:

- v49
- v50
- metav4_v13
- k256_h2_q_v1
- market_rhythm
- story_of_seasons
- thomas_router_93
- tetsutani_dpts_b
- jaxa_2802
- ready_stock

Primary bronze-policy signal is outcome regression/improvement, not only mean money delta.

## Decision gates

Immediate REJECT if:

- telemetry `errors > 0`;
- canonical run has exception/timeout;
- `reorders == 0` across validation -> no activation;
- reproducible external outcome regression appears without a stronger robust outcome improvement.

Promotion requires all normal current-lineage gates: matched improvement, seat robustness, acceptable worst regression, sealed reproduction, external regression safety, runtime, and a telemetry-backed causal explanation.

## Current decision

KEEP TESTING.

v117 remains the currently queued self-hosted candidate. v118 is prepared in parallel so runner time can be used immediately after v117 resolves. Formal champion remains v112.
