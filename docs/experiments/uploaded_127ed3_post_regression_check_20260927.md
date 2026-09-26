# uploaded 127ed3 safety-v3 post-regression check — 2026-09-27 JST

## Champion / candidate

- formal champion: `v147_candidate_confirmed_v111_clone.py`
- champion SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- safety-v3 SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- parent raw SHA256: `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`

## Existing positive evidence

- formal dev: 8W/2L/0D vs v147, mean `+688.5`.
- burned stress: 11W/1L/0D vs v147, mean `+856.6667`, mean-2SE `+360.1307`.
- raw-isolation: safety-v3 and raw parent exactly equal on all 20 per-seat games.
- canonical precommitted sealed: 11W/1L/0D, mean `+722.625`, mean-2SE `+398.5356`, worst `-39`, exceptions `0`, short games `0`.

## Final preflight — PASS

Actions run `36247002100` completed successfully.

Verified:

- `kaggle-environments==1.32.7`
- Kaggriculture engine source SHA256 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`
- exact raw parent reconstruction
- exact safety-v3 reconstruction
- static audit / Kaggle loader safety
- broken-observation fallback checks
- official-engine full 720-turn smoke in both seats: DONE, zero errors
- exact submission archive containing only `main.py`

Final package metadata:

- `main.py` SHA256: `87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df`
- archive SHA256: `370e478315ab7756e8bbb1f474822439c5f8db6614f86fac8926c15528423111`
- archive bytes: `178991`

## Public-opponent money regression panel — completed, requires outcome-flip follow-up

Self-hosted Actions run `36247674737` completed successfully on burned seeds `621-624`, both seats, exact safety-v3 and exact v147.

Primary metric in this workflow was candidate final money minus champion final money against the same opponent/seed/seat. This is useful for regression detection but is not the competition-primary win/loss metric.

Per-opponent summary:

- `starter`: W/L/D by money-delta seeds `0/4/0`, mean `-2812.0`, worst `-9690.0`.
- `beat_v48`: `1/3/0`, mean `-7074.25`, worst `-22559.0`, best `+24484.0`.
- `bl_v20`: `2/2/0`, mean `+337.875`, worst `-963.0`, best `+2615.5`.
- `bl_v21`: `1/3/0`, mean `+56.375`, worst `-961.0`, best `+2628.5`.
- `farming_v2`: `1/3/0`, mean `-7251.5`, worst `-22718.0`, best `+24508.0`.
- `frontier_prvsiyan`: `3/1/0`, mean `+72.5`, worst `-727.0`, best `+527.0`.
- candidate/champion exceptions: `0` for every opponent.

`starter`, `beat_v48`, and `farming_v2` therefore show substantial final-money regression versus v147. However, this workflow did not record whether those money changes flip actual game wins/losses versus the public opponent. Because Kaggriculture promotion prioritizes final-money win/loss over margin magnitude, this result blocks immediate promotion but is not by itself a final REJECT.

A dedicated outcome-flip workflow was created:

- workflow: `.github/workflows/uploaded-127ed3-safe-v3-public-outcome-flips.yml`
- commit: `ba110c20da6e8b27c5debab6a2ab04a23c781377`
- run: `36252342056`
- seeds: burned `621-624`
- opponents: `starter`, `beat_v48`, `bl_v20`, `bl_v21`, `farming_v2`, `frontier_prvsiyan`
- records actual candidate-vs-opponent and champion-vs-opponent W/L/D for each seed and seat, favorable flips, regression flips, and raw final money.
- status at creation: queued.

## CARROT2 day<=22 — REJECT

Actions run `36247703056` completed successfully on the already-burned ten-seed dev block.

Candidate SHA256: `a397bb19046e82a50fee5701df882af3700d7727747089ff2b1f2c2384bb6ed5`.

Candidate minus exact safety-v3 parent:

- W/L/D: `0/4/6`
- mean: `-140.4`
- median: `0`
- SE: `100.7128`
- mean-2SE: `-341.8256`
- worst: `-1028` on seed `641`
- best: `0`
- exceptions: `0/0`

Per-seed direct-parent deltas:
`641 -1028, 350003 -62, 101 0, 211 0, 347 0, 509 0, 733 0, 911 0, 1201 -151, 1601 -163`.

Although candidate minus v147 was `8/2/0`, mean `+686.6`, it strictly worsened its direct safety-v3 parent and never improved any burned seed. Decision: REJECT. Do not allocate sealed seeds.

## Decision

- formal champion remains v147.
- safety-v3 remains the leading promotion candidate, but **DO NOT PROMOTE yet** because the important-opponent panel shows large money regressions whose actual win/loss impact has not yet been resolved.
- final preflight is PASS.
- global feed2 and day<=22 feed2 are both REJECTED.
- next gate: exact public-opponent outcome-flip run `36252342056`.
- no Kaggle submission performed.
