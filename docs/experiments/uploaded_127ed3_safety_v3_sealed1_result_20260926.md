# uploaded 127ed3 safety-v3 — canonical sealed block 1 result

## Candidate / parent / champion

- candidate: uploaded 127ed3 safety-v3
- candidate SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- tactical parent: uploaded raw candidate SHA256 `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- formal champion: `v147_candidate_confirmed_v111_clone.py`
- champion SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`

## Hypothesis

The uploaded tactical path should retain its dev/stress advantage over v147 on a precommitted fresh seed block, without seat dependence, exceptions, or incomplete games. The safety-v3 wrapper is already isolated as tactically inert on the burned dev block.

## Environment / provenance

- GitHub Actions run: `36243519132`
- workflow: `.github/workflows/uploaded-127ed3-safe-v3-sealed-reserved1.yml`
- runner: self-hosted Windows X64
- Python: 3.11
- `kaggle-environments==1.32.7`
- engine source SHA256: `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- seed reservation: `docs/experiments/uploaded_127ed3_safety_v3_sealed1_seed_reservation_20260926.md`
- canonical precommitted seeds: `645491, 839835, 927489, 524295, 654541, 709211, 640183, 546018, 709378, 901935, 574041, 685514`
- both seats for every seed; `jobs=1`

## Result

Candidate minus champion is defined as `safety-v3 - v147`.

- matched pairs: 12
- W/L/D: **11 / 1 / 0**
- mean: **+722.625**
- median: **+760.75**
- SE: **162.0447133**
- mean - 2SE: **+398.5355734**
- worst: **-39**
- best: **+1834**
- seat0 mean: **+714.0833333**
- seat1 mean: **+731.1666667**
- candidate exceptions: **0**
- champion exceptions: **0**
- games shorter than 720 turns: **0**

Per-seed pair mean deltas:

| seed | candidate_minus_champion | result |
|---:|---:|:---:|
| 645491 | +1834.0 | W |
| 839835 | +168.0 | W |
| 927489 | +746.5 | W |
| 524295 | -39.0 | L |
| 654541 | +1172.0 | W |
| 709211 | +746.0 | W |
| 640183 | +775.0 | W |
| 546018 | +893.0 | W |
| 709378 | +1144.0 | W |
| 901935 | +29.0 | W |
| 574041 | +143.0 | W |
| 685514 | +1060.0 | W |

Only seed `927489` had non-identical seat deltas (`+644`, `+849`); the aggregate seat means remain close. The sole losing seed `524295` was `-39` in both seats.

## Interpretation

The canonical sealed gate passes. Improvement is distributed across the fresh block rather than being driven by one seed, the two-seat aggregate is balanced, the lower confidence-style check `mean - 2SE` remains strongly positive, and no exception or short-game regression occurred.

This result does not by itself authorize promotion. Important-opponent regression and a final runtime gate remain required.

## Decision

**KEEP TESTING — SEALED PASS.**

Champion remains v147 until the public-opponent regression panel and final runtime checks complete.

## Next

1. safety-v3 vs v147 on the frozen six-opponent public regression panel using already-burned seeds only.
2. final single-process timing gate: p99 < 50 ms and worst < 200 ms.
3. inspect any material opponent-specific regression before PROMOTE.
4. corrected CARROT2 feed2 remains a separate burned-dev experiment and must not contaminate this promotion decision.
