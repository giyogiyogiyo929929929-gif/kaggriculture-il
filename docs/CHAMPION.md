# Formal Champion

Updated: 2026-09-27

## Current champion

- Name: `uploaded_127ed3_ca_feed0`
- SHA256: `cc300eda64d0fe1f884bd164f973de2177eb68c1808cafed06bfeadc5b446e44`
- Tactical parent: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Reproducer: `ci/build_uploaded_127ed3_ca_feed0.py`
- Formal engine: `kaggle_environments==1.32.7`
- Official Kaggriculture source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- Verified submission archive SHA256: `db3df5d7fcc3246ba93b6102ee8fdd1dab83f32fc972986780ce0271b46994b0`
- Verified submission archive bytes: `178987`

Promotion record: `docs/experiments/uploaded_127ed3_ca_feed0_PROMOTE_20260927.md`.

The previous `uploaded_127ed3_safety_v3`, its uploaded raw tactical parent, and v147 must remain unchanged for reproducibility/rollback. Do not infer champion from version numbers or filenames; verify this file together with the latest promotion record and exact source SHA.

Known follow-up risk: feed0 preserves formal known-opponent outcomes but compresses winning margin versus builtin starter on some known seeds; this is documented in the promotion record and must be considered in future robustness work.

No Kaggle submission is implied by champion promotion.
