# uploaded 127ed3 CARROT2 feed0 — known/public opponent regression — 2026-09-27

Decision: **PASS — zero outcome regression; continue promotion gates**

## Identity

- Formal champion: `uploaded_127ed3_safety_v3`
- Champion SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `uploaded_127ed3_ca_feed0`
- Candidate SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Formal engine: `kaggle-environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Run

GitHub Actions run: `36295410170`

Artifact: `uploaded-127ed3-ca-feed0-known-regression`, artifact id `10924830836`.

The workflow reconstructs and hash-checks both exact agents, then evaluates both against the same six known/public opponents. Because both candidate and champion are rerun, the job executes 192 games total: 96 candidate seat-games plus 96 champion seat-games.

Opponents:

- `starter`
- `beat_v48`
- `bl_v20`
- `bl_v21`
- `farming_v2`
- `frontier_prvsiyan`

Seed blocks, both seats:

- public burned: `621–624`
- formal known: `641–644`

## Competition-primary outcome result

### Public burned 621–624

- candidate = **48W / 0L / 0D**
- champion = **48W / 0L / 0D**
- outcome regressions = **0**
- outcome improvements = `0`

### Formal-known 641–644

- candidate = **48W / 0L / 0D**
- champion = **48W / 0L / 0D**
- outcome regressions = **0**
- outcome improvements = `0`

### Aggregate

- candidate = **96W / 0L / 0D**
- champion = **96W / 0L / 0D**
- W→L / W→D / D→L regressions = **0 / 96**
- exceptions = `0` by workflow assertions
- each evaluated match = 720 turns by workflow assertions

This passes the precommitted known-opponent outcome gate.

## Margin telemetry

Outcome remained perfect, but margin compression is retained as a concern rather than ignored.

Formal-known mean / worst candidate-minus-champion margin by opponent:

| opponent | mean margin delta | worst margin delta | outcome |
|---|---:|---:|---|
| starter | -8906.5 | -19279 | 8× W→W |
| beat_v48 | -26.25 | -171 | 8× W→W |
| bl_v20 | +13.5 | -39 | 8× W→W |
| bl_v21 | +0.375 | -28 | 8× W→W |
| farming_v2 | -8.5 | -100 | 8× W→W |
| frontier_prvsiyan | -247.5 | -1017 | 8× W→W |

Public-burned margins are much less concerning: every opponent remains 8× W→W; worst margin delta is `0` for five opponents and `-78` for starter.

The large starter-money compression does not change the competition-primary W/L outcome on these known seeds, but it remains a robustness telemetry concern for future stronger opponents. It is not treated as a reason to promote by itself.

## Decision

**PASS this gate.** Do not promote yet. Continue with:

1. direct first-sealed completion verification (run `36295374931`),
2. only if that passes, execute the already-precommitted second sealed block,
3. causal divergence trace,
4. dedicated runtime,
5. final submission preflight,
6. final PROMOTE / KEEP TESTING / REJECT decision.
