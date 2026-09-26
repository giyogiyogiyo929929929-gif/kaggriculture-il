# EXP-20260926 v148 duplicate-same-item SELL guard

## Status

**Decision: EVALUATION PENDING. Do not promote.**

The formal champion remains the exact v115 `v115_champion_same_turn_open_squeeze` reconstruction from `EXP-20260926-v147-resume-result.md`, SHA256 `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`.

Do not infer champion identity from older workflow/job labels that mention v121. The latest v147 experiment explicitly resolved the v115/v121 naming ambiguity by exact SHA and is the governing record for this branch.

## Version / parent / champion

- candidate: `v148_duplicate_sell_guard`
- parent concept: `v147_confirmed_v111_clone`
- builder: `ci/build_v148_duplicate_sell_guard.py`
- formal champion: `v115_champion_same_turn_open_squeeze`
- champion SHA256: `c6b9986f6cbdf8663ed33096f55e93ef665bd560d55bf9baffbe4a5f8c74fff2`
- evaluation branch: `eval-v148-duplicate-sell-guard-20260926`
- fixed evaluation HEAD: `5ac0866c1b5ac2772f0347fb9470dc284bbd5f97`

## Hypothesis

v147's confirmed second-pass `_v111_reorder` produced reproducible positive direct gains on nine of twelve burned matched pairs, but seed 691 exposed a seat-sensitive -52 / +56 split. Focused replay showed that seed 691's first same-state divergence contained two separate `SELL CARROT` fragments and v147 moved one fragment across `SELL WHEAT`.

A single narrow safety guard may preserve v147's clean order-only gains while removing this seat-sensitive failure mode: **skip the second-pass reorder whenever the parent action contains more than one SELL order for the same item; otherwise leave v147 behavior unchanged.**

## Changes

One strategic change only:

1. Before the confirmed second-pass `_v111_reorder`, collect SELL item kinds from the current market action. If any item occurs more than once, skip the second pass for that turn.

The candidate is intentionally built directly on exact v115 and reimplements v147's confirmation logic plus this guard. Building on v147 itself would be incorrect because v147 may already have applied the unsafe second pass before v148 could inspect/undo it.

## Implementation note / pre-evaluation bug fix

The first draft of the builder accidentally called `_V147_PARENT`, which is undefined when the v148 overlay is appended directly to v115. Static review caught this before a valid evaluation run. It was corrected to `_V148_PARENT` in commit `551c4e5923f9a75d83216c1ace92aa031bc30149`.

The valid evaluation target therefore starts at branch HEAD `5ac0866c1b5ac2772f0347fb9470dc284bbd5f97`. Any earlier v148 workflow run is pre-fix infrastructure evidence only and must not be used for candidate performance judgment.

## Environment

- repository: `giyogiyogiyo929929929-gif/kaggriculture-il`
- engine: `kaggle_environments==1.32.7`
- primary runner: self-hosted Windows X64 (`CIYOI`)
- metric: `candidate_minus_champion = candidate - champion`
- valid primary workflow run: `36230507162`
- pre-fix queued run: `36230251225` — invalid for candidate judgment
- GitHub-hosted Ubuntu fallback run: `36230319599` — failed before executing workflow steps; infrastructure failure, not candidate failure

At the time of this record, the self-hosted runner is occupied by `export-local-eval` run `36229648381`, whose engine verification and reconstruction steps completed and whose bundle assembly step is still running. Consequently valid v148 run `36230507162` is queued.

## Static / syntax / focused test plan

The workflow reconstructs and SHA-verifies exact v115 and exact v147, builds v148 directly from v115, and runs:

1. `py_compile` for v115/v147/v148 and the v148 builder.
2. Focused synthetic tests asserting duplicate `SELL CARROT` fragments trigger the guard while unique SELL item kinds do not.
3. Runtime preflight on seed 681.

Results are pending the valid workflow run.

## Burned matched gate

Seeds `681..692`, same seeds with seat swap, exact v148 versus exact v115.

The burned gate must satisfy all of:

- pair losses = 0;
- pair mean `candidate_minus_champion >= +45` (v147 baseline was +47.5);
- pair worst regression >= 0;
- seed 691 minimum single-seat leg >= 0, directly testing removal of the observed -52 failure;
- candidate exceptions = 0.

If this gate fails, the workflow stops before sealed seeds are consumed.

## Known-opponent regression plan

Only after the burned gate passes, compare candidate and champion on the same known-opponent panel used for v147:

- starter
- beat_v48
- bl_v20
- bl_v21
- farming_v2
- frontier_prvsiyan

Seeds `661..664` per opponent.

## Sealed / stress plan

Only after the burned gate passes:

- unused sealed direct matched seeds: `701..712`, seat swap;
- stress direct matched seeds: `713..732`, seat swap.

These seeds must not be interpreted before confirming they were actually reached by the gated workflow.

## Results

Pending valid run `36230507162`.

## candidate_minus_champion

Pending.

## Worst regression

Pending. Primary targeted risk is seed 691's prior -52 single-seat leg.

## Telemetry findings

Parent v147 evidence motivating this candidate:

- positive seeds generally changed SELL ordering without changing the SELL multiset;
- seed 689 improved +230 in both seats with identical farm health, strong evidence for direct market-order timing benefit;
- seed 691's action contained two CARROT SELL fragments and produced -52 / +56 seat legs after reordering one fragment relative to WHEAT.

v148-specific telemetry is pending evaluation.

## Runtime

Pending valid workflow. v147 had clean runtime and zero exceptions; v148 adds only a small scan of the market action before a second-pass reorder.

## Decision

**EVALUATION PENDING; champion remains v115. Do not promote.**

## Next hypothesis

Do not create v149 from speculation before v148's burned result is known. If v148 removes seed 691's negative leg while preserving v147's other gains, inspect sealed/stress divergences and use those telemetry results for the next candidate. If the guard removes legitimate gains or another duplicate pattern remains harmful, refine the guard using the first new failing replay rather than broadening it blindly.
