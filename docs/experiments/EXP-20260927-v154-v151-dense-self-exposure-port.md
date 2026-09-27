# EXP-20260927 — v154 exact-v151 dense self-exposure port

## Status

KEEP TESTING / NOT READY TO PROMOTE.

Formal champion remains `v151_none_observation_guard`. Fresh sealed block `894322..894333` remains reserved and **unconsumed**. No Kaggle submission.

v154 passed focused, burned, safety/preflight, and internal telemetry checks. The broad hard panel preserved/improved all sampled outcomes but failed the pre-registered non-negative cash-worst gate (`worst = -19`). The first formal runtime stress also failed raw max `<200 ms`; importantly, the exact v151 control failed the same raw-max threshold in that run, so this is not yet evidence of a v154-specific timeout regression.

## Parent / candidate identity

- formal champion: `v151_none_observation_guard`
- champion SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- candidate: `v154`
- candidate SHA256: `9643521253a9c3bb41e27d103353f76ac7e805d91cb838559b8227bc93bff593`
- lineage: v115 -> v147 -> v150 -> v151 -> v154
- engine: `kaggle_environments==1.32.7`

## Hypothesis / change

Port the v153 dense leading-SELL self-exposure order change onto exact v151:

- only steps 288..693;
- only a contiguous leading block of at least five distinct SELL items;
- stable-sort that leading SELL block descending by executable self-impact exposure;
- preserve quantities;
- never cross the first non-SELL / BUY_PRODUCT barrier;
- preserve v151 `observation is None` semantics exactly.

## Focused qualification

Run `36284148569`: SUCCESS.

`score_2820`, seed `520104`, both seats:

- candidate_minus_champion: `+20 / +20`;
- mean `+20`, worst `+20`;
- margin `-9 -> +34`, improvement `+43`;
- candidate/champion exceptions: 0;
- v154 telemetry each seat: `eligible=3`, `changed=1`, `errors=0`;
- `observation=None` returned the same v151 PASS action;
- `py_compile` and exact-v151 SHA check passed.

## Burned direct qualification

Run `36290874071`, seeds `681..692`, seat swap. The burned step passed.

Matched-seed candidate_minus_champion:

- `8W / 0L / 4T`;
- mean `+37.0`;
- worst `0`;
- best `+97`;
- exceptions 0.

Per seed:

`681 0, 682 +67, 683 0, 684 +37, 685 +62, 686 0, 687 +53, 688 +97, 689 +46, 690 +36, 691 0, 692 +46`.

Seed 691 seat legs are `-54/+54`, so the matched pair is 0. Do not misclassify a single seat leg as a matched-pair regression.

## Hard opponent qualification

Run `36290874071`: all individual hard panels completed successfully; aggregate step failed only because the workflow required `min(candidate_minus_champion_cash) >= 0`.

Panel: 8 opponents x seeds `520101..520104` x seat swap = 64 games.

Outcome transitions:

- `W->W`: 62;
- `L->W`: 2;
- outcome regressions: 0;
- outcome improvements: 2;
- exceptions: 0.

Both improvements are `score_2820`, seed `520104`, both seats:

- champion margin `-9`;
- candidate margin `+34`;
- candidate_minus_champion cash `+20`.

Cash-delta summary across opponent/seed matched pairs:

- mean `+1.90625`;
- worst `-19`;
- best `+23`.

By opponent:

- `peak_2950`: mean `-3.75`, worst `-19`, best `+12`;
- `tetsutani_ms`: mean `-1.25`, worst `-4`, best `+1`;
- `score_2820`: mean `+5.5`, worst `-2`, best `+20`;
- `jaxa_2802`: mean `+4.5`, worst `-2`, best `+20`;
- `shop_router_v7`: mean `+4.5`, worst `-2`, best `+20`;
- `melon_squeeze`: mean `+5.75`, worst `0`, best `+23`;
- `salem_2900`: all zero;
- `thomas_router_95`: all zero.

Worst cell is `peak_2950 / 520104`: `-19` cash, but outcome remains W->W and margin remains strongly positive (`+368 -> +329`). The negative cells are symmetric across both seats in this panel, so they are not explained by seat assignment.

Decision implication: the useful `score_2820` loss-to-win flip reproduces exactly, but the candidate violates the pre-registered non-negative worst-cash qualification rule. Do not silently move that goalpost. Investigate whether a narrower activation rule can retain the L->W cells while removing the `peak_2950` / `tetsutani_ms` cash regressions.

## Safety / internal telemetry qualification

Run `36291497324`: SUCCESS.

Kaggle-compatible preflight:

- last function/callable is `agent`;
- standard library / own code only;
- Kaggle-style loader succeeds;
- action shape valid;
- five malformed-observation patterns do not crash.

Normal-game internal telemetry over 88 consumed-panel games:

- `eligible = 166`;
- `changed = 66`;
- `errors = 0`.

This rules out hidden v154 wrapper exceptions as the cause of the observed cash differences.

## Runtime qualification

Run `36291516091`: FAIL on raw max `<200 ms`.

Sequential single-process, GC enabled, `score_2820`, seeds `520101..520104`, both seats, 5,752 calls per agent.

v151 control:

- median `2.861 ms`;
- p95 `6.989 ms`;
- p99 `13.506 ms`;
- max `218.260 ms`;
- wall calls >200 ms: 1;
- errors: 0.

v154 candidate:

- median `3.005 ms`;
- p95 `7.538 ms`;
- p99 `13.732 ms`;
- max `227.679 ms`;
- wall calls >200 ms: 1;
- errors: 0.

Both agents comfortably pass the p99 `<50 ms` criterion, but both fail the raw max `<200 ms` criterion in the same run. This is consistent with the previously observed GC/raw-max tail-noise problem, but it is still a formal runtime FAIL and must not be counted as a pass. Re-run with a pre-registered repeated-control methodology before promotion; do not cherry-pick a passing single rerun.

## Historical v153 correction

The retained v153 artifact, not older prose, is authoritative. It records:

- burned: `8W/0L/4T`, mean `+37`, worst `0`, best `+97`;
- hard outcome transitions: `W->W 62`, `L->W 2`, regressions 0;
- hard cash worst `-19`, not 0.

See `CORRECTION-20260927-v153-artifact-summary.md`.

## Sealed reservation

Fresh block `894322..894333` was preregistered from candidate SHA before outcomes were observed. It remains RESERVED / NOT CONSUMED.

Do **not** spend it yet because the pre-sealed qualification gates are not all passed.

## Current decision

`KEEP TESTING`, formal champion remains v151.

Reasons not to promote yet:

1. hard panel violates the pre-registered non-negative worst-cash gate (`-19`);
2. runtime raw max gate failed (`227.679 ms`), even though the v151 control also failed (`218.260 ms`);
3. fresh sealed evidence has intentionally not been spent;
4. public-diversity / important-opponent final regression and final package/preflight are still pending.

## Next hypothesis / next candidate

Create a narrow follow-up candidate rather than weakening the v154 gate after seeing results. Use telemetry/replay contrast between:

- positive causal cell: `score_2820 / 520104`, and
- negative cash cells, especially `peak_2950 / 520104` and `peak_2950 / 520103`.

Goal: retain the scarce/high-priced MILK order-index race that flips `score_2820` L->W while suppressing activations that only reduce cash inside already-safe wins. Keep this as a 1-mechanism candidate and re-run focused/burned/hard before any sealed spend.

Separately, use a pre-registered repeated runtime/control test to characterize the >200 ms outlier rather than treating a single rerun as qualification.
