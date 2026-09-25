# EXP-20260926 v133 positive telemetry -> v135 rationale

Status: **ANALYSIS COMPLETE / v135 FORMAL EVAL STILL PENDING**

## Identity

- Formal champion: `v121_champion_same_turn_unwind.py`
- Formal-lineage candidate under test: `v135_candidate_milk_quote_boundary.py`
- v133 positive telemetry workflow: `.github/workflows/v133-positive-telemetry-selfhosted.yml`
- v133 telemetry run: `36141048570`
- job: `108090692760`
- result: `success`
- engine: `kaggle_environments==1.32.7`
- artifact id: `10875528152`
- artifact: `v133-positive-telemetry-selfhosted`
- difference convention: `candidate_minus_champion = candidate - champion`

`v66` is not used.

## Cases

Five inherited v133 positive controls were traced in both seats:

- `beat_v48 / 381003`
- `bl_v16rc2 / 382001`
- `bl_v21 / 382001`
- `bl_v21 / 382004`
- `starter / 382001`

The result is seat-symmetric for every case.

| opponent / seed | seat 0 margin delta | seat 1 margin delta | first divergence |
|---|---:|---:|---|
| beat_v48 / 381003 | +3 | +3 | step 600 |
| bl_v16rc2 / 382001 | +5 | +5 | step 600 |
| bl_v21 / 382001 | +75 | +75 | step 600 |
| bl_v21 / 382004 | +10 | +10 | step 600 |
| starter / 382001 | +4 | +4 | step 600 |

## Common first-divergence shape

All ten traces have the same product-level first divergence at step 600:

- v121: `SELL STRAWBERRY 2`
- v133: `SELL STRAWBERRY 1`

This differs from the inherited known v133 regression `bl_v21 / 382002`, whose first important divergence was:

- v121: `SELL MILK 2`
- v133: `SELL MILK 1`
- terminal relative regression: `-2`

Therefore the observed positive and negative controls separate cleanly by product in the current evidence: positives are STRAWBERRY deferrals; the known negative is a MILK deferral.

## Deferred-unit recovery

The one STRAWBERRY unit withheld at step 600 is not abandoned. In all positive controls v133 sells one extra STRAWBERRY later, restoring cumulative target STRAWBERRY SELL quantity to v121:

| opponent / seed | step 600 quote | recovery step | recovery-step quote |
|---|---:|---:|---:|
| beat_v48 / 381003 | 191 | 603 | 193 |
| bl_v16rc2 / 382001 | 252 | 610 | 255 |
| bl_v21 / 382001 | 12 | 610 | 22 |
| bl_v21 / 382004 | 190 | 610 | 188 |
| starter / 382001 | 240 | 610 | 243 |

The effect is not reducible to delayed sale at a higher direct quote. `bl_v21 / 382004` improves by +10 despite the deferred unit's observed quote moving from 190 to 188. Town consumption, market-inventory path, and opponent price externality must therefore be included in the causal interpretation.

For `bl_v21 / 382001`, terminal cash decomposition is especially informative:

- target own cash delta: `-37`
- rival cash delta: `-112`
- relative margin delta: `+75`

So own gross/cash improvement alone is not a valid selector; opponent market exposure is material.

For the other four positive controls, rival terminal cash is unchanged and target own cash improves by the reported margin delta.

## Implication for v135

v134's blanket same-item no-split rule erased both the known MILK regression and all v133 improvements. The telemetry above supports a narrower exception instead:

- retain v133 Town-Center hold for STRAWBERRY and all other unproven product paths;
- release the hold only for the known dangerous MILK same-turn split when one additional MILK unit crosses an actual rounded quote boundary.

That is exactly the scope of v135. It should preserve all currently traced positive STRAWBERRY activations while removing the known MILK price-boundary regression if the hypothesis is correct.

This is mechanistic support, not PROMOTE evidence. Formal champion remains v121 until v135 completes matched-seat evaluation, fresh/sealed regression checks, and runtime/preflight.

## Runner state at analysis time

After the user restarted self-hosted runner `CIYOI`, run `36141048570` executed successfully, proving the runner connection is working. The formal v135 focused run `36144084808` remained queued because the same single self-hosted runner was subsequently occupied by other pre-existing exploratory workflows. This is infrastructure scheduling state, not candidate evidence.
