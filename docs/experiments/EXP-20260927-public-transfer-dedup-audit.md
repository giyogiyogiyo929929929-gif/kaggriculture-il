# EXP-20260927 — public transfer dedup audit

## Status

STATIC AUDIT / CLOSED for the guarded four-turn sale reservation transfer. Formal champion remains v147. No seed consumed. No Kaggle submission.

## Why this audit was done

While the v153 hard gate was using the self-hosted runner, old public-notebook transfer priorities were rechecked so that runner idle time would not cause duplicate experiments.

The older priority document listed the public V36 / Market-Smart guarded four-turn sale reservation as a top transfer candidate against v115.

## Evidence recovered from the original v145 run

Original Actions run: `36133205261`, branch `eval-v115-v145-public-four-turn-sales-20260925`.

The run reached exact-v115 reconstruction successfully, then `ci/build_v145_public_four_turn_sales.py` intentionally stopped with:

`exact v115 already appears to contain public four-turn override`

Therefore no direct or public-panel games were run for v145. The reported workflow failure is not an agent failure; it is a static deduplication result showing that the proposed mechanism was already present in the exact parent.

The intended v145 change was only to replace the existing sale-reservation horizon with a minimum horizon of four during steps 288..695 while preserving the existing block-boundary and terminal guards. The builder detected that exact v115 already contained the public four-turn override and refused to create a duplicate candidate.

## Implication for current lineage

Current formal champion v147 is reconstructed from exact v115 and then adds the confirmed-v111-clone overlay. Therefore the four-turn sale reservation is inherited by v147 as part of the parent lineage.

Do not create another candidate whose main change is this same four-turn reservation unless a later code audit proves the inherited mechanism was removed or materially changed.

## Decision

- guarded four-turn sales transfer: CLOSED AS ALREADY PRESENT
- do not spend development or sealed seeds on this mechanism again
- remove it from the active next-candidate queue
- continue v153 dense self-exposure evaluation

## Remaining public-transfer queue

1. Sparse Shop Hybrid: static audit only; first prove that v147 lacks an equivalent observable YARN branch and that compatible continuations exist before implementing anything.
2. public-room-guard: lower priority; only revisit if outcome-centric evidence suggests capacity overflow is causing losses.
3. six-sheep / broad production expansion: hold until market-only hypotheses are exhausted or telemetry identifies a repeatable production deficit.

## Next hypothesis discipline

If v153 fails a hard-panel cell, derive one gating refinement from the exact regression replay. Do not jump to an unrelated public transfer. If v153 passes, proceed through runtime/stress and unused sealed evaluation before combining any orthogonal mechanism.
