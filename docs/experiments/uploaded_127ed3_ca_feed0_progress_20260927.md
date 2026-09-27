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

## Burned dev

Run `36291633075`, artifact `10923825327`.

10 distinct seeds, both seats:

- W/L/D = `4 / 1 / 5`
- mean = `+40.9`
- SE = `22.8169`
- mean - 2SE = `-4.7338`
- worst = `-12`
- best = `+193`
- exceptions = `0`

Focal deltas: seed641 `+193`, seed350003 `+147`, seed733 `0`, seed911 `0`.

## Burned stress

Run `36294326359`, artifact `10923721766`.

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

## First fresh sealed

Precommit document: `uploaded_127ed3_ca_feed0_sealed_precommit_20260927.md`.

Run `36294919199`, artifact `10923970552`.

Precommitted seeds:

`446910,885820,619329,999159,438040,240018,833802,418449,899805,893017,955463,986686`

Seed-list SHA256: `7fcdac52798e5bcb00fe13d108c9324de5ab89f7ce909a0d9f17417e005bc456`.

Pair deltas in seed order:

`0, 0, 0, 0, 0, 0, +118, 0, 0, +258, -38, 0`

- W/L/D = `2 / 1 / 9`
- mean = `+28.1667`
- median = `0`
- SE = `23.4216`
- mean - 2SE = `-18.6766`
- worst = `-38`
- best = `+258`
- candidate exceptions = `0`
- parent exceptions = `0`
- all 24 seat-games reached 720 turns

The workflow conclusion was `failure` because `scripts/eval.py` serializes scalar status `"DONE"` as `list("DONE") == ["D","O","N","E"]`; the money/exceptions/full-length evidence itself is valid. A direct final-state verifier is queued as run `36295374931` and must reproduce all 12 expected pair deltas and direct `env.state` DONE statuses before the first sealed gate is considered formally clean.

## Aggregate performance evidence so far

Across 34 distinct seeds (22 burned + 12 first sealed):

- W/L/D = `10 / 4 / 20`
- mean = `+35.4412`
- SE = `13.4645`
- mean - 2SE = `+8.5122`
- worst = `-38`
- best = `+258`

This is positive promotion evidence but is not sufficient alone.

## Known/public opponent gate

Formal current run: `36295410170`.

Opponents:

- `starter`
- `beat_v48`
- `bl_v20`
- `bl_v21`
- `farming_v2`
- `frontier_prvsiyan`

Blocks: burned `621–624` and formal-known `641–644`, both seats.

Historical formal safety-v3 artifact from run `36250594997` confirms safety-v3 was `48W/0L/0D` in each block (96/96 seat-games total) against these opponents. The current feed0 workflow reruns both feed0 and safety-v3, so it executes 192 games total. Promotion gate requires zero outcome regressions relative to safety-v3.

Status at this log creation: **in progress**.

## Causal explanation gate

Queued run `36295996084` records candidate-vs-parent action divergence under the same observation. Current hypothesis is that the one-day CARROT2 feed reserve can over-protect current WHEAT shed while under-crediting near-term standing WHEAT harvest, blocking profitable WHEAT-to-CARROT conversion. The trace must establish the decision chain rather than relying on firing-count correlation.

## Second fresh sealed

Precommit document: `uploaded_127ed3_ca_feed0_sealed2_precommit_20260927.md`.

Fixed seeds:

`323743,992353,766816,468935,311561,814751,325596,507226,602943,874235,479622,296115`

Compact-list SHA256: `da7aeb107fa8dcf4501e196f813aa9ea5ce75059fc4a8d7dd2821d1286cf33b9`.

Dormant workflow: `.github/workflows/uploaded-127ed3-ca-feed0-second-sealed.yml`.

It must not be triggered until both conditions hold:

1. known/public-opponent outcome regression gate passes with zero material regression;
2. first sealed direct completion verifier confirms the status bug and reproduces the expected results.

## Final technical gates

- Dedicated runtime run `36295797394`: queued.
- Final submission preflight run `36295816696`: queued.

Runtime fixes candidate/engine/source hashes and requires p99 `< 50 ms` and worst turn `< 200 ms`. Final preflight checks exact reconstruction, static/import audit, Kaggle loader selection, malformed-observation fallback, both-seat 720-turn smoke, and a `main.py`-only submission archive.

## Promotion decision

**KEEP TESTING.** Do not update `docs/CHAMPION.md` and do not submit to Kaggle until the known-opponent gate, first sealed verifier, second sealed, causal explanation, runtime, and final preflight are all reviewed. Kaggle submission remains a separate user decision after promotion-quality evidence is complete.
