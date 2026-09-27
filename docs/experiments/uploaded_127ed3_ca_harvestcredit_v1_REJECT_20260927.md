# uploaded 127ed3 CARROT2 harvest-credit v1 — REJECT — 2026-09-27

Decision: **REJECT**

## Identity

- Formal champion / parent: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate: `uploaded_127ed3_ca_harvestcredit_v1`
- Candidate SHA256: `ea296402b43b2e389e2f9cf8a23e27f92434b5b25212c3095f720840d9a91eb0`
- Engine: `kaggle-environments==1.32.7`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Hypothesis

Keep `_CA_FEED_DAYS=1`, but when current WHEAT stock alone fails the one-day reserve, credit route-scheduled standing WHEAT harvests only if projected stock remains nonnegative at every planned FEED step.

The goal was to retain useful CARROT2 swaps while avoiding `ca_feed0`'s large W->W margin compression versus starter on known seeds642/643.

## Burned dev

Run `36300251792`, artifact `10925369076`, ten burned seeds, both seats.

- W/L/D: `4 / 1 / 5`
- mean: `+25.4`
- median: `0`
- SE: `15.3935`
- mean - 2SE: `-5.3870`
- worst: `-12`
- best: `+147`
- exceptions: `0/0`
- non-DONE: `0`
- all games: 720 turns

Per-seed deltas:

`641:+38, 350003:+147, 101:0, 211:0, 347:-12, 509:0, 733:0, 911:0, 1201:+66, 1601:+15`

On the same ten seeds `ca_feed0` is identical on 9/10 seeds but gives seed641 `+193` instead of `+38`. Thus harvest-credit v1 gives up `155` on the strongest observed gain and does not remove the `-12` regression on seed347.

## Focused starter-margin check

Run `36302238368`, artifact `10925427798`.

Known seeds641-644 only, both seats, comparing parent / feed0 / harvestcredit-v1 against builtin starter. No fresh seeds were consumed.

### feed0 minus parent margin

- seed641: `+7`
- seed642: `-19279`
- seed643: `-16354`
- seed644: `0`
- mean: `-8906.5`
- worst: `-19279`

### harvestcredit-v1 minus parent margin

- seed641: `+7`
- seed642: `-18043`
- seed643: `-15911`
- seed644: `0`
- mean: `-8486.75`
- worst: `-18043`

### harvestcredit-v1 minus feed0 margin

- seed641: `0`
- seed642: `+1236`
- seed643: `+443`
- seed644: `0`

The focused change recovers only a small fraction of the starter margin compression. The large negative margin signal remains, while the burned direct-parent benefit is materially weaker than feed0.

## Decision

**REJECT `uploaded_127ed3_ca_harvestcredit_v1`.**

Reason:

- does not materially solve the motivating starter-margin weakness;
- sacrifices seed641 direct-parent improvement from `+193` to `+38`;
- retains the burned `-12` regression;
- has weaker burned aggregate evidence than feed0.

Do not allocate stress or fresh sealed seeds to this candidate. Keep the result to avoid repeating the same standing-harvest-credit design.

`uploaded_127ed3_ca_feed0` remains the primary promotion candidate pending its corrected formal runtime gate. No Kaggle submission is implied.
