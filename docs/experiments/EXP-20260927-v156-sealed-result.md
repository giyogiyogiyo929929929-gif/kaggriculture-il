# EXP-20260927 — v156 fresh sealed result

## Identity

- formal champion: `v151_none_observation_guard`
- v151 SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- candidate: `v156`
- v156 SHA256: `14f142f9ca933a208150895e60fa3ee5838d6230782e7fa7807707280b26bcdb`
- engine: `kaggle_environments==1.32.7`
- metric: `candidate_minus_champion = candidate - champion`

## Reservation

The block was preregistered before first execution in `docs/experiments/SEALED-RESERVATION-20260927-v156.md` using:

`start = 700000 + int(candidate_sha256[:8], 16) % 200000`

This produced fresh seeds `855641..855652`, 12 matched seeds with both seats. The block is now consumed and must not be reused as fresh evidence.

## First sealed execution

- workflow run: `36310398164`
- artifact: `v156-v151-sealed-855641-855652`
- PR #14: closed without merge after result collection
- exact v151/v156 SHA assertions: PASS
- pairs: `12`
- wins / losses / ties: `5 / 0 / 7`
- mean candidate_minus_champion: `+24.3333333333`
- SE: `11.7752522545`
- mean - 2*SE: `+0.7828288244`
- worst: `0`
- best: `+135`
- candidate exceptions: `0`
- champion exceptions: `0`

Per-seed matched deltas:

- 855641: `+41`
- 855642: `+135`
- 855643: `0`
- 855644: `+62`
- 855645: `0`
- 855646: `0`
- 855647: `0`
- 855648: `0`
- 855649: `+17`
- 855650: `0`
- 855651: `0`
- 855652: `+37`

For every seed, the two seat legs produced the same candidate-minus-champion delta. The sealed improvement is therefore not driven by seat asymmetry in this block.

Preregistered gate required: 12 pairs, zero exceptions, zero matched losses, worst >=0, at least one win, and mean - 2*SE >0. All conditions passed.

## Post-consumption telemetry replay

Telemetry was replayed only after the first sealed evaluation consumed the seeds:

- games: `24`
- eligible: `14`
- changed: `10`
- ahead_skips: `338`
- exposure_skips: `20`
- errors: `0`

Changed actions occurred on the same positive seed subset in both seats for seeds 855641, 855642, 855644, 855649 and 855652. This provides causal consistency with the measured positive deltas while the no-change / gated seeds tied.

## Decision

SEALED PASS. Continue with consumed public-diversity and strength/climb-band regression, then strict final runtime and final package/preflight. Formal champion remains v151 until all remaining promotion gates pass. No Kaggle submission performed.
