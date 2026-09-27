# EXP-20260927 — v123 WOOL late runtime probe

## Status

**PROBE RUNNING — NO CANDIDATE / DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Parent / purpose

- exact parent under inspection: `v112_wheat_lead3_lowdemand`
- branch: `eval/v112-v123-wool-late-probe-20260927`
- canonical engine: `kaggle_environments==1.32.7`
- this is action-identical diagnostic work, not a tactical candidate.

## Why this probe exists

v122 was rejected because static `_ACTIONS[456]` did not match the exact runtime v112 market order after wrappers. Therefore SELL-order candidates must be based on exact runtime actions, not static tape shape alone.

The v120b external artifact was re-read directly. WOOL clean-signal events at steps 598–600 occur only in seed `309001`, in these three opponents:

- `metav4_v13` — both seats;
- `k256_h2_q_v1` — both seats;
- `story_of_seasons` — both seats.

Observed v120b fields:

- step 598: WOOL market inventory `10021 -> 10023`, price `174 -> 169`, shed `2`, parent same-turn WOOL SELL `0`, static WOOL SELL at +2 = `10`;
- `metav4_v13` and `story_of_seasons` also show step 599: inventory `10023 -> 10030`, price `169 -> 148`, shed `2`, parent same-turn WOOL SELL `0`, static +1 SELL `10`;
- `k256_h2_q_v1` shows step 600: inventory `10023 -> 10030`, price `169 -> 148`, shed `10`, parent same-turn WOOL SELL `10`.

This suggests a possible two-unit short-horizon timing opportunity, but the evidence is single-world-seed concentrated and static future SELL fields are not sufficient to define a candidate.

## Diagnostic

Self-hosted run `36310469244` captures exact v112 runtime actions and public/private WOOL state at steps `597–601` for the three opponent/seed cases above, both seats.

The diagnostic records:

- WOOL market inventory and price;
- WOOL shed stock;
- exact runtime market order list;
- actual same-turn WOOL SELL quantity;
- any BUY-like orders.

## Decision rule

Do **not** implement a tactical candidate unless the exact runtime trace shows all of the following:

1. WOOL is actually available in shed before the native runtime SELL;
2. the native runtime SELL really occurs later (not already dynamically advanced by v112 wrappers);
3. a two-unit move can be repaid exactly from that later runtime SELL;
4. no BUY dependency is crossed;
5. no premium SELL ordering dependency is disturbed.

Even if those conditions hold, any resulting candidate must first replay the evidence-backed cases and then activate on fresh external seeds. A gain confined to seed `309001` is insufficient for promotion.

## Adjacent findings

The same v120b artifact shows the only conservative MILK executable overlap is also seed `309001`: `metav4_v13` and `story_of_seasons`, both seats, step 360, price `135`, shed/current SELL `6`. Thus MILK is not currently a better multi-seed escape route.
