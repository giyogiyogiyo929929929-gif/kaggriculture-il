# uploaded 127ed3 evaluation audit — 2026-09-26 21:47+ JST

## Scope

Audit the uploaded raw candidate and the current safety-v3 / CARROT2 feed2 evaluation path before any promotion decision.

## Champion

- formal champion: `v147_candidate_confirmed_v111_clone.py`
- SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`

## Uploaded raw candidate

- SHA256: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- size: 501543 bytes
- current upload `main(2).py` was independently re-hashed and is byte-identical to the previously evaluated uploaded candidate.
- syntax / AST: PASS.

## Surviving candidate: safety-v3

- parent: uploaded raw candidate
- SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- change: outer exception-safe final entrypoint only; tactical path remains the uploaded `ig_agent` path.
- formal dev H2H already recorded: 10 matched pairs, both seats, 8W/2L/0D, mean candidate_minus_champion +688.5, median +392, worst -520, best +3428, exceptions 0, non-DONE 0.
- burned stress already recorded: seeds 621-632, 11W/1L/0D, mean +856.6667, mean-2SE +360.1307, worst -946, exceptions 0, non-DONE 0.

## Raw-isolation attribution — PASS

Actions run `36242466654`, job `108405426847`, self-hosted Windows X64 runner `CIYOI`.

Compared byte-exact safety-v3 against its byte-exact raw parent on the ten already-burned dev seeds `641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`, both seats.

- exact raw SHA256: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`
- exact safety-v3 SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- all 20 per-seat deltas: exactly `0`
- matched-pair W/L/D: `0/0/10`
- mean / median / SE / worst / best safety-v3-minus-raw: all `0`
- safety-v3 exceptions: `0`
- raw exceptions: `0`

Conclusion: on this burned dev block the safety-only wrapper is tactically inert. The previously observed improvement versus v147 is attributable to the uploaded raw tactical path, not to the wrapper; safety-v3 retains the raw trajectory while adding the outer exception fallback.

## Canonical sealed block 1 — PASS

Canonical precommitted seeds from `uploaded_127ed3_safety_v3_sealed1_seed_reservation_20260926.md`:
`645491, 839835, 927489, 524295, 654541, 709211, 640183, 546018, 709378, 901935, 574041, 685514`.

Actions run `36243519132`, exact engine/candidate/champion SHA checks, both seats, serial self-hosted evaluation.

- matched-pair W/L/D: `11/1/0`
- mean candidate_minus_champion: `+722.625`
- median: `+760.75`
- SE: `162.04471330422504`
- mean - 2SE: `+398.5355733915499`
- worst: `-39` on seed `524295`
- best: `+1834` on seed `645491`
- seat0 mean: `+714.0833333333334`
- seat1 mean: `+731.1666666666666`
- candidate exceptions: `0`
- champion exceptions: `0`
- short games: `0`

Per-seed pair means:
`645491 +1834, 839835 +168, 927489 +746.5, 524295 -39, 654541 +1172, 709211 +746, 640183 +775, 546018 +893, 709378 +1144, 901935 +29, 574041 +143, 685514 +1060`.

Conclusion: the fresh precommitted sealed block strongly reproduces the dev/stress advantage, with no meaningful seat dependence and only a small worst regression. Safety-v3 advances past the sealed gate. This does not by itself promote the candidate; important-opponent regression and final runtime/submission preflight still gate promotion.

The later contiguous `409001-409012` workflow is not relabeled as the canonical sealed block. Hosted sealed cross-check run `36241495134` failed before any job steps were provisioned (`runner_id=0`, steps empty) and is infrastructure failure, not candidate evidence.

## CARROT2 global feed2 — REJECT

Corrected exact global two-day child:

- parent safety-v3 SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- change: first/only `_CA_FEED_DAYS = 1` -> `2`
- child SHA256: `a2e69e32513280051709bfc921104a3574bc87f484e6a0d1c07466a377e8cc26`
- Actions run: `36243480932`
- burned dev seeds only: `641, 350003, 101, 211, 347, 509, 733, 911, 1201, 1601`, both seats.

Candidate minus exact safety-v3 parent:

- W/L/D: `2/5/3`
- mean: `-165.9`
- median: `-23`
- SE: `130.77958131485545`
- mean - 2SE: `-427.45916262971093`
- worst: `-1308` on seed `641`
- best: `+126` on seed `350003`
- exceptions: `0/0`

Per-seed parent deltas:
`641 -1308, 350003 +126, 101 0, 211 -142, 347 +14, 509 0, 733 -53, 911 0, 1201 -46, 1601 -250`.

Candidate minus v147 was still `7/3/0`, mean `+588.5`, but attribution against its direct parent is clearly negative. Therefore the global two-day reserve is REJECTED as a tactical change and must not replace safety-v3.

This validates the need for the narrower already-identified follow-up rather than a global horizon increase.

## CARROT2 day<=22 follow-up — DEV TEST ONLY

New exact child prepared after global feed2 rejection:

- parent: exact safety-v3
- change: use a two-day FEED reserve only when `day <= 22`; retain original one-day reserve afterward
- child SHA256: `a397bb19046e82a50fee5701df882af3700d7727747089ff2b1f2c2384bb6ed5`
- local exact-byte hash / AST: PASS
- workflow: `.github/workflows/uploaded-127ed3-ca-feed2-day22-dev.yml`
- run `36247703056`: queued at the time of this update
- uses only the already-burned ten-seed dev block; no fresh sealed seeds allocated.

## Public-opponent regression

The existing public panel defines six repo-resident opponents: `starter`, `beat_v48`, `bl_v20`, `bl_v21`, `farming_v2`, and `frontier_prvsiyan`.

First exact safety-v3 regression workflow run `36247594877` used GitHub-hosted Ubuntu. All six jobs failed before any steps were provisioned and no job log blob existed. This is infrastructure failure, not a tactical regression result.

A self-hosted Windows X64 serial replacement was created:
`.github/workflows/uploaded-127ed3-safe-v3-public-regression-selfhosted.yml`.
It reconstructs exact safety-v3 and exact v147, records opponent SHA provenance, and evaluates burned seeds `621-624` against each opponent with both seats. Run `36247674737` is queued at the time of this update.

## Environment

Formal workflows target:

- Python 3.11
- `kaggle-environments==1.32.7`
- engine source SHA256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- exact safety-v3 SHA256 `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- exact v147 SHA256 `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`

## Decision

- raw uploaded candidate: immutable parent/reference.
- safety-v3: **KEEP TESTING, PROMOTION CANDIDATE**. Dev, burned stress, raw-isolation, and canonical fresh sealed all passed. Remaining required gates are important-opponent regression plus final runtime/submission preflight.
- global feed2 exact child `a2e69e...`: **REJECT** due direct-parent regression.
- day<=22 feed2 exact child `a397bb...`: **DEV TEST ONLY** pending burned-dev result.
- formal champion remains v147 until the remaining safety-v3 gates pass and a promotion record explicitly changes it.
- no Kaggle submission performed.

## Next action order

1. Complete exact safety-v3 public-opponent regression panel on the self-hosted runner.
2. Verify the already-created safety-v3 final runtime/submission preflight; do not treat its existence as promotion evidence until its result is checked.
3. If public regression and runtime/preflight pass with no material regression, write an explicit safety-v3 PROMOTE record and update `docs/CHAMPION.md`; promotion still does not imply Kaggle submission.
4. Evaluate the day<=22 feed2 child only on burned dev seeds. Keep it separate from the safety-v3 promotion decision unless it produces clear direct-parent improvement and later earns its own full validation path.
5. Exact v134 remains a separate regression item only if byte-exact source becomes available.
