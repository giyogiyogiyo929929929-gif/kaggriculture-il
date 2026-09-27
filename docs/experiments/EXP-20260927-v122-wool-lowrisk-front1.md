# EXP-20260927 — v122_wool_lowrisk_front1

## Status

**REJECT — no canonical activation; exact runtime parent already has WOOL before WHEAT**

Formal champion remains `v112_wheat_lead3_lowdemand`.

## Parent / lineage

- parent: `v112_wheat_lead3_lowdemand`
- sibling candidate; no stacking with v121
- branch: `eval/v112-v122-wool-lowrisk-front-20260927`
- canonical engine: `kaggle_environments==1.32.7`

## Hypothesis

v120b recorded a step-456 external WOOL clean-signal overlap in six games. v122 attempted one narrow same-turn order change only: move WOOL ahead of exactly one preceding WHEAT SELL, without changing turn, quantity, premium-to-premium order, or BUY dependencies.

Intended transformation:

`... SELL WHEAT q, SELL WOOL q2 ...`

→

`... SELL WOOL q2, SELL WHEAT q ...`.

## Focused evaluation

Focused self-hosted run `36305589691`: **SUCCESS**.

Candidate SHA256: `aa15c09b3fe5d554a5fd47fae0a5a053f65f7597d07fb30aa8607f1b75f5457d`.

### Static / synthetic

- synthetic: PASS;
- exact v112 reconstruction: PASS;
- py_compile: PASS;
- telemetry errors: 0.

### Fresh champion H2H

Seeds `314001–314004`, same seed and both seats:

- 0W / 0L / 4D;
- mean `candidate_minus_champion = 0.0`;
- worst `0.0`;
- reorders: 0.

### Targeted external replay

Seeds `309003` and `309004` against all 10 bronze-panel opponents, champion and candidate both seat-swapped:

- all 20 matched opponent-seed pairs: `candidate_minus_champion = 0.0`;
- outcome regressions: 0;
- outcome improvements: 0;
- active pairs: 0;
- total reorders: 0;
- errors: 0.

The tactical change never executed, so this run did not provide positive or negative tactical evidence.

## Exact step-456 diagnostic

Diagnostic run `36308818490`: **SUCCESS**.

The six v120b target games were replayed with exact v112 runtime action capture at steps 455 and 456.

### `metav4_v13`, seed 309004, both seats

Step 455:

- WOOL market inventory: 9993;
- WOOL price: 218;
- shed WOOL: 0;
- market orders: none;
- BUY-like orders: none.

Step 456:

- WOOL market inventory: 9996 (`+3` clean increase);
- WOOL price: 214;
- shed WOOL: 8;
- exact runtime market action:
  - `SELL STRAWBERRY 14`;
  - `SELL WOOL 8`;
  - `SELL WHEAT 4`;
  - six `HIRE` orders;
- BUY-like orders: none.

### `story_of_seasons`, seed 309004, both seats

Exact same step-455/456 state and action shape as `metav4_v13`.

### `tetsutani_dpts_b`, seed 309003, both seats

Step 455:

- WOOL market inventory: 9979;
- WOOL price: 227;
- shed WOOL: 0;
- market orders: none.

Step 456:

- WOOL market inventory: 9983 (`+4` clean increase);
- WOOL price: 225;
- shed WOOL: 8;
- exact runtime market action:
  - `SELL STRAWBERRY 14`;
  - `SELL WOOL 8`;
  - `SELL WHEAT 4`;
  - six `HIRE` orders;
- BUY-like orders: none.

## Root cause

The old v120b probe correctly identified the public WOOL signal and same-turn WOOL SELL, but it did not preserve the exact runtime market-order shape. The v122 design inferred the shape from static `_ACTIONS[456]` and assumed WHEAT preceded WOOL.

That assumption was false after the existing v112 wrappers ran. In the exact runtime parent action, WOOL is **already ahead of WHEAT** in every intended target game.

Therefore the v122 gate correctly produced zero reorders: there is no WHEAT slot to cross. This is not a BUY-dependency issue and not tactical evidence against WOOL-first ordering. The parent is already in the intended order.

## Decision

**REJECT — no canonical activation / incorrect static-order assumption.**

Do not loosen the shape gate just to force activation. Doing so would cross a premium SELL or otherwise test a different mechanism than the one justified by telemetry.

Fresh external seeds `315001–315004`, sealed/stress, and runtime expansion are not run for v122 because the intended mechanism is already present in v112 at the target state.

## Do not repeat

Do not infer actionable market-order position from static `_ACTIONS` when parent wrappers can reorder the effective action. Any future same-turn order candidate must capture and segment the **exact runtime parent market-order list** first.

## Next hypothesis

The remaining WOOL overlap around steps 598–600 should not be converted directly into a candidate. First use an action-identical exact-order probe to capture runtime market-order shape, shed, current/future WOOL quantity, BUY dependencies, and opponent/seed concentration at those windows. Only create another WOOL candidate if that probe identifies a real runtime ordering or timing gap not already handled by v112.
