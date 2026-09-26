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

## Orchestration history — 2026-09-27

The first broad gate used a non-transitive auxiliary assertion on `(v153 vs v115) - (v147 vs v115)` and failed despite the direct matched v153-v147 comparison being non-negative on every burned seed. Kaggriculture market interaction means this indirect quantity is not a valid replacement for direct matched candidate-minus-champion evidence. The workflow was corrected so direct v153-v147 matched results are the gate and the v115 lineage comparison is diagnostic only.

Confirmed direct burned evidence on seeds 681..692:

- 8 wins / 0 losses / 4 ties by `candidate_minus_champion`
- mean `+37`
- worst `0`
- best `+150`
- exceptions `0`

A GitHub-hosted hard-gate attempt ended before meaningful match execution and is infrastructure-only evidence, not a v153 tactical regression.

## Static contingency analysis while runner was occupied

No fresh seed was consumed. Existing diagnostic compact-step artifacts were scanned for the exact v153 eligibility shape: steps 288..693, action begins with a contiguous leading SELL block, at least five SELL orders, all distinct items.

These artifacts compare another candidate against v147, so the v147/champion side was inspected explicitly rather than the candidate side.

Observed v147 eligible contexts:

- seed 641 (diagnostic loss context): four contexts on the v147 side — steps 458, 506, 578, 650
- seed 350003 (diagnostic loss context): two contexts — steps 578, 650
- seed 733 (diagnostic win context): zero contexts
- seed 911 (diagnostic win context): one context — step 674

This does not prove that v153 would reorder every eligible block, because eligibility is broader than the final self-exposure sort actually changing the order. It does show that the structural trigger is concentrated in the two known loss contexts and nearly absent in the two win controls.

The focused causal win occurs at step 649. Therefore, if a later sealed or stress panel exposes a regression associated with late activation, the first refinement to test should be a single-condition window tightening around the observed causal region (for example excluding the late step-674 class) rather than changing farm logic, quantities, or the exposure score itself.

## Corrected hard-opponent gate result

Self-hosted run `36256798350` completed successfully after the direct matched gate correction.

Panel: eight hard opponents (`peak_2950`, `salem_2900`, `score_2820`, `jaxa_2802`, `thomas_router_95`, `tetsutani_ms`, `melon_squeeze`, `shop_router_v7`) × seeds 520101..520104 × both seats = 64 games.

Outcome transitions:

- `W→W`: 62
- `L→W`: 2
- regressions (`W→D`, `W→L`, `D→L`): 0
- improvements: 2
- exceptions: 0

Both improvements are the intended causal cell, `score_2820` seed 520104, one in each seat:

- champion margin: -9
- candidate margin: +34
- margin improvement: +43
- candidate-minus-champion final money: +20 per seat

All other 62 games preserved their outcome. Seven of the eight opponents had exactly zero candidate-minus-champion cash delta on all four seed pairs. `score_2820` had mean seed-level cash delta +54.5 with worst 0; aggregate hard-panel seed-level mean was +6.8125 and worst was 0.

This gate therefore shows a narrowly localized benefit with no observed hard-opponent outcome or cash regression. It is materially stronger than the focused result alone, but fresh sealed evidence and runtime/stress remain required before promotion.

## Current decision

KEEP TESTING. Formal champion remains v147. Proceed to runtime/stress on already-consumed seeds; only after that passes may v153 spend a genuinely unused sealed block.
