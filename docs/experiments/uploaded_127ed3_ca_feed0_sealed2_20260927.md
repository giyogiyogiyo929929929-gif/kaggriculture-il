# uploaded 127ed3 CARROT2 feed0 — second fresh sealed — 2026-09-27

Decision: **PASS — continue final technical gates**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `uploaded_127ed3_ca_feed0`
- Candidate SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Tactical change: `_CA_FEED_DAYS = 1 -> 0` only
- Formal engine: `kaggle-environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Precommit

The fixed fresh seed set was precommitted before execution in `uploaded_127ed3_ca_feed0_sealed2_precommit_20260927.md`:

`323743,992353,766816,468935,311561,814751,325596,507226,602943,874235,479622,296115`

Compact-list SHA256:

`da7aeb107fa8dcf4501e196f813aa9ea5ce75059fc4a8d7dd2821d1286cf33b9`

Execution was released only after both prerequisites passed:

1. known/public-opponent outcome regression = 0;
2. first sealed direct verifier reproduced exact money and direct `DONE`/720-turn completion.

## Run

- GitHub Actions run: `36300290715`
- Artifact: `uploaded-127ed3-ca-feed0-second-sealed`
- Artifact id: `10926040825`

## Results

Per-seed pair-mean deltas in precommitted order:

`0, 0, +4, +53, 0, +211, 0, +104, 0, 0, 0, 0`

- W/L/D = **4 / 0 / 8**
- mean = **+31.0**
- median = `0`
- SE = `18.7951`
- mean - 2SE = `-6.5903`
- worst = **0**
- best = **+211**
- seat0 mean = `+31.9167`
- seat1 mean = `+30.0833`
- candidate exceptions = `0`
- parent exceptions = `0`
- non-DONE = `0`
- every seat-game = `720` turns

Seed `296115` had seat deltas `+11/-11`, yielding pair mean `0`; all other nonzero pair improvements were seat-symmetric.

## Aggregate through two sealed blocks

Combining burned dev/stress + first sealed + this second sealed gives 46 distinct seeds:

- W/L/D = **14 / 4 / 28**
- mean = **+34.2826**
- SE = **10.9944**
- mean - 2SE = **+12.2938**
- median = `0`
- worst = **-38**
- best = **+258**

The second fresh block adds no negative pair regression and strengthens the aggregate lower bound. This is strong direct-parent promotion evidence, but promotion remains blocked until final runtime and final submission preflight pass. Known-opponent outcome regression already passed 0/96; causal divergence trace also passed.

## Decision

**PASS second sealed. KEEP TESTING only for final technical gates.** Do not update `docs/CHAMPION.md` until runtime and final preflight are clean. No Kaggle submission is implied.
