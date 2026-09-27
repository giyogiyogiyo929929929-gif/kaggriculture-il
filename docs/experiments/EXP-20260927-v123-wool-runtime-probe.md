# EXP-20260927 — v123_wool_runtime_probe

## Status

**PROBE RUNNING — NOT A CANDIDATE — DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Motivation

v122 was rejected because its step-456 order hypothesis was derived from static `_ACTIONS`, while exact v112 runtime output already had WOOL before WHEAT. Therefore subsequent SELL-order/timing research must use runtime parent actions rather than static tape order.

v120b had shown executable WOOL clean-signal overlap near steps 598–600 across multiple seeds, but its future windows used static schedule and did not preserve exact runtime actions. v123 resolves that evidence gap before any further tactical mutation.

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

Only create a tactical candidate if the runtime evidence reveals a repeated, multi-seed state where all of the following are true:

1. clean opponent-like WOOL sell-pressure signal is present;
2. we have WOOL in shed or a concrete near-term runtime WOOL SELL;
3. the proposed change does not cross a BUY dependency;
4. the proposed change does not disturb premium-to-premium ordering without separate evidence;
5. the same runtime shape occurs in more than one world seed or has a strong independent opponent rationale.

If 598–600 is already handled optimally by v112 runtime wrappers, close this WOOL axis rather than inventing a redundant candidate.
