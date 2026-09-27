# uploaded 127ed3 safety-v3 PROMOTE — 2026-09-27

Decision: **PROMOTE**

## Identity

- Previous formal champion: `v147_candidate_confirmed_v111_clone.py`
- Previous champion SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- New formal champion: uploaded 127ed3 safety-v3
- New champion SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- Tactical parent: uploaded raw candidate SHA256 `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- Reproducer: `ci/build_uploaded_127ed3_safety_v3.py`
- Formal engine: `kaggle-environments==1.32.7`
- Official Kaggriculture engine source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- Difference convention: `candidate_minus_champion = candidate - champion`

The uploaded raw candidate remains immutable. Safety-v3 adds only the final exception-safe entrypoint wrapper; it does not overwrite either the raw parent or v147.

## Hypothesis / change

Safety-v3 preserves the uploaded raw `ig_agent` tactical path and adds one safety-only wrapper around the final Kaggle entrypoint. On an exception, the wrapper returns a valid no-op action dictionary instead of allowing the submission call to fail.

Raw-isolation evaluation shows that the wrapper itself is tactically inert on the burned dev block. Therefore the performance improvement versus v147 is attributed to the uploaded raw tactical path, while safety-v3 contributes the exception fallback and deterministic loader selection.

## Formal dev H2H — PASS

Actions run `36236548782`; ten burned dev seeds, both seats.

- matched-pair W/L/D: **8 / 2 / 0**
- mean candidate_minus_champion: **+688.5**
- median: **+392**
- worst: **-520**
- best: **+3428**
- seat0 mean: **+688.5**
- seat1 mean: **+688.5**
- candidate exceptions: **0**
- non-DONE games: **0**

## Burned stress — PASS

Actions run `36237376092`; seeds 621-632, both seats.

- W/L/D: **11 / 1 / 0**
- mean: **+856.6667**
- median: **+1008.5**
- SE: **248.2680**
- mean - 2*SE: **+360.1307**
- worst: **-946**
- best: **+2239**
- seat0 mean: **+856.6667**
- seat1 mean: **+856.6667**
- exceptions: **0**
- non-DONE: **0**

## Raw-isolation attribution — PASS

Actions run `36242466654`; exact safety-v3 versus exact uploaded raw parent on the ten burned dev seeds, both seats.

- all 20 per-seat deltas: exactly `0`
- matched-pair W/L/D: `0/0/10`
- mean / median / SE / worst / best: all `0`
- exceptions: `0/0`

Conclusion: safety-v3 wrapper is tactically inert on this block. The gains versus v147 come from the uploaded raw tactical path, not from the exception wrapper.

## Canonical precommitted sealed — PASS

Actions run `36243519132` on the precommitted fresh seeds:

`645491, 839835, 927489, 524295, 654541, 709211, 640183, 546018, 709378, 901935, 574041, 685514`

Both seats were evaluated.

- matched-pair W/L/D: **11 / 1 / 0**
- mean: **+722.625**
- median: **+760.75**
- SE: **162.0447**
- mean - 2*SE: **+398.5356**
- worst regression: **-39** on seed `524295`
- best improvement: **+1834** on seed `645491`
- seat0 mean: **+714.0833**
- seat1 mean: **+731.1667**
- candidate exceptions: **0**
- champion exceptions: **0**
- short games: **0**

The effect reproduces on untouched seeds with negligible seat dependence and a small worst regression.

## Known/public opponent regression — PASS on competition-primary outcome

The first exact money-delta panel, Actions run `36247674737`, found substantial candidate final-money compression versus v147 against some already-dominated opponents, notably `starter`, `beat_v48`, and `farming_v2`. Because Kaggriculture is decided by win/loss from final cash rather than margin magnitude, this triggered dedicated outcome-centric follow-up rather than an immediate promotion or rejection.

Outcome-centric Actions run `36250594997` then evaluated the same six known opponents:

- `starter`
- `beat_v48`
- `bl_v20`
- `bl_v21`
- `farming_v2`
- `frontier_prvsiyan`

Two burned blocks were checked, both seats:

### Public burned 621-624

- candidate aggregate: **48W / 0L / 0D**
- v147 aggregate: **48W / 0L / 0D**
- favorable outcome flips: `0`
- regression outcome flips: **0**
- exceptions: `0/0`

### Formal-known 641-644

- candidate aggregate: **48W / 0L / 0D**
- v147 aggregate: **48W / 0L / 0D**
- favorable outcome flips: `0`
- regression outcome flips: **0**
- exceptions: `0/0`

A second dedicated public-outcome workflow, run `36252342056`, independently confirmed on seeds 621-624 that all 48 candidate games and all 48 v147 games remain wins, with no W->L or W->D regression.

Risk note: margin compression against already-dominated opponents is retained as a telemetry concern for future strategy work. It is not ignored. On the tested panel it did not change the competition-primary outcome.

## Formal runtime — PASS

Dedicated serial runtime result recorded from run `36237376092`, Python 3.11, official engine 1.32.7, starter opponent, seeds 641/642, both seats.

Safety-v3 aggregate:

- median of game medians: **2.08895 ms**
- max game p99: **17.2066 ms**
- worst turn: **169.2014 ms**
- exceptions: **0**
- non-DONE: **0**

Formal thresholds:

- max p99 < 50 ms: **PASS**
- worst turn < 200 ms: **PASS**
- exceptions/timeouts/non-DONE: **PASS**

## Final submission preflight — PASS

Actions run `36247002100` completed successfully.

Verified:

1. exact `kaggle-environments==1.32.7`;
2. exact official Kaggriculture engine SHA256;
3. exact raw parent reconstruction;
4. exact safety-v3 reconstruction;
5. static/import audit and Kaggle-like loader selection;
6. malformed/broken-observation fallback returns a valid `{farmer,hands,market}` action with lists;
7. official-engine full 720-turn smoke on seed 641 in both seats: `DONE`, zero wrapper errors;
8. submission package contains exactly root `main.py` and re-hashes to the promoted source.

Final package metadata:

- `main.py` SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- archive SHA256: `370e478315ab7756e8bbb1f474822439c5f8db6614f86fac8926c15528423111`
- archive bytes: **178,991**

## Rejected children retained for attribution

### CARROT2 global feed2

Exact child SHA256 `a2e69e32513280051709bfc921104a3574bc87f484e6a0d1c07466a377e8cc26`:

- direct-parent W/L/D: `2/5/3`
- mean safety-v3 delta: `-165.9`
- mean - 2SE: `-427.4592`
- worst: `-1308`

Decision: **REJECT**.

### CARROT2 two-day reserve through day 22

Exact child SHA256 `a397bb19046e82a50fee5701df882af3700d7727747089ff2b1f2c2384bb6ed5`:

- direct-parent W/L/D: `0/4/6`
- mean safety-v3 delta: `-140.4`
- mean - 2SE: `-341.8256`
- worst: `-1028`
- best: `0`

Decision: **REJECT**. No sealed seeds are allocated to either feed2 child.

## Promotion decision

PROMOTE conditions are satisfied:

- formal matched improvement: PASS
- seat swap: PASS
- burned stress: PASS
- fresh precommitted sealed reproduction: PASS
- worst sealed regression small (`-39`)
- no meaningful seat dependence
- known/public opponent outcome regression: PASS, zero W->L/W->D flips
- exact source and engine identity pinned
- wrapper attribution explained
- runtime: PASS
- exceptions/timeouts/non-DONE: 0
- final package/static/loader/full-game smoke: PASS

**PROMOTE exact safety-v3 SHA256 `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df` as the formal champion.**

No Kaggle submission was performed by this promotion record.
