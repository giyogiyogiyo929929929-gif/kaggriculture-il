# uploaded 127ed3 DAWNPX no-hour0 — 2026-09-27

Decision: **KEEP TESTING (burned dev queued)**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Candidate SHA256: `ff5932a9cb7ceb2f6db9d1f052083fdb442e7270ac70048ce078a93fec819116`
- Formal engine: `kaggle-environments==1.32.7`
- Official Kaggriculture source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Hypothesis

DAWNPX currently performs lead sales at hours `(0, 1, 2)` once `step >= 96`. Kaggriculture processes market orders before Town/shop consumption. Therefore an hour-0 DAWNPX sale occurs before the daily Town-centre consumption on that turn and can front-run demand that would otherwise reduce market inventory and improve the following price. Keep hours 1-2, but stop only hour-0 DAWNPX pre-sales.

## Change

Single tactical change only:

```python
_DP_HOURS = (0, 1, 2)
```

becomes

```python
_DP_HOURS = (1, 2)
```

All other safety-v3 bytes are unchanged.

Local exact reconstruction from the immutable uploaded raw parent plus the canonical safety-v3 wrapper verified:

- raw SHA256 `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- parent SHA256 `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- replacement occurrence count: exactly 1
- child SHA256 `ff5932a9cb7ceb2f6db9d1f052083fdb442e7270ac70048ce078a93fec819116`
- AST/syntax: PASS

## Diagnostic basis

Existing safety-v3-v147 telemetry on contrast seeds shows:

- seed 641: safety-v3 minus v147 = `-406`; WHEAT net-market contribution difference `-1722`, partly offset by CARROT `+1691`.
- seed 350003: safety-v3 minus v147 = `-520`; WHEAT net-market contribution difference `-1008`, with smaller CARROT/high-value offsets.
- seed 733: safety-v3 minus v147 = `+3428`; CARROT `+2324`, WOOL `+1926`, STRAWBERRY `+996` dominate despite WHEAT `-1472`.
- seed 911: safety-v3 minus v147 = `+1178`; STRAWBERRY `+860`, MILK `+425`, WHEAT `+163`.

This makes blanket CARROT suppression inappropriate. A previously tested CARROT2 swap-cap-24 child was already negative (`0W/3L/7D`, mean `-176.4`, worst `-1572`) and is not repeated.

DAWNPX telemetry on these same games fired on loss seeds (641: 8 fires / 27 units; 350003: 4 / 11), was absent on strong seed 733 (0 / 0), and small on seed 911 (1 / 4). This is suggestive but not sufficient alone; the direct-parent ablation is the decision evidence.

## Evaluation

Workflow: `.github/workflows/uploaded-127ed3-dp-nohour0-dev.yml`

Actions run: `36284441745`

Burned matched seeds, both seats:

`641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`

Current state at log creation: **queued** because the self-hosted runner is occupied by another long evaluation.

A separate full DAWNPX-off causal diagnostic run `36284150337` is also queued. Hosted four-seed CH/DP screen `36284180138` failed before producing an artifact and is not tactical evidence.

## Promotion rule

Compare no-hour0 directly against safety-v3 first. Do not use v147 as the parent decision comparator. Advance only if the matched burned block is clearly non-negative with acceptable worst regression and no exceptions. If promising, run stress and then allocate fresh sealed seeds; do not inherit safety-v3 sealed evidence.
