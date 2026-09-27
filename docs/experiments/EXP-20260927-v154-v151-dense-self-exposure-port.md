# EXP-20260927 — v154 exact-v151 dense self-exposure port

## Status

KEEP TESTING. Formal champion remains `v151_none_observation_guard`. No fresh sealed seed spent. No Kaggle submission.

## Parent / champion

- formal champion: `v151_none_observation_guard`
- exact champion SHA256: `54edf1f1663b161457c6d31daccb68b496e5a61dffb6f140f69af2e0b380bf31`
- lineage: v115 -> v147 -> v150 -> v151
- candidate branch: `eval-v154-v151-dense-self-exposure-port-20260927`

## Hypothesis

The v153 dense leading-SELL self-exposure ordering showed a narrowly localized, seat-robust benefit against `score_2820` seed `520104`, but v153 was built on stale formal parent v147. Port exactly that tactical reorder onto exact v151 so that all subsequent evidence is against the current formal champion.

## Changes

One tactical mechanism only:

- steps 288..693, only when the action begins with a contiguous block of at least five distinct SELL items, stable-sort that leading SELL block descending by executable self-impact exposure;
- preserve quantities and never cross the first non-SELL / BUY_PRODUCT barrier.

Compatibility detail: after calling the v151 parent, `observation is None` returns the parent's action unchanged. This preserves v151's existing None-observation safety semantics and is not a new tactical/safety behavior.

## Historical v153 evidence (not v154 promotion evidence)

v153 was built on exact v147, so these results are hypothesis support only:

- burned direct v153-v147 seeds 681..692: 8W / 0L / 4T, mean +37, worst 0, best +150, exceptions 0;
- hard panel: 8 opponents x seeds 520101..520104 x seat swap = 64 games;
- outcome transitions: W->W 62, L->W 2, regressions 0;
- both L->W are `score_2820`, seed 520104, both seats;
- champion margin -9 -> candidate margin +34; candidate-minus-champion final cash +20 per seat; margin improvement +43;
- runtime stress run 36260008638: v153 5,752 calls, median 2.6585 ms, p99 13.2385 ms, max 199.1765 ms, errors 0. The v147 control in the same run had max 210.2851 ms, consistent with previously observed raw-max/GC noise.

## v154 evaluation plan

1. Reconstruct exact v151 and assert champion SHA.
2. Static / syntax check v151 and v154.
3. Verify `observation=None` preserves v151 PASS action and adds no v154 telemetry error.
4. Focused `score_2820`, seed 520104, both seats; require v153's causal behavior to survive the v151 port and telemetry errors = 0.
5. Burned direct v154-v151 seeds 681..692 with seat swap.
6. Hard panel seeds 520101..520104 with seat swap; inspect every transition and worst cash regression.
7. Runtime/stress on already consumed seeds.
8. Only after gates pass, spend a genuinely unused sealed block.
9. Important-opponent regression plus final formal runtime before any PROMOTE.

## Orchestration

Focused run: `36284148569` (triggered via temporary evaluation-only child PR because connector-created branch commits do not themselves trigger the workflow). The child PR must not be merged.

## Decision rule

Do not PROMOTE from v153 historical evidence or the focused cell alone. Formal baseline is exact v151. Require same-seed seat-swap matched evidence, non-negative worst regression on the qualification panels, zero exceptions/timeouts, fresh sealed reproduction, important-opponent regression check, and formal runtime gate.
