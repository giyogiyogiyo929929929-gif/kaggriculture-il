# uploaded 127ed3 CARROT2 feed0 — first sealed direct verification — 2026-09-27

Decision: **PASS — prior sealed money evidence is valid; status failure was harness-only**

## Identity

- Candidate: `uploaded_127ed3_ca_feed0`
- Candidate SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- First sealed precommit SHA256: `7fcdac52798e5bcb00fe13d108c9324de5ab89f7ce909a0d9f17417e005bc456`

## Direct verifier

- Run: `36295374931`
- Artifact: `uploaded-127ed3-ca-feed0-sealed-verify`, id `10925024481`
- Workflow conclusion: **success**
- Candidate exceptions: `0`
- Parent exceptions: `0`
- non-DONE games: `0`
- every seat-game: exactly `720` turns
- every direct final-state status: `DONE`

Precommitted seeds:

`446910,885820,619329,999159,438040,240018,833802,418449,899805,893017,955463,986686`

Direct reproduced seat deltas, both seats identical:

`0, 0, 0, 0, 0, 0, +118, 0, 0, +258, -38, 0`

This exactly reproduces the earlier first sealed final-money result. Therefore the earlier workflow failure was caused only by the known `scripts/eval.py` scalar-status serialization issue (`"DONE"` becoming a character list), not by a candidate runtime/game failure.

## Gate consequence

The two prerequisites for the already-precommitted second fresh sealed block are now both satisfied:

1. known/public-opponent outcome gate: PASS, zero regressions (`36295410170`);
2. first sealed direct completion verification: PASS (`36295374931`).

The second sealed trigger was therefore released in commit `fd50d0707ff2c5b2b50f0d01f5644956ae7ff2c2`, starting run `36300290715` on the previously fixed seed list. No seed was selected after observing the first sealed outcome.
