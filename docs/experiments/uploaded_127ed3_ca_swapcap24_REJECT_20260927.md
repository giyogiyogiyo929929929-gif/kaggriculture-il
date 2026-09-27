# uploaded 127ed3 CARROT2 swap-cap24 — REJECT — 2026-09-27

## Identity

- formal parent/champion: `uploaded_127ed3_safety_v3`
- parent SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- candidate SHA256: `bdec654d4d94bec52f56ec28d7ea16787ecefb0e2a1efb38a66dc1e710ade939`
- Actions run: `36283589084`
- artifact id: `10919995864`
- artifact digest: `sha256:62a101ae5b2592b848f09134e174a789ec5b09ca3a27a11ba2a34d532256cad1`
- environment: self-hosted Windows X64, Python 3.11, `kaggle-environments==1.32.7`
- official engine source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`

## Hypothesis

Contrast telemetry showed CARROT2 substitutions were much more frequent on the two v147-regression seeds than on two positive controls:

- seed 641: 46 swaps, final safety-v3-minus-v147 `-406`
- seed 350003: 29 swaps, `-520`
- seed 733: 22 swaps, `+3428`
- seed 911: 0 swaps, `+1178`

Hypothesis: late/high-count CARROT2 substitutions might become over-intervention after the useful early swaps.

## Change

One tactical condition only:

```python
if _CA_FROM <= day <= _CA_TO and pays_now:
```

became

```python
if _CA_FROM <= day <= _CA_TO and pays_now and _CA_REPORT["ca_swaps"] < 24:
```

No feed reserve, price margin, rescue, market ordering, or wrapper logic changed.

## Static/runtime construction

The exact safety-v3 parent was reconstructed with `ci/build_uploaded_127ed3_safety_v3.py`, exact parent SHA and official engine SHA were asserted, the one byte-level replacement was asserted unique, exact child SHA was asserted, and both files passed `py_compile`.

## Burned direct-parent result

Seeds: `641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`; same seed, both seats.

Candidate-minus-parent matched-pair result:

- W/L/D: **0 / 3 / 7**
- mean: **-176.4**
- median: **0**
- SE: **155.6206**
- mean - 2*SE: **-487.6411**
- worst: **-1572** (seed 641)
- best: **0**
- seat0 mean: **-176.4**
- seat1 mean: **-176.4**
- candidate exceptions: **0**
- parent exceptions: **0**

Per-seed pair mean:

- 641: `-1572`
- 350003: `-120`
- 101: `0`
- 211: `0`
- 347: `0`
- 509: `0`
- 733: `0`
- 911: `0`
- 1201: `-72`
- 1601: `0`

## Workflow status-parser note

The GitHub job concluded `failure` only because the diagnostic `non_done` assertion treated the returned `"DONE"` status value as an iterable of characters. It reported a false `non_done=20`. This is an evaluation-harness assertion bug, not a candidate runtime failure: the evaluation completed, the artifact was uploaded, and candidate/parent exception counts are both zero.

This parser bug must not be reused as a tactical signal. Future workflows should either use the runner's actual status schema correctly or omit this redundant assertion when `evaluate()` completed normally and exceptions are checked.

## Interpretation

The correlation between high CARROT2 swap count and the two observed losses was not causal in the proposed direction. Suppressing swaps after the 24th intervention materially hurts seed 641 and never improves a tested seed. In particular, CARROT2's late substitutions appear to mitigate rather than cause the seed-641 deficit.

Therefore do **not** continue blind CARROT2 swap-cap variants. The earlier feed-reserve variants were already negative as well.

## Decision

**REJECT.**

- no stress test
- no sealed seeds
- no champion change

## Next hypothesis

Inspect loss-specific layers outside CARROT2. The strongest clean contrast signal is the CAPHARV (`_CH_REPORT`) layer: seeds 641/350003 record `ch_collect_swaps=8/9` and `ch_saved=16/19`, while contrast wins 733/911 record zero CH activity. Use a burned direct-parent CH ablation first as a causal diagnostic before designing any narrower CAPHARV rule.
