# uploaded 127ed3 CARROT2 trace — 2026-09-26

## Context

- parent tactical source SHA256: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- evaluated robust parent: safety-v3 SHA256 `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- champion: v147 SHA256 `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- formal engine: `kaggle-environments==1.32.7`
- trace Actions run: `36239755063`
- artifact: `uploaded-127ed3-carrot2-trace`, artifact id `10906055140`
- trace itself changes telemetry only; recorded games reproduce the known safety-v3 final deltas.

## Contrast seeds

Both candidate seats produced the same final delta and the same accepted-swap sequence.

| seed | safety-v3 minus v147 | accepted CARROT2 swaps |
|---:|---:|---:|
| 641 | -406 | 46 |
| 350003 | -520 | 29 |
| 733 | +3428 | 22 |
| 911 | +1178 | 0 |

This confirms the CARROT2 layer is active on the two losses and on one large win, so simply disabling CARROT2 is not supported.

## Feed-horizon separation

The current source uses `_CA_FEED_DAYS = 1`. Every accepted swap in the trace had enough WHEAT for the one-day planned FEED horizon, as expected from the existing guard.

Count of accepted swaps where current total WHEAT was already below planned two-day FEED demand:

| seed | swap count with `wheat_total < feed2` | decision turns |
|---:|---:|---:|
| 641 | 23 | 17 |
| 350003 | 8 | 5 |
| 733 | 4 | 3 |
| 911 | 0 | 0 |

Thus the two loss seeds contain 31 such swaps across 22 decision turns, versus only 4 swaps across 3 turns in the two win seeds.

Three-day demand is less discriminative: 641 has 37 shortfall swaps, 350003 16, 733 14, 911 0.

## Time localization

For `wheat_total < feed2` and day <= 22:

- seed641: 13 accepted swaps
- seed350003: 1
- seed733: 0
- seed911: 0

At day23 and later, seed733 also has four two-day-shortfall swaps, so a global two-day reserve can plausibly damage part of the successful seed733 path. If the global experiment regresses because of this, the next narrower hypothesis is a two-day reserve only through day22; do not jump directly to it without the global ablation result.

## Why this differs from the rejected margin experiment

The rejected early-margin candidate tightened the immediate CARROT-vs-WHEAT value expression and produced 0W/4L/6D versus the parent. The trace shows feed-horizon shortfall is a different state variable: many problematic-looking seed641 swaps have strongly positive immediate value edge while WHEAT is already below the next two days of planned FEED demand. Therefore a feed-reserve guard tests future production continuity rather than re-testing immediate market margin.

## Candidate feed2

Single tactical change:

`_CA_FEED_DAYS = 1` -> `_CA_FEED_DAYS = 2`

Safety wrapper is unchanged.

- candidate SHA256: `01440baf73114416663588be2a9f44b2873cf77acbf65aaff57791fcb8383fdd`
- local syntax / py_compile: PASS
- workflow: `.github/workflows/uploaded-127ed3-ca-feed2-dev.yml`
- evaluation uses only the already-burned ten dev seeds; no sealed seed is used for this hypothesis.
- comparisons: feed2 vs safety-v3 parent for attribution, then feed2 vs v147 for practical effect.

## Decision

Trace result: **mechanism hypothesis strengthened, no tactical promotion yet**.

The surviving formal candidate remains safety-v3 until the feed2 candidate demonstrates a reproducible improvement. The main safety-v3 sealed block remains independent of this experiment.
