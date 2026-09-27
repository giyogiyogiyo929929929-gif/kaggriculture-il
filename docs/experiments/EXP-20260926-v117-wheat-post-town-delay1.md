# EXP-20260926 — v117_wheat_post_town_delay1

## Status

**REJECT — no activation**

Formal champion remains `v112_wheat_lead3_lowdemand`.

This candidate belongs only to the current v90→…→v112 lineage. It is a sibling of v116 and was built directly on v112; it was never stacked with the separate v130+ lineage.

## Parent / candidate

- champion / parent: `v112_wheat_lead3_lowdemand`
- candidate: `v117_wheat_post_town_delay1`
- canonical engine: `kaggle_environments==1.32.7`
- sign: `candidate_minus_champion = candidate - champion`
- v112 SHA-256: `1c6e00ff0bd46b16189b1f6a93ce5e498ff8ffb5b0acb33591cdd247cd8b4771`
- v117 SHA-256: `65ba577e826a4ebc0c48e4b20749d8ea650d964866c54c6ce62cb3fa89e06565`
- canonical self-hosted run: `36258359316`
- self-hosted runner: `CIYOI`, Windows X64, runner 2.337.0, Python 3.11.9

## Hypothesis

v111 showed that high-WHEAT-demand worlds can benefit from waiting through Town consumption instead of selling earlier. v112 therefore allows late lead3 only when WHEAT-demanding unlocked shop count is at most 3.

v117 tested the reverse direction in high-demand worlds: delay an otherwise untouched native late-batch WHEAT SELL by exactly one turn when the current step is a deterministic WHEAT Town-consumption tick, existing WHEAT market inventory is positive, and several safety gates pass. The intent was to let Town remove inventory before the delayed SELL.

## Tactical change

A native late-batch WHEAT SELL could be delayed one turn only when all of the following held:

1. `step >= 300` and a next step exists;
2. static schedule and post-v112 action contain the same native WHEAT quantity;
3. no active future v112 WHEAT lead repayment;
4. WHEAT-demanding unlocked shop count >= 4;
5. current step is a deterministic WHEAT Town-demand tick;
6. current public WHEAT market inventory > 0;
7. current market action is SELL-only;
8. next static market action has repayment headroom;
9. no native WHEAT SELL at step+2/+3/+4.

Activation removed the exact native WHEAT quantity now and repaid it at step+1. Repayment shortfall was a hard rejection condition.

## Focused checks

`experiments/v112_v116_milk_micro/test_v117_suffix_synthetic.py` passed the designed activation, merge, low-demand, zero-inventory, BUY/cash, slot-pressure, parent-lead, and near-future-WHEAT cases.

Result: `v117 synthetic checks: PASS`.

The byte-stable source builder reconstructed the canonical sources successfully on Windows. Evaluator loading was also corrected before this canonical run to use explicit module entrypoints / callable fallback and sibling-import paths.

## Canonical exact evaluation

GitHub Actions run `36258359316` executed on the self-hosted `CIYOI` runner with `kaggle_environments==1.32.7`.

Same-seed + seat-swap results:

| block | seeds | W | L | D | mean candidate_minus_champion | worst | best |
|---|---:|---:|---:|---:|---:|---:|---:|
| validation | 296001–296012 | 0 | 0 | 12 | 0.0 | 0.0 | 0.0 |
| sealed | 297001–297004 | 0 | 0 | 4 | 0.0 | 0.0 | 0.0 |
| stress | 298001–298008 | 0 | 0 | 8 | 0.0 | 0.0 | 0.0 |

All 24 matched seed pairs were exactly identical to v112.

Starter regression was also identical to v112 on seeds 1–5: both candidates won all 5 matched starter comparisons with the same pair differences `[151790, 157276, 185415, 163990, 148593]`.

## Telemetry

Canonical telemetry showed no tactical activation:

- validation: `shifts=0`, `errors=0`, `repay_shortfalls=0`
- sealed: `shifts=0`, `errors=0`, `repay_shortfalls=0`
- stress: `shifts=0`, `errors=0`, `repay_shortfalls=0`
- activation steps: none

The dominant blocks were parent lead-state interaction and near-future native WHEAT conflicts; e.g. validation recorded `parent_shift_blocks=96` and `future_wheat_blocks=22`.

This means the candidate logic is synthetically valid but its full conjunction of real-game gates does not occur in the tested canonical distribution.

## Runtime

Canonical runtime pair seed `800501`:

- callbacks: 1438
- median: ~0.553 ms
- p99: ~1.054 ms
- max: ~1.616 ms
- callback errors: 0

Runtime is comfortably inside the project gate. Runtime was not the rejection reason.

## Bronze external panel

The external panel was intentionally not executed after the activation gate failed. With `shifts=0`, external H2H would only reproduce v112 and provide no tactical evidence.

## Decision

**REJECT — no activation.**

The predeclared gate was `shifts == 0 → REJECT`. Canonical validation + sealed + stress produced zero activations and exact equality with v112, so no further evaluation is justified.

Do not repeat the same conjunction of v117 gates. A future Town-consumption timing experiment would need materially different, telemetry-supported eligibility conditions rather than merely widening the seed set.

Formal champion remains `v112_wheat_lead3_lowdemand`.
