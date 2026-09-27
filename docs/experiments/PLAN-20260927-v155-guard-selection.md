# PLAN-20260927 — v155 guard selection from v154 consumed-cell telemetry

Status: exploratory on already-consumed data only. Formal champion remains exact v151. Fresh sealed block 894322..894333 remains unconsumed.

## Objective

Retain the demonstrated v154 loss-to-win mechanism at `score_2820 / seed 520104` while suppressing v154 changed events associated with negative final-cash deltas, especially `peak_2950 / 520103-520104` and `tetsutani_ms` negatives.

## Constraints

- Parent for any v155 candidate is exact v151 SHA256 `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`.
- One tactical mechanism only; do not mix runtime/safety changes.
- No opponent name, seed, seat, or hard-panel identity may be used by the agent.
- Do not weaken the v154 qualification rule after observing v154 results.
- Candidate selection may use only already-consumed telemetry/replay evidence.
- Fresh sealed seeds are not touched until focused + burned + hard + safety/runtime preconditions pass.

## Diagnostic comparison

Capture changed-event features for consumed cells:

- positive causal cell: `score_2820 / 520104`;
- negative contrast: `peak_2950 / 520101..520104`;
- negative contrast: `tetsutani_ms / 520101..520104`;
- burned positive seeds: `682,684,685,687,688,689,690,692`.

For every changed event record step, original/reordered leading SELL block, item quantities, market inventory, and executable self-impact exposure.

## Selection rule

Prefer the simplest general rule supported by the event features. Candidate guard families, in priority order:

1. item-semantic guard if the positive mechanism has a distinct scarce/high-value item signature not shared by negative events;
2. exposure-strength guard if there is a clean, stable separation in executable self-impact magnitude;
3. narrow temporal/state guard only if it is supported across more than the single positive hard cell.

Reject the narrowing idea rather than encode opponent/seed-specific behavior if no simple separator exists.

## Required re-evaluation before sealed

Any v155 candidate must be compared directly against exact v151 with the same sign convention `candidate_minus_champion = candidate - champion` and must:

1. retain the `score_2820 / 520104` both-seat L->W focused result;
2. pass burned 681..692 matched seeds with seat swap and non-negative matched-pair worst;
3. hard 8 x 4 panel: zero outcome regressions, at least one reproduced improvement, and non-negative cash worst under the same pre-registered gate that v154 failed;
4. zero exceptions/internal wrapper errors;
5. runtime characterized on consumed seeds before any fresh sealed spend.

If these conditions are not met, do not consume the reserved sealed block.
