# EXP-20260927 — v120_public_market_race_probe

## Status

**TELEMETRY PROBE — NOT PROMOTION ELIGIBLE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

v120 is deliberately action-identical to v112. Its only purpose is to measure whether public market state exposes opponent-specific premium-item sell pressure strongly enough to justify a later tactical candidate.

## Motivation

v119 proved that blindly reordering premium SELLs is harmful: canonical matched H2H was 0W/8L/4D validation, 0W/4L sealed, and 0W/8L stress, with MILK and some WOOL reorders producing very large losses. Future premium intervention therefore needs opponent-specific evidence rather than current-price scarcity alone.

## Probe signal

For each premium item (`STRAWBERRY`, `MELON`, `MILK`, `WOOL`), v120 stores the previous public market inventory and our previous-turn SELL quantity.

At the next observation:

`excess = max(0, current_inventory - previous_inventory - our_previous_sell_quantity)`

This is treated as a conservative lower bound on opponent sell pressure. Town consumption and our market purchases reduce inventory, so they cannot create a positive residual. The probe does not claim exact attribution when multiple mechanics occur on the same turn.

It records:

- positive inventory-change events/units;
- clean positive events where we sold zero of that item;
- positive residual (`excess`) events/units;
- residual events accompanied by a price drop;
- negative inventory-change counts;
- up to 128 residual events with step, item, inventory before/after, own SELL, excess, and price before/after.

## Safety invariant

The wrapper returns the exact parent action object unchanged. It does not reorder, add, remove, delay, or advance any action.

Focused synthetic checks verify:

- parent action identity is preserved;
- own MILK SELL is subtracted from the observed inventory rise;
- a clean STRAWBERRY inventory rise is detected;
- price-drop joint signal is recorded;
- episode/reset handling does not create a fake transition;
- parent telemetry remains attached.

Local result: `v120 synthetic checks: PASS`.

## Canonical probe plan

Engine: `kaggle_environments==1.32.7`.

### Clone baseline

- seeds 308001–308004
- v120 vs v112
- seat swap
- every matched pair diff must be exactly zero or the semantic gate fails.

### External panel

- seeds 309001–309004
- seat swap
- opponents: v49, v50, metav4_v13, k256_h2_q_v1, market_rhythm, story_of_seasons, thomas_router_93, tetsutani_dpts_b, jaxa_2802, ready_stock.

Primary output is telemetry distribution, not score.

## Decision rule for v121

Only create an opponent-reactive tactical candidate if external opponents show a repeatable public-state signal that is materially enriched relative to the v112-clone baseline, preferably concentrated in specific item/step regimes.

Do not use the probe to justify broad MILK/WOOL reordering. Any later action change must preserve the learned v112 premium order unless a separately tested, narrowly gated response is supported by the probe.

If the external distributions do not separate from clone baseline, abandon this race-detector axis rather than tuning thresholds on noise.

## Infrastructure

- suffix: `experiments/v112_v116_milk_micro/v120_suffix.pyfrag`
- focused test: `test_v120_probe_synthetic.py`
- builder: `build_v120.py`
- runner: `run_v120_probe.py`
- workflow: `.github/workflows/v112-v120-probe-selfhosted.yml`
- run: `36291456907`

## Decision

**Probe in progress. Formal champion remains v112.**
