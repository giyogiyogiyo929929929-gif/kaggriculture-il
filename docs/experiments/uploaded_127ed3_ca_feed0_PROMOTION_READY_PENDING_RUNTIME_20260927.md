# uploaded 127ed3 CARROT2 feed0 — promotion-ready pending runtime — 2026-09-27

Status: **PROMOTION-READY EXCEPT CORRECTED FORMAL RUNTIME — NOT YET PROMOTED**

## Identity

- Formal champion / parent: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `uploaded_127ed3_ca_feed0`
- Candidate SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Builder: `ci/build_uploaded_127ed3_ca_feed0.py`
- Tactical change: `_CA_FEED_DAYS = 1 -> 0` only
- Engine: `kaggle-environments==1.32.7`
- Official Kaggriculture source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Direct-parent matched evidence

### Burned dev

Run `36291633075`, 10 distinct seeds, both seats:

- W/L/D: `4 / 1 / 5`
- mean: `+40.9`
- mean - 2SE: `-4.7338`
- worst: `-12`
- best: `+193`
- exceptions: `0`

### Burned stress

Run `36294326359`, seeds621-632, both seats:

- W/L/D: `4 / 2 / 6`
- mean: `+38.1667`
- mean - 2SE: `-12.0214`
- worst: `-16`
- best: `+255`
- exceptions: `0`

Combined 22 burned seeds:

- W/L/D: `8 / 3 / 11`
- mean: `+39.4091`
- mean - 2SE: `+5.8578`
- worst: `-16`
- best: `+255`

### First fresh sealed

Run `36294919199`, direct verifier `36295374931`.

Precommitted 12 seeds, exact pair deltas:

`0,0,0,0,0,0,+118,0,0,+258,-38,0`

- W/L/D: `2 / 1 / 9`
- mean: `+28.1667`
- worst: `-38`
- best: `+258`
- candidate/parent exceptions: `0/0`
- direct verifier reproduced every expected seat delta
- all 24 seat-games: `DONE`, 720 turns

### Second fresh sealed

Run `36300290715`, artifact `10926040825`.

Precommitted 12 seeds, pair deltas:

`0,0,+4,+53,0,+211,0,+104,0,0,0,0`

- W/L/D: `4 / 0 / 8`
- mean: `+31.0`
- worst: `0`
- best: `+211`
- candidate/parent exceptions: `0/0`
- all 24 seat-games: `DONE`, 720 turns

### Aggregate through two sealed blocks

46 distinct seeds total:

- W/L/D: **`14 / 4 / 28`**
- mean: **`+34.2826`**
- SE: `10.9944`
- mean - 2SE: **`+12.2938`**
- median: `0`
- worst: **`-38`**
- best: `+258`

## Known/public opponent regression

Run `36295410170`, artifact `10924830836`.

Opponents:

- starter
- beat_v48
- bl_v20
- bl_v21
- farming_v2
- frontier_prvsiyan

Blocks621-624 and641-644, both seats:

- candidate: `96W / 0L / 0D`
- champion: `96W / 0L / 0D`
- outcome regressions: **`0 / 96`**

Competition-primary outcome gate passes.

Robustness concern retained explicitly: against builtin starter on formal-known seeds, feed0 compresses winning margins versus parent, especially seed642 `-19279` and seed643 `-16354`; four-seed mean margin delta `-8906.5`. A narrower standing-harvest-credit attempt was tested and rejected because it repaired only a small fraction of this margin signal while sacrificing direct-parent gains. See `uploaded_127ed3_ca_harvestcredit_v1_REJECT_20260927.md`.

## Causal telemetry

Run `36295996084`, artifact `10924761416`.

Same-observation candidate versus independently loaded parent shadow established that the first divergences are the intended CARROT2 feed-reserve decisions:

- seed641: step323, final `+193`
- seed350003: step656, final `+147`
- seed629: step500, final `+255`

The parent increments `ca_feed_block` while feed0 performs the additional WHEAT-to-CARROT substitution. Small negative seeds start from the same mechanism, explaining both benefit and bounded regression.

## Final submission preflight

Run `36295816696`, artifact `10925512998`: **PASS**.

Passed:

- exact candidate/engine/source reconstruction and SHA assertions;
- compile/import/static audit with no new risky signature;
- Kaggle-compatible last-callable selection;
- five malformed-observation fallback cases;
- official-engine seed641 full 720-turn smoke, both seats, `DONE`, errors0;
- exact submission archive verification.

Package:

- members: `['main.py']`
- main SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- archive SHA256: `db3df5d7fcc3246ba93b6102ee8fdd1dab83f32fc972986780ce0271b46994b0`
- archive bytes: `178987`

## Runtime gate

Original run `36295797394` is **INVALID AS PERFORMANCE EVIDENCE**: it attempted to load builtin `starter` as a file path and stopped with `FileNotFoundError` before timing data existed.

Corrected formal self-hosted runtime:

- run `36301925723`
- candidate both seats
- seeds71,75
- opponents builtin starter and exact v147
- requires all games `DONE`, 720 turns
- thresholds p99 `< 50 ms`, worst turn `< 200 ms`

Status at this record creation: **queued behind unrelated self-hosted evaluation**.

A supplementary `windows-latest` screen (`36302903003`) failed before any workflow steps were allocated and is not candidate evidence.

## Current decision

**DO NOT PROMOTE YET.** All substantive performance, sealed, regression, causal, exception, completion, and package gates are clean enough for promotion; the only unresolved formal gate is valid corrected runtime timing.

If corrected run `36301925723` passes the predefined timing thresholds with full DONE/720 completion, promote `uploaded_127ed3_ca_feed0`, update `docs/CHAMPION.md`, and create the final PROMOTE record. Kaggle submission remains a separate user decision and is not implied by promotion.
