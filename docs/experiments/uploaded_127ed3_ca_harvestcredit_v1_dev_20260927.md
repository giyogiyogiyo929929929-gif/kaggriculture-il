# uploaded 127ed3 CARROT2 harvest-credit v1 — burned dev — 2026-09-27

Status: **KEEP ONLY FOR FOCUSED MARGIN CHECK; NOT READY FOR STRESS/SEALED**

## Identity

- Parent/formal champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `uploaded_127ed3_ca_harvestcredit_v1`
- Candidate SHA256: `ea296402b43b2e389e2f9cf8a23e27f92434b5b25212c3095f720840d9a91eb0`
- Engine: `kaggle-environments==1.32.7`
- Run: `36300251792`
- Artifact id: `10925369076`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Hypothesis

Retain `_CA_FEED_DAYS=1`, but when current WHEAT stock alone is insufficient, credit route-scheduled near-term standing WHEAT harvests if feed solvency remains nonnegative at every planned FEED step.

This was intended to recover useful CARROT2 swaps without the unconditional reserve removal used by `ca_feed0`.

## Burned dev

Seeds, both seats:

`641,350003,101,211,347,509,733,911,1201,1601`

Results:

- W/L/D = **4 / 1 / 5**
- mean = **+25.4**
- median = `0`
- SE = `15.3935`
- mean - 2SE = **-5.3870**
- worst = **-12**
- best = **+147**
- seat0 mean = `+25.4`
- seat1 mean = `+25.4`
- candidate exceptions = `0`
- parent exceptions = `0`
- non-DONE = `0`
- all seat-games = 720 turns

Per-seed pair deltas:

- 641: `+38`
- 350003: `+147`
- 101: `0`
- 211: `0`
- 347: `-12`
- 509: `0`
- 733: `0`
- 911: `0`
- 1201: `+66`
- 1601: `+15`

Harvest-credit telemetry fired on 641/350003/211/347/1201/1601 and was seat-symmetric.

## Comparison with feed0 on the same burned-dev seeds

`ca_feed0` had pair deltas:

`+193,+147,0,0,-12,0,0,0,+66,+15`

Thus harvest-credit v1 is identical to feed0 on 9/10 seeds, but seed641 drops from `+193` to `+38`. It does **not** remove the known `-12` regression on seed347.

Therefore v1 currently fails to dominate feed0: it sacrifices `155` of the strongest observed gain without reducing the small burned regression.

## Next focused check

Because v1 was specifically motivated by feed0's large W->W margin compression versus `starter` on known seeds642/643, run a focused non-fresh comparison on known seeds641-644 only:

- parent vs starter
- feed0 vs starter
- harvestcredit_v1 vs starter
- both seats

Workflow: `.github/workflows/uploaded-127ed3-ca-harvestcredit-v1-starter-focused.yml`

Do not consume stress or sealed seeds for v1 unless this focused check materially repairs the starter-margin weakness.

## Current decision

**KEEP ONLY FOR FOCUSED MARGIN CHECK.** If starter 642/643 margin compression is not materially repaired, REJECT v1 and retain feed0 as the primary promotion candidate. No Kaggle submission is implied.
