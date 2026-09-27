# EXP-20260927 v154 sealed declaration — seeds 1801..1812

## Pre-run declaration

This file is committed before any sealed evaluation is started.

- candidate: v154
- champion: exact v147 SHA `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- engine: `kaggle_environments==1.32.7`
- sealed seeds: `1801..1812` inclusive
- seats: both seats / matched pair per seed
- metric: `candidate_minus_champion = candidate - champion`, pair averaged across seats
- purpose: fresh sealed confirmation after focused, direct, hard-panel, and burned stress gates

These seeds must not be inspected, tuned on, or reused before the run. After the first sealed evaluation they are burned regardless of outcome.

## Prior evidence before opening the seal

Burned stress `641..672`, run `36301876016`, completed successfully:

- 32 pairs
- 21W / 2L / 9D
- mean `+21.671875`
- SE `5.12621`
- mean - 2SE `+11.41946`
- worst `-13`
- best `+86`
- seat0 mean `+26.78125`
- seat1 mean `+16.5625`
- candidate exceptions `0`
- champion exceptions `0`

Known hard-panel residual regression is `tetsutani_ms / 520104 = -4`, symmetric across seats and not an outcome flip. There are zero known win-to-loss conversions and one known loss-to-win conversion (`score_2820 / 520104`).

## Acceptance intent

Do not promote from the sealed aggregate alone. Require acceptable worst regression, no exception/timeout issue, seat stability, and replay/telemetry explanation for material differing seeds, followed by dedicated runtime/preflight and important-opponent regression checks.
