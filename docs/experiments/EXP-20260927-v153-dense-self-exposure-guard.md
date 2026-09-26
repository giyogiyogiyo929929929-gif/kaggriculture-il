# EXP-20260927 — v153 dense self-exposure guard

## Status

KEEP TESTING. Formal champion remains v147. No fresh sealed seed spent by this experiment yet. No Kaggle submission.

## Parent / champion

- formal champion: v147
- exact v147 SHA256: `8b755e96f7d294f23297e3d452ee8b16966afbdfc440972a826d92621cbcf923`
- tactical parent: v152 experiment (`EXP-20260926-v152-dense-self-exposure.md`), reconstructed from exact v147

## Hypothesis

Dense multi-item leading SELL blocks can lose cash to order-index races. Existing r37 public rival-standing exposure does not measure the executable stock exposure of our own batch. Ranking only a dense leading block by self-impact exposure can protect the item whose price curve is most vulnerable if an equal-size same-item batch reaches the market first.

v152 already isolated the intended causal cell against `score_2820`, seed `520104`, step `649`, but its telemetry wrapper had a robustness bug: when the parent action's first market order was an empty list (`[]`), the test `orders[0][0]` raised `IndexError`. The broad wrapper catch returned the original action, so match play remained valid, but telemetry recorded 11 exceptions per game. PROMOTE requires zero exceptions.

## Changes

One tactical mechanism plus one robustness bugfix:

1. Same v152 tactic: during steps 288..693, only when the action begins with a contiguous block of at least five distinct SELL items, stable-sort that leading SELL block descending by self-impact exposure. Preserve quantities and never cross the first non-SELL / BUY_PRODUCT barrier.
2. Add an explicit empty-leading-order guard: if `orders[0]` is empty, return the original action unchanged before indexing it.

The robustness guard intentionally preserves v152's effective action semantics on those steps: v152 caught the exception and returned the original action; v153 returns the original action without throwing.

## v152 focused precursor evidence

Existing self-hosted focused run `36250312541`, opponent `score_2820`, seed `520104`, both seats:

- candidate v152: money 1138, opponent 1104, margin +34, outcome W in both seats
- champion v147: money 1118, opponent 1127, margin -9, outcome L in both seats
- candidate_minus_champion cash: +20 in each seat
- margin improvement: +43 in each seat
- transition: L→W in both seats
- match-level agent errors: 0 for candidate and champion
- v152 telemetry: eligible=3, changed=1, errors=11; changed step was 649 and estimated self-impact delta was 57

Root cause of all 11 telemetry exceptions was the empty-leading-order access, not the tactical reorder or engine execution.

## Environment

Target evaluation environment: `kaggle_environments==1.32.7`, Python 3.11, exact v147 reconstruction and SHA assertion before candidate build.

## Evaluation plan

1. Static / syntax build from exact v147.
2. Focused `score_2820`, seed 520104, both seats. Require the same L→W behavior and zero v153 telemetry errors; expected activation remains only the causal step 649 (`eligible=3`, `changed=1`).
3. Burned direct v147 seeds 681..692, both seats; evaluate outcome transitions first, then cash deltas and net market revenue where relevant.
4. Hard panel seeds 520101..520104 with seat swap; inspect every outcome difference and any worst regression.
5. Stress/runtime and exception check.
6. Only after the above gates, use a fresh sealed block. Do not reuse previously consumed sealed1 seeds as fresh evidence.
7. Important known-opponent regression and final runtime before any PROMOTE.

## Promotion criteria

Do not promote on the focused win alone. Require no W→L regression in matched hard/burned evaluation, zero exceptions/timeouts, seat-robust benefit, and fresh sealed reproduction. Formal champion remains v147 until those conditions and the project-wide PROMOTE criteria are met.

## Initial decision

KEEP TESTING.
