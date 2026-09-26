# EXP-20260927 — public transfer dedup audit

## Status

STATIC AUDIT / CLOSED for the guarded four-turn sale reservation transfer. Formal champion remains v147. No new seed consumed by this audit. No Kaggle submission.

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

## Recovered public-room-guard screen

The old public-room-guard run `36132699144` completed successfully against exact v115. Its artifact was re-read without running any new games.

Direct seeds 681..692:

- 9 positive / 1 negative / 2 zero candidate-minus-champion pairs
- mean `+49.67`
- worst `-84` on seed 689
- best `+492`
- exceptions 0

Old easy public panel, 6 opponents x 4 seeds:

- 9 positive / 12 negative / 3 zero candidate-minus-champion rows
- mean `+40.83`
- worst `-4`
- exceptions 0

These are cash-delta diagnostics rather than outcome-transition evidence. They show activity but not clean safety, and the evaluation parent was v115 rather than current v147. There is no reason to spend new seeds on this mechanism before the stronger v153 line is resolved.

Decision for current queue: public-room-guard is HOLD / LOW PRIORITY, not an active candidate. Revisit only if current replay telemetry identifies shed-capacity overflow as a repeated cause of actual losses.

## Sparse Shop Hybrid source check

The public notebook page for Kaito Fukami's `103-128-fresh-public-v43-sparse-shop-hybrid` is still available and reports Apache-2.0. The project already has a published `main.py` SHA-256 (`69f06a802b62aa08f28705dab5728eb924bb6a7c23ffe0164f65b104cc3dadf3`) and summarized branch behavior in the older transfer-priority log.

However the current static audit has not recovered the exact source body from the repository or Kaggle page. Do not implement an inferred YARN branch from prose. Require the audited source or an equivalent exact artifact before comparing it to v147 internals.

## Decision

- guarded four-turn sales transfer: CLOSED AS ALREADY PRESENT
- public-room-guard: HOLD / LOW PRIORITY
- Sparse Shop Hybrid: STATIC AUDIT ONLY; source body required before implementation
- six-sheep / broad production expansion: HOLD
- continue v153 dense self-exposure evaluation

## Next hypothesis discipline

If v153 fails a hard-panel cell, derive one gating refinement from the exact regression replay. Do not jump to an unrelated public transfer. If v153 passes, proceed through runtime/stress and unused sealed evaluation before combining any orthogonal mechanism.
