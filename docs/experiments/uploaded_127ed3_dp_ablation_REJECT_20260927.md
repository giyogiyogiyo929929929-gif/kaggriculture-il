# uploaded 127ed3 DAWNPX full ablation — REJECT — 2026-09-27

Decision: **REJECT**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Diagnostic child SHA256: `f1384b23502d992e6c93628d24b689d54fecfcc67cb8df420fdb9a463fe814f1`
- Formal engine: `kaggle-environments==1.32.7`
- Official Kaggriculture source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Hypothesis

DAWNPX activation was concentrated on the two v147-relative loss seeds in the four-seed contrast. Disable the full layer as a causal diagnostic before using DAWNPX fire count as a tactical gate.

## Change

Single diagnostic change:

```python
_DP_HOURS = (0, 1, 2)
```

became an empty tuple, disabling the DAWNPX lead-sale layer while leaving all other safety-v3 behavior unchanged.

Workflow build verified exact parent SHA, exact formal engine/source SHA, exact child SHA, and syntax before evaluation.

## Evaluation

Actions run: `36284150337`

Burned matched seeds, both seats:

`641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`

Direct parent comparison:

- W/L/D = **1 / 7 / 2**
- mean = **-134.7**
- median = `-79.5`
- SE = `59.7995`
- mean - 2SE = **-254.2990**
- worst = **-594**
- best = `+13`
- seat0 mean = `-134.7`
- seat1 mean = `-134.7`
- candidate exceptions = `0`
- parent exceptions = `0`

Seed deltas:

| seed | candidate - parent |
|---:|---:|
| 641 | **-318** |
| 350003 | **-74** |
| 101 | +13 |
| 211 | **-594** |
| 347 | 0 |
| 509 | -164 |
| 733 | 0 |
| 911 | -33 |
| 1201 | -85 |
| 1601 | -92 |

## Interpretation

Blanket DAWNPX removal is directly harmful. In particular, it worsens both focal loss seeds, so the observed loss-seed activation is not evidence that the whole lead-sale layer causes the loss.

Do not repeat full DAWNPX disablement or gate behavior solely by DAWNPX fire count.

This does **not** settle the narrower market-ordering hypothesis that only hour-0 pre-sales are mistimed. The separate child that retains hours 1-2 but removes hour 0 changes only one timing condition and remains a valid direct-parent test.

## Next hypothesis

Evaluate `DAWNPX no-hour0` independently. If that narrow child also fails, stop this DAWNPX direction and instrument the upstream CARROT2/crop-realization decision state rather than suppressing downstream protective layers.
