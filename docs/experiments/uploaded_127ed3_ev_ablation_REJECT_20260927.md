# uploaded 127ed3 EV evening lead-sell ablation — REJECT — 2026-09-27

Decision: **REJECT**

## Identity

- Formal parent/champion: `uploaded_127ed3_safety_v3`
- Parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Diagnostic child SHA256: `794500e12e4e2c965417698c7e9b5dadef77316f431138e7c459921c617b4f19`
- Formal engine: `kaggle-environments==1.32.7`
- Official Kaggriculture source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- Difference convention: `candidate_minus_champion = candidate - champion`

## Hypothesis

Focal telemetry showed evening lead-sale (`EV`) activity concentrated on the two v147-relative loss seeds:

- 641: `ev_fires=20`, `ev_units=64`
- 350003: `6`, `23`
- 733: `2`, `9`
- 911: `1`, `6`

EV pulls premium-item sells from the next 8 turns into hours 15-20 when the current quote is at or above its trailing average. Because Town/shop demand is processed after market orders, early lead-sale can in principle sell before nearby demand that would have improved the quote. Test whether the correlation is causal.

## Change

Single diagnostic change only:

```python
_EV_HOURS = (15, 16, 17, 18, 19, 20)
```

became

```python
_EV_HOURS = ()
```

All other safety-v3 behavior is unchanged.

Build checks verified exact parent SHA, exact formal engine/source SHA, exact child SHA, and `py_compile` before evaluation.

## Evaluation

Actions run: `36287230790`

Artifact: `uploaded-127ed3-ev-ablation-dev`, artifact id `10921440107`

Burned matched seeds, both seats:

`641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`

Direct-parent result:

- W/L/D = **2 / 4 / 4**
- mean = **-25.9**
- median = `0`
- SE = `17.5521`
- mean - 2SE = **-61.0042**
- worst = **-160**
- best = `+33`
- seat0 mean = `-25.9`
- seat1 mean = `-25.9`
- candidate exceptions = `0`
- parent exceptions = `0`

Seed deltas:

| seed | EV-off - parent |
|---:|---:|
| 641 | **-76** |
| 350003 | **-37** |
| 101 | 0 |
| 211 | -24 |
| 347 | 0 |
| 509 | **-160** |
| 733 | +33 |
| 911 | 0 |
| 1201 | +5 |
| 1601 | 0 |

Both seat deltas were identical for every seed.

## Interpretation

The loss-side activation correlation is not causal evidence that EV should be suppressed. Removing EV makes **both focal loss seeds worse**, and the block as a whole is negative.

This matches the pattern seen in the DAWNPX and CAPHARV causal screens: several high-activation counters are reactive markers of a difficult farm/market state, while their interventions are locally protective. Fire count alone must not be promoted into a gate.

Do not spend stress/sealed seeds on EV-off. Do not repeat blanket EV disablement without materially new evidence.

## Decision

**REJECT.** Formal champion remains `uploaded_127ed3_safety_v3`.

## Next direction

The combined evidence now argues against suppressing downstream safety/lead-sale layers (`CAPHARV`, `DAWNPX`, `EV`) and against blanket CARROT2 limits. The remaining v147-relative losses are better treated as state-dependent portfolio outcomes: WHEAT revenue is lower, but whether that is harmful depends on CARROT/premium realization driven partly by the seed's shop/market path.

The next candidate should therefore require a positive, directly-measured failure condition rather than a high telemetry fire count. In the absence of such a condition, retain safety-v3 rather than overfit the two focal losses.
