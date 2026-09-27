# EXP-20260927 — v120_public_market_race_probe

## Status

**PROBE COMPLETE — SIGNAL FOUND — NOT PROMOTION ELIGIBLE**

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

Canonical result: `v120 synthetic checks: PASS`.

## Canonical probe execution

Engine: `kaggle_environments==1.32.7`.

Run: `36291456907` on self-hosted Windows X64 runner `CIYOI`.

Source SHAs reconstructed successfully, including exact v112 SHA `1c6e00ff0bd46b16189b1f6a93ce5e498ff8ffb5b0acb33591cdd247cd8b4771` as printed by the workflow source builder. v120 probe SHA was `e42783e7863eeb6f81e5ec0a17aa0163fb006efb68180afedbb11db7bb5217c9`.

### Clone semantic gate

Seeds 308001–308004, seat swapped.

Pair diffs:

- 308001: 0.0
- 308002: 0.0
- 308003: 0.0
- 308004: 0.0

Errors: 0.

Decision: semantic gate **PASS**. v120 is action-identical to v112 on the canonical clone panel.

### Self-play baseline telemetry

Across 8 games / 5,744 transitions:

| item | clean positive events | excess events | excess units |
|---|---:|---:|---:|
| STRAWBERRY | 0 | 214 | 1478 |
| MELON | 0 | 48 | 664 |
| MILK | 0 | 320 | 1146 |
| WOOL | 0 | 104 | 606 |

The key baseline is that **clean positive events are zero for all four premium items** when v112 plays its action-identical clone.

### External panel separation

Seeds 309001–309004, seat swapped, against 10 independent/historical opponents.

For every external opponent and every tracked premium item, clean positive events became nonzero. Across opponents, the per-opponent ranges were:

| item | clean events min | median | max | clean units min | median | max |
|---|---:|---:|---:|---:|---:|---:|
| STRAWBERRY | 146 | 235 | 262 | 996 | 1105 | 1198 |
| MELON | 48 | 48 | 48 | 480 | 480 | 480 |
| MILK | 156 | 220 | 276 | 706 | 900 | 936 |
| WOOL | 170 | 212 | 240 | 680 | 848 | 1180 |

This is a strong distributional separation from the clone baseline (`0` clean events for every item).

Most positive residual events also coincided with a price drop. Across external opponents, the joint-excess/price-drop fraction ranged approximately:

- STRAWBERRY: 97.6%–100%
- MELON: 100%
- MILK: 100%
- WOOL: 84.8%–94.4%

This supports treating the signal as economically relevant sell pressure rather than arbitrary inventory noise, while still not claiming exact opponent-action attribution for non-clean residuals.

The external event streams also show repeated short runs rather than only isolated spikes. In the aggregate external telemetry, consecutive clean-event streaks reached length 4 for STRAWBERRY/MILK/WOOL and length 5 for MELON. This makes a short-horizon opponent-response hypothesis plausible, but it does not yet prove that v112 has executable stock or a safe SELL window immediately after the signal.

### External strength context

Because v120 is action-identical to v112, its external score is effectively the current champion's score on this panel, not a candidate-vs-champion delta.

Across 40 seed-opponent matched pairs:

- wins: 0
- losses: 40
- draws: 0
- mean champion-vs-opponent pair diff: -48,754.15
- worst: -59,294
- best: -25,475

This reinforces the bronze-medal policy: the main remaining problem is robust external-opponent performance, not extracting a few more self-play dollars.

## Interpretation

The broad `excess` count alone is not a safe trigger: self-play already has many non-clean excess events because mirrored actions can produce simultaneous inventory rises.

The **clean positive event** is the useful discriminator. It requires our previous SELL quantity for that item to be zero, and it was absent in the clone baseline but abundant against all 10 external opponents.

Therefore the race-detector axis is retained.

However, v119 already showed that blind premium reordering is harmful. The next action-changing candidate must not simply front-run every clean signal. Before changing actions, measure overlap between a clean signal at step `t` and:

1. executable shed stock at `t`;
2. an existing native/premium SELL of the same item at `t` or within a short horizon;
3. current price remaining materially above the floor;
4. no BUY/cash dependency and no existing parent preemption repayment;
5. repeated signal / short streak where useful.

## Next experiment

Create an action-identical overlap probe before a tactical v121 if needed. It should log, for every clean premium signal, whether the parent action at the same step or the next few static steps already contains a SELL of the same item and whether executable stock exists.

Only then create v121 with one narrow response. Candidate changes must preserve the existing v112 premium ordering unless the clean-signal overlap demonstrates a specific safe timing opportunity.

MELON deserves special attention because every external opponent produced exactly 48 clean events / 480 clean units while clone baseline was zero, but previous v114 evidence showed that a simple one-turn shed-only MELON lead had zero activation. Any MELON candidate therefore needs stock/horizon evidence first rather than re-running v114 in another form.

## Infrastructure

- suffix: `experiments/v112_v116_milk_micro/v120_suffix.pyfrag`
- focused test: `test_v120_probe_synthetic.py`
- builder: `build_v120.py`
- runner: `run_v120_probe.py`
- workflow: `.github/workflows/v112-v120-probe-selfhosted.yml`
- run: `36291456907`
- artifact: `v112-v120-public-market-race-probe`, artifact ID `10922558581`, SHA256 `91fff829db7e5762c36dc809b1f3cae3a20f0e6d8c63559267a4e0de83397424`

## Decision

**PROBE SUCCESS. Race-detector research continues. Formal champion remains `v112_wheat_lead3_lowdemand`. v120 itself is not promotion eligible.**
