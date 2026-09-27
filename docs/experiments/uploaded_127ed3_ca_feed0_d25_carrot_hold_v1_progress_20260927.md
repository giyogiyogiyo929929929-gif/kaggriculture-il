# uploaded_127ed3_ca_feed0_d25_carrot_hold_v1 — progress — 2026-09-27

Status: **KEEP TESTING; DEV + STRESS PASS; SEALED1 QUEUED; NOT PROMOTED**

## Identity

- formal champion / parent: `uploaded_127ed3_ca_feed0`
- parent SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- candidate: `uploaded_127ed3_ca_feed0_d25_carrot_hold_v1`
- candidate SHA256: `2aab62a693bd3a357ad87649b8ba90a79b512d383a7694b07bbcdbe0deef48c8`
- builder: `ci/build_uploaded_127ed3_ca_feed0_d25_carrot_hold_v1.py`
- formal engine: `kaggle-environments==1.32.7`
- official source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`

## Single tactical change

At observation step 600 only, remove parent-selected market orders matching `SELL CARROT`. All other actions are unchanged. CARROT remains in shed and unchanged parent logic may sell it from the next observation onward.

## Burned dev

Run `36311006300`, artifact `10928434749`.

Seeds `[641,350003,101,211,347,509,733,911,1201,1601]`, both seats, candidate directly versus current champion.

- W/L/D: `4/0/6`
- mean: `+12.2`
- SE: `6.2907`
- mean - 2SE: `-0.3815`
- worst: `0`
- best: `+55`
- seat0 / seat1 mean: `+12.2 / +12.2`
- exceptions `0`; all games `DONE`, 720 turns

Pair deltas: 641 `+55`, 350003 `+8`, 101 `0`, 211 `0`, 347 `0`, 509 `0`, 733 `0`, 911 `0`, 1201 `+19`, 1601 `+40`.

The original focal-four subset `[641,350003,733,911]` remains `2W/0L/2D`, mean `+15.75`, worst `0`, best `+55`.

## Burned stress

Run `36311427676`, artifact `10929013848`.

Seeds621-632, both seats:

- W/L/D: `4/0/8`
- mean: `+4.5833`
- SE: `2.4261`
- mean - 2SE: `-0.2688`
- worst: `0`
- best: `+25`
- seat0 / seat1 mean: `+4.5833 / +4.5833`

Non-zero pair deltas: seed623 `+12`, 628 `+16`, 629 `+25`, 630 `+2`; all others `0`.

## Combined burned evidence

22 distinct seeds across dev + stress:

- W/L/D: `8/0/14`
- mean: `+8.0455`
- SE: `3.1742`
- mean - 2SE: `+1.6970`
- worst: `0`
- best: `+55`

This is a sparse but reproducible positive timing effect with no observed burned regression and a positive combined lower bound.

## Fresh sealed1

Seeds were precommitted before evaluation in `uploaded_127ed3_ca_feed0_d25_carrot_hold_v1_sealed1_precommit_20260927.md`:

`957488,985781,382781,394323,430506,566548,140231,622742,329503,941134,700022,422167`

Seed-list SHA256: `4aafd85f727795aecf289fda662b8f2998b910d839b3bf8e026d102e90cc2cf4`.

Run `36311965589` has been triggered and is currently queued behind another self-hosted job. No sealed result has been inspected yet.

If sealed1 retains a positive/no-regression pattern, proceed to known-opponent regression, runtime/preflight, and promotion-quality review. Formal champion remains `uploaded_127ed3_ca_feed0`. No Kaggle submission is implied.
