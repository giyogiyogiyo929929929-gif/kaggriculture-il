# EXP-20260927 — v123_wool_runtime_probe

## Status

**PROBE RUNNING — NOT A CANDIDATE — DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Motivation

v122 was rejected because its step-456 order hypothesis was derived from static `_ACTIONS`, while exact v112 runtime output already had WOOL before WHEAT. Therefore subsequent SELL-order/timing research must use runtime parent actions rather than static tape order.

v120b had shown executable WOOL clean-signal overlap in several parts of the game across multiple seeds, but re-analysis of the specific late window showed that the **598–600 executable subset is concentrated entirely in seed `309001`**. The old probe also used static future SELL windows and did not preserve exact runtime actions. v123 resolves that evidence gap before any further tactical mutation and explicitly tests whether this single-seed late window has any runtime action opportunity worth pursuing.

The v120b late-window rows that motivated this probe were:

- `metav4_v13`, seed `309001`, both seats: signal at 598 (`price=169`, `shed=2`, static h+2 WOOL SELL 10) and 599 (`price=148`, `shed=2`, static h+1 SELL 10);
- `k256_h2_q_v1`, seed `309001`, both seats: signal at 598 (`price=169`, `shed=2`, static h+2 SELL 10) and 600 (`price=148`, `shed=10`, same-turn parent WOOL SELL 10);
- `story_of_seasons`, seed `309001`, both seats: same pattern as `metav4_v13`.

No 598–600 executable WOOL overlap from v120b was found in seeds `309003` or `309004`. Therefore any later tactical candidate from this window starts with a strong seed-overfit warning.

## Probe design

No candidate wrapper is used. Exact `v112_wheat_lead3_lowdemand` is called directly and its returned action is traced.

Panel:

- seeds: `309001`, `309003`, `309004`;
- opponents: `v49`, `v50`, `metav4_v13`, `k256_h2_q_v1`, `market_rhythm`, `story_of_seasons`, `thomas_router_93`, `tetsutani_dpts_b`, `jaxa_2802`, `ready_stock`;
- both seats;
- canonical engine: `kaggle_environments==1.32.7`.

For WOOL clean positive inventory transitions in steps 560–620 where our previous runtime action sold zero WOOL, record:

- signal step and inventory delta;
- WOOL market inventory / price;
- shed WOOL;
- exact runtime market order list;
- actual WOOL SELL quantity;
- BUY-like orders;
- the next three exact runtime action frames.

## Decision rule

Only create a tactical candidate if the runtime evidence reveals a repeated state where all of the following are true:

1. clean opponent-like WOOL sell-pressure signal is present;
2. we have WOOL in shed or a concrete near-term runtime WOOL SELL;
3. the proposed change does not cross a BUY dependency;
4. the proposed change does not disturb premium-to-premium ordering without separate evidence;
5. the runtime opportunity is not merely a static-tape artifact.

Because the motivating 598–600 evidence is confined to one world seed, even a clean runtime opportunity is **insufficient for promotion evidence**. A tactical candidate would first need fresh-seed reactivation or another independent rationale. If v112 runtime wrappers already handle the late window optimally, close this WOOL axis rather than inventing a redundant candidate.
