# EXP-20260927 — v120b_clean_signal_overlap_probe

## Status

**TELEMETRY PROBE — NOT PROMOTION ELIGIBLE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

Parent evidence: v120 established that `clean positive` premium market-inventory events separate v112-clone self-play from all 10 external opponents. v120b does not change actions; it measures whether those signals overlap an executable and safe SELL opportunity.

## Hypothesis

A clean signal is useful only if the current v112 state can actually respond. Before creating tactical v121, measure whether a clean signal at step `t` coincides with:

- positive same-item quantity in private shed;
- a v112 parent SELL at `t`;
- a native/static same-item SELL at `t+1`, `t+2`, or `t+3`;
- no current BUY/cash dependency;
- price still above 100% or 75% of nominal base.

This isolates feasible intervention windows without repeating the harmful blind premium reordering from v119 or the zero-activation MELON lead from v114.

## Changes

Telemetry-only wrapper over exact v112. The exact parent action object is returned unchanged.

Tracked items: `STRAWBERRY`, `MELON`, `MILK`, `WOOL`.

For each clean signal (`inventory_delta > 0` and our previous-turn SELL quantity for that item is zero), record:

- current shed quantity;
- actual parent same-turn SELL quantity;
- static SELL quantity at horizons +1/+2/+3;
- whether current parent action contains a BUY;
- market inventory and price before/after;
- price-above-base and price-above-75%-base counts.

## Environment

- branch: `eval/v112-v120b-overlap-probe-20260927`
- canonical engine: `kaggle_environments==1.32.7`
- champion: `v112_wheat_lead3_lowdemand`
- probe: `v120b_clean_signal_overlap_probe`

## Evaluation

Use the same panel as v120 for direct comparability.

### Clone semantic gate

- seeds 308001–308004
- v120b vs v112
- seat swap
- every pair diff must be exactly zero
- telemetry errors must be zero

### External overlap panel

- seeds 309001–309004
- seat swap
- opponents: v49, v50, metav4_v13, k256_h2_q_v1, market_rhythm, story_of_seasons, thomas_router_93, tetsutani_dpts_b, jaxa_2802, ready_stock

Primary outputs are overlap rates, not score.

## Decision rule

v120b itself cannot be promoted.

Create tactical v121 only if at least one item shows a repeatable external-only clean signal with a meaningful number of events satisfying a narrow feasible window, preferably:

`clean signal + shed>0 + same-item SELL within h0..h3 + no BUY dependency + price not already collapsed`.

If most clean signals occur after price collapse, with empty shed, or far from any SELL window, do not force a tactical response from this axis.

Any v121 change must remain 1–3 major changes and preserve existing premium order unless the overlap evidence supports a specific timing modification.

## Files

- `experiments/v112_v116_milk_micro/v120b_suffix.pyfrag`
- `experiments/v112_v116_milk_micro/test_v120b_probe_synthetic.py`
- `experiments/v112_v116_milk_micro/build_v120b.py`
- `experiments/v112_v116_milk_micro/run_v120b_probe.py`
- `.github/workflows/v112-v120b-overlap-probe-selfhosted.yml`

## Decision

**Probe in progress. Formal champion remains v112.**
