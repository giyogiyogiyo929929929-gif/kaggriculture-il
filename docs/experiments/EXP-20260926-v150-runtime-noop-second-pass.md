# EXP-20260926-v150-runtime-noop-second-pass

## Status
KEEP TESTING — focused and full burned action equivalence passed; final runtime and sealed-panel equivalence queued.

## Parent / champion
- parent candidate: `v147_confirmed_v111_clone`
- formal champion: `v115_champion_same_turn_open_squeeze`
- v147 SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`

## Motivation
v147 has strong strategic evidence (burned matched seeds, sealed holdout, hard-opponent stress, public diversity) but its final runtime qualification exceeded the absolute `<200 ms` max threshold. Follow-up paired runtime diagnostics showed that extreme tails are strongly GC-dependent, while targeted cProfile identified `_v111_reorder` as a real hot path on some late turns.

The v147 wrapper calls the parent v115 agent, detects whether the parent's v111 pass changed the action via `_V111_REPORT['changed_turns']`, and then may call `_v111_reorder` again after clone confirmation. When the parent v111 pass made no change, repeating the final reorder is expected to be a redundant no-op. Avoiding that call should reduce candidate enumeration, margin evaluation, temporary allocations, and GC pressure without changing strategic actions.

## Candidate
`v150_skip_noop_second_pass`

Builder: `ci/build_v150_skip_noop_second_pass.py`

### Change
One guard only:

- v147: run confirmed second `_v111_reorder` whenever clone/standard gates pass.
- v150: run that second pass only when `parent_changed` is also true.

No farm policy, market scoring, SELL quantity, order priority, prediction, race detection, or endgame parameter is changed.

## Hypothesis
If the parent v111 pass did not change the final market action, a second deterministic v111 pass on the same final action should be a no-op. Skipping such calls should therefore preserve v147 action traces while lowering runtime and allocation pressure.

## Duplicate-candidate probe
Run `36245268147` completed successfully.

- evaluated candidates: 436,786
- duplicate evaluated candidates: 72
- duplicate fraction: ~0.0165%
- known heavy 20,160-candidate late steps had no useful duplicate concentration

Decision on the alternative factor-cache idea: REJECT. Duplicate reuse is too rare to explain or materially reduce the hot path.

## Focused equivalence/runtime result
Run `36245566714` completed successfully.

Seeds: `681,682,689,691,692`, both seats, 2 repetitions.

Correctness:
- candidate calls compared: 14,380 per version
- complete v147/v150 action traces: identical in every tested game
- final rewards: identical in every tested game
- mismatches: 0
- exceptions: 0
- v147 and v150 `second_pass_changed` counts: identical for every row

Work reduction:
- total `_V111_REPORT.evaluations`, v147: 26,724
- total `_V111_REPORT.evaluations`, v150: 22,052
- reduction: 4,672 evaluations = ~17.48%

GC-on wall-clock summary:

| metric | v147 | v150 |
|---|---:|---:|
| median | 4.379 ms | 4.297 ms |
| p95 | 9.881 ms | 10.478 ms |
| p99 | 18.821 ms | 18.378 ms |
| >50 ms | 51 | 42 |
| >200 ms | 2 | 3 |
| max | 798.094 ms | 1620.081 ms |

Interpretation:
- The focused panel supports semantic equivalence and confirms a real reduction in v111 search work.
- Median and p99 improve slightly; >50 ms calls also fall.
- Absolute max remains dominated by rare GC/tail events and is not improved in this one run; v150 recorded a 1.62 s spike on seed 691 seat 0 despite an otherwise identical action trace. This prevents treating the focused timing sample as a formal runtime PASS.
- Because paired tail diagnostics already showed large GC spikes in both v115 and v147, max must be reassessed with the established GC-on paired protocol rather than inferred from one raw maximum.

## Full burned action-equivalence result
Run `36249173738` completed successfully.

Seeds: `681..692`, both seats, one comparison per seat = 24 games.

Correctness:
- complete v147/v150 action traces: identical in all 24 games
- final rewards: identical in all 24 games
- mismatches: 0
- exceptions: 0

Work reduction:
- total `_V111_REPORT.evaluations`, v147: 29,058
- total `_V111_REPORT.evaluations`, v150: 22,710
- reduction: 6,348 evaluations = 21.8459632459%

Per-seed behavior remained action-equivalent even where the amount of work removed varied substantially. Seed 687, for example, dropped from 3,180 to 1,967 v111 evaluations per seat while returning the exact same actions and rewards.

Interpretation:
- The broader burned panel strengthens the claim that v150 is a runtime-only implementation change rather than a strategic change.
- This is still not sufficient by itself to inherit every v147 opponent/holdout result, because different opponents can induce different observations. A sealed-panel equivalence check and final runtime qualification are therefore queued.

## Validation plan
1. Build exact v115 and v147 and verify their known SHA256 values. PASS.
2. Build v150 and `py_compile` all three agents. PASS.
3. Focused complete action-equivalence test. PASS.
4. Focused runtime/work reduction. PASS for work reduction; formal runtime still unresolved due GC tail.
5. Expand complete action equivalence to all burned seeds `681..692`, both seats. PASS.
6. Verify complete v147/v150 action equivalence on the prior sealed panel `1701..1712`, both seats. QUEUED.
7. Run fresh sequential GC-on runtime qualification for v150 with v115/v147 controls under the same instrumentation. QUEUED.
8. If runtime is satisfactory, run/verify the important known-opponent regression gate for v150 before any PROMOTE.
9. Formal champion remains v115 until all gates pass.

## Runs
- duplicate-candidate diagnostic: `36245268147` — success
- focused v150 equivalence/runtime: `36245566714` — success
- full burned action equivalence: `36249173738` — success
- v150 final runtime qualification: `36252343922` — queued
- v150 sealed action equivalence: `36252365551` — queued

## Decision
KEEP TESTING.
