# EXP-20260925-v135 milk quote-boundary guard

Status: **PENDING SELF-HOSTED CI — DO NOT PROMOTE**

## Identity

- Formal champion: `v121_champion_same_turn_unwind.py`
- Champion SHA256: `1a44487de886d59f612cfbd083cacadf872ad56d0db13604cbf8af0056c600c2`
- Parent tactical candidate: `v133_candidate_center_only.py`
- Candidate: `v135_candidate_milk_quote_boundary.py`
- Candidate SHA256: pending exact rebuild on CI
- Exact builder: `eval_assets/v130/build_v135.py`
- Branch: `eval-v135-milk-quote-boundary-20260925`
- Workflow: `.github/workflows/v135-focused.yml`
- GitHub Actions run: `36144084808`
- Engine: `kaggle_environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`

`v66` is not used.

## Motivation / prior evidence

v133's Town-Center-only hold showed aggregate improvement over v121, but had one known regression against `bl_v21 / seed 382002`:

- v121 around step 600: `SELL MILK 2`
- v133 around step 600: `SELL MILK 1`
- v133 own terminal cash: `+1` vs v121
- opponent terminal cash: `+3` vs v121
- relative margin: `-2`

The telemetry interpretation is a one-unit market-price externality: retaining one MILK left the market one unit scarcer, allowing the opponent to receive a higher subsequent quote.

v134 fixed the regression by disabling all same-item native/advanced partial splits, but its 49-row scout was exactly equal to v121 on every row. That guard was therefore safe but too broad and likely removed v133's useful activations.

## Hypothesis

Keep v133's 24-turn Town Center hold by default, but restore v121-style immediate advancement only for the narrowly observed dangerous split shape:

1. the item is `MILK`;
2. the native action is already selling `MILK` on this turn;
3. adding one more MILK sale would cross an actual one-dollar market quote boundary (`next_quote < current_quote`).

This should remove the known `bl_v21 / 382002` opponent-price externality without applying v134's blanket same-item exemption.

The rule is intentionally not generalized to other items yet. Earlier exploratory quote-only rules in the v115 lineage produced regressions, so product/generalization should require telemetry evidence.

## Change

One tactical change relative to v133:

- v133 blocks sale advance across the next Town Center tick;
- v135 bypasses that block only for native-sold MILK when the exact one-unit next inventory state lowers the rounded MILK quote.

MILK pricing uses the competition formula used by the official engine:

- base = 160
- initial inventory = 10000
- threshold = 122
- scarcity side = sqrt with target 0.60
- glut side = linear with target 1.60
- rounded with Python `int(round(price))`, floor 1

Focused boundary check:

- inventory 9955 -> quote 218
- inventory 9956 -> quote 218
- inventory 9957 -> quote 217

Thus the known negative-control shape at 9956 has a real one-unit quote discontinuity.

## Static / synthetic checks

`build_v135.py`:

- requires exact v130 SHA256 `7a8e337b5651ba3bf0f805b588ba871ba1ad629f515e47bc4c42494862eacfa8`;
- reconstructs and verifies exact v133 SHA256 `ff7e198954f3d0b1198184966e4ae76a16e0d344ca93cfccb30f99253c54ba65`;
- replaces exactly one v133 block;
- compiles the resulting source;
- synthetic tests cover:
  - MILK 9956 -> 9957 quote 218 -> 217: release the hold;
  - same-item MILK without a quote boundary: keep v133 hold;
  - no native MILK sell: keep v133 hold;
  - EGG: do not generalize the exception;
  - no Town Center crossing: no hold.

The exact candidate SHA and actual syntax/runtime execution remain pending CI because the self-hosted runner has not accepted the job yet.

## Planned formal panel

All comparisons are same-seed with seat swap, candidate vs the same external opponent and v121 vs the same external opponent, then normalized as `candidate_minus_champion`.

Known controls:

- `beat_v48`, seed 381003, 1 pair — v133 positive control
- `bl_v21`, seeds 382001-382006, 6 pairs — includes positive controls 382001/382004 and negative control 382002
- `bl_v16rc2`, seeds 382001-382006, 6 pairs
- `starter`, seeds 382001-382006, 6 pairs

Regression/generalization:

- `dz_more_wheat`, seeds 382101-382106, 6 pairs
- `frontier_prvsiyan`, seeds 382001-382006, 6 pairs
- `farming_v2`, seeds 382001-382006, 6 pairs
- `farming_v2_b`, seeds 382001-382006, 6 pairs
- `first_in_line`, seeds 382001-382006, 6 pairs

Total planned matched rows: **49**.

The workflow aggregates:

- W/L/D
- mean
- SE
- mean - 2SE
- worst regression
- best improvement
- technical status / exceptions

It also traces both seats for:

- `beat_v48 / 381003`
- `bl_v21 / 382001`
- `bl_v21 / 382002`
- `bl_v21 / 382004`

with first divergence, actions, SELL quantities, own/rival cash, market inventory/prices, and late-draw gate state.

## Current execution state

As of the experiment setup, run `36144084808` is **queued** with job `108100737763` and has not started. The earlier v133 positive-telemetry run `36141048570` is also queued. There were no in-progress repository workflow runs when checked, while multiple self-hosted jobs were queued.

This is infrastructure / runner-assignment state, not candidate evidence. Do not classify v135 as pass, fail, PROMOTE, or REJECT until the intended self-hosted evaluation actually runs.

## Runtime

Pending. Final acceptance must use the project standard:

- p99 < 50 ms
- worst < 200 ms
- exceptions = 0

Timing should be checked serially / preflight rather than inferred from parallel panel noise.

## Decision

**KEEP TESTING / PENDING CI. Formal champion remains v121.**

No PROMOTE decision is permitted from the synthetic boundary check alone.

## Next hypothesis / decision tree

1. If v135 fixes `bl_v21 / 382002` while preserving multiple v133 positive controls and introduces no material regression, proceed to fresh/sealed seeds and final runtime/preflight.
2. If v135 still erases most positive controls, inspect whether useful v133 divergences are MILK without an immediate quote boundary, then add a confirmed opponent-exposure/race discriminator rather than broadening to all quote changes.
3. If v135 introduces new losses, use first-divergence telemetry to determine whether the one-unit quote boundary predicts opponent benefit poorly; prefer an observed-confirmation gate before any wider rule.
4. Do not reuse burned sealed seeds from unrelated exploratory lineages as fresh evidence.
