# EXP-20260927 — v126_day10_melon_inventory_probe

## Status

**PROBE RUNNING — NOT A CANDIDATE — DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Motivation

v124 economic attribution identified day 10 MELON cash-in as the first large common external deficit. v125 exact-runtime tracing confirmed that important external opponents start a MELON liquidation wave around step 250 while v112's corresponding wave starts around step 256.

At step 250 v125 reported `private.shed.MELON = 0` for v112, but the observation model also exposes `private.inventories` for the farmer and hands. Opponents can request MELON sales while their shed snapshot is also zero, so shed alone cannot determine executable inventory.

## Probe design

No action mutation. Exact v112 and the opponent are traced directly.

Panel:

- opponents: `thomas_router_93`, `metav4_v13`, `k256_h2_q_v1`, `ready_stock`, `jaxa_2802`;
- seeds: `309001`, `309004`;
- both seats;
- engine: `kaggle_environments==1.32.7`.

For steps 248–256 record for both agents:

- full `private.inventories`;
- recursively summed carried MELON quantity;
- shed;
- public farmer / hands state;
- MELON public market inventory and price;
- exact runtime action and MELON SELL orders;
- money trajectory.

## Questions

1. Does v112 already carry MELON at step 249/250 even though shed is zero?
2. If yes, is the external gap primarily a SELL scheduling problem and can an earlier quantity-preserving SELL be tested?
3. If no, when does v112 first acquire carried MELON relative to the opponents, and is the root cause harvest / DROP / routing timing?

## Decision rule

- If v112 has executable carried MELON at ~250 across both seeds, create a bounded SELL-timing candidate rather than changing farm production.
- If v112 lacks MELON until ~256 while opponents have it around 249/250, do not add a blind SELL order; move to a harvest/routing candidate or probe.
- Any candidate must remain sibling to v112 and must pass same-seed seat swap, fresh seeds, external regression panel and runtime gates before promotion.
