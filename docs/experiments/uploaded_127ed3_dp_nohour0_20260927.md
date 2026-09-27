# uploaded 127ed3 DAWNPX no-hour0 — REJECT — 2026-09-27

Decision: **REJECT**

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

became

```python
_DP_HOURS = (1, 2)
```

All other safety-v3 behavior was unchanged.

Exact reconstruction/build checks verified:

- raw SHA256 `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- parent SHA256 `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- replacement occurrence count: exactly 1
- child SHA256 `ff5932a9cb7ceb2f6db9d1f052083fdb442e7270ac70048ce078a93fec819116`
- AST/syntax: PASS

## Evaluation

Workflow: `.github/workflows/uploaded-127ed3-dp-nohour0-dev.yml`

Actions run: `36284441745`

Artifact: `uploaded-127ed3-dp-nohour0-dev`, artifact id `10920309507`

Burned matched seeds, both seats:

`641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`

Direct-parent result:

- W/L/D = **1 / 1 / 8**
- mean = **-2.2**
- median = `0`
- SE = `4.4242`
- mean - 2SE = **-11.0484**
- worst = **-39**
- best = `+17`
- seat0 mean = `-2.2`
- seat1 mean = `-2.2`
- candidate exceptions = `0`
- parent exceptions = `0`

Seed deltas:

| seed | candidate - parent |
|---:|---:|
| 641 | 0 |
| 350003 | 0 |
| 101 | +17 |
| 211 | -39 |
| 347 | 0 |
| 509 | 0 |
| 733 | 0 |
| 911 | 0 |
| 1201 | 0 |
| 1601 | 0 |

Both seat deltas were identical for every seed.

## Interpretation

The candidate does not improve either focal loss seed: 641 and 350003 are exact behavior-equivalent to the parent under this change. The two contrast wins 733 and 911 are also exact ties. The only observed changes are a small `+17` on seed 101 and a larger `-39` regression on seed 211, leaving the block slightly negative.

There is therefore no evidence that hour-0 DAWNPX front-running explains the late loss pattern. Combined with the full DAWNPX-off diagnostic (`1W/7L/2D`, mean `-134.7`, worst `-594`), the DAWNPX suppression direction is closed.

Do not spend stress or sealed seeds on this child. Do not repeat full DAWNPX-off or hour-0-only suppression without materially new evidence.

## Decision

**REJECT.** Formal champion remains `uploaded_127ed3_safety_v3`.

## Next hypothesis

Move upstream to the crop-realization decision rather than suppressing downstream protective/lead-sale layers. Existing late-market decomposition shows the loss structure is uncompensated WHEAT opportunity cost, whereas winning seed 733 has an even larger WHEAT shortfall that is more than repaid by CARROT/premium realized revenue. The next analysis should inspect CARROT2 decision-state chronology (including rejected opportunities), harvest horizon, market inventory, Town demand, standing crop mix, and planned SELL pipeline before introducing another tactical gate.
