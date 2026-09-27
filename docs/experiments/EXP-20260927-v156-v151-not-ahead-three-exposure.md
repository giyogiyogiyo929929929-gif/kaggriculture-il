# EXP-20260927 — v156 exact-v151 not-ahead + three-exposure guard

## Status

PREPARED / NOT YET RUN. Formal champion remains `v151_none_observation_guard`.

No fresh sealed seeds consumed. No Kaggle submission.

## Parent / identity

- formal champion / source parent: exact `v151_none_observation_guard`
- v151 SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- v156 branch: `eval-v156-v151-not-ahead-three-exposure-20260927`
- v156 is reconstructed directly from exact v151; it does not use generated v155 or v154 source as its input.

## Hypothesis

The v154 dense leading-SELL reorder has a reproducible loss-to-win cell against `score_2820 / 520104`, but also small cash regressions in preserved wins. The v155 `do not reorder while already ahead in cash` guard removes the historical `peak_2950` regressions on the stale-v147 test, but leaves `tetsutani_ms / 520104 = -4`.

Consumed-cell diagnostics show a structural distinction in the remaining trailing/tie cases:

- positive `score_2820 / 520104`, step 649: exposure values include `57, 35, 14, 0, 0` — three SELL items have exposure >= 10;
- negative `tetsutani_ms / 520104`, step 649: `57, 35, 4, 0, 0` — only two items have exposure >= 10;
- negative `tetsutani_ms / 520101`, step 673: `9, 8, 4, 0, 0` — zero items >= 10;
- negative `tetsutani_ms / 520102`, step 505: `12, 4, 3, 2, 0` — one item >= 10;
- another `tetsutani_ms / 520102` changed event, step 577: `23, 16, 12, 2, 1` — three items >= 10 and historical matched delta is slightly positive overall.

Historical burned-positive events are also generally multi-item exposure states: the useful seeds contain at least one changed event with three exposures >= 10. This suggests the tactic is safer when the market race is genuinely multi-item rather than when only one or two items have material self-impact.

## Single change relative to v155

Keep all v155 conditions, and additionally require:

`count(self_exposure >= 10.0) >= 3`

inside the leading distinct SELL block before reordering.

The threshold `10.0` is a round, preregistered development threshold chosen from already-consumed diagnostics. It is not fresh evidence. Do not adjust it after seeing v156 evaluation results.

No opponent name, seed, seat, or hard-cell identifier is used by the agent.

## Evaluation order

Do not run v156 before exact-v151 v155 focused result is known. If v155 unexpectedly passes the strict focused gate, continue v155 instead and leave v156 unrun.

If v155 reproduces the stale-parent `tetsutani -4` failure:

1. exact v151 reconstruction + SHA assertion;
2. py_compile / `None` safety;
3. focused consumed cells: `score_2820 / 520104`, `peak_2950 / 520101..520104`, `tetsutani_ms / 520101..520104`, both seats;
4. require score improvement >0, zero exceptions, and focused cash worst >=0 for peak and tetsutani;
5. burned 681..692 with seat swap, require matched worst >=0;
6. full hard 8-opponent panel with seat swap, require zero outcome regressions, at least one improvement, and cash worst >=0;
7. internal telemetry / malformed preflight;
8. repeated-control runtime methodology;
9. only then reserve a new SHA-derived fresh sealed block for v156. Do not reuse v154's reserved `894322..894333` as v156 fresh evidence.

## Decision

PREPARED only. No PROMOTE decision and no sealed evidence yet.
