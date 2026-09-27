# EXP-20260927-v118-premium-scarce-sell-front

## Status

**KEEP TESTING — canonical self-hosted evaluation queued**

Formal champion remains `v112_wheat_lead3_lowdemand`.

`v118_premium_scarce_sell_front` is a sibling of v116/v117 and is built directly on v112. It is not stacked with unpromoted sibling mechanisms. v117 has now been REJECTED for zero canonical activation.

## Hypothesis

Kaggriculture market orders are processed one order at a time with alternating players. Earlier SELL orders can therefore obtain the pre-race price before an opponent's same-item sell increases market inventory.

Premium items (`STRAWBERRY`, `MELON`, `MILK`, `WOOL`) have much steeper oversupply-side price collapse than WHEAT/EGG/FERTILIZER. When exactly one premium item is currently scarce and it appears behind only low-risk, non-scarce SELLs in the same action, moving that premium SELL to the front may improve race robustness without changing quantity, turn, slots, or cash dependencies.

## Change

One major change only: reorder exactly one premium SELL to market position 0 when all gates pass.

Safety gates:

1. step >= 239;
2. at least two market orders;
3. every market order is `SELL`;
4. exactly one positive-quantity premium SELL among `STRAWBERRY`, `MELON`, `MILK`, `WOOL`;
5. premium item is publicly scarce: market inventory < 10000 and current price >= 110% of base;
6. premium SELL is not already first;
7. every preceding SELL is one of `WHEAT`, `EGG`, `FERTILIZER`;
8. no preceding low-risk item is itself scarce/racing: inventory < 10000 and price >= 105% of base blocks the reorder.

The candidate preserves market order count, every item quantity, action turn, and relative order of every non-moved order. Mixed BUY/SELL actions are blocked.

## Telemetry

`agent.telemetry["premium_scarce_sell_front"]` records:

- `reorders`, `units`, `moved_positions`
- per-item counts: `strawberry`, `melon`, `milk`, `wool`
- `non_sell_blocks`, `multi_premium_blocks`, `already_front_blocks`
- `scarcity_blocks`, `unsafe_prefix_blocks`, `front_race_blocks`
- `errors`
- activation `steps`

## Static / synthetic

`test_v118_suffix_synthetic.py` covers scarce MILK and STRAWBERRY reorder cases plus already-front, non-scarce, multiple-premium, unsafe prefix, racing WHEAT prefix, mixed BUY/SELL, and zero-inventory scarcity.

Result: `v118 synthetic checks: PASS`.

The zero-inventory case also caught and fixed a truthiness bug that would otherwise have treated `inventory=0` as missing and suppressed an extreme-scarcity activation.

## Canonical evaluation plan

Engine: `kaggle_environments==1.32.7`.

Sign: `candidate_minus_champion = candidate - champion`.

Same-seed + seat-swap throughout.

### Champion H2H

- validation: seeds 300001–300012
- sealed: 301001–301004
- stress: 302001–302008
- starter regression: seeds 1–5 for v118 and v112
- runtime: seed 800502

Immediate safety gate after exact H2H:

- telemetry errors > 0 → REJECT
- runtime callback errors > 0 → REJECT
- validation `reorders == 0` → REJECT as no activation

### Bronze external panel

If the activation gate passes, seeds 303001–303004 are seat-swapped against:

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

Primary bronze-policy signal is outcome regression/improvement, then candidate-minus-champion money delta and worst regression.

## Execution infrastructure

Dedicated workflow: `.github/workflows/v112-v118-selfhosted.yml`.

It runs on `[self-hosted, Windows, X64]` and is path-filtered to v118/build-source files, so unrelated documentation changes and v117 files do not waste CIYOI time. Sequence:

1. install/verify `kaggle-environments==1.32.7`;
2. v118 synthetic;
3. byte-stable source reconstruction;
4. py_compile;
5. exact v118-v112 matched H2H;
6. activation/safety gate;
7. bronze external panel if the gate survives;
8. always produce summary/artifact.

Workflow creation commit: `1cd12e4ee746ad53444b21680e466edc757527d3`.

Current run: GitHub Actions `36281995854`, run #1, currently queued on the self-hosted runner.

## Decision

**KEEP TESTING — DO NOT PROMOTE.**

No score claim is made until canonical v118 telemetry and matched results exist. Formal champion remains `v112_wheat_lead3_lowdemand`.
