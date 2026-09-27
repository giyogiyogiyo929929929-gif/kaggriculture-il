# EXP-20260927 — v121_strawberry_race_shift4

## Status

**KEEP TESTING — DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Parent / lineage

- parent: `v112_wheat_lead3_lowdemand`
- sibling of v116/v117/v118; no stacking
- branch: `eval/v112-v121-strawberry-race-20260927`
- canonical engine: `kaggle_environments==1.32.7`

## Hypothesis

v120/v120b identified a public-state clean premium sell-pressure signal that is absent in v112 clone self-play but present against independent external opponents. The strongest under-liquidated executable STRAWBERRY hotspot occurs when external selling increases STRAWBERRY market inventory while v112 still has substantial shed stock and price remains high.

In the v120b raw artifact, the gate

`step>=500 + clean external inventory increase >=4 + STRAWBERRY price>=145 + market inventory<10000 + current parent STRAWBERRY SELL>0 + shed>=parent SELL+4 + no BUY`

selected exactly 10 external games in the 80-game panel. All 10 were the same economic state at step 577:

- opponents: v49, v50, metav4_v13, k256_h2_q_v1, story_of_seasons;
- seed: 309003;
- both seats for every opponent;
- external inventory delta: +5;
- post-signal STRAWBERRY price: 153;
- shed: 32;
- parent same-turn STRAWBERRY SELL: 8.

No other post-step-500 STRAWBERRY event in that panel satisfied the same gate. This is therefore a narrow public-state race response rather than a broad premium timing rewrite.

## Schedule evidence

The raw v120b overlap artifact also proves a later static STRAWBERRY SELL at step 599 with quantity 22 in captured observations. The candidate does not hard-code step 599. At activation it scans the exact parent `_ACTIONS` schedule for the first STRAWBERRY SELL within 48 turns having at least 8 units, records that step as the repayment target, and advances only 4 units now.

This makes the tactical change quantity-conserving:

- activation turn: add 4 units to the existing parent STRAWBERRY SELL in place;
- repayment turn: subtract exactly 4 units from the parent STRAWBERRY SELL;
- all other market-order ordering is preserved;
- if the target parent's actual SELL is unexpectedly too small, debt is deferred to the next future static STRAWBERRY SELL rather than silently increasing lifetime quantity.

## Changes

Single major tactical change:

1. Public-state STRAWBERRY race shift of 4 units.

Activation gates:

- step >= 500;
- previous observed STRAWBERRY inventory exists;
- our previous-turn STRAWBERRY SELL quantity is zero;
- current market inventory increase >= 4;
- current STRAWBERRY price >= 145;
- current STRAWBERRY market inventory < 10000;
- current parent action contains no BUY;
- current parent action already sells STRAWBERRY;
- private shed contains at least `parent_sell + 4` STRAWBERRY;
- a future static STRAWBERRY SELL of at least 8 exists within 48 turns.

No WOOL/MILK/MELON changes are included.

## Telemetry

`agent.telemetry["strawberry_race_shift4"]` records:

- activations / units_shifted;
- repayments / units_repaid;
- repay_deferrals / repay_shortfalls;
- signal/price/inventory/shed/BUY/current-SELL/repay-window blocks;
- errors;
- activation step, repayment step, signal delta, price, shed and parent SELL quantity.

Promotion is impossible with any nonzero `errors` or `repay_shortfalls`.

## Focused evaluation plan

### 1. Synthetic/static gate

- focused synthetic tests covering activation, exact 4-unit conservation, low-signal block, low-price block, insufficient-shed block, BUY block, missing repayment-window block, repayment deferral, seat-state independence;
- exact v112 reconstruction;
- candidate build;
- py_compile.

### 2. Fresh champion H2H

Seeds 310001–310004, same seed and both seats, `v121 - v112`.

This mainly checks that the external-only public signal does not create self-play regressions. A zero-difference result is expected if v112 clone play does not generate the signal.

### 3. Targeted external replay

Replay seed 309003 against all 10 bronze-panel opponents, champion and candidate each with seat swap.

Expected discriminator from the prior telemetry:

- activation expected: v49, v50, metav4_v13, k256_h2_q_v1, story_of_seasons;
- no activation expected: market_rhythm, thomas_router_93, tetsutani_dpts_b, jaxa_2802, ready_stock under the current gate.

Primary decision variables:

- candidate_minus_champion external pair diff;
- outcome regressions / improvements;
- exact activation count and repayment count;
- zero errors and zero repay shortfalls.

## Decision rule after focused run

Immediate **REJECT** if any of the following occurs:

- synthetic/source/runtime failure attributable to candidate;
- errors > 0;
- repay_shortfalls > 0;
- activation occurs broadly outside the telemetry-supported state;
- reproducible external outcome regression;
- activated opponents show no economic benefit or materially worse money.

Proceed to fresh multi-seed external validation only if:

- H2H has no meaningful regression;
- targeted external activation matches the intended public-state signal;
- activated cases improve or remain outcome-safe;
- repayment is exact.

Even if targeted money improves, do not PROMOTE from this run. Fresh external seeds, sealed/stress and runtime gates remain required.

## Files

- `experiments/v112_v116_milk_micro/v121_suffix.pyfrag`
- `experiments/v112_v116_milk_micro/build_v121.py`
- `experiments/v112_v116_milk_micro/test_v121_suffix_synthetic.py`
- `experiments/v112_v116_milk_micro/run_v121_focused.py`
- `.github/workflows/v112-v121-focused-selfhosted.yml`

## Run

Focused self-hosted run: `36302445916` — initially queued.

## Decision

**KEEP TESTING — DO NOT PROMOTE. Formal champion remains v112.**
