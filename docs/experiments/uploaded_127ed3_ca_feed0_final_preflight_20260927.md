# uploaded 127ed3 CARROT2 feed0 — final submission preflight — 2026-09-27

Decision: **PASS**

## Identity

- Candidate: `uploaded_127ed3_ca_feed0`
- Candidate SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Formal engine: `kaggle-environments==1.32.7`
- Official Kaggriculture source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`

## Run

- GitHub Actions run: `36295816696`
- Artifact: `uploaded-127ed3-ca-feed0-final-preflight`
- Artifact id: `10925512998`
- Workflow conclusion: **success**

## Checks

All workflow stages passed:

1. exact engine and candidate reconstruction/hash checks;
2. Python compile/import/static audit with no new risky signature versus parent;
3. Kaggle-compatible last-callable loader selection;
4. malformed-observation fallback on five broken observation patterns;
5. official-engine 720-turn smoke on seed641 in both seats;
6. exact submission archive construction and verification.

Smoke results:

- seat0: `DONE`, 720 turns, errors `0`;
- seat1: `DONE`, 720 turns, errors `0`.

All five malformed-observation cases returned a correctly shaped fallback action without exception.

## Submission package

- archive member list: `['main.py']`
- `main.py` SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- archive SHA256: `db3df5d7fcc3246ba93b6102ee8fdd1dab83f32fc972986780ce0271b46994b0`
- archive bytes: `178987`

## Decision

**PASS final preflight.** Feed0 remains unpromoted only because the corrected final runtime gate is still pending. No Kaggle submission is implied.
