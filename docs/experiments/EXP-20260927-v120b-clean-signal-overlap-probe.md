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

## Pre-probe hotspot audit from v120 artifact

Before running v120b, the captured v120 raw event stream was aggregated across the 80 external games (10 opponents × 4 seeds × 2 seats). The event list in v120 was capped, so this audit is useful for hotspot selection but is not treated as an exhaustive event count.

Several clean-signal steps were present for all 10 opponents and all 80 games in the captured stream:

- WOOL: steps 151, 294, 343;
- MELON: steps 250, 251, 252, 253, 254, 256;
- MILK: step 340, with 339/341 also common;
- STRAWBERRY: steps 404, 428, 430, plus 518 (but 518 often occurs after price collapse).

Median post-signal prices at representative ubiquitous hotspots:

- WOOL@151: 199 (~99.5% of nominal base 200);
- WOOL@294: 151 (~75.5% of base);
- WOOL@343: 183 (~91.5% of base);
- MELON@250: 266 (~106.4% of base), falling deterministically across the 250–256 sequence to 226 (~90.4%);
- MILK@339: 169 (~105.6% of base), @340: 137 (~85.6%);
- STRAWBERRY@404/428/430: median roughly 170.5/170.5/164, all still materially above nominal base 120;
- STRAWBERRY@518: median 1, therefore unsuitable as a generic reactive trigger despite universal detection.

This confirms that the detector sees both economically actionable early/mid-season pressure and useless post-collapse noise. v120b must therefore retain explicit price-state telemetry rather than treating all clean events equally.

### Partial SELL-window inference from v120 event stream

The v120 event record also contains `own_prev_sell`. When a clean signal at `t` is followed by another recorded event for the same item at `t+h+1`, a positive `own_prev_sell` there proves that v112 executed a same-item SELL at `t+h`. This is only a partial inference because the event list is capped and a later observation may not itself be recorded.

Within the captured stream, the ubiquitous clean hotspots above generally showed no proven v112 SELL within h0..h3. A few narrower high-price overlaps did appear:

- MILK@358 -> proven 6-unit v112 SELL at step 360 (h2) in 16 captured games, concentrated in v49/v50/tetsutani_dpts_b; median signal price ~154 versus nominal 160;
- STRAWBERRY@453 -> proven 14-unit SELL at step 456 (h3) in 12 captured games; median signal price ~145 versus nominal 120;
- WOOL@456 -> proven 8-unit same-turn SELL in 2 captured games; median signal price ~214 versus nominal 200;
- STRAWBERRY@577 -> proven 8-unit same-turn SELL in 6 captured games; median signal price ~153.

MILK@358 is therefore a concrete provisional v121 hypothesis: if v120b confirms shed stock is already executable at the signal step, a narrowly gated two-turn reactive lead could front-run the observed external sell pressure without affecting clone self-play. It must not be implemented if shed stock is absent or BUY/parent-state conflicts dominate.

## Decision rule

v120b itself cannot be promoted.

Create tactical v121 only if at least one item shows a repeatable external-only clean signal with a meaningful number of events satisfying a narrow feasible window, preferably:

`clean signal + shed>0 + same-item SELL within h0..h3 + no BUY dependency + price not already collapsed`.

If most clean signals occur after price collapse, with empty shed, or far from any SELL window, do not force a tactical response from this axis.

Any v121 change must remain 1–3 major changes and preserve existing premium order unless the overlap evidence supports a specific timing modification.

## Public-reference cross-check

Current public research also contains a `Kaggriculture V35 — Reactive Sales & Sheep Expansion` notebook explicitly organized around public-response sales and evaluated against independent strong opponents / reacting worlds. This is treated only as directional support for reactive-sales research. Its code is not copied into this lineage; v121 must be justified by the local v120/v120b telemetry and canonical H2H/external evaluation.

## Files

- `experiments/v112_v116_milk_micro/v120b_suffix.pyfrag`
- `experiments/v112_v116_milk_micro/test_v120b_probe_synthetic.py`
- `experiments/v112_v116_milk_micro/build_v120b.py`
- `experiments/v112_v116_milk_micro/run_v120b_probe.py`
- `.github/workflows/v112-v120b-overlap-probe-selfhosted.yml`

## Run

- workflow run: `36295388838`
- job: `108553169251`
- initial status: queued behind another self-hosted evaluation

## Decision

**Probe in progress. Formal champion remains v112.**
