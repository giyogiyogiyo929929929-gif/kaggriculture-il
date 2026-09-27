# uploaded_127ed3_ca_feed0_d25_carrot_hold_v1 — progress — 2026-09-27

Status: **KEEP TESTING; BURNED DEV PASS; STRESS QUEUED; NOT PROMOTED**

## Identity

- formal champion / parent: `uploaded_127ed3_ca_feed0`
- parent SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- candidate: `uploaded_127ed3_ca_feed0_d25_carrot_hold_v1`
- candidate SHA256: `2aab62a693bd3a357ad87649b8ba90a79b512d383a7694b07bbcdbe0deef48c8`
- builder: `ci/build_uploaded_127ed3_ca_feed0_d25_carrot_hold_v1.py`
- formal engine: `kaggle-environments==1.32.7`
- official source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`

## Single tactical change

At observation step 600 only, remove parent-selected market orders matching `SELL CARROT`. All other actions are unchanged. CARROT remains in shed and parent logic is free to sell it from the next observation onward.

## Burned dev

Run `36311006300`, artifact `10928434749`.

Seeds `[641,350003,101,211,347,509,733,911,1201,1601]`, both seats, candidate directly versus current champion.

Summary:

- W/L/D: `4/0/6`
- mean candidate-minus-champion: `+12.2`
- median: `0`
- SE: `6.2907`
- mean - 2SE: `-0.3815`
- worst: `0`
- best: `+55`
- seat0 mean: `+12.2`
- seat1 mean: `+12.2`
- exact hash / engine / source / syntax gates: PASS
- exceptions: `0`
- all games: `DONE`, 720 turns

Per-seed pair deltas:

- 641: `+55`
- 350003: `+8`
- 101: `0`
- 211: `0`
- 347: `0`
- 509: `0`
- 733: `0`
- 911: `0`
- 1201: `+19`
- 1601: `+40`

The original focal-four subset `[641,350003,733,911]` remains `2W/0L/2D`, mean `+15.75`, worst `0`, best `+55`. Thus the old focal effect transfers from safety-v3 to the current feed0 parent, although seed641's gain compresses from the old +73 to +55.

## Interpretation

This is a narrow, reproducible positive timing effect with no burned-dev regression. It is not yet promotion-quality because the dev block is sparse and `mean - 2SE` is approximately zero.

## Next gate

Burned stress workflow for seeds621-632 both seats was triggered after the dev PASS:

- workflow: `.github/workflows/uploaded-127ed3-ca-feed0-d25-carrot-hold-v1-stress.yml`
- run: `36311427676`

No fresh/sealed seeds are used before reviewing stress. If stress retains a useful positive signal with acceptable worst regression, proceed to a precommitted fresh sealed block and known-opponent regression checks. If stress is neutral/negative or introduces concerning losses, REJECT or refine before any fresh allocation.

Formal champion remains `uploaded_127ed3_ca_feed0`. No Kaggle submission is implied.
