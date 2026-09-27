# uploaded 127ed3 CARROT2 early-margin — REJECT — 2026-09-27

Decision: **REJECT / recovered historical experiment**

## Identity

- Historical tactical parent: uploaded raw `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- Candidate SHA256: `bad25166aa91712007af8a010f571dab5cf87873dc75f762f2e83b152849faad`
- Builder: `ci/build_uploaded_127ed3_ca_early_margin.py`
- Workflow: `.github/workflows/uploaded-127ed3-ca-early-margin.yml`
- Actions run: `36235967167`
- Artifact: `uploaded-127ed3-ca-early-margin`, artifact id `10903909192`
- Engine: `kaggle-environments==1.32.7`
- Difference convention: candidate minus direct tactical parent.

The formal champion is now `uploaded_127ed3_safety_v3`; its wrapper was subsequently shown behavior-inert against exact uploaded raw on the burned dev block. This recovered test is therefore retained as tactical evidence and should not be repeated merely to add the safety wrapper.

## Change

Before step 540, tighten the CARROT2 economic margin from `_CA_MARGIN=-20` to an early margin of `0`; after step 540 retain `-20`. Both the global pays-now test and route-aware `cu` versus `wu` test use the stricter early margin.

## Burned matched result

Seeds: `641,350003,101,211,347,509,733,911,1201,1601`, both seats.

- W/L/D = **0 / 4 / 6**
- mean = **-112.0**
- median = `0`
- worst = **-693**
- best = `0`
- seat0 mean = `-112.0`
- seat1 mean = `-112.0`
- exceptions = `0`
- non-DONE = `0`

Seed pair deltas:

- 641: **-693**
- 350003: **-222**
- 101: 0
- 211: 0
- 347: 0
- 509: 0
- 733: 0
- 911: 0
- 1201: **-78**
- 1601: **-127**

## Interpretation

The later CARROT2 decision-state trace showed a small set of accepted negative-current-edge swaps, but this historical causal test already demonstrates that tightening the early CARROT2 margin is harmful, including on both focal v147-relative loss seeds. Do not infer that weak current edge alone is a failure condition.

This is consistent with later evidence that current-price-only valuation is incomplete: harvest timing, Town demand, and downstream realization can make a swap useful even when the decision-time edge is modestly negative.

## Decision

**REJECT.** Do not repeat generic early margin tightening without materially new telemetry.
