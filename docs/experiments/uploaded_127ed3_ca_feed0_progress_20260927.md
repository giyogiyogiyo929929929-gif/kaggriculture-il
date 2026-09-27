# uploaded 127ed3 CARROT2 feed0 — promotion-gate progress — 2026-09-27

Status: **KEEP TESTING — NOT PROMOTED**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `uploaded_127ed3_ca_feed0`
- Candidate SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Tactical change: `_CA_FEED_DAYS = 1 -> 0` only
- Formal engine: `kaggle-environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Burned evidence

### Burned dev — run `36291633075`

10 distinct seeds, both seats:

- W/L/D = `4 / 1 / 5`
- mean = `+40.9`
- SE = `22.8169`
- mean - 2SE = `-4.7338`
- worst = `-12`
- best = `+193`
- exceptions = `0`

Focal deltas: seed641 `+193`, seed350003 `+147`, seed733 `0`, seed911 `0`.

### Burned stress — run `36294326359`

Seeds `621–632`, both seats:

- W/L/D = `4 / 2 / 6`
- mean = `+38.1667`
- SE = `25.0940`
- mean - 2SE = `-12.0214`
- worst = `-16`
- best = `+255`
- exceptions = `0`

Combined burned 22 distinct seeds:

- W/L/D = `8 / 3 / 11`
- mean = `+39.4091`
- SE = `16.7757`
- mean - 2SE = `+5.8578`
- worst = `-16`
- best = `+255`

## First fresh sealed — PASS after direct verification

Precommitted seeds:

`446910,885820,619329,999159,438040,240018,833802,418449,899805,893017,955463,986686`

Seed-list SHA256: `7fcdac52798e5bcb00fe13d108c9324de5ab89f7ce909a0d9f17417e005bc456`.

Original run `36294919199` produced pair deltas:

`0,0,0,0,0,0,+118,0,0,+258,-38,0`

- W/L/D = `2 / 1 / 9`
- mean = `+28.1667`
- SE = `23.4216`
- mean - 2SE = `-18.6766`
- worst = `-38`
- best = `+258`
- exceptions = `0`

Its workflow failure was caused by the known scalar-status serialization bug.

Direct verifier run `36295374931`, artifact `10925024481`, then reproduced **every expected seat delta exactly** and confirmed:

- candidate exceptions = `0`
- parent exceptions = `0`
- non-DONE = `0`
- every seat-game = `720` turns
- every direct `env.state` status = `DONE`

Therefore the first sealed gate is formally **PASS**. See `uploaded_127ed3_ca_feed0_sealed_VERIFY_20260927.md`.

## Aggregate direct-parent evidence through first sealed

Across 34 distinct seeds (22 burned + 12 first sealed):

- W/L/D = `10 / 4 / 20`
- mean = `+35.4412`
- SE = `13.4645`
- mean - 2SE = `+8.5122`
- worst = `-38`
- best = `+258`

This is positive evidence but is not sufficient by itself for promotion.

## Known/public opponent gate — PASS with margin concern

Run `36295410170`, artifact `10924830836`.

Opponents: `starter`, `beat_v48`, `bl_v20`, `bl_v21`, `farming_v2`, `frontier_prvsiyan`.

Blocks: `621–624` and `641–644`, both seats.

- candidate = `96W / 0L / 0D`
- champion = `96W / 0L / 0D`
- outcome regressions = **0 / 96**

Competition-primary gate therefore passes. However formal-known starter margins compress sharply: mean `-8906.5`, worst `-19279` candidate-minus-champion. This is retained as a robustness concern rather than ignored. See `uploaded_127ed3_ca_feed0_known_regression_20260927.md`.

## Causal explanation gate — PASS

Run `36295996084`, artifact `10924761416` completed successfully with zero exceptions and full 720-turn DONE games.

The workflow evaluates feed0 and an independently loaded safety-v3 shadow on the **same observation**. The first behavioral divergences are the intended reserve-blocked WHEAT-to-CARROT substitutions:

- seed641: step323, final `+193`;
- seed350003: step656, final `+147`;
- seed629: step500, final `+255`;
- small negative cases 347/625/628 also start from the same extra CARROT substitution.

At first divergence the shadow parent has incremented `ca_feed_block` while feed0 performs the additional swap. This supports the intended causal mechanism, while also showing that unconditional reserve removal can create both gains and small losses. See `uploaded_127ed3_ca_feed0_divergence_trace_20260927.md`.

## Second fresh sealed — RELEASED / QUEUED

Precommitted seeds:

`323743,992353,766816,468935,311561,814751,325596,507226,602943,874235,479622,296115`

Seed-list SHA256: `da7aeb107fa8dcf4501e196f813aa9ea5ce75059fc4a8d7dd2821d1286cf33b9`.

Both release prerequisites are now PASS:

1. known/public-opponent zero outcome regression;
2. first sealed direct completion verification.

Trigger commit: `fd50d0707ff2c5b2b50f0d01f5644956ae7ff2c2`.

Run: `36300290715` — queued.

## Final technical gates

- Runtime run `36295797394`: queued.
- Final preflight run `36295816696`: queued.

Runtime requires p99 `< 50 ms` and worst turn `< 200 ms`; preflight checks exact reconstruction, static/import audit, Kaggle loader, malformed observations, both-seat 720-turn smoke, and `main.py`-only archive.

The self-hosted runner is currently occupied by unrelated run `36300134144` on another branch, so these feed0 jobs are waiting rather than failing.

## Narrower follow-up candidate

Because feed0 has large W→W margin compression against starter, `uploaded_127ed3_ca_harvestcredit_v1` is being screened separately on burned dev only. It retains `_CA_FEED_DAYS=1` and relaxes the reserve only when route-scheduled near-term WHEAT harvests keep feed inventory solvent.

Corrected candidate SHA256: `ea296402b43b2e389e2f9cf8a23e27f92434b5b25212c3095f720840d9a91eb0`.

Corrected burned-dev run `36300251792` is queued. No stress/sealed seeds are consumed for this candidate unless burned dev justifies continuation.

## Promotion decision

**KEEP TESTING.** Do not update `docs/CHAMPION.md` and do not submit to Kaggle until second sealed, runtime, and final preflight are reviewed. `harvestcredit_v1` is a separate challenger and does not change the formal champion or feed0 gate status.
