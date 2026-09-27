# uploaded 127ed3 CARROT2 feed0 — burned dev — 2026-09-27

Decision: **KEEP TESTING — advance to burned stress**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `uploaded_127ed3_ca_feed0`
- Candidate SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Formal engine: `kaggle-environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Hypothesis

CARROT2's one-day WHEAT feed reserve may be overprotective. Focal seed 641 had substantial CARROT2 feed blocking, while prior changes that increased the reserve or globally suppressed swaps were clearly harmful. Test the opposite single change.

## Change

Single tactical change only:

```python
_CA_FEED_DAYS = 1
```

became

```python
_CA_FEED_DAYS = 0
```

No other tactical change.

## Burned dev evaluation

GitHub Actions run: `36291633075`

Artifact: `uploaded-127ed3-ca-feed0-dev`, artifact id `10923825327`.

Seeds, both seats:

`641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`

Results:

- W/L/D = **4 / 1 / 5**
- mean = **+40.9**
- median = `0`
- SE = `22.8169`
- mean - 2SE = **-4.7338**
- worst = **-12**
- best = **+193**
- seat0 mean = `+40.9`
- seat1 mean = `+40.9`
- candidate exceptions = `0`
- parent exceptions = `0`

Seed deltas:

| seed | feed0 - parent |
|---:|---:|
| 641 | **+193** |
| 350003 | **+147** |
| 101 | 0 |
| 211 | 0 |
| 347 | -12 |
| 509 | 0 |
| 733 | 0 |
| 911 | 0 |
| 1201 | +66 |
| 1601 | +15 |

Both seat deltas were identical for every seed.

## Interpretation

This is the first CARROT2 follow-up in the current sequence with a positive direct-parent block and very small worst regression. It improves both focal v147-relative loss seeds while leaving the two focal win seeds unchanged.

The block is not yet promotion-quality because `mean - 2SE` remains slightly below zero and only ten burned seeds were used. Therefore no sealed seed is consumed yet.

## Decision

**KEEP TESTING.** Advance to the pre-existing burned stress block `621–632`, both seats. If the stress result is not robustly positive, stop and reject rather than consume fresh sealed seeds.
