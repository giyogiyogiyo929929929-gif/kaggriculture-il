# EXP-20260927 — v123 WOOL late runtime probe

## Status

**PROBE COMPLETE — VALID MICRO WINDOW, NO TACTICAL CANDIDATE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Parent / purpose

- exact parent under inspection: `v112_wheat_lead3_lowdemand`
- branch: `eval/v112-v123-wool-late-probe-20260927`
- canonical engine: `kaggle_environments==1.32.7`
- action-identical diagnostic only; not promotion eligible.

## Why this probe existed

v122 was rejected because static `_ACTIONS[456]` did not match exact runtime v112 market ordering. Therefore later SELL-order ideas must be based on exact runtime actions.

The v120b artifact showed WOOL clean-signal events at steps 598–600 only in seed `309001`, for `metav4_v13`, `k256_h2_q_v1`, and `story_of_seasons`, both seats.

## Canonical diagnostic result

Self-hosted run `36310469244`: **SUCCESS**.

All six inspected games show the same core v112 runtime structure:

- step 597: WOOL shed `2`, no WOOL SELL;
- step 598: WOOL shed `2`, no market orders, WOOL price `169` after the external inventory increase;
- step 599: WOOL still `2`, v112 sells STRAWBERRY only;
- step 600: WOOL shed `10`, v112 sells all `10` WOOL first in the runtime market order; no BUY-like dependency is present;
- step 601: WOOL shed `0`.

The exact market path differs slightly by opponent, but the possible timing move is real: two WOOL units already exist at step 598 and are not sold until the native step-600 ten-unit batch.

Examples:

- `metav4_v13` / seed309001: WOOL price `169` at step598, `148` at step600;
- `k256_h2_q_v1` / seed309001: same step598 price `169`, step600 `148`;
- `story_of_seasons` / seed309001: same pattern.

No BUY-like order blocks the move, and the native step600 WOOL SELL is first in the runtime market list, so an exact two-unit repayment would be mechanically possible.

## Decision

**Do not create a v123 tactical candidate.**

Reason:

1. every known activation is concentrated in one world seed, `309001`;
2. only two WOOL units can be moved by two turns;
3. the observed price difference is only about `$21` per unit before accounting for the full alternating-market path, so the plausible gain is only tens of dollars;
4. v112 is losing the same external opponent family by roughly `$25k–$59k` in the bronze panel;
5. bronze policy prioritizes robust loss→win mechanisms over tiny margin gains that cannot plausibly alter the outcome.

This is a valid micro-opportunity, but not a useful next candidate under the remaining competition time.

## Adjacent finding

The only conservative MILK executable overlap in v120b is also seed `309001` (`metav4_v13` and `story_of_seasons`, both seats, around step360). It is not a better multi-seed escape route.

## Next hypothesis

Pivot from premium micro-timing to external economic-gap attribution. Measure where the `$25k–$59k` deficit is created using action-identical traces of:

- per-item SELL quantity;
- BUY quantities and market-order mix;
- HIRE / BUY_LAND usage;
- day-by-day money gap;
- sell-price exposure as a diagnostic proxy (not realized revenue);
- final/late shed state.

Use those results to select a higher-leverage 1–3 change candidate.
