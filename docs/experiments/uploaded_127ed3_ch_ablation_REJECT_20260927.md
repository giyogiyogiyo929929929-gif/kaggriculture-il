# uploaded 127ed3 CAPHARV ablation — REJECT — 2026-09-27

Decision: **REJECT**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Diagnostic child SHA256: `f771c1b323eda8ee9f972f522b5489c9a448ac15a88611a0b29beb10a68f0cc7`
- Formal engine: `kaggle-environments==1.32.7`
- Official Kaggriculture source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Hypothesis

The contrast telemetry showed CAPHARV activity only on the two v147-relative loss seeds among `641, 350003, 733, 911`. Test whether this layer is causal rather than merely responding to an already-different farm state.

## Change

Single diagnostic change:

```python
_CH_SHED = 100
```

became

```python
_CH_SHED = 0
```

This blocks every eligible CAPHARV substitution before it can rewrite `CARE` / `COLLECT_FERTILIZER` to `HARVEST`. All other safety-v3 behavior is unchanged.

Workflow build verified the exact safety-v3 parent SHA, exact formal engine/source SHA, exact child SHA, and `py_compile` before evaluation.

## Evaluation

Actions run: `36284078828`

Burned matched seeds, both seats:

`641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`

Direct parent comparison:

- W/L/D = **1 / 5 / 4**
- mean = **-217.3**
- median = `-72.5`
- SE = `102.7336`
- mean - 2SE = **-422.7673**
- worst = **-946**
- best = `+12`
- seat0 mean = `-217.3`
- seat1 mean = `-217.3`
- candidate exceptions = `0`
- parent exceptions = `0`

Seed deltas:

| seed | candidate - parent |
|---:|---:|
| 641 | **-611** |
| 350003 | **-152** |
| 101 | -145 |
| 211 | -331 |
| 347 | +12 |
| 509 | 0 |
| 733 | 0 |
| 911 | 0 |
| 1201 | **-946** |
| 1601 | 0 |

## Interpretation

The loss-only activation seen in the four-seed contrast was **not causal evidence that CAPHARV should be disabled**. Removing the layer makes both focal loss seeds worse and introduces a large `-946` regression on seed 1201.

CAPHARV is therefore better interpreted as a reactive protection layer: it fires in farm states where productive-animal overflow makes a harvest substitution economically attractive. Those states correlate with the upstream tactical divergence, but the intervention itself is generally beneficial relative to removing it.

Do not repeat blanket CAPHARV disablement, and do not condition future candidates solely on CAPHARV fire count.

## Next hypothesis

Keep CAPHARV intact. Continue tracing the upstream crop/market state that produces uncompensated WHEAT opportunity cost on 641/350003. The pending DAWNPX hour-0-only candidate is a narrower market-ordering intervention and should be judged independently against safety-v3.
