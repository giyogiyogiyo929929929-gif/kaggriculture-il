# uploaded 127ed3 day25 hour0 CARROT hold — focal screen — 2026-09-27

Decision: **KEEP TESTING — expand to burned dev block**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `uploaded_127ed3_day25_carrot_hold`
- Candidate SHA256: `96bc8be3cd0159c6c3536ee28a6dd19769cb1b0015c1861c6bf0f1841c283459`
- Formal engine: `kaggle-environments==1.32.7`
- Official source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Hypothesis

The two focal v147-relative loss seeds both begin day 25 with a CARROT inventory that safety-v3 sells immediately from observation step 600 while v147 carries the same inventory one turn longer. Test only that timing decision without changing production or any other sale layer.

## Change

Outer wrapper removes only `SELL CARROT` market orders returned by the parent when `observation.step == 600`. All other orders/actions are unchanged; retained CARROT returns to the unmodified parent policy on the next observation.

## Evaluation

Actions run: `36293715077`

Artifact: `uploaded-127ed3-day25-carrot-hold-focal`, artifact id `10923068102`.

Burned focal seeds, both seats: `641, 350003, 733, 911`.

- W/L/D = **2 / 0 / 2**
- mean = **+20.25**
- median = `+4`
- SE = `17.6842`
- mean - 2SE = `-15.1183`
- worst = **0**
- best = **+73**
- seat0 mean = `+20.25`
- seat1 mean = `+20.25`
- candidate exceptions = `0`
- parent exceptions = `0`
- all games = 720 turns

Seed deltas:

| seed | candidate - parent |
|---:|---:|
| 641 | **+73** |
| 350003 | **+8** |
| 733 | 0 |
| 911 | 0 |

Both seat deltas were identical for every seed.

## Interpretation

The immediate one-turn CARROT sale price comparison alone suggested that selling early was locally favorable, but the full replay shows a positive final-money effect after downstream policy/market interactions. Therefore the timing intervention cannot be rejected from local price arithmetic alone.

The screen is too small for promotion and `mean - 2SE` remains below zero. Expand to the same burned 10-seed direct-parent block before any stress or fresh seed is consumed.
