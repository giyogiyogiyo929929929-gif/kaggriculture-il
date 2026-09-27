# EXP-20260927 — v122_wool_lowrisk_front1

## Status

**KEEP TESTING — DO NOT PROMOTE**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Parent / lineage

- parent: `v112_wheat_lead3_lowdemand`
- sibling candidate; no stacking with v121
- branch: `eval/v112-v122-wool-lowrisk-front-20260927`
- canonical engine: `kaggle_environments==1.32.7`

## Motivation from v120b / v119 / v121

v120b found 40 executable WOOL clean-signal overlap events across seeds 309001, 309003 and 309004. However most do not justify a quantity/timing change:

- step 432 is the dominant multi-seed WOOL event, but v112 already places `SELL WOOL 24` first and sells the full shed stock, so there is no safe quantity/timing improvement to make;
- step 598–600 would require a quantity lead and is concentrated in fewer opponent/seed states;
- v119 already showed that broad premium front-running is harmful;
- v121 showed that identical public inventory/price state can still have opponent-sensitive economics when quantity is moved across turns.

The remaining narrow, previously untested state is the step-456 pattern. In the v120b 80-game external panel, the telemetry event occurred in exactly six games:

- `metav4_v13`, seed 309004, both seats;
- `story_of_seasons`, seed 309004, both seats;
- `tetsutani_dpts_b`, seed 309003, both seats.

Observed v120b event fields:

- clean WOOL inventory increase: +3 or +4;
- WOOL price after signal: 214 or 225;
- market inventory below 10000;
- shed WOOL: 8;
- parent same-turn WOOL SELL: 8.

The initial candidate design additionally assumed the effective parent action shape matched the static schedule `STRAWBERRY 14 -> WHEAT 4 -> WOOL 8 -> HIRE...` and that no BUY-like order was present. The focused run showed this assumption must be verified from the actual runtime parent action rather than inferred from v120b's limited overlap fields.

## Hypothesis

When an external clean WOOL sell-pressure signal is already visible and v112 is selling all available WOOL on the same turn, moving WOOL forward across exactly one low-risk WHEAT SELL may reduce one unit of opponent interleaving before the WOOL sale without disturbing premium-to-premium order or changing quantity/timing.

This tests order timing only.

## Change

Single major change:

- if the narrow public-state WOOL gate fires, transform only
  `... SELL WHEAT q, SELL WOOL q2 ...`
  into
  `... SELL WOOL q2, SELL WHEAT q ...`.

Safety gates:

- step 400–520;
- previous WOOL market inventory available;
- our previous-turn WOOL SELL quantity is zero;
- current WOOL market inventory increase >=3;
- current WOOL price >=210;
- current WOOL market inventory <10000;
- no BUY / BUY_PRODUCT / BUY_SEED style order in the parent market action;
- exactly one positive WOOL SELL;
- current shed WOOL equals current parent WOOL SELL quantity, so no quantity decision is introduced;
- WOOL is immediately preceded by exactly one `SELL WHEAT`;
- candidate never crosses a premium SELL;
- candidate never crosses two low-risk SELLs.

No quantity, turn, repayment, farm, BUY, or other premium logic changes.

## Telemetry

`agent.telemetry["wool_lowrisk_front1"]` records:

- reorders;
- units;
- moved_slots;
- signal / price / inventory / shed / BUY / current-SELL / shape blocks;
- errors;
- activation step/state details.

## Focused evaluation

Focused self-hosted run `36305589691`: **SUCCESS**.

Candidate SHA256: `aa15c09b3fe5d554a5fd47fae0a5a053f65f7597d07fb30aa8607f1b75f5457d`.

### Synthetic/static

- focused synthetic: PASS;
- exact v112 reconstruction: PASS;
- py_compile: PASS;
- telemetry errors: 0.

### Fresh self-H2H

Seeds `314001–314004`, same seed and seat swap:

- 0W / 0L / 4D;
- mean `candidate_minus_champion = 0.0`;
- worst `0.0`;
- reorders: 0.

No self-play regression was introduced.

### Targeted external replay

Seeds `309003` and `309004` against all 10 bronze-panel opponents, champion and candidate both seat-swapped:

- all 20 matched opponent-seed pairs: `candidate_minus_champion = 0.0`;
- outcome regressions: 0;
- outcome improvements: 0;
- **active pairs: 0**;
- total reorders: 0;
- errors: 0.

This means the intended step-456 state did not satisfy the full v122 runtime gate even in the six games where v120b had recorded a clean WOOL overlap event.

## Probe discrepancy / diagnostic

The no-activation result is not tactical evidence yet; the tactical reorder was never executed. A diagnostic was therefore started instead of proceeding to fresh external seeds.

One concrete discrepancy is already identified in the old v120b probe: its `_v120b_has_buy()` only recognized an order whose opcode was exactly `BUY`. It did **not** classify `BUY_PRODUCT` or `BUY_SEED` as BUY dependencies. v122 intentionally uses `startswith("BUY")`, so some v120b events labelled `has_buy_now=False` may not be safe under the stricter candidate gate.

A second possible mismatch is that v120b recorded only aggregate `sell_h0_parent` and did not preserve the actual runtime market-order shape. The static `_ACTIONS[456]` order therefore cannot be assumed to be the effective v112 action after parent wrappers.

Targeted diagnostic run `36308818490` captures the exact v112 actions and WOOL state at steps 455/456 for:

- `metav4_v13` / seed 309004 / both seats;
- `story_of_seasons` / seed 309004 / both seats;
- `tetsutani_dpts_b` / seed 309003 / both seats.

Do not loosen v122 before that diagnostic identifies the blocking condition.

## Decision rule

Immediate REJECT if:

- errors >0;
- fresh self-H2H introduces a reproducible regression;
- activation appears outside the evidence-backed shape without a clear reason;
- any intended activated opponent shows a reproducible material regression;
- aggregate active-pair economics are negative without an outcome improvement.

If the diagnostic shows the six old v120b events are invalidated by real BUY dependencies or a materially different runtime order shape, reject the current v122 gate as **no canonical activation / incorrect probe assumption** rather than weakening safety guards.

Proceed to fresh external seeds only if a telemetry-supported runtime shape survives the diagnostic and can be tested without crossing BUY dependencies or premium SELLs.

Even a positive focused result cannot promote v122 directly. Fresh external, sealed/stress and runtime gates remain required.
