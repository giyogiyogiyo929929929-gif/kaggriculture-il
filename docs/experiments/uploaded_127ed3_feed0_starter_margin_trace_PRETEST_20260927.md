# uploaded 127ed3 feed0 — starter margin trace pretest — 2026-09-27

Status: **DIAGNOSTIC QUEUED — FORMAL CHAMPION UNCHANGED**

## Current formal champion

- `uploaded_127ed3_ca_feed0`
- SHA256 `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Previous champion/control: `uploaded_127ed3_safety_v3`
- Previous SHA256 `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`

## Problem

Feed0 passed the formal known-opponent outcome gate with zero regressions, but versus builtin `starter` its winning margin compresses sharply on known seeds:

- seed642: `feed0 - safety_v3 = -19279`
- seed643: `feed0 - safety_v3 = -16354`
- seed641 is a useful positive/control case.

Because the competition is decided by win/loss rather than margin magnitude, this did not block promotion. It remains the clearest robustness weakness for the new champion and could matter against a stronger opponent that converts the same resource loss into an outcome flip.

## Diagnostic hypothesis

The large starter margin loss is downstream of one or a small number of CARROT2 WHEAT-to-CARROT substitutions enabled by `_CA_FEED_DAYS=0`, but the harmful pathway is more contextual than the rejected generic standing-harvest-credit fix.

Potential separators to inspect rather than assume:

- first same-observation feed0/safety-v3 action divergence;
- day of divergence and cash trajectory afterward;
- WHEAT/CARROT plot composition at divergence;
- market state at divergence;
- item-level SELL gross / BUY cost / net revenue after divergence;
- final CARROT2 report counts;
- seat symmetry.

## Evaluation

Workflow: `.github/workflows/uploaded-127ed3-feed0-starter-margin-trace.yml`

Run: `36303683760`

Known/burned seeds only:

- 641 positive control
- 642 large margin-loss case
- 643 large margin-loss case

For each seed and both seats:

1. run exact feed0 vs builtin starter;
2. run exact safety-v3 vs builtin starter;
3. in each actual run, call the other version as a state-isolated shadow on the same observation;
4. record up to 40 action divergences, including the first divergence snapshot and `_CA_REPORT` state;
5. record candidate-side daily cash and crop counts;
6. instrument exact engine market commits and aggregate per-item SELL gross, BUY cost and net revenue;
7. verify `DONE`, 720 turns, and zero actual/shadow exceptions.

No fresh sealed seeds are consumed. This diagnostic does not change the champion.

## Decision rule

Do not create a tactical candidate until the trace identifies a concrete separator shared by 642/643 but absent or materially different in positive control 641. Do not reuse the rejected generic `harvestcredit_v1` design.
