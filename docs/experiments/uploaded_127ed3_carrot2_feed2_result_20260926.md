# uploaded 127ed3 CARROT2 feed2 — exact-parent result

## Identity

- parent: safety-v3 SHA256 `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- candidate: exact feed2 child SHA256 `a2e69e32513280051709bfc921104a3574bc87f484e6a0d1c07466a377e8cc26`
- formal champion: v147 SHA256 `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- only tactical change: first/only `_CA_FEED_DAYS = 1` -> `2`
- Actions run: `36243480932`
- artifact: `uploaded-127ed3-ca-feed2-dev-exact-parent`
- burned dev seeds only: `641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`
- both seats; exact engine `kaggle-environments==1.32.7`; exceptions 0

## Attribution result: feed2 - safety-v3

`candidate_minus_parent = feed2 - safety-v3`.

- W/L/D: **2 / 5 / 3**
- mean: **-165.9**
- median: **-23.0**
- SE: **130.7796**
- mean - 2SE: **-427.4592**
- worst: **-1308** (seed 641)
- best: **+126** (seed 350003)
- candidate exceptions: 0
- parent exceptions: 0

Per-seed pair deltas:

| seed | feed2 - safety-v3 |
|---:|---:|
| 641 | -1308 |
| 350003 | +126 |
| 101 | 0 |
| 211 | -142 |
| 347 | +14 |
| 509 | 0 |
| 733 | -53 |
| 911 | 0 |
| 1201 | -46 |
| 1601 | -250 |

## Practical comparison: feed2 - v147

- W/L/D: 7 / 3 / 0
- mean: +588.5
- median: +385
- SE: 387.3876
- mean - 2SE: -186.2752
- worst: -1248
- best: +3395
- exceptions: 0

The child remains stronger than v147 on several burned seeds only because its parent safety-v3 is already substantially stronger there. The attribution comparison is decisively negative, so this is not an improvement over the current candidate.

## Mechanism interpretation

The prior trace showed 23 accepted CARROT2 swaps on seed641 where `wheat_total < feed2`, including 13 through day22. The exact global feed2 result makes seed641 dramatically worse (-1308 vs parent), so the original interpretation “blocking two-day-shortfall swaps preserves useful WHEAT continuity” is falsified for this important loss seed.

The global child also regresses seed733 (-53), but seed733 is not the main failure: seed641 is. Therefore the previously suggested automatic fallback “apply two-day reserve only through day22” is not justified; seed641 itself contains many early two-day-shortfall swaps and is the largest regression.

Do not threshold-tune this feed-horizon family post hoc on these burned seeds without a new mechanism separator.

## Decision

**REJECT feed2.**

- safety-v3 remains the leading candidate.
- do not allocate fresh/sealed seeds to feed2.
- do not create the day<=22 child by default.
- revisit CARROT2 only with new telemetry that explains why preserving WHEAT helps some worlds without suppressing profitable CARROT conversion in seed641-like worlds.
