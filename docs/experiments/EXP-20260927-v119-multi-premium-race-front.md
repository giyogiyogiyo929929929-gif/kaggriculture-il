# EXP-20260927 — v119_multi_premium_race_front

## Status

**KEEP TESTING — canonical self-hosted exact H2H in progress**

Formal champion remains `v112_wheat_lead3_lowdemand`.

v119 is a sibling candidate built directly on v112. It does not stack rejected v117/v118 tactical logic.

## Motivation

v118 attempted to move exactly one scarce premium SELL to the front of an all-SELL action. Canonical evaluation showed zero activation. The main structural blockers were `multi_premium_blocks` and `already_front_blocks`; validation alone observed 202 multi-premium blocks, so multi-premium SELL actions are common enough to justify a focused sibling experiment.

v119 targets only that previously blocked multi-premium regime. It does not relax v118's mixed BUY/SELL safety rule and does not change action timing, quantity, or slot count.

## Hypothesis

When two or more premium items are sold in the same all-SELL action, the premium item with the strongest public scarcity signal may deserve the first market slot. Because market orders interleave between players, a clearly more race-sensitive premium item can lose price before a later slot executes.

Premium items are `STRAWBERRY`, `MELON`, `MILK`, `WOOL`.

## One major change

Among multi-premium all-SELL actions:

1. require step >= 239;
2. require at least two positive-quantity premium SELLs;
3. require at least one premium item with market inventory < 10000 and price/base >= 1.10;
4. rank eligible premium items by price/base ratio, then lower inventory;
5. candidate must not already be first;
6. every preceding non-premium SELL must be one of WHEAT/EGG/FERTILIZER and must not itself be scarce/racing;
7. if a premium SELL precedes the candidate, candidate price/base must exceed that preceding premium by at least 0.03;
8. move only the selected premium SELL to position 0.

The candidate preserves the full market-order multiset, every quantity, action turn, order count, and relative order of all non-moved orders.

## Telemetry

`agent.telemetry["multi_premium_race_front"]` records:

- `reorders`, `units`, `moved_positions`
- `multi_premium_seen`
- per-item reorder counts
- `non_sell_blocks`, `single_premium_blocks`, `scarcity_blocks`
- `already_front_blocks`, `unsafe_prefix_blocks`, `front_race_blocks`, `dominance_blocks`
- `errors`
- activation steps

## Focused tests

Synthetic coverage includes:

- WOOL clearly more race-sensitive than MILK -> move WOOL to front;
- close MILK/WOOL signal -> dominance block;
- strongest premium already first -> block;
- mixed BUY/SELL -> block;
- racing WHEAT prefix -> block;
- no scarce premium -> block;
- only one premium -> block.

Local dependency-free result: `v119 synthetic checks: PASS`.

Canonical workflow has also passed synthetic, deterministic source reconstruction, and py_compile.

## Canonical evaluation

Engine: `kaggle_environments==1.32.7`.

Sign: `candidate_minus_champion = candidate - champion`.

Same-seed + seat-swap throughout.

- validation: 304001–304012
- sealed: 305001–305004
- stress: 306001–306008
- starter regression: 1–5 for v119 and v112
- runtime: 800503

Immediate REJECT if validation `reorders == 0`, telemetry/runtime errors occur, or a reproducible harmful regression appears.

If activation gate passes, bronze external panel uses seeds 307001–307004 against v49, v50, metav4_v13, k256_h2_q_v1, market_rhythm, story_of_seasons, thomas_router_93, tetsutani_dpts_b, jaxa_2802, and ready_stock. Outcome regressions/improvements are primary under the bronze-medal policy.

## Infrastructure

- suffix: `experiments/v112_v116_milk_micro/v119_suffix.pyfrag`
- focused test: `test_v119_suffix_synthetic.py`
- deterministic builder: `build_v119.py`
- exact runner: `run_v119_eval.py`
- external runner: `run_v119_external_eval.py`
- workflow: `.github/workflows/v112-v119-selfhosted.yml`
- workflow creation commit: `a91162285ac1d1ae85e765d9a28a0945e5ab0f8a`
- active self-hosted run: `36283893966`, job `108520855126`
- current phase at last check: `Exact v119 vs v112 matched evaluation`

## Decision

**KEEP TESTING. Formal champion remains v112.**
