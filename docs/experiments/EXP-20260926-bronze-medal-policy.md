# EXP-20260926 — Bronze-medal optimization policy

## Status

ACTIVE POLICY for the current v90→…→v112 lineage.

Formal champion remains `v112_wheat_lead3_lowdemand` unless a candidate passes the full promotion gates. `v66` is not a champion or evaluation target. The separate `v130+` lineage must not be mixed into this lineage's promotion evidence.

## Objective

Optimize for a realistic bronze-medal outcome, not for maximum self-play money margin.

Kaggriculture ranking is driven by match wins/losses rather than the magnitude of the final-money difference, so the primary objective is to convert reproducible losses/draws into wins while avoiding matchup-specific regressions.

## Evaluation priority

For future candidates in this lineage, use the following priority order:

1. exact same-seed + seat-swap vs formal champion;
2. win/loss/draw changes before mean money delta;
3. worst regression and seed concentration;
4. sealed unused seeds;
5. stress seeds;
6. strong / independent external opponents, especially known divergent opponents and close public-top-style agents;
7. runtime, exceptions and timeout safety;
8. telemetry/replay explanation of why the result changed.

A candidate with a positive average money delta but a new reproducible loss is not automatically promotable. A small-money improvement that flips several stable losses/draws to wins with no meaningful regression is strategically more valuable.

## Candidate design preference

Prefer 1–3-change mechanisms that are:

- public-state based;
- locally gated rather than globally applied;
- measurable by activation telemetry;
- orthogonal to the already explored WHEAT horizon expansions;
- testable against external opponents without relying on hidden information.

Current preferred research axes:

- premium-item local SELL ordering;
- Town-consumption-adjacent timing without crossing beneficial consumption ticks;
- market-inventory regime gates;
- opponent public-state race detection;
- safe post-classifier extensions to other items;
- shop-composition / shop-order local routing.

## Current candidate

`v116_milk_micro_lead1` remains KEEP TESTING against `v112_wheat_lead3_lowdemand`.

It should only advance if exact H2H has nonzero activation and acceptable matched-pair results, then passes sealed/stress and a broad external safety panel. For bronze-medal optimization, external-opponent regressions are a stronger rejection signal than a small positive self-play mean.

## Promotion rule

PROMOTE only when all of the following are supported:

- matched-seed improvement survives seat swap;
- no unacceptable worst regression;
- effect is not one-seed-only;
- sealed seeds reproduce the effect;
- stress does not expose a systematic regression;
- important external opponents do not regress materially;
- runtime remains within project limits;
- exceptions/timeouts are zero;
- telemetry/replay gives a reproducible causal explanation.

If evidence is mixed, KEEP TESTING rather than promoting for a small average gain.
