# uploaded 127ed3 CARROT2 feed0 — PROMOTE — 2026-09-27

Decision: **PROMOTE**

## Identity

- Previous formal champion / parent: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- New formal champion: `uploaded_127ed3_ca_feed0`
- New champion SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Reproducer: `ci/build_uploaded_127ed3_ca_feed0.py`
- Formal engine: `kaggle-environments==1.32.7`
- Official Kaggriculture source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Tactical change

Exactly one tactical change from safety-v3:

`_CA_FEED_DAYS = 1 -> 0`

This removes CARROT2's one-day current-shed WHEAT feed-reserve veto while retaining the existing CARROT2 route, edge, cash, rescue, seed, and replacement checks.

## Burned matched evidence

### Dev

Run `36291633075`, 10 distinct seeds, both seats:

- W/L/D = `4 / 1 / 5`
- mean = `+40.9`
- SE = `22.8169`
- mean - 2SE = `-4.7338`
- worst = `-12`
- best = `+193`
- exceptions = `0`

Focal deltas include seed641 `+193` and seed350003 `+147`.

### Stress

Run `36294326359`, seeds621-632, both seats:

- W/L/D = `4 / 2 / 6`
- mean = `+38.1667`
- SE = `25.0940`
- mean - 2SE = `-12.0214`
- worst = `-16`
- best = `+255`
- exceptions = `0`

Combined 22 burned seeds:

- W/L/D = `8 / 3 / 11`
- mean = `+39.4091`
- mean - 2SE = `+5.8578`
- worst = `-16`
- best = `+255`

## Fresh sealed evidence

### First sealed

Original run `36294919199`; direct verifier `36295374931`, artifact `10925024481`.

Precommitted 12 seeds produced pair deltas:

`0,0,0,0,0,0,+118,0,0,+258,-38,0`

- W/L/D = `2 / 1 / 9`
- mean = `+28.1667`
- worst = `-38`
- best = `+258`
- candidate/parent exceptions = `0/0`
- direct verifier reproduced every expected seat delta exactly
- all 24 seat-games = `DONE`, 720 turns

The original workflow conclusion was invalidated only by the known `scripts/eval.py` status serialization bug; direct final-state verification passed.

### Second sealed

Run `36300290715`, artifact `10926040825`.

Precommitted 12 fresh seeds produced pair deltas:

`0,0,+4,+53,0,+211,0,+104,0,0,0,0`

- W/L/D = `4 / 0 / 8`
- mean = `+31.0`
- median = `0`
- SE = `18.7951`
- mean - 2SE = `-6.5903`
- worst = `0`
- best = `+211`
- seat0 mean = `+31.9167`
- seat1 mean = `+30.0833`
- candidate/parent exceptions = `0/0`
- all 24 seat-games = `DONE`, 720 turns

### Aggregate direct-parent evidence

Across 46 distinct burned + sealed seeds:

- W/L/D = **`14 / 4 / 28`**
- mean = **`+34.2826`**
- SE = `10.9944`
- mean - 2SE = **`+12.2938`**
- median = `0`
- worst = **`-38`**
- best = `+258`

The positive aggregate lower bound survives two independently precommitted fresh sealed blocks, and the second block contains no negative pair regression.

## Known/public opponent regression

Run `36295410170`, artifact `10924830836`.

Opponents:

- `starter`
- `beat_v48`
- `bl_v20`
- `bl_v21`
- `farming_v2`
- `frontier_prvsiyan`

Blocks621-624 and641-644, both seats:

- candidate = `96W / 0L / 0D`
- previous champion = `96W / 0L / 0D`
- outcome regressions = **`0 / 96`**

Competition-primary known-opponent gate therefore passes.

### Retained robustness concern

Against builtin starter on formal-known seeds, feed0 compresses winning margin versus safety-v3, notably:

- seed642: `-19279`
- seed643: `-16354`
- four-seed mean margin delta: `-8906.5`

This does not produce an outcome regression in the formal panel, but remains a documented robustness risk.

A narrower `uploaded_127ed3_ca_harvestcredit_v1` was built specifically to repair this signal. Burned dev and a focused starter check showed it recovered only `+1236` on seed642 and `+443` on seed643 relative to feed0 while reducing seed641 direct-parent gain from `+193` to `+38` and retaining the `-12` burned regression. It was formally REJECTED without consuming stress or fresh sealed seeds. See `uploaded_127ed3_ca_harvestcredit_v1_REJECT_20260927.md`.

## Causal explanation

Run `36295996084`, artifact `10924761416`.

The trace compares feed0 with an independently loaded safety-v3 shadow on the **same observation** each turn.

First divergences are the intended reserve-blocked WHEAT-to-CARROT substitutions:

- seed641: step323, final `+193`
- seed350003: step656, final `+147`
- seed629: step500, final `+255`

At the first divergence the shadow parent increments `ca_feed_block` while feed0 performs the extra CARROT replacement. Small negative cases begin from the same mechanism. This directly explains both the improvement and the bounded regressions instead of relying only on activation-count correlation.

## Final runtime

Corrected formal runtime run `36301925723`, artifact `10926810083`: **PASS**.

Exact candidate / engine / source hashes were asserted. Seeds71 and75 were run against builtin starter and exact v147 with the candidate in both seats; every game was required to be `DONE` and 720 turns.

Thresholds:

- p99 `< 50 ms`
- worst turn `< 200 ms`

Measured candidate latency:

### vs starter

- calls: `2876`
- median: **`1.3113 ms`**
- p99: **`8.7067 ms`**
- worst: **`125.6586 ms`**
- PASS

### vs v147

- calls: `2876`
- median: **`1.58785 ms`**
- p99: **`8.4217 ms`**
- worst: **`132.1788 ms`**
- PASS

The earlier run `36295797394` is not performance evidence: it stopped before timing because builtin `starter` was mistakenly treated as a filesystem path. The corrected run above is the formal runtime result.

## Final submission preflight

Run `36295816696`, artifact `10925512998`: **PASS**.

Passed:

1. exact candidate/engine/source reconstruction and SHA assertions;
2. compile/import/static audit with no new risky signature versus parent;
3. Kaggle-compatible last-callable selection;
4. five malformed-observation fallback cases;
5. official-engine 720-turn smoke on seed641 in both seats, `DONE`, errors0;
6. exact submission archive construction and verification.

Submission package:

- members: `['main.py']`
- `main.py` SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- archive SHA256: `db3df5d7fcc3246ba93b6102ee8fdd1dab83f32fc972986780ce0271b46994b0`
- archive bytes: `178987`

## Promotion decision

**PROMOTE `uploaded_127ed3_ca_feed0` to formal champion.**

Promotion basis:

- matched burned improvement is positive in aggregate;
- two precommitted fresh sealed blocks reproduce the improvement;
- 46-seed aggregate mean - 2SE remains positive;
- worst direct-parent pair regression is bounded at `-38`;
- seat-swap evidence is stable;
- known/public-opponent outcome regressions are `0/96`;
- causal telemetry explains the behavioral divergence;
- exceptions / non-DONE / timeout issues are absent in formal gates;
- corrected runtime is comfortably inside thresholds;
- final submission preflight and exact package verification pass.

The documented starter-margin compression remains a follow-up robustness target, but the attempted conservative harvest-credit alternative did not improve the tradeoff enough to displace feed0.

Update `docs/CHAMPION.md` to this candidate. Preserve safety-v3 and uploaded raw parents for rollback/reproducibility.

**No Kaggle submission is implied or performed by this promotion.**
