# uploaded 127ed3 CARROT2 feed0 — burned stress — 2026-09-27

Decision: **KEEP TESTING — advance to precommitted fresh sealed**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `uploaded_127ed3_ca_feed0`
- Candidate SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Formal engine: `kaggle-environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Burned stress

Actions run: `36294326359`

Artifact: `uploaded-127ed3-ca-feed0-stress`, artifact id `10923721766`.

Seeds `621–632`, both seats:

- W/L/D = **4 / 2 / 6**
- mean = **+38.1667**
- median = `0`
- SE = `25.0940`
- mean - 2SE = `-12.0214`
- worst = **-16**
- best = **+255**
- seat0 mean = `+38.1667`
- seat1 mean = `+38.1667`
- candidate exceptions = `0`
- parent exceptions = `0`

Per seed:

| seed | candidate - parent |
|---:|---:|
| 621 | 0 |
| 622 | 0 |
| 623 | +15 |
| 624 | 0 |
| 625 | -4 |
| 626 | 0 |
| 627 | 0 |
| 628 | -16 |
| 629 | +255 |
| 630 | +22 |
| 631 | 0 |
| 632 | +186 |

Both seat deltas were identical for every seed.

## Harness note

The workflow conclusion is `failure` only because the status checker still iterated scalar `"DONE"` as characters, yielding `non_done=24`. Build/hash/static checks passed, exceptions are zero, and the evaluation produced full final-money results. Future workflows normalize scalar status before checking.

## Combined burned evidence

Combining this pre-existing burned stress block with the earlier burned dev 10-seed block gives 22 distinct burned seeds:

- W/L/D = **8 / 3 / 11**
- mean = **+39.4091**
- SE = **16.7757**
- mean - 2SE = **+5.8578**
- worst = **-16**
- best = **+255**

The positive effect is not confined to the original focal losses: positive deltas appear on 641, 350003, 1201, 1601, 623, 629, 630, and 632. Negative deltas remain small (`-12`, `-4`, `-16`).

## Interpretation

Stress alone is positive but not individually 2SE-significant. The combined 22-seed burned evidence crosses zero on mean-2SE while preserving a very small worst regression and exact seat symmetry. This is sufficient to consume the already-precommitted fresh sealed set, but not sufficient to promote.

## Next gate

Use only the fresh seeds precommitted before this stress result in `docs/experiments/uploaded_127ed3_ca_feed0_sealed_precommit_20260927.md`. Promotion remains forbidden until sealed, known-opponent regression, runtime, telemetry explanation, and final preflight pass.
